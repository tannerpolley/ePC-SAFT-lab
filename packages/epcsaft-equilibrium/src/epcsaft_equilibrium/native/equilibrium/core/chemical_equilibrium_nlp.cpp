#include "equilibrium/core/chemical_equilibrium_nlp.h"

#include "equilibrium/core/chemical_equilibrium_objective.h"
#include "equilibrium/core/route_metadata.h"
#include "equilibrium/derivatives/nlp_contract_snapshot.h"
#include "model/native_types.h"

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <limits>
#include <memory>
#include <numeric>
#include <sstream>
#include <utility>

namespace epcsaft::native::equilibrium_nlp {

namespace {

constexpr double kMinimumPositiveLogAmount = 1.0e-22;

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

double matrix_abs_max(const std::vector<double>& matrix) {
    double out = 0.0;
    for (double value : matrix) {
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

std::vector<int> independent_row_indices(
    std::vector<double> matrix,
    int rows,
    int columns
) {
    const double tolerance = 1.0e-12 * std::max(1.0, matrix_abs_max(matrix));
    std::vector<int> row_indices(static_cast<std::size_t>(rows), 0);
    std::iota(row_indices.begin(), row_indices.end(), 0);
    std::vector<int> independent;
    int rank = 0;
    for (int column = 0; column < columns && rank < rows; ++column) {
        int pivot_row = rank;
        double pivot_abs = std::abs(matrix[static_cast<std::size_t>(rank * columns + column)]);
        for (int row = rank + 1; row < rows; ++row) {
            const double candidate = std::abs(matrix[static_cast<std::size_t>(row * columns + column)]);
            if (candidate > pivot_abs) {
                pivot_abs = candidate;
                pivot_row = row;
            }
        }
        if (pivot_abs <= tolerance) {
            continue;
        }
        if (pivot_row != rank) {
            for (int swap_column = column; swap_column < columns; ++swap_column) {
                std::swap(
                    matrix[static_cast<std::size_t>(rank * columns + swap_column)],
                    matrix[static_cast<std::size_t>(pivot_row * columns + swap_column)]
                );
            }
            std::swap(row_indices[static_cast<std::size_t>(rank)], row_indices[static_cast<std::size_t>(pivot_row)]);
        }
        independent.push_back(row_indices[static_cast<std::size_t>(rank)]);
        const double pivot = matrix[static_cast<std::size_t>(rank * columns + column)];
        for (int row = rank + 1; row < rows; ++row) {
            const double factor = matrix[static_cast<std::size_t>(row * columns + column)] / pivot;
            matrix[static_cast<std::size_t>(row * columns + column)] = 0.0;
            for (int eliminate_column = column + 1; eliminate_column < columns; ++eliminate_column) {
                matrix[static_cast<std::size_t>(row * columns + eliminate_column)] -=
                    factor * matrix[static_cast<std::size_t>(rank * columns + eliminate_column)];
            }
        }
        ++rank;
    }
    std::sort(independent.begin(), independent.end());
    return independent;
}

std::vector<double> solve_damped_linear_system(
    std::vector<double> matrix,
    std::vector<double> rhs,
    int dimension
) {
    require_size(matrix.size(), static_cast<std::size_t>(dimension * dimension), "linear system matrix");
    require_size(rhs.size(), static_cast<std::size_t>(dimension), "linear system rhs");
    for (int pivot = 0; pivot < dimension; ++pivot) {
        int pivot_row = pivot;
        double pivot_abs = std::abs(matrix[static_cast<std::size_t>(pivot * dimension + pivot)]);
        for (int row = pivot + 1; row < dimension; ++row) {
            const double candidate = std::abs(matrix[static_cast<std::size_t>(row * dimension + pivot)]);
            if (candidate > pivot_abs) {
                pivot_abs = candidate;
                pivot_row = row;
            }
        }
        if (pivot_abs <= 0.0 || !std::isfinite(pivot_abs)) {
            throw ValueError("chemical equilibrium multiplier warm start system is singular.");
        }
        if (pivot_row != pivot) {
            for (int column = 0; column < dimension; ++column) {
                std::swap(
                    matrix[static_cast<std::size_t>(pivot * dimension + column)],
                    matrix[static_cast<std::size_t>(pivot_row * dimension + column)]
                );
            }
            std::swap(rhs[static_cast<std::size_t>(pivot)], rhs[static_cast<std::size_t>(pivot_row)]);
        }
        const double diagonal = matrix[static_cast<std::size_t>(pivot * dimension + pivot)];
        for (int row = pivot + 1; row < dimension; ++row) {
            const double factor = matrix[static_cast<std::size_t>(row * dimension + pivot)] / diagonal;
            matrix[static_cast<std::size_t>(row * dimension + pivot)] = 0.0;
            for (int column = pivot + 1; column < dimension; ++column) {
                matrix[static_cast<std::size_t>(row * dimension + column)] -=
                    factor * matrix[static_cast<std::size_t>(pivot * dimension + column)];
            }
            rhs[static_cast<std::size_t>(row)] -= factor * rhs[static_cast<std::size_t>(pivot)];
        }
    }

    std::vector<double> solution(static_cast<std::size_t>(dimension), 0.0);
    for (int row = dimension - 1; row >= 0; --row) {
        double value = rhs[static_cast<std::size_t>(row)];
        for (int column = row + 1; column < dimension; ++column) {
            value -= matrix[static_cast<std::size_t>(row * dimension + column)]
                * solution[static_cast<std::size_t>(column)];
        }
        const double diagonal = matrix[static_cast<std::size_t>(row * dimension + row)];
        if (diagonal == 0.0 || !std::isfinite(diagonal)) {
            throw ValueError("chemical equilibrium multiplier warm start system is singular.");
        }
        solution[static_cast<std::size_t>(row)] = value / diagonal;
    }
    return solution;
}

std::vector<double> estimate_constraint_multipliers(
    const ChemicalEquilibriumNlpInput& input,
    const std::vector<double>& physical_gradient,
    double objective_scaling,
    const std::vector<double>& balance_scaling
) {
    const int species_count = static_cast<int>(input.species_labels.size());
    const int balance_count = static_cast<int>(input.conservation_labels.size());
    require_size(
        physical_gradient.size(),
        static_cast<std::size_t>(species_count),
        "chemical equilibrium physical gradient"
    );
    require_positive_finite(objective_scaling, "chemical equilibrium objective scaling");
    require_size(
        balance_scaling.size(),
        static_cast<std::size_t>(balance_count),
        "chemical equilibrium balance scaling"
    );
    std::vector<double> normal_matrix(static_cast<std::size_t>(balance_count * balance_count), 0.0);
    std::vector<double> rhs(static_cast<std::size_t>(balance_count), 0.0);
    double max_diagonal = 0.0;
    for (int row = 0; row < balance_count; ++row) {
        for (int species = 0; species < species_count; ++species) {
            const double row_value =
                input.conservation_matrix_row_major[static_cast<std::size_t>(row * species_count + species)];
            rhs[static_cast<std::size_t>(row)] -=
                row_value * objective_scaling * physical_gradient[static_cast<std::size_t>(species)];
            for (int column = 0; column < balance_count; ++column) {
                normal_matrix[static_cast<std::size_t>(row * balance_count + column)] +=
                    row_value
                    * input.conservation_matrix_row_major[
                        static_cast<std::size_t>(column * species_count + species)
                    ];
            }
        }
        max_diagonal = std::max(
            max_diagonal,
            std::abs(normal_matrix[static_cast<std::size_t>(row * balance_count + row)])
        );
    }
    const double ridge = std::max(1.0e-14, 1.0e-14 * max_diagonal);
    for (int row = 0; row < balance_count; ++row) {
        normal_matrix[static_cast<std::size_t>(row * balance_count + row)] += ridge;
    }
    std::vector<double> scaled_multipliers =
        solve_damped_linear_system(std::move(normal_matrix), std::move(rhs), balance_count);
    for (int row = 0; row < balance_count; ++row) {
        const double scale = balance_scaling[static_cast<std::size_t>(row)];
        require_positive_finite(scale, "chemical equilibrium balance scaling");
        scaled_multipliers[static_cast<std::size_t>(row)] /= scale;
    }
    return scaled_multipliers;
}

std::vector<double> log_amounts_from_physical_amounts(const std::vector<double>& amounts) {
    std::vector<double> out;
    out.reserve(amounts.size());
    for (double amount : amounts) {
        require_positive_finite(amount, "chemical equilibrium positive-log initial amount");
        if (amount < kMinimumPositiveLogAmount) {
            throw ValueError("chemical equilibrium initial amount is below the positive-log lower bound.");
        }
        out.push_back(std::log(amount));
    }
    return out;
}

std::vector<double> physical_amounts_from_log_amounts(const std::vector<double>& solver_variables) {
    std::vector<double> out;
    out.reserve(solver_variables.size());
    for (double value : solver_variables) {
        require_finite(value, "chemical equilibrium positive-log solver variable");
        const double amount = std::exp(value);
        require_positive_finite(amount, "chemical equilibrium physical amount");
        out.push_back(amount);
    }
    return out;
}

NlpBounds make_bounds(const ChemicalEquilibriumNlpInput& input) {
    const int species_count = static_cast<int>(input.species_labels.size());
    const int balance_count = static_cast<int>(input.conservation_labels.size());
    const double upper = amount_upper_bound(input.conservation_totals, input.initial_amounts);
    NlpBounds out;
    out.variable_lower.assign(static_cast<std::size_t>(species_count), std::log(kMinimumPositiveLogAmount));
    out.variable_upper.assign(static_cast<std::size_t>(species_count), std::log(upper));
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
    if (!input.initial_amounts.empty()) {
        require_size(input.initial_amounts.size(), species_count, "chemical equilibrium initial amounts");
    }
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
    if (input.eos_activity_enabled) {
        if (
            input.eos_activity_convention != "eos_x_phi"
            && input.eos_activity_convention != "eos_x_gamma"
        ) {
            throw ValueError("chemical equilibrium EOS activity convention must be eos_x_phi or eos_x_gamma.");
        }
        require_positive_finite(input.eos_activity_temperature, "chemical equilibrium EOS activity temperature");
        require_positive_finite(input.eos_activity_pressure, "chemical equilibrium EOS activity pressure");
        if (input.eos_activity_phase_kind != 0 && input.eos_activity_phase_kind != 1) {
            throw ValueError("chemical equilibrium EOS activity phase kind must be liquid or vapor.");
        }
        if (input.eos_activity_convention == "eos_x_gamma" && input.eos_activity_phase_kind != 0) {
            throw ValueError("chemical equilibrium eos_x_gamma standard states require a liquid reference phase.");
        }
        if (!input.eos_activity_args) {
            throw ValueError("chemical equilibrium EOS activity standard states require native EOS parameters.");
        }
        if (!input.eos_activity_args->m.empty() && input.eos_activity_args->m.size() != species_count) {
            throw ValueError("chemical equilibrium EOS activity mixture component count must match species count.");
        }
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
    if (layout.solver_coordinate_basis != "log_species_amounts"
        || layout.transform_policy != "positive_log_coordinates") {
        throw ValueError("chemical-equilibrium-nlp-ineligible: reactive_speciation must use positive log amount coordinates.");
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
    if (input_.eos_activity_enabled) {
        return "reactive_speciation_" + input_.eos_activity_convention + "_gibbs_nlp";
    }
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
    return log_amounts_from_physical_amounts(input_.initial_amounts);
}

HomogeneousChemicalEquilibriumBlockResult HomogeneousChemicalEquilibriumNlp::evaluate_block(
    const std::vector<double>& variables
) const {
    return evaluate_physical_block(physical_amounts_from_solver_variables(variables));
}

HomogeneousChemicalEquilibriumBlockResult HomogeneousChemicalEquilibriumNlp::evaluate_physical_block(
    const std::vector<double>& amounts
) const {
    return evaluate_chemical_equilibrium_objective(input_, amounts);
}

double HomogeneousChemicalEquilibriumNlp::objective(const std::vector<double>& variables) const {
    return evaluate_block(variables).objective_value;
}

std::vector<double> HomogeneousChemicalEquilibriumNlp::objective_gradient(
    const std::vector<double>& variables
) const {
    const std::vector<double> amounts = physical_amounts_from_solver_variables(variables);
    const HomogeneousChemicalEquilibriumBlockResult block = evaluate_physical_block(amounts);
    std::vector<double> out;
    out.reserve(amounts.size());
    for (std::size_t index = 0; index < amounts.size(); ++index) {
        out.push_back(block.objective_gradient[index] * amounts[index]);
    }
    return out;
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
    const std::vector<double> amounts = physical_amounts_from_solver_variables(variables);
    std::vector<double> out;
    out.reserve(input_.conservation_matrix_row_major.size());
    const int species_count = variable_count();
    const int balance_count = constraint_count();
    for (int row = 0; row < balance_count; ++row) {
        for (int column = 0; column < species_count; ++column) {
            out.push_back(
                input_.conservation_matrix_row_major[static_cast<std::size_t>(row * species_count + column)]
                * amounts[static_cast<std::size_t>(column)]
            );
        }
    }
    return out;
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
    require_size(
        constraint_multipliers.size(),
        static_cast<std::size_t>(constraint_count()),
        "chemical equilibrium constraint multiplier vector"
    );
    const std::vector<double> amounts = physical_amounts_from_solver_variables(variables);
    const HomogeneousChemicalEquilibriumBlockResult block = evaluate_physical_block(amounts);
    std::vector<double> out;
    out.reserve(hessian_structure_.rows.size());
    const int species_count = variable_count();
    for (int index = 0; index < hessian_nonzero_count(); ++index) {
        const int row = hessian_structure_.rows[static_cast<std::size_t>(index)];
        const int column = hessian_structure_.cols[static_cast<std::size_t>(index)];
        double value =
            objective_factor
            * block.hessian_row_major[static_cast<std::size_t>(row * species_count + column)]
            * amounts[static_cast<std::size_t>(row)]
            * amounts[static_cast<std::size_t>(column)];
        if (row == column) {
            value += objective_factor
                * block.objective_gradient[static_cast<std::size_t>(row)]
                * amounts[static_cast<std::size_t>(row)];
            for (int balance = 0; balance < constraint_count(); ++balance) {
                value += constraint_multipliers[static_cast<std::size_t>(balance)]
                    * input_.conservation_matrix_row_major[
                        static_cast<std::size_t>(balance * species_count + row)
                    ]
                    * amounts[static_cast<std::size_t>(row)];
            }
        }
        out.push_back(value);
    }
    return out;
}

std::string HomogeneousChemicalEquilibriumNlp::hessian_backend() const {
    if (input_.eos_activity_enabled) {
        if (input_.eos_activity_convention == "eos_x_gamma") {
            return "cppad_phase_state_activity_coefficient";
        }
        return "cppad_phase_state_fugacity";
    }
    return "analytic";
}

NlpScaling HomogeneousChemicalEquilibriumNlp::scaling() const {
    const HomogeneousChemicalEquilibriumBlockResult block = evaluate_physical_block(input_.initial_amounts);
    NlpScaling out;
    out.objective = block.objective_scaling;
    out.variables.assign(static_cast<std::size_t>(variable_count()), 1.0);
    out.constraints = block.balance_scaling;
    return out;
}

std::map<std::string, std::string> HomogeneousChemicalEquilibriumNlp::diagnostics() const {
    RouteMetadata metadata;
    metadata.variable_model = "single_phase_species_amounts";
    metadata.density_backend = input_.eos_activity_enabled
        ? "eos_pressure_root_activity"
        : "homogeneous_standard_state_activity";
    metadata.residual_families = {"conserved_balance", "reaction_stationarity"};
    metadata.constraint_families = {"conserved_balance"};
    std::map<std::string, std::string> out = route_metadata_diagnostics(metadata);
    out["activation_compiler"] = "activation_plan";
    out["activation_family"] = plan_.family_key;
    out["solver_coordinate_basis"] = "log_species_amounts";
    out["transform_policy"] = "positive_log_coordinates";
    out["thermodynamic_block"] = "homogeneous_chemical_equilibrium";
    out["activity_model"] = input_.eos_activity_enabled
        ? input_.eos_activity_convention
        : "mole_fraction_activity";
    return out;
}

std::vector<double> HomogeneousChemicalEquilibriumNlp::physical_amounts_from_solver_variables(
    const std::vector<double>& solver_variables
) const {
    require_size(
        solver_variables.size(),
        static_cast<std::size_t>(variable_count()),
        "chemical equilibrium solver variable vector"
    );
    return physical_amounts_from_log_amounts(solver_variables);
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
    const HomogeneousChemicalEquilibriumBlockResult block = problem.evaluate_physical_block(input.initial_amounts);
    out.balance_row_count = static_cast<int>(input.conservation_labels.size());
    out.reaction_count = static_cast<int>(input.reaction_labels.size());
    out.standard_mu_rt = block.standard_mu_rt;
    return out;
}

namespace {

ChemicalEquilibriumNlpInput input_with_initial_amounts(
    const ChemicalEquilibriumNlpInput& input,
    const std::vector<double>& initial_amounts
) {
    ChemicalEquilibriumNlpInput out = input;
    out.initial_amounts = initial_amounts;
    return out;
}

FeasibleInitializationInput feasible_initialization_input_from_ce(
    const ChemicalEquilibriumNlpInput& input
) {
    FeasibleInitializationInput out;
    out.species_labels = input.species_labels;
    out.conservation_labels = input.conservation_labels;
    out.conservation_matrix_row_major = input.conservation_matrix_row_major;
    out.conservation_totals = input.conservation_totals;
    out.amount_floor = kMinimumPositiveLogAmount;
    return out;
}

IpoptSolveOptions ce_stage_options(
    const IpoptSolveOptions& options,
    const std::string& option_profile
) {
    IpoptSolveOptions out = options;
    out.option_profile = option_profile;
    if (out.bound_push <= 0.0) {
        out.bound_push = 1.0e-12;
    }
    if (out.bound_frac <= 0.0) {
        out.bound_frac = 1.0e-12;
    }
    return out;
}

ContinuationStageSpec ce_homotopy_stage(
    const ChemicalEquilibriumNlpInput& base_input,
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout,
    const IpoptSolveOptions& options,
    const std::string& stage_id,
    double lambda,
    bool final_proof
) {
    ContinuationStageSpec stage;
    stage.stage_id = stage_id;
    stage.parameter_value = lambda;
    stage.final_proof = final_proof;
    stage.options = ce_stage_options(options, final_proof ? "proof" : "continuation_trace");
    ChemicalEquilibriumNlpInput stage_input =
        chemical_equilibrium_input_with_log_k_lambda(base_input, lambda);
    stage.problem_factory = [stage_input, plan, layout]() {
        return std::make_unique<HomogeneousChemicalEquilibriumNlp>(stage_input, plan, layout);
    };
    return stage;
}

struct PhysicalProofResidualSystem {
    HomogeneousChemicalEquilibriumBlockResult block;
    std::vector<double> residuals;
    std::vector<double> jacobian_row_major;
    double residual_inf_norm = 0.0;
    double balance_inf_norm = 0.0;
    double reaction_stationarity_inf_norm = 0.0;
};

bool physical_proof_passed(
    const HomogeneousChemicalEquilibriumBlockResult& block,
    double balance_tolerance,
    double reaction_stationarity_tolerance
) {
    return vector_inf_norm(block.balance_residuals) <= balance_tolerance
        && vector_inf_norm(block.reaction_affinities) <= reaction_stationarity_tolerance;
}

PhysicalProofResidualSystem evaluate_physical_proof_residual_system(
    const HomogeneousChemicalEquilibriumNlp& problem,
    const std::vector<double>& variables,
    const std::vector<int>& independent_balance_rows,
    double balance_tolerance,
    double reaction_stationarity_tolerance
) {
    const int species_count = problem.variable_count();
    const int reaction_count = static_cast<int>(problem.input().reaction_labels.size());
    const std::vector<double> amounts = problem.physical_amounts_from_solver_variables(variables);
    PhysicalProofResidualSystem out;
    out.block = problem.evaluate_physical_block(amounts);
    out.balance_inf_norm = vector_inf_norm(out.block.balance_residuals);
    out.reaction_stationarity_inf_norm = vector_inf_norm(out.block.reaction_affinities);
    const int equation_count = static_cast<int>(independent_balance_rows.size()) + reaction_count;
    out.residuals.assign(static_cast<std::size_t>(equation_count), 0.0);
    out.jacobian_row_major.assign(static_cast<std::size_t>(equation_count * species_count), 0.0);

    int equation = 0;
    for (int balance_row : independent_balance_rows) {
        out.residuals[static_cast<std::size_t>(equation)] =
            out.block.balance_residuals[static_cast<std::size_t>(balance_row)] / balance_tolerance;
        for (int species = 0; species < species_count; ++species) {
            out.jacobian_row_major[static_cast<std::size_t>(equation * species_count + species)] =
                out.block.balance_jacobian_row_major[
                    static_cast<std::size_t>(balance_row * species_count + species)
                ] * amounts[static_cast<std::size_t>(species)] / balance_tolerance;
        }
        ++equation;
    }
    for (int reaction = 0; reaction < reaction_count; ++reaction) {
        out.residuals[static_cast<std::size_t>(equation)] =
            out.block.reaction_affinities[static_cast<std::size_t>(reaction)] / reaction_stationarity_tolerance;
        for (int species = 0; species < species_count; ++species) {
            out.jacobian_row_major[static_cast<std::size_t>(equation * species_count + species)] =
                out.block.affinity_jacobian_row_major[
                    static_cast<std::size_t>(reaction * species_count + species)
                ] * amounts[static_cast<std::size_t>(species)] / reaction_stationarity_tolerance;
        }
        ++equation;
    }
    out.residual_inf_norm = vector_inf_norm(out.residuals);
    return out;
}

PhysicalProofCorrectorResult run_physical_proof_corrector(
    const ChemicalEquilibriumNlpInput& input,
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout,
    const std::vector<double>& initial_variables,
    double balance_tolerance,
    double reaction_stationarity_tolerance
) {
    constexpr int kMaxIterations = 24;
    constexpr int kMaxLineSearchTrials = 16;
    constexpr double kMinimumStepDecrease = 1.0e-12;

    PhysicalProofCorrectorResult out;
    out.attempted = true;
    out.status = "started";
    HomogeneousChemicalEquilibriumNlp problem(input, plan, layout);
    const int species_count = problem.variable_count();
    const int balance_count = problem.constraint_count();
    require_size(
        initial_variables.size(),
        static_cast<std::size_t>(species_count),
        "chemical equilibrium proof-corrector initial variables"
    );
    const std::vector<int> independent_balance_rows = independent_row_indices(
        input.conservation_matrix_row_major,
        balance_count,
        species_count
    );
    if (independent_balance_rows.empty()) {
        out.status = "rejected_no_independent_balance_rows";
        return out;
    }
    const int equation_count =
        static_cast<int>(independent_balance_rows.size()) + static_cast<int>(input.reaction_labels.size());
    if (equation_count != species_count) {
        out.status = "rejected_non_square_physical_proof_system";
        return out;
    }

    std::vector<double> variables = initial_variables;
    PhysicalProofResidualSystem system = evaluate_physical_proof_residual_system(
        problem,
        variables,
        independent_balance_rows,
        balance_tolerance,
        reaction_stationarity_tolerance
    );
    for (int iteration = 0; iteration <= kMaxIterations; ++iteration) {
        out.iteration_count = iteration;
        out.residual_inf_norm = system.residual_inf_norm;
        out.balance_inf_norm = system.balance_inf_norm;
        out.reaction_stationarity_inf_norm = system.reaction_stationarity_inf_norm;
        out.variables = variables;
        out.postsolve = system.block;
        if (physical_proof_passed(system.block, balance_tolerance, reaction_stationarity_tolerance)) {
            out.accepted = true;
            out.status = "accepted";
            return out;
        }
        if (iteration == kMaxIterations) {
            break;
        }

        std::vector<double> rhs = system.residuals;
        for (double& value : rhs) {
            value = -value;
        }
        std::vector<double> step;
        try {
            step = solve_damped_linear_system(system.jacobian_row_major, rhs, species_count);
        } catch (const std::exception&) {
            out.status = "rejected_singular_physical_proof_jacobian";
            return out;
        }
        out.step_inf_norm = vector_inf_norm(step);
        if (!(std::isfinite(out.step_inf_norm) && out.step_inf_norm > 0.0)) {
            out.status = "rejected_invalid_physical_proof_step";
            return out;
        }

        bool accepted_step = false;
        double step_scale = 1.0;
        if (out.step_inf_norm > 8.0) {
            step_scale = 8.0 / out.step_inf_norm;
        }
        for (int trial = 0; trial < kMaxLineSearchTrials; ++trial) {
            const double alpha = step_scale * std::pow(0.5, trial);
            std::vector<double> trial_variables = variables;
            for (int species = 0; species < species_count; ++species) {
                trial_variables[static_cast<std::size_t>(species)] +=
                    alpha * step[static_cast<std::size_t>(species)];
            }
            PhysicalProofResidualSystem trial_system = evaluate_physical_proof_residual_system(
                problem,
                trial_variables,
                independent_balance_rows,
                balance_tolerance,
                reaction_stationarity_tolerance
            );
            if (physical_proof_passed(trial_system.block, balance_tolerance, reaction_stationarity_tolerance)
                || trial_system.residual_inf_norm < system.residual_inf_norm * (1.0 - kMinimumStepDecrease)) {
                variables = std::move(trial_variables);
                system = std::move(trial_system);
                accepted_step = true;
                break;
            }
        }
        if (!accepted_step) {
            out.status = "rejected_no_decreasing_physical_proof_step";
            return out;
        }
    }

    out.status = "rejected_iteration_limit";
    return out;
}

ChemicalEquilibriumNlpResult build_ce_result_from_solve(
    const ChemicalEquilibriumNlpInput& input,
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout,
    const IpoptSolveResult& solve,
    double balance_tolerance,
    double reaction_stationarity_tolerance
) {
    HomogeneousChemicalEquilibriumNlp problem(input, plan, layout);
    ChemicalEquilibriumNlpResult out;
    out.contract = evaluate_activated_chemical_equilibrium_nlp_contract(input, plan, layout);
    out.solve = solve;
    const std::vector<double>& variables = out.solve.variables.empty()
        ? problem.initial_point()
        : out.solve.variables;
    const std::vector<double> amounts = problem.physical_amounts_from_solver_variables(variables);
    out.postsolve = problem.evaluate_physical_block(amounts);
    out.balance_inf_norm = vector_inf_norm(out.postsolve.balance_residuals);
    out.reaction_stationarity_inf_norm = vector_inf_norm(out.postsolve.reaction_affinities);
    out.accepted = ipopt_solve_result_allows_postsolve(out.solve)
        && out.balance_inf_norm <= balance_tolerance
        && out.reaction_stationarity_inf_norm <= reaction_stationarity_tolerance;
    return out;
}

ChemicalEquilibriumNlpResult solve_single_ce_proof(
    const ChemicalEquilibriumNlpInput& input,
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout,
    const IpoptSolveOptions& options,
    double balance_tolerance,
    double reaction_stationarity_tolerance
) {
    HomogeneousChemicalEquilibriumNlp problem(input, plan, layout);
    validate_nlp_problem_shape(problem);
    IpoptSolveOptions solve_options = ce_stage_options(options, "proof");
    if (solve_options.initial_constraint_multipliers.empty()) {
        const HomogeneousChemicalEquilibriumBlockResult initial_block =
            problem.evaluate_physical_block(input.initial_amounts);
        solve_options.initial_constraint_multipliers = estimate_constraint_multipliers(
            input,
            initial_block.objective_gradient,
            initial_block.objective_scaling,
            initial_block.balance_scaling
        );
        solve_options.initial_bound_lower_multipliers.assign(
            static_cast<std::size_t>(problem.variable_count()),
            0.0
        );
        solve_options.initial_bound_upper_multipliers.assign(
            static_cast<std::size_t>(problem.variable_count()),
            0.0
        );
    }
    return build_ce_result_from_solve(
        input,
        plan,
        layout,
        solve_ipopt_nlp(problem, solve_options),
        balance_tolerance,
        reaction_stationarity_tolerance
    );
}

ChemicalEquilibriumNlpResult result_from_homotopy_trace(
    const ChemicalEquilibriumNlpInput& true_input,
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout,
    const ContinuationTraceResult& trace,
    double balance_tolerance,
    double reaction_stationarity_tolerance
) {
    if (trace.trace.empty()) {
        ChemicalEquilibriumNlpResult out;
        out.continuation = trace;
        return out;
    }
    ChemicalEquilibriumNlpResult out = build_ce_result_from_solve(
        true_input,
        plan,
        layout,
        trace.trace.back().solve,
        balance_tolerance,
        reaction_stationarity_tolerance
    );
    out.continuation = trace;
    out.accepted = trace.accepted && out.accepted;
    return out;
}

}  // namespace

ChemicalEquilibriumNlpResult solve_activated_chemical_equilibrium_nlp(
    const ChemicalEquilibriumNlpInput& input,
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout,
    const IpoptSolveOptions& options,
    double balance_tolerance,
    double reaction_stationarity_tolerance
) {
    if (!input.initial_amounts.empty()) {
        ChemicalEquilibriumNlpInput true_input =
            chemical_equilibrium_input_with_log_k_lambda(input, 1.0);
        ChemicalEquilibriumNlpResult out = solve_single_ce_proof(
            true_input,
            plan,
            layout,
            options,
            balance_tolerance,
            reaction_stationarity_tolerance
        );
        if (!out.accepted && !out.solve.variables.empty()) {
            out.proof_corrector = run_physical_proof_corrector(
                true_input,
                plan,
                layout,
                out.solve.variables,
                balance_tolerance,
                reaction_stationarity_tolerance
            );
            if (out.proof_corrector.accepted) {
                out.postsolve = out.proof_corrector.postsolve;
                out.balance_inf_norm = out.proof_corrector.balance_inf_norm;
                out.reaction_stationarity_inf_norm = out.proof_corrector.reaction_stationarity_inf_norm;
                out.accepted = true;
            }
        }
        out.source_oracle_initial_amounts = true;
        out.seed_source = "caller_initial_amounts";
        out.direct_final_proof_attempted = true;
        out.direct_final_proof_accepted = out.accepted;
        out.continuation.final_proof_status = out.accepted ? "accepted" : "rejected";
        out.continuation.final_stage_id = "lambda_1";
        out.continuation.accepted = out.accepted;
        out.continuation_lambdas = {1.0};
        if (out.accepted) {
            return out;
        }
    }

    FeasibleInitializationResult feasible = solve_max_min_feasible_initialization(
        feasible_initialization_input_from_ce(input),
        ce_stage_options(options, "proof"),
        balance_tolerance
    );
    ChemicalEquilibriumNlpInput seeded_input = input_with_initial_amounts(input, feasible.amounts);
    ChemicalEquilibriumNlpInput true_input =
        chemical_equilibrium_input_with_log_k_lambda(seeded_input, 1.0);

    ChemicalEquilibriumNlpResult direct;
    if (feasible.accepted) {
        direct = solve_single_ce_proof(
            true_input,
            plan,
            layout,
            options,
            balance_tolerance,
            reaction_stationarity_tolerance
        );
    }
    if (feasible.accepted && !direct.accepted && !direct.solve.variables.empty()) {
        direct.proof_corrector = run_physical_proof_corrector(
            true_input,
            plan,
            layout,
            direct.solve.variables,
            balance_tolerance,
            reaction_stationarity_tolerance
        );
        if (direct.proof_corrector.accepted) {
            direct.postsolve = direct.proof_corrector.postsolve;
            direct.balance_inf_norm = direct.proof_corrector.balance_inf_norm;
            direct.reaction_stationarity_inf_norm = direct.proof_corrector.reaction_stationarity_inf_norm;
            direct.accepted = true;
        }
    }
    if (feasible.accepted && direct.accepted) {
        direct.source_oracle_initial_amounts = false;
        direct.seed_source = "max_min_feasible_interior";
        direct.feasible_initialization = feasible;
        direct.direct_final_proof_attempted = true;
        direct.direct_final_proof_accepted = true;
        direct.continuation.final_proof_status = "accepted";
        direct.continuation.final_stage_id = "lambda_1";
        direct.continuation.accepted = true;
        direct.continuation_lambdas = {1.0};
        return direct;
    }

    ContinuationTraceResult trace;
    std::vector<double> lambdas;
    if (feasible.accepted) {
        std::vector<ContinuationStageSpec> stages;
        stages.push_back(ce_homotopy_stage(seeded_input, plan, layout, options, "lambda_0", 0.0, false));
        stages.push_back(ce_homotopy_stage(seeded_input, plan, layout, options, "lambda_half", 0.5, false));
        stages.push_back(ce_homotopy_stage(seeded_input, plan, layout, options, "lambda_1", 1.0, true));
        ContinuationState initial_state;
        initial_state.variables = log_amounts_from_physical_amounts(feasible.amounts);
        trace = run_continuation_plan(stages, initial_state);
        lambdas = {0.0, 0.5, 1.0};
    }

    ChemicalEquilibriumNlpResult out = feasible.accepted
        ? result_from_homotopy_trace(
            true_input,
            plan,
            layout,
            trace,
            balance_tolerance,
            reaction_stationarity_tolerance
        )
        : ChemicalEquilibriumNlpResult{};
    out.continuation = trace;
    if (feasible.accepted
        && !out.accepted
        && !trace.trace.empty()
        && trace.final_stage_id == "lambda_1"
        && !trace.trace.back().solve.variables.empty()) {
        out.proof_corrector = run_physical_proof_corrector(
            true_input,
            plan,
            layout,
            trace.trace.back().solve.variables,
            balance_tolerance,
            reaction_stationarity_tolerance
        );
        if (out.proof_corrector.accepted) {
            out.postsolve = out.proof_corrector.postsolve;
            out.balance_inf_norm = out.proof_corrector.balance_inf_norm;
            out.reaction_stationarity_inf_norm = out.proof_corrector.reaction_stationarity_inf_norm;
            out.accepted = true;
            out.continuation.accepted = true;
            out.continuation.final_proof_status = "accepted";
        }
    }
    out.source_oracle_initial_amounts = false;
    out.seed_source = "max_min_feasible_interior";
    out.feasible_initialization = feasible;
    out.direct_final_proof_attempted = feasible.accepted;
    out.direct_final_proof_accepted = feasible.accepted && direct.accepted;
    out.continuation_lambdas = lambdas;
    return out;
}

}  // namespace epcsaft::native::equilibrium_nlp
