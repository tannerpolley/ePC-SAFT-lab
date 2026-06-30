#pragma once

#include "equilibrium/blocks/chemical_equilibrium_block.h"
#include "equilibrium/core/activation_plan.h"
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

struct ChemicalEquilibriumNlpInput {
    std::vector<std::string> species_labels;
    std::vector<std::string> reaction_labels;
    std::vector<std::string> conservation_labels;
    std::vector<double> stoichiometry_row_major;
    std::vector<double> conservation_matrix_row_major;
    std::vector<double> conservation_totals;
    std::vector<double> log_equilibrium_constants;
    double log_equilibrium_constants_lambda = 1.0;
    std::vector<double> initial_amounts;
    bool eos_activity_enabled = false;
    std::string eos_activity_convention = "mole_fraction_activity";
    std::shared_ptr<add_args> eos_activity_args;
    double eos_activity_temperature = 0.0;
    double eos_activity_pressure = 0.0;
    int eos_activity_phase_kind = -1;
    std::string eos_activity_reference_phase;
};

struct PhysicalProofCorrectorResult {
    bool attempted = false;
    bool accepted = false;
    std::string status;
    int iteration_count = 0;
    double initial_residual_inf_norm = 0.0;
    double initial_balance_inf_norm = 0.0;
    double initial_reaction_stationarity_inf_norm = 0.0;
    double residual_inf_norm = 0.0;
    double balance_inf_norm = 0.0;
    double reaction_stationarity_inf_norm = 0.0;
    double step_inf_norm = 0.0;
    std::vector<double> variables;
    HomogeneousChemicalEquilibriumBlockResult postsolve;
};

struct ChemicalEquilibriumNlpResult {
    NeutralTwoPhaseEosNlpContract contract;
    IpoptSolveResult solve;
    HomogeneousChemicalEquilibriumBlockResult postsolve;
    bool accepted = false;
    double balance_inf_norm = 0.0;
    double reaction_stationarity_inf_norm = 0.0;
    bool source_oracle_initial_amounts = true;
    std::string seed_source = "caller_initial_amounts";
    FeasibleInitializationResult feasible_initialization;
    bool direct_final_proof_attempted = false;
    bool direct_final_proof_accepted = false;
    PhysicalProofCorrectorResult proof_corrector;
    ContinuationTraceResult continuation;
    std::vector<double> continuation_lambdas;
};

class HomogeneousChemicalEquilibriumNlp final : public NlpProblem {
public:
    HomogeneousChemicalEquilibriumNlp(
        ChemicalEquilibriumNlpInput input,
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

    HomogeneousChemicalEquilibriumBlockResult evaluate_block(
        const std::vector<double>& variables
    ) const;
    HomogeneousChemicalEquilibriumBlockResult evaluate_physical_block(
        const std::vector<double>& amounts
    ) const;
    std::vector<double> physical_amounts_from_solver_variables(
        const std::vector<double>& solver_variables
    ) const;

    const ChemicalEquilibriumNlpInput& input() const;
    const epcsaft::native::equilibrium::ActivationPlan& plan() const;
    const epcsaft::native::equilibrium::VariableLayout& layout() const;

private:
    ChemicalEquilibriumNlpInput input_;
    epcsaft::native::equilibrium::ActivationPlan plan_;
    epcsaft::native::equilibrium::VariableLayout layout_;
    NlpJacobianStructure jacobian_structure_;
    NlpHessianStructure hessian_structure_;
    NlpBounds bounds_;
};

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
