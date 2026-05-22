#include "equilibrium/core/activated_equilibrium_nlp.h"

#include "equilibrium/core/route_metadata.h"
#include "model/native_types.h"

#include <utility>

namespace epcsaft::native::equilibrium_nlp {

namespace {

void require_activated_neutral_flash_plan(
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout
) {
    if (plan.family_key != "neutral_tp_flash" || plan.route != "neutral_tp_flash") {
        throw ValueError("activation-nlp-ineligible: only neutral_tp_flash is supported.");
    }
    if (layout.family_key != plan.family_key || layout.route != plan.route) {
        throw ValueError("activation-nlp-ineligible: variable layout route does not match activation plan.");
    }
    if (layout.variable_model != plan.variable_model || layout.variable_count <= 0) {
        throw ValueError("activation-nlp-ineligible: variable layout does not match activation plan model.");
    }
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
    out.constraints_at_initial = problem.constraints(initial);
    out.jacobian_rows = structure.rows;
    out.jacobian_cols = structure.cols;
    out.jacobian_values_at_initial = problem.jacobian_values(initial);
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
      delegate_(make_neutral_tp_flash_eos_problem(
          args,
          plan_.temperature,
          plan_.pressure,
          plan_.feed_composition,
          "neutral_tp_flash_eos"
      )) {
    require_activated_neutral_flash_plan(plan_, layout_);
    if (!delegate_) {
        throw ValueError("activation-nlp-ineligible: neutral_tp_flash delegate was not created.");
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

}  // namespace epcsaft::native::equilibrium_nlp
