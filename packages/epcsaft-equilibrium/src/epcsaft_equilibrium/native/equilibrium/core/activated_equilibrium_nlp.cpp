#include "equilibrium/core/activated_equilibrium_nlp.h"

#include "equilibrium/derivatives/nlp_contract_snapshot.h"
#include "model/native_types.h"

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
    return make_neutral_two_phase_nlp_contract_snapshot(
        problem,
        layout.phase_count,
        layout.species_count,
        NlpContractSnapshotDetail::FullDerivativeEvidence
    );
}

NeutralTwoPhaseEosNlpContract evaluate_activated_neutral_lle_nlp_contract(
    const add_args& args,
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout
) {
    ActivatedEquilibriumNlp problem(args, plan, layout);
    return make_neutral_two_phase_nlp_contract_snapshot(
        problem,
        layout.phase_count,
        layout.species_count,
        NlpContractSnapshotDetail::FullDerivativeEvidence
    );
}

}  // namespace epcsaft::native::equilibrium_nlp
