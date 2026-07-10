#include "equilibrium/core/chemical_equilibrium_nlp.h"

#include "equilibrium/core/chemical_equilibrium_objective.h"
#include "equilibrium/core/route_metadata.h"
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

void require_unit_interval(double value, const std::string& label) {
    if (std::isfinite(value) && value >= 0.0 && value <= 1.0) {
        return;
    }
    throw ValueError(label + " must be finite and between zero and one.");
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

ReactionProofScalingMetrics reaction_proof_scaling_metrics_for(
    const ChemicalEquilibriumNlpInput& input,
    const HomogeneousChemicalEquilibriumBlockResult& block,
    double reaction_stationarity_tolerance
) {
    const int species_count = static_cast<int>(input.species_labels.size());
    const int reaction_count = static_cast<int>(input.reaction_labels.size());
    require_positive_finite(
        reaction_stationarity_tolerance,
        "chemical equilibrium reaction stationarity tolerance"
    );
    require_size(
        input.stoichiometry_row_major.size(),
        static_cast<std::size_t>(reaction_count * species_count),
        "chemical equilibrium reaction stoichiometry"
    );
    require_size(
        input.log_equilibrium_constants.size(),
        static_cast<std::size_t>(reaction_count),
        "chemical equilibrium log equilibrium constants"
    );
    require_size(
        block.reaction_affinities.size(),
        static_cast<std::size_t>(reaction_count),
        "chemical equilibrium reaction affinity proof metrics"
    );

    ReactionProofScalingMetrics out;
    out.reaction_scaling_factors.assign(static_cast<std::size_t>(reaction_count), 1.0);
    out.reaction_row_norms.assign(static_cast<std::size_t>(reaction_count), 0.0);
    out.reaction_scaling_min = reaction_count == 0 ? 1.0 : std::numeric_limits<double>::infinity();
    out.reaction_scaling_max = reaction_count == 0 ? 1.0 : 0.0;

    for (int reaction = 0; reaction < reaction_count; ++reaction) {
        const std::size_t row_offset = static_cast<std::size_t>(reaction * species_count);
        double row_l1_norm = 0.0;
        double row_l2_norm_squared = 0.0;
        for (int species = 0; species < species_count; ++species) {
            const double coefficient =
                input.stoichiometry_row_major[row_offset + static_cast<std::size_t>(species)];
            row_l1_norm += std::abs(coefficient);
            row_l2_norm_squared += coefficient * coefficient;
        }
        const double row_l2_norm = std::sqrt(row_l2_norm_squared);
        out.reaction_row_norms[static_cast<std::size_t>(reaction)] = row_l2_norm;
        const double denominator = std::max(
            {1.0, row_l1_norm, std::abs(input.log_equilibrium_constants[static_cast<std::size_t>(reaction)])}
        );
        const double scale = 1.0 / denominator;
        out.reaction_scaling_factors[static_cast<std::size_t>(reaction)] = scale;
        out.reaction_scaling_min = std::min(out.reaction_scaling_min, scale);
        out.reaction_scaling_max = std::max(out.reaction_scaling_max, scale);
        out.scaled_reaction_stationarity_inf_norm = std::max(
            out.scaled_reaction_stationarity_inf_norm,
            scale
                * std::abs(block.reaction_affinities[static_cast<std::size_t>(reaction)])
                / reaction_stationarity_tolerance
        );
    }

    double condition_estimate = 1.0;
    for (int row = 0; row < reaction_count; ++row) {
        const double row_norm = out.reaction_row_norms[static_cast<std::size_t>(row)];
        if (!(row_norm > 0.0)) {
            continue;
        }
        for (int column = row + 1; column < reaction_count; ++column) {
            const double column_norm = out.reaction_row_norms[static_cast<std::size_t>(column)];
            if (!(column_norm > 0.0)) {
                continue;
            }
            double dot = 0.0;
            for (int species = 0; species < species_count; ++species) {
                dot += input.stoichiometry_row_major[
                    static_cast<std::size_t>(row * species_count + species)
                ] * input.stoichiometry_row_major[
                    static_cast<std::size_t>(column * species_count + species)
                ];
            }
            const double correlation = std::min(
                1.0 - 1.0e-16,
                std::abs(dot / (row_norm * column_norm))
            );
            condition_estimate = std::max(
                condition_estimate,
                std::sqrt((1.0 + correlation) / std::max(1.0e-16, 1.0 - correlation))
            );
        }
    }
    out.reaction_basis_condition_estimate = condition_estimate;
    out.unscaled_reaction_stationarity_inf_norm = vector_inf_norm(block.reaction_affinities);
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
        require_unit_interval(input.eos_activity_lambda, "chemical equilibrium EOS activity continuation lambda");
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

ReactionProofScalingMetrics HomogeneousChemicalEquilibriumNlp::reaction_proof_scaling_metrics(
    const HomogeneousChemicalEquilibriumBlockResult& block,
    double reaction_stationarity_tolerance
) const {
    return reaction_proof_scaling_metrics_for(input_, block, reaction_stationarity_tolerance);
}

ChemicalEquilibriumProofEvaluation HomogeneousChemicalEquilibriumNlp::evaluate_physical_proof(
    const std::vector<double>& solver_variables,
    double balance_tolerance,
    double reaction_stationarity_tolerance
) const {
    require_positive_finite(balance_tolerance, "chemical equilibrium balance tolerance");
    ChemicalEquilibriumProofEvaluation out;
    const std::vector<double> amounts = physical_amounts_from_solver_variables(solver_variables);
    out.block = evaluate_physical_block(amounts);
    out.balance_inf_norm = vector_inf_norm(out.block.balance_residuals);
    out.reaction_stationarity_inf_norm = vector_inf_norm(out.block.reaction_affinities);
    out.proof_metrics = reaction_proof_scaling_metrics(
        out.block,
        reaction_stationarity_tolerance
    );
    out.thermodynamically_accepted = out.balance_inf_norm <= balance_tolerance
        && out.reaction_stationarity_inf_norm <= reaction_stationarity_tolerance;
    return out;
}

std::vector<double> HomogeneousChemicalEquilibriumNlp::initial_constraint_multipliers() const {
    const HomogeneousChemicalEquilibriumBlockResult block = evaluate_physical_block(input_.initial_amounts);
    return estimate_constraint_multipliers(
        input_,
        block.objective_gradient,
        block.objective_scaling,
        block.balance_scaling
    );
}

FeasibleInitializationInput chemical_equilibrium_feasible_initialization_input(
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

namespace {

struct PhysicalProofResidualSystem {
    HomogeneousChemicalEquilibriumBlockResult block;
    ReactionProofScalingMetrics proof_metrics;
    std::vector<double> residuals;
    std::vector<double> jacobian_row_major;
    double residual_inf_norm = 0.0;
    double balance_inf_norm = 0.0;
    double reaction_stationarity_inf_norm = 0.0;
    bool thermodynamically_accepted = false;
};

PhysicalProofResidualSystem evaluate_physical_proof_residual_system(
    const HomogeneousChemicalEquilibriumNlp& problem,
    const std::vector<double>& variables,
    const std::vector<int>& independent_balance_rows,
    double balance_tolerance,
    double reaction_stationarity_tolerance
) {
    const int species_count = problem.variable_count();
    const int reaction_count = static_cast<int>(problem.input().reaction_labels.size());
    const ChemicalEquilibriumProofEvaluation proof = problem.evaluate_physical_proof(
        variables,
        balance_tolerance,
        reaction_stationarity_tolerance
    );
    const std::vector<double>& amounts = proof.block.amounts;
    PhysicalProofResidualSystem out;
    out.block = proof.block;
    out.balance_inf_norm = proof.balance_inf_norm;
    out.reaction_stationarity_inf_norm = proof.reaction_stationarity_inf_norm;
    out.proof_metrics = proof.proof_metrics;
    out.thermodynamically_accepted = proof.thermodynamically_accepted;
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
        const double reaction_scale =
            out.proof_metrics.reaction_scaling_factors[static_cast<std::size_t>(reaction)];
        out.residuals[static_cast<std::size_t>(equation)] =
            reaction_scale
            * out.block.reaction_affinities[static_cast<std::size_t>(reaction)]
            / reaction_stationarity_tolerance;
        for (int species = 0; species < species_count; ++species) {
            out.jacobian_row_major[static_cast<std::size_t>(equation * species_count + species)] =
                reaction_scale
                *
                out.block.affinity_jacobian_row_major[
                    static_cast<std::size_t>(reaction * species_count + species)
                ] * amounts[static_cast<std::size_t>(species)] / reaction_stationarity_tolerance;
        }
        ++equation;
    }
    out.residual_inf_norm = vector_inf_norm(out.residuals);
    return out;
}

}  // namespace

PhysicalProofCorrectorResult HomogeneousChemicalEquilibriumNlp::correct_physical_proof(
    const std::vector<double>& initial_variables,
    double balance_tolerance,
    double reaction_stationarity_tolerance
) const {
    constexpr int kMaxIterations = 24;
    constexpr int kMaxLineSearchTrials = 16;
    constexpr double kMinimumStepDecrease = 1.0e-12;

    PhysicalProofCorrectorResult out;
    out.attempted = true;
    out.status = "started";
    const int species_count = variable_count();
    const int balance_count = constraint_count();
    require_size(
        initial_variables.size(),
        static_cast<std::size_t>(species_count),
        "chemical equilibrium proof-corrector initial variables"
    );
    const std::vector<int> independent_balance_rows = independent_row_indices(
        input_.conservation_matrix_row_major,
        balance_count,
        species_count
    );
    if (independent_balance_rows.empty()) {
        out.status = "rejected_no_independent_balance_rows";
        return out;
    }
    const int equation_count =
        static_cast<int>(independent_balance_rows.size())
        + static_cast<int>(input_.reaction_labels.size());
    if (equation_count != species_count) {
        out.status = "rejected_non_square_physical_proof_system";
        return out;
    }

    std::vector<double> variables = initial_variables;
    PhysicalProofResidualSystem system = evaluate_physical_proof_residual_system(
        *this,
        variables,
        independent_balance_rows,
        balance_tolerance,
        reaction_stationarity_tolerance
    );
    out.initial_residual_inf_norm = system.residual_inf_norm;
    out.initial_balance_inf_norm = system.balance_inf_norm;
    out.initial_reaction_stationarity_inf_norm = system.reaction_stationarity_inf_norm;
    out.proof_metrics = system.proof_metrics;
    for (int iteration = 0; iteration <= kMaxIterations; ++iteration) {
        out.iteration_count = iteration;
        out.residual_inf_norm = system.residual_inf_norm;
        out.balance_inf_norm = system.balance_inf_norm;
        out.reaction_stationarity_inf_norm = system.reaction_stationarity_inf_norm;
        out.proof_metrics = system.proof_metrics;
        out.variables = variables;
        out.postsolve = system.block;
        if (system.thermodynamically_accepted) {
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
                *this,
                trial_variables,
                independent_balance_rows,
                balance_tolerance,
                reaction_stationarity_tolerance
            );
            if (trial_system.thermodynamically_accepted
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

}  // namespace epcsaft::native::equilibrium_nlp
