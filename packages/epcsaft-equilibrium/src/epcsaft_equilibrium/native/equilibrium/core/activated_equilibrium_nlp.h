#pragma once

#include "equilibrium/core/activation_plan.h"
#include "equilibrium/core/chemical_equilibrium_nlp.h"
#include "equilibrium/core/continuation_driver.h"
#include "equilibrium/core/feasible_initialization.h"
#include "equilibrium/core/nlp_problem.h"
#include "equilibrium/core/two_phase_eos_route.h"
#include "equilibrium/core/variable_layout.h"
#include "equilibrium/solvers/ipopt_adapter.h"

#include <memory>
#include <string>
#include <vector>

struct add_args;

namespace epcsaft::native::equilibrium_nlp {

struct ChemicalEquilibriumNlpResult {
    NeutralTwoPhaseEosNlpContract contract;
    IpoptSolveResult solve;
    HomogeneousChemicalEquilibriumBlockResult postsolve;
    bool accepted = false;
    double balance_inf_norm = 0.0;
    double reaction_stationarity_inf_norm = 0.0;
    ReactionProofScalingMetrics proof_metrics;
    bool source_oracle_initial_amounts = true;
    std::string seed_source = "caller_initial_amounts";
    std::string accepted_seed_source;
    std::vector<std::string> seed_attempt_order;
    bool caller_seed_attempted = false;
    bool caller_seed_final_proof_attempted = false;
    bool caller_seed_final_proof_accepted = false;
    bool caller_seed_escalated = false;
    std::string caller_seed_rejection_source;
    std::string caller_seed_rejection_reason;
    bool caller_seed_exception_observed = false;
    std::string caller_seed_exception_message;
    FeasibleInitializationResult feasible_initialization;
    bool direct_final_proof_attempted = false;
    bool direct_final_proof_accepted = false;
    PhysicalProofCorrectorResult proof_corrector;
    ContinuationTraceResult continuation;
    std::string continuation_parameter_name = "log_equilibrium_constants_lambda";
    std::vector<double> continuation_lambdas;
    std::vector<double> activity_continuation_lambdas;
    std::string activity_continuation_mode;
    double activity_continuation_minimum_step = 0.0;
    int activity_continuation_maximum_stage_count = 0;
    std::vector<double> accepted_activity_steps;
    std::vector<double> rejected_activity_steps;
};

class ActivatedEquilibriumNlp final : public NlpProblem {
public:
    ActivatedEquilibriumNlp(
        const add_args& args,
        epcsaft::native::equilibrium::ActivationPlan plan,
        epcsaft::native::equilibrium::VariableLayout layout
    );

    std::string name() const override;
    int variable_count() const override;
    int constraint_count() const override;
    int jacobian_nonzero_count() const override;
    NlpBounds bounds() const override;
    std::vector<double> initial_point() const override;
    double objective(const std::vector<double>& variables) const override;
    std::vector<double> objective_gradient(const std::vector<double>& variables) const override;
    std::vector<double> constraints(const std::vector<double>& variables) const override;
    NlpJacobianStructure jacobian_structure() const override;
    std::vector<double> jacobian_values(const std::vector<double>& variables) const override;
    bool has_exact_hessian() const override;
    int hessian_nonzero_count() const override;
    NlpHessianStructure hessian_structure() const override;
    std::vector<double> hessian_values(
        const std::vector<double>& variables,
        double objective_factor,
        const std::vector<double>& constraint_multipliers
    ) const override;
    std::string hessian_backend() const override;
    NlpScaling scaling() const override;
    std::map<std::string, std::string> diagnostics() const override;

    const epcsaft::native::equilibrium::ActivationPlan& plan() const;
    const epcsaft::native::equilibrium::VariableLayout& layout() const;

private:
    epcsaft::native::equilibrium::ActivationPlan plan_;
    epcsaft::native::equilibrium::VariableLayout layout_;
    std::unique_ptr<NlpProblem> delegate_;
};

NeutralTwoPhaseEosNlpContract evaluate_activated_neutral_tp_flash_nlp_contract(
    const add_args& args,
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout
);

NeutralTwoPhaseEosNlpContract evaluate_activated_neutral_lle_nlp_contract(
    const add_args& args,
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout
);

NeutralTwoPhaseEosNlpContract evaluate_activated_chemical_equilibrium_nlp_contract(
    const ChemicalEquilibriumNlpInput& input,
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout
);

ChemicalEquilibriumNlpResult solve_activated_chemical_equilibrium_nlp(
    const ChemicalEquilibriumNlpInput& input,
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout,
    const IpoptSolveOptions& options,
    double balance_tolerance,
    double reaction_stationarity_tolerance
);

}  // namespace epcsaft::native::equilibrium_nlp
