#include "equilibrium/core/activated_equilibrium_nlp.h"

#include "equilibrium/core/route_metadata.h"
#include "model/native_types.h"

#include <algorithm>
#include <cmath>
#include <limits>
#include <utility>

namespace epcsaft::native::equilibrium_nlp {

namespace {

std::vector<int> phase_kind_tokens(const std::vector<std::string>& phase_kinds) {
    std::vector<int> out;
    out.reserve(phase_kinds.size());
    for (const std::string& phase_kind : phase_kinds) {
        if (phase_kind == "liquid") {
            out.push_back(0);
        } else if (phase_kind == "vapor") {
            out.push_back(1);
        } else {
            throw ValueError("activation-nlp-ineligible: unsupported phase kind in activation plan.");
        }
    }
    return out;
}

void require_activated_neutral_two_phase_plan(
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout
) {
    if (!((plan.family_key == "neutral_tp_flash" && plan.route == "neutral_tp_flash")
          || (plan.family_key == "neutral_lle" && plan.route == "neutral_lle"))) {
        throw ValueError("activation-nlp-ineligible: only activation-matrix neutral two-phase routes are supported.");
    }
    if (layout.family_key != plan.family_key || layout.route != plan.route) {
        throw ValueError("activation-nlp-ineligible: variable layout route does not match activation plan.");
    }
    if (layout.variable_model != plan.variable_model || layout.variable_count <= 0) {
        throw ValueError("activation-nlp-ineligible: variable layout does not match activation plan model.");
    }
}

std::unique_ptr<NlpProblem> make_delegate(
    const add_args& args,
    const epcsaft::native::equilibrium::ActivationPlan& plan
) {
    if (plan.route == "neutral_tp_flash") {
        return make_neutral_tp_flash_eos_problem(
            args,
            plan.temperature,
            plan.pressure,
            plan.feed_composition,
            "neutral_tp_flash_eos"
        );
    }
    return make_neutral_two_phase_eos_problem_from_feed(
        args,
        plan.temperature,
        plan.pressure,
        plan.feed_composition,
        phase_kind_tokens(plan.phase_kinds),
        "neutral_lle_eos",
        1.0e-8
    );
}

NeutralTwoPhaseEosNlpContract make_activated_contract(
    const ActivatedEquilibriumNlp& problem,
    int phase_count,
    int species_count
) {
    validate_nlp_problem_shape(problem);

    const std::vector<double> initial = problem.initial_point();
    const NlpBounds bounds = problem.bounds();
    const NlpJacobianStructure structure = problem.jacobian_structure();
    const NlpScaling scaling = problem.scaling();
    const std::vector<double> constraints = problem.constraints(initial);
    const std::map<std::string, std::string> diagnostics = problem.diagnostics();

    NeutralTwoPhaseEosNlpContract out;
    out.problem_name = problem.name();
    out.derivative_backend = "analytic_cppad";
    const auto activation_compiler = diagnostics.find("activation_compiler");
    out.activation_compiler =
        activation_compiler == diagnostics.end() ? "" : activation_compiler->second;
    const RouteMetadata metadata = route_metadata_from_diagnostics(diagnostics);
    out.variable_model = metadata.variable_model;
    out.density_backend = metadata.density_backend;
    out.residual_families = metadata.residual_families;
    out.constraint_families = metadata.constraint_families;
    out.phase_count = phase_count;
    out.species_count = species_count;
    out.variable_count = problem.variable_count();
    out.constraint_count = problem.constraint_count();
    out.jacobian_nonzero_count = problem.jacobian_nonzero_count();
    out.exact_hessian_available = problem.has_exact_hessian();
    out.hessian_nonzero_count = problem.hessian_nonzero_count();
    out.hessian_backend = problem.hessian_backend();
    out.initial_point = initial;
    out.variable_lower_bounds = bounds.variable_lower;
    out.variable_upper_bounds = bounds.variable_upper;
    out.constraint_lower_bounds = bounds.constraint_lower;
    out.constraint_upper_bounds = bounds.constraint_upper;
    out.objective_at_initial = problem.objective(initial);
    out.gradient_at_initial = problem.objective_gradient(initial);
    out.constraints_at_initial = constraints;
    out.jacobian_rows = structure.rows;
    out.jacobian_cols = structure.cols;
    out.jacobian_values_at_initial = problem.jacobian_values(initial);
    out.objective_scaling = scaling.objective;
    out.variable_scaling = scaling.variables;
    out.constraint_scaling = scaling.constraints;
    out.initial_variable_lower_margin = std::numeric_limits<double>::infinity();
    out.initial_variable_upper_margin = std::numeric_limits<double>::infinity();
    out.initial_amount_lower_margin = std::numeric_limits<double>::infinity();
    out.initial_volume_lower_margin = std::numeric_limits<double>::infinity();
    for (int index = 0; index < problem.variable_count(); ++index) {
        const std::size_t i = static_cast<std::size_t>(index);
        const double lower_margin = initial[i] - bounds.variable_lower[i];
        const double upper_margin = bounds.variable_upper[i] - initial[i];
        out.initial_variable_lower_margin = std::min(out.initial_variable_lower_margin, lower_margin);
        out.initial_variable_upper_margin = std::min(out.initial_variable_upper_margin, upper_margin);
        const bool is_volume = species_count > 0 && (index % (species_count + 1)) == species_count;
        if (is_volume) {
            out.initial_volume_lower_margin = std::min(out.initial_volume_lower_margin, lower_margin);
        } else {
            out.initial_amount_lower_margin = std::min(out.initial_amount_lower_margin, lower_margin);
        }
    }
    out.initial_variable_bound_margin =
        std::min(out.initial_variable_lower_margin, out.initial_variable_upper_margin);
    out.initial_constraint_bound_violation = 0.0;
    for (int index = 0; index < problem.constraint_count(); ++index) {
        const std::size_t i = static_cast<std::size_t>(index);
        if (constraints[i] < bounds.constraint_lower[i]) {
            out.initial_constraint_bound_violation =
                std::max(out.initial_constraint_bound_violation, bounds.constraint_lower[i] - constraints[i]);
        }
        if (constraints[i] > bounds.constraint_upper[i]) {
            out.initial_constraint_bound_violation =
                std::max(out.initial_constraint_bound_violation, constraints[i] - bounds.constraint_upper[i]);
        }
    }
    if (!std::isfinite(out.initial_amount_lower_margin)) {
        out.initial_amount_lower_margin = 0.0;
    }
    if (!std::isfinite(out.initial_volume_lower_margin)) {
        out.initial_volume_lower_margin = 0.0;
    }
    return out;
}

}  // namespace

ActivatedEquilibriumNlp::ActivatedEquilibriumNlp(
    const add_args& args,
    epcsaft::native::equilibrium::ActivationPlan plan,
    epcsaft::native::equilibrium::VariableLayout layout
)
    : plan_(std::move(plan)),
      layout_(std::move(layout)),
      delegate_(make_delegate(args, plan_)) {
    require_activated_neutral_two_phase_plan(plan_, layout_);
    if (!delegate_) {
        throw ValueError("activation-nlp-ineligible: two-phase delegate was not created.");
    }
    if (delegate_->variable_count() != layout_.variable_count) {
        throw ValueError("activation-nlp-ineligible: compiled NLP variable count does not match layout.");
    }
}

std::string ActivatedEquilibriumNlp::name() const {
    return delegate_->name();
}

int ActivatedEquilibriumNlp::variable_count() const {
    return delegate_->variable_count();
}

int ActivatedEquilibriumNlp::constraint_count() const {
    return delegate_->constraint_count();
}

int ActivatedEquilibriumNlp::jacobian_nonzero_count() const {
    return delegate_->jacobian_nonzero_count();
}

NlpBounds ActivatedEquilibriumNlp::bounds() const {
    return delegate_->bounds();
}

std::vector<double> ActivatedEquilibriumNlp::initial_point() const {
    return delegate_->initial_point();
}

double ActivatedEquilibriumNlp::objective(const std::vector<double>& variables) const {
    return delegate_->objective(variables);
}

std::vector<double> ActivatedEquilibriumNlp::objective_gradient(
    const std::vector<double>& variables
) const {
    return delegate_->objective_gradient(variables);
}

std::vector<double> ActivatedEquilibriumNlp::constraints(const std::vector<double>& variables) const {
    return delegate_->constraints(variables);
}

NlpJacobianStructure ActivatedEquilibriumNlp::jacobian_structure() const {
    return delegate_->jacobian_structure();
}

std::vector<double> ActivatedEquilibriumNlp::jacobian_values(
    const std::vector<double>& variables
) const {
    return delegate_->jacobian_values(variables);
}

bool ActivatedEquilibriumNlp::has_exact_hessian() const {
    return delegate_->has_exact_hessian();
}

int ActivatedEquilibriumNlp::hessian_nonzero_count() const {
    return delegate_->hessian_nonzero_count();
}

NlpHessianStructure ActivatedEquilibriumNlp::hessian_structure() const {
    return delegate_->hessian_structure();
}

std::vector<double> ActivatedEquilibriumNlp::hessian_values(
    const std::vector<double>& variables,
    double objective_factor,
    const std::vector<double>& constraint_multipliers
) const {
    return delegate_->hessian_values(variables, objective_factor, constraint_multipliers);
}

std::string ActivatedEquilibriumNlp::hessian_backend() const {
    return delegate_->hessian_backend();
}

NlpScaling ActivatedEquilibriumNlp::scaling() const {
    return delegate_->scaling();
}

std::map<std::string, std::string> ActivatedEquilibriumNlp::diagnostics() const {
    std::map<std::string, std::string> out = delegate_->diagnostics();
    out["activation_compiler"] = "activation_plan";
    out["activation_family"] = plan_.family_key;
    return out;
}

const epcsaft::native::equilibrium::ActivationPlan& ActivatedEquilibriumNlp::plan() const {
    return plan_;
}

const epcsaft::native::equilibrium::VariableLayout& ActivatedEquilibriumNlp::layout() const {
    return layout_;
}

NeutralTwoPhaseEosNlpContract evaluate_activated_neutral_tp_flash_nlp_contract(
    const add_args& args,
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout
) {
    ActivatedEquilibriumNlp problem(args, plan, layout);
    return make_activated_contract(problem, layout.phase_count, layout.species_count);
}

NeutralTwoPhaseEosNlpContract evaluate_activated_neutral_lle_nlp_contract(
    const add_args& args,
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout
) {
    ActivatedEquilibriumNlp problem(args, plan, layout);
    return make_activated_contract(problem, layout.phase_count, layout.species_count);
}

}  // namespace epcsaft::native::equilibrium_nlp
