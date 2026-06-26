#include "equilibrium/core/chemical_equilibrium_nlp.h"

#include "equilibrium/core/route_metadata.h"
#include "equilibrium/derivatives/nlp_contract_snapshot.h"
#include "model/native_types.h"

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <limits>
#include <numeric>
#include <sstream>
#include <utility>

namespace epcsaft::native::equilibrium_nlp {

namespace {

void require_finite(double value, const std::string& label) {
    if (std::isfinite(value)) {
        return;
    }
    throw ValueError(label + " must be finite.");
}

void require_positive_finite(double value, const std::string& label) {
    if (std::isfinite(value) && value > 0.0) {
        return;
    }
    throw ValueError(label + " must be positive and finite.");
}

void require_size(std::size_t actual, std::size_t expected, const std::string& label) {
    if (actual == expected) {
        return;
    }
    std::ostringstream msg;
    msg << label << " has size " << actual << " but expected " << expected << ".";
    throw ValueError(msg.str());
}

double vector_inf_norm(const std::vector<double>& values) {
    double out = 0.0;
    for (double value : values) {
        out = std::max(out, std::abs(value));
    }
    return out;
}

double amount_upper_bound(const std::vector<double>& totals, const std::vector<double>& initial) {
    double scale = std::accumulate(initial.begin(), initial.end(), 0.0);
    for (double value : totals) {
        scale = std::max(scale, std::abs(value));
    }
    return 10.0 * std::max(1.0, scale);
}

NlpBounds make_bounds(const ChemicalEquilibriumNlpInput& input) {
    const int species_count = static_cast<int>(input.species_labels.size());
    const int balance_count = static_cast<int>(input.conservation_labels.size());
    const double upper = amount_upper_bound(input.conservation_totals, input.initial_amounts);
    NlpBounds out;
    out.variable_lower.assign(static_cast<std::size_t>(species_count), 1.0e-14);
    out.variable_upper.assign(static_cast<std::size_t>(species_count), upper);
    out.constraint_lower.assign(static_cast<std::size_t>(balance_count), 0.0);
    out.constraint_upper.assign(static_cast<std::size_t>(balance_count), 0.0);
    return out;
}

NlpJacobianStructure make_jacobian_structure(int row_count, int column_count) {
    NlpJacobianStructure out;
    out.rows.reserve(static_cast<std::size_t>(row_count) * static_cast<std::size_t>(column_count));
    out.cols.reserve(static_cast<std::size_t>(row_count) * static_cast<std::size_t>(column_count));
    for (int row = 0; row < row_count; ++row) {
        for (int column = 0; column < column_count; ++column) {
            out.rows.push_back(row);
            out.cols.push_back(column);
        }
    }
    return out;
}

NlpHessianStructure make_lower_triangle_structure(int dimension) {
    NlpHessianStructure out;
    out.rows.reserve(static_cast<std::size_t>(dimension) * static_cast<std::size_t>(dimension + 1) / 2U);
    out.cols.reserve(static_cast<std::size_t>(dimension) * static_cast<std::size_t>(dimension + 1) / 2U);
    for (int row = 0; row < dimension; ++row) {
        for (int column = 0; column <= row; ++column) {
            out.rows.push_back(row);
            out.cols.push_back(column);
        }
    }
    return out;
}

void validate_input_shape(const ChemicalEquilibriumNlpInput& input) {
    const auto species_count = input.species_labels.size();
    const auto reaction_count = input.reaction_labels.size();
    const auto balance_count = input.conservation_labels.size();
    if (species_count == 0U) {
        throw ValueError("Chemical equilibrium NLP requires at least one species.");
    }
    if (reaction_count == 0U) {
        throw ValueError("Chemical equilibrium NLP requires at least one reaction.");
    }
    if (balance_count == 0U) {
        throw ValueError("Chemical equilibrium NLP requires at least one conservation row.");
    }
    require_size(
        input.stoichiometry_row_major.size(),
        reaction_count * species_count,
        "chemical equilibrium stoichiometry"
    );
    require_size(
        input.conservation_matrix_row_major.size(),
        balance_count * species_count,
        "chemical equilibrium conservation matrix"
    );
    require_size(
        input.conservation_totals.size(),
        balance_count,
        "chemical equilibrium conservation totals"
    );
    require_size(
        input.log_equilibrium_constants.size(),
        reaction_count,
        "chemical equilibrium log equilibrium constants"
    );
    require_size(input.initial_amounts.size(), species_count, "chemical equilibrium initial amounts");
    for (double value : input.stoichiometry_row_major) {
        require_finite(value, "chemical equilibrium stoichiometry");
    }
    for (double value : input.conservation_matrix_row_major) {
        require_finite(value, "chemical equilibrium conservation matrix");
    }
    for (double value : input.conservation_totals) {
        require_finite(value, "chemical equilibrium conservation totals");
    }
    for (double value : input.log_equilibrium_constants) {
        require_finite(value, "chemical equilibrium log equilibrium constants");
    }
    for (double value : input.initial_amounts) {
        require_positive_finite(value, "chemical equilibrium initial amount");
    }
}

void validate_plan_layout(
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout,
    int species_count
) {
    if (plan.family_key != "reactive_speciation" || plan.route != "reactive_speciation") {
        throw ValueError("chemical-equilibrium-nlp-ineligible: activation plan must be reactive_speciation.");
    }
    if (layout.family_key != plan.family_key || layout.route != plan.route) {
        throw ValueError("chemical-equilibrium-nlp-ineligible: variable layout route does not match activation plan.");
    }
    if (layout.variable_model != "single_phase_species_amounts") {
        throw ValueError("chemical-equilibrium-nlp-ineligible: variable layout model mismatch.");
    }
    if (layout.variable_count != species_count) {
        throw ValueError("chemical-equilibrium-nlp-ineligible: variable count must match species count.");
    }
}

}  // namespace

HomogeneousChemicalEquilibriumNlp::HomogeneousChemicalEquilibriumNlp(
    ChemicalEquilibriumNlpInput input,
    epcsaft::native::equilibrium::ActivationPlan plan,
    epcsaft::native::equilibrium::VariableLayout layout
)
    : input_(std::move(input)),
      plan_(std::move(plan)),
      layout_(std::move(layout)) {
    validate_input_shape(input_);
    validate_plan_layout(plan_, layout_, static_cast<int>(input_.species_labels.size()));
    jacobian_structure_ = make_jacobian_structure(
        static_cast<int>(input_.conservation_labels.size()),
        static_cast<int>(input_.species_labels.size())
    );
    hessian_structure_ = make_lower_triangle_structure(static_cast<int>(input_.species_labels.size()));
    bounds_ = make_bounds(input_);
}

std::string HomogeneousChemicalEquilibriumNlp::name() const {
    return "reactive_speciation_ideal_gibbs_nlp";
}

int HomogeneousChemicalEquilibriumNlp::variable_count() const {
    return static_cast<int>(input_.species_labels.size());
}

int HomogeneousChemicalEquilibriumNlp::constraint_count() const {
    return static_cast<int>(input_.conservation_labels.size());
}

int HomogeneousChemicalEquilibriumNlp::jacobian_nonzero_count() const {
    return static_cast<int>(jacobian_structure_.rows.size());
}

NlpBounds HomogeneousChemicalEquilibriumNlp::bounds() const {
    return bounds_;
}

std::vector<double> HomogeneousChemicalEquilibriumNlp::initial_point() const {
    return input_.initial_amounts;
}

HomogeneousChemicalEquilibriumBlockResult HomogeneousChemicalEquilibriumNlp::evaluate_block(
    const std::vector<double>& variables
) const {
    return evaluate_homogeneous_chemical_equilibrium_block(
        variables,
        static_cast<int>(input_.reaction_labels.size()),
        input_.stoichiometry_row_major,
        static_cast<int>(input_.conservation_labels.size()),
        input_.conservation_matrix_row_major,
        input_.conservation_totals,
        input_.log_equilibrium_constants
    );
}

double HomogeneousChemicalEquilibriumNlp::objective(const std::vector<double>& variables) const {
    return evaluate_block(variables).objective_value;
}

std::vector<double> HomogeneousChemicalEquilibriumNlp::objective_gradient(
    const std::vector<double>& variables
) const {
    return evaluate_block(variables).objective_gradient;
}

std::vector<double> HomogeneousChemicalEquilibriumNlp::constraints(
    const std::vector<double>& variables
) const {
    return evaluate_block(variables).balance_residuals;
}

NlpJacobianStructure HomogeneousChemicalEquilibriumNlp::jacobian_structure() const {
    return jacobian_structure_;
}

std::vector<double> HomogeneousChemicalEquilibriumNlp::jacobian_values(
    const std::vector<double>& variables
) const {
    (void)variables;
    return input_.conservation_matrix_row_major;
}

bool HomogeneousChemicalEquilibriumNlp::has_exact_hessian() const {
    return true;
}

int HomogeneousChemicalEquilibriumNlp::hessian_nonzero_count() const {
    return static_cast<int>(hessian_structure_.rows.size());
}

NlpHessianStructure HomogeneousChemicalEquilibriumNlp::hessian_structure() const {
    return hessian_structure_;
}

std::vector<double> HomogeneousChemicalEquilibriumNlp::hessian_values(
    const std::vector<double>& variables,
    double objective_factor,
    const std::vector<double>& constraint_multipliers
) const {
    (void)constraint_multipliers;
    const HomogeneousChemicalEquilibriumBlockResult block = evaluate_block(variables);
    std::vector<double> out;
    out.reserve(hessian_structure_.rows.size());
    const int species_count = variable_count();
    for (int index = 0; index < hessian_nonzero_count(); ++index) {
        const int row = hessian_structure_.rows[static_cast<std::size_t>(index)];
        const int column = hessian_structure_.cols[static_cast<std::size_t>(index)];
        out.push_back(
            objective_factor
            * block.hessian_row_major[static_cast<std::size_t>(row * species_count + column)]
        );
    }
    return out;
}

std::string HomogeneousChemicalEquilibriumNlp::hessian_backend() const {
    return "analytic";
}

NlpScaling HomogeneousChemicalEquilibriumNlp::scaling() const {
    const HomogeneousChemicalEquilibriumBlockResult block = evaluate_block(input_.initial_amounts);
    NlpScaling out;
    out.objective = block.objective_scaling;
    out.variables = block.variable_scaling;
    out.constraints = block.balance_scaling;
    return out;
}

std::map<std::string, std::string> HomogeneousChemicalEquilibriumNlp::diagnostics() const {
    RouteMetadata metadata;
    metadata.variable_model = "single_phase_species_amounts";
    metadata.density_backend = "homogeneous_standard_state_activity";
    metadata.residual_families = {"conserved_balance", "reaction_stationarity"};
    metadata.constraint_families = {"conserved_balance"};
    std::map<std::string, std::string> out = route_metadata_diagnostics(metadata);
    out["activation_compiler"] = "activation_plan";
    out["activation_family"] = plan_.family_key;
    out["thermodynamic_block"] = "homogeneous_chemical_equilibrium";
    return out;
}

const ChemicalEquilibriumNlpInput& HomogeneousChemicalEquilibriumNlp::input() const {
    return input_;
}

const epcsaft::native::equilibrium::ActivationPlan& HomogeneousChemicalEquilibriumNlp::plan() const {
    return plan_;
}

const epcsaft::native::equilibrium::VariableLayout& HomogeneousChemicalEquilibriumNlp::layout() const {
    return layout_;
}

NeutralTwoPhaseEosNlpContract evaluate_activated_chemical_equilibrium_nlp_contract(
    const ChemicalEquilibriumNlpInput& input,
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout
) {
    HomogeneousChemicalEquilibriumNlp problem(input, plan, layout);
    NeutralTwoPhaseEosNlpContract out = make_neutral_two_phase_nlp_contract_snapshot(
        problem,
        layout.phase_count,
        layout.species_count,
        NlpContractSnapshotDetail::FullDerivativeEvidence
    );
    const HomogeneousChemicalEquilibriumBlockResult block = problem.evaluate_block(problem.initial_point());
    out.balance_row_count = static_cast<int>(input.conservation_labels.size());
    out.reaction_count = static_cast<int>(input.reaction_labels.size());
    out.standard_mu_rt = block.standard_mu_rt;
    return out;
}

ChemicalEquilibriumNlpResult solve_activated_chemical_equilibrium_nlp(
    const ChemicalEquilibriumNlpInput& input,
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout,
    const IpoptSolveOptions& options,
    double balance_tolerance,
    double reaction_stationarity_tolerance
) {
    HomogeneousChemicalEquilibriumNlp problem(input, plan, layout);
    validate_nlp_problem_shape(problem);
    ChemicalEquilibriumNlpResult out;
    out.contract = evaluate_activated_chemical_equilibrium_nlp_contract(input, plan, layout);
    out.solve = solve_ipopt_nlp(problem, options);
    const std::vector<double>& variables = out.solve.variables.empty()
        ? input.initial_amounts
        : out.solve.variables;
    out.postsolve = problem.evaluate_block(variables);
    out.balance_inf_norm = vector_inf_norm(out.postsolve.balance_residuals);
    out.reaction_stationarity_inf_norm = vector_inf_norm(out.postsolve.reaction_affinities);
    out.accepted = ipopt_solve_result_allows_postsolve(out.solve)
        && out.balance_inf_norm <= balance_tolerance
        && out.reaction_stationarity_inf_norm <= reaction_stationarity_tolerance;
    return out;
}

}  // namespace epcsaft::native::equilibrium_nlp
