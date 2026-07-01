#include "equilibrium/core/feasible_initialization.h"

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

double amount_upper_bound(const FeasibleInitializationInput& input) {
    double scale = input.amount_floor;
    for (double value : input.conservation_totals) {
        scale = std::max(scale, std::abs(value));
    }
    return 10.0 * std::max(1.0, scale);
}

double matrix_abs_max(const std::vector<double>& matrix) {
    double out = 0.0;
    for (double value : matrix) {
        out = std::max(out, std::abs(value));
    }
    return out;
}

struct ConservationRankProfile {
    std::vector<int> independent_rows;
    std::vector<int> pivot_columns;
};

ConservationRankProfile conservation_rank_profile(
    std::vector<double> matrix,
    int rows,
    int columns
) {
    const double tolerance = 1.0e-12 * std::max(1.0, matrix_abs_max(matrix));
    std::vector<int> row_indices(static_cast<std::size_t>(rows), 0);
    std::iota(row_indices.begin(), row_indices.end(), 0);
    ConservationRankProfile profile;
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
        profile.independent_rows.push_back(row_indices[static_cast<std::size_t>(rank)]);
        profile.pivot_columns.push_back(column);
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
    return profile;
}

std::vector<double> solve_square_linear_system(
    std::vector<double> matrix,
    std::vector<double> rhs,
    int dimension
) {
    require_size(matrix.size(), static_cast<std::size_t>(dimension * dimension), "extent/nullspace matrix");
    require_size(rhs.size(), static_cast<std::size_t>(dimension), "extent/nullspace right hand side");
    const double tolerance = 1.0e-14 * std::max(1.0, matrix_abs_max(matrix));
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
        if (pivot_abs <= tolerance) {
            throw ValueError("extent/nullspace feasible initialization pivot matrix is singular.");
        }
        if (pivot_row != pivot) {
            for (int column = pivot; column < dimension; ++column) {
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
        solution[static_cast<std::size_t>(row)] =
            value / matrix[static_cast<std::size_t>(row * dimension + row)];
    }
    return solution;
}

FeasibleInitializationInput input_with_conservation_rows(
    const FeasibleInitializationInput& input,
    const std::vector<int>& rows
) {
    const int species_count = static_cast<int>(input.species_labels.size());
    FeasibleInitializationInput out;
    out.species_labels = input.species_labels;
    out.amount_floor = input.amount_floor;
    out.conservation_labels.reserve(rows.size());
    out.conservation_totals.reserve(rows.size());
    out.conservation_matrix_row_major.reserve(rows.size() * static_cast<std::size_t>(species_count));
    for (int row : rows) {
        out.conservation_labels.push_back(input.conservation_labels[static_cast<std::size_t>(row)]);
        out.conservation_totals.push_back(input.conservation_totals[static_cast<std::size_t>(row)]);
        const auto offset = static_cast<std::size_t>(row * species_count);
        out.conservation_matrix_row_major.insert(
            out.conservation_matrix_row_major.end(),
            input.conservation_matrix_row_major.begin() + offset,
            input.conservation_matrix_row_major.begin() + offset + species_count
        );
    }
    return out;
}

std::vector<double> balance_residuals(
    const FeasibleInitializationInput& input,
    const std::vector<double>& amounts
) {
    const int species_count = static_cast<int>(input.species_labels.size());
    const int balance_count = static_cast<int>(input.conservation_labels.size());
    std::vector<double> out(static_cast<std::size_t>(balance_count), 0.0);
    for (int row = 0; row < balance_count; ++row) {
        double value = -input.conservation_totals[static_cast<std::size_t>(row)];
        for (int species = 0; species < species_count; ++species) {
            value += input.conservation_matrix_row_major[
                static_cast<std::size_t>(row * species_count + species)
            ] * amounts[static_cast<std::size_t>(species)];
        }
        out[static_cast<std::size_t>(row)] = value;
    }
    return out;
}

void validate_input(const FeasibleInitializationInput& input) {
    const std::size_t species_count = input.species_labels.size();
    const std::size_t balance_count = input.conservation_labels.size();
    if (species_count == 0U) {
        throw ValueError("feasible initialization requires at least one species.");
    }
    if (balance_count == 0U) {
        throw ValueError("feasible initialization requires at least one conservation row.");
    }
    require_size(
        input.conservation_matrix_row_major.size(),
        species_count * balance_count,
        "feasible initialization conservation matrix"
    );
    require_size(
        input.conservation_totals.size(),
        balance_count,
        "feasible initialization conservation totals"
    );
    require_positive_finite(input.amount_floor, "feasible initialization amount floor");
    for (double value : input.conservation_matrix_row_major) {
        require_finite(value, "feasible initialization conservation matrix");
    }
    for (double value : input.conservation_totals) {
        require_finite(value, "feasible initialization conservation totals");
    }
}

class MaxMinFeasibleInitializationNlp final : public NlpProblem {
public:
    explicit MaxMinFeasibleInitializationNlp(FeasibleInitializationInput input)
        : input_(std::move(input)),
          upper_bound_(amount_upper_bound(input_)) {}

    std::string name() const override {
        return "max_min_feasible_initialization";
    }

    int variable_count() const override {
        return static_cast<int>(input_.species_labels.size()) + 1;
    }

    int constraint_count() const override {
        return static_cast<int>(input_.conservation_labels.size() + input_.species_labels.size());
    }

    int jacobian_nonzero_count() const override {
        const int species_count = static_cast<int>(input_.species_labels.size());
        const int balance_count = static_cast<int>(input_.conservation_labels.size());
        return balance_count * species_count + 2 * species_count;
    }

    NlpBounds bounds() const override {
        const std::size_t species_count = input_.species_labels.size();
        const std::size_t balance_count = input_.conservation_labels.size();
        NlpBounds out;
        out.variable_lower.assign(species_count + 1U, input_.amount_floor);
        out.variable_upper.assign(species_count + 1U, upper_bound_);
        out.constraint_lower.assign(balance_count, 0.0);
        out.constraint_upper.assign(balance_count, 0.0);
        out.constraint_lower.insert(out.constraint_lower.end(), species_count, 0.0);
        out.constraint_upper.insert(out.constraint_upper.end(), species_count, upper_bound_);
        return out;
    }

    std::vector<double> initial_point() const override {
        const std::size_t species_count = input_.species_labels.size();
        const double amount = std::max(10.0 * input_.amount_floor, upper_bound_ / (10.0 * species_count));
        std::vector<double> out(species_count + 1U, amount);
        out.back() = input_.amount_floor;
        return out;
    }

    double objective(const std::vector<double>& variables) const override {
        return -variables.back();
    }

    std::vector<double> objective_gradient(const std::vector<double>& variables) const override {
        std::vector<double> out(variables.size(), 0.0);
        out.back() = -1.0;
        return out;
    }

    std::vector<double> constraints(const std::vector<double>& variables) const override {
        const int species_count = static_cast<int>(input_.species_labels.size());
        const int balance_count = static_cast<int>(input_.conservation_labels.size());
        std::vector<double> out;
        out.reserve(static_cast<std::size_t>(constraint_count()));
        for (int row = 0; row < balance_count; ++row) {
            double value = -input_.conservation_totals[static_cast<std::size_t>(row)];
            for (int species = 0; species < species_count; ++species) {
                value += input_.conservation_matrix_row_major[
                    static_cast<std::size_t>(row * species_count + species)
                ] * variables[static_cast<std::size_t>(species)];
            }
            out.push_back(value);
        }
        const double margin = variables.back();
        for (int species = 0; species < species_count; ++species) {
            out.push_back(variables[static_cast<std::size_t>(species)] - margin);
        }
        return out;
    }

    NlpJacobianStructure jacobian_structure() const override {
        const int species_count = static_cast<int>(input_.species_labels.size());
        const int balance_count = static_cast<int>(input_.conservation_labels.size());
        NlpJacobianStructure out;
        out.rows.reserve(static_cast<std::size_t>(jacobian_nonzero_count()));
        out.cols.reserve(static_cast<std::size_t>(jacobian_nonzero_count()));
        for (int row = 0; row < balance_count; ++row) {
            for (int species = 0; species < species_count; ++species) {
                out.rows.push_back(row);
                out.cols.push_back(species);
            }
        }
        for (int species = 0; species < species_count; ++species) {
            const int row = balance_count + species;
            out.rows.push_back(row);
            out.cols.push_back(species);
            out.rows.push_back(row);
            out.cols.push_back(species_count);
        }
        return out;
    }

    std::vector<double> jacobian_values(const std::vector<double>& variables) const override {
        (void)variables;
        const int species_count = static_cast<int>(input_.species_labels.size());
        const int balance_count = static_cast<int>(input_.conservation_labels.size());
        std::vector<double> out;
        out.reserve(static_cast<std::size_t>(jacobian_nonzero_count()));
        out.insert(
            out.end(),
            input_.conservation_matrix_row_major.begin(),
            input_.conservation_matrix_row_major.end()
        );
        for (int species = 0; species < species_count; ++species) {
            out.push_back(1.0);
            out.push_back(-1.0);
        }
        (void)balance_count;
        return out;
    }

    bool has_exact_hessian() const override {
        return true;
    }

    int hessian_nonzero_count() const override {
        return 1;
    }

    NlpHessianStructure hessian_structure() const override {
        const int margin_index = variable_count() - 1;
        return {{margin_index}, {margin_index}};
    }

    std::vector<double> hessian_values(
        const std::vector<double>& variables,
        double objective_factor,
        const std::vector<double>& constraint_multipliers
    ) const override {
        (void)variables;
        (void)objective_factor;
        (void)constraint_multipliers;
        return {0.0};
    }

    std::string hessian_backend() const override {
        return "linear_zero_hessian";
    }

    NlpScaling scaling() const override {
        const std::size_t species_count = input_.species_labels.size();
        const std::size_t balance_count = input_.conservation_labels.size();
        NlpScaling out;
        out.objective = 1.0 / std::max(1.0, upper_bound_);
        out.variables.assign(species_count + 1U, 1.0 / std::max(1.0, upper_bound_));
        out.constraints.reserve(balance_count + species_count);
        for (double total : input_.conservation_totals) {
            out.constraints.push_back(1.0 / std::max(1.0, std::abs(total)));
        }
        out.constraints.insert(out.constraints.end(), species_count, 1.0 / std::max(1.0, upper_bound_));
        return out;
    }

    std::map<std::string, std::string> diagnostics() const override {
        return {
            {"initializer", "max_min_feasible_interior"},
            {"constraint_model", "conservation_equalities_plus_amount_margin_inequalities"},
            {"hessian_backend", "linear_zero_hessian"},
        };
    }

private:
    FeasibleInitializationInput input_;
    double upper_bound_;
};

FeasibleInitializationResult rejected_without_solve(const std::string& rejection_reason) {
    FeasibleInitializationResult out;
    out.accepted = false;
    out.solver_ran = false;
    out.rejection_reason = rejection_reason;
    return out;
}

double positive_nullspace_fill_amount(const FeasibleInitializationInput& input) {
    double max_total = input.amount_floor;
    double min_positive_total = std::numeric_limits<double>::infinity();
    for (double total : input.conservation_totals) {
        max_total = std::max(max_total, std::abs(total));
        if (total > 0.0) {
            min_positive_total = std::min(min_positive_total, total);
        }
    }
    const double species_count = static_cast<double>(std::max<std::size_t>(1U, input.species_labels.size()));
    const double interior_cap = std::max(input.amount_floor, max_total / (10.0 * species_count));
    const double positive_scale = std::isfinite(min_positive_total)
        ? min_positive_total
        : 10.0 * input.amount_floor;
    return std::max(10.0 * input.amount_floor, std::min(interior_cap, positive_scale));
}

std::string rank_status_for(
    const ConservationRankProfile& profile,
    int balance_count,
    double balance_inf_norm,
    double balance_tolerance
) {
    if (static_cast<int>(profile.independent_rows.size()) == balance_count) {
        return "full_rank";
    }
    return balance_inf_norm <= balance_tolerance
        ? "rank_deficient_consistent"
        : "rank_deficient_inconsistent";
}

FeasibleInitializationAttempt attempt_from_result(
    const FeasibleInitializationResult& result,
    const ConservationRankProfile& profile,
    int balance_count,
    double amount_floor,
    double balance_tolerance
) {
    FeasibleInitializationAttempt out;
    out.initializer = "max_min_feasible_interior";
    out.accepted = result.accepted;
    out.solver_ran = result.solver_ran;
    out.rejection_reason = result.rejection_reason;
    out.amounts = result.amounts;
    out.margin = result.margin;
    out.minimum_amount = result.minimum_amount;
    out.balance_residuals = result.balance_residuals;
    out.balance_inf_norm = result.balance_inf_norm;
    out.active_margin_constraint_count = result.active_margin_constraint_count;
    out.rank = static_cast<int>(profile.independent_rows.size());
    out.independent_row_count = out.rank;
    out.rank_status = rank_status_for(profile, balance_count, result.balance_inf_norm, balance_tolerance);
    out.positive = result.minimum_amount > amount_floor;
    out.conservation_closed = result.balance_inf_norm <= balance_tolerance;
    return out;
}

FeasibleInitializationAttempt solve_extent_nullspace_feasible_initialization(
    const FeasibleInitializationInput& input,
    const ConservationRankProfile& profile,
    double balance_tolerance
) {
    const int species_count = static_cast<int>(input.species_labels.size());
    const int balance_count = static_cast<int>(input.conservation_labels.size());
    const int rank = static_cast<int>(profile.independent_rows.size());
    FeasibleInitializationAttempt out;
    out.initializer = "extent_nullspace_feasible";
    out.rank = rank;
    out.independent_row_count = rank;
    if (rank == 0) {
        out.rejection_reason = "extent_nullspace_rank_deficient_conservation_constraints";
        out.rank_status = "rank_deficient_inconsistent";
        return out;
    }

    out.amounts.assign(static_cast<std::size_t>(species_count), positive_nullspace_fill_amount(input));
    std::vector<bool> pivot_species(static_cast<std::size_t>(species_count), false);
    for (int column : profile.pivot_columns) {
        pivot_species[static_cast<std::size_t>(column)] = true;
    }

    std::vector<double> pivot_matrix(static_cast<std::size_t>(rank * rank), 0.0);
    std::vector<double> rhs(static_cast<std::size_t>(rank), 0.0);
    for (int equation = 0; equation < rank; ++equation) {
        const int row = profile.independent_rows[static_cast<std::size_t>(equation)];
        rhs[static_cast<std::size_t>(equation)] = input.conservation_totals[static_cast<std::size_t>(row)];
        for (int species = 0; species < species_count; ++species) {
            const double coefficient =
                input.conservation_matrix_row_major[static_cast<std::size_t>(row * species_count + species)];
            if (pivot_species[static_cast<std::size_t>(species)]) {
                continue;
            }
            rhs[static_cast<std::size_t>(equation)] -=
                coefficient * out.amounts[static_cast<std::size_t>(species)];
        }
        for (int pivot = 0; pivot < rank; ++pivot) {
            const int column = profile.pivot_columns[static_cast<std::size_t>(pivot)];
            pivot_matrix[static_cast<std::size_t>(equation * rank + pivot)] =
                input.conservation_matrix_row_major[static_cast<std::size_t>(row * species_count + column)];
        }
    }

    try {
        const std::vector<double> pivot_amounts =
            solve_square_linear_system(std::move(pivot_matrix), std::move(rhs), rank);
        for (int pivot = 0; pivot < rank; ++pivot) {
            const int column = profile.pivot_columns[static_cast<std::size_t>(pivot)];
            out.amounts[static_cast<std::size_t>(column)] = pivot_amounts[static_cast<std::size_t>(pivot)];
        }
    } catch (const std::exception&) {
        out.rejection_reason = "extent_nullspace_singular_pivot_system";
        out.balance_residuals = balance_residuals(input, out.amounts);
        out.balance_inf_norm = vector_inf_norm(out.balance_residuals);
        out.rank_status = rank_status_for(profile, balance_count, out.balance_inf_norm, balance_tolerance);
        return out;
    }

    out.minimum_amount = *std::min_element(out.amounts.begin(), out.amounts.end());
    out.margin = out.minimum_amount;
    out.positive = std::all_of(out.amounts.begin(), out.amounts.end(), [amount_floor = input.amount_floor](double amount) {
        return std::isfinite(amount) && amount > amount_floor;
    });
    out.balance_residuals = balance_residuals(input, out.amounts);
    out.balance_inf_norm = vector_inf_norm(out.balance_residuals);
    out.conservation_closed = out.balance_inf_norm <= balance_tolerance;
    out.rank_status = rank_status_for(profile, balance_count, out.balance_inf_norm, balance_tolerance);
    if (!out.positive) {
        out.rejection_reason = "extent_nullspace_nonpositive_candidate";
        return out;
    }
    if (!out.conservation_closed) {
        out.rejection_reason = "extent_nullspace_conservation_residual";
        return out;
    }
    out.accepted = true;
    return out;
}

}  // namespace

FeasibleInitializationResult solve_max_min_feasible_initialization(
    const FeasibleInitializationInput& input,
    const IpoptSolveOptions& options,
    double balance_tolerance
) {
    validate_input(input);
    require_positive_finite(balance_tolerance, "feasible initialization balance tolerance");
    const int species_count = static_cast<int>(input.species_labels.size());
    const int balance_count = static_cast<int>(input.conservation_labels.size());
    const ConservationRankProfile profile = conservation_rank_profile(
        input.conservation_matrix_row_major,
        balance_count,
        species_count
    );
    std::vector<int> independent_rows = profile.independent_rows;
    std::sort(independent_rows.begin(), independent_rows.end());
    if (independent_rows.empty()) {
        FeasibleInitializationResult out =
            rejected_without_solve("rank_deficient_conservation_constraints");
        FeasibleInitializationAttempt max_attempt =
            attempt_from_result(out, profile, balance_count, input.amount_floor, balance_tolerance);
        FeasibleInitializationAttempt extent_attempt =
            solve_extent_nullspace_feasible_initialization(input, profile, balance_tolerance);
        out.attempt_order = {"max_min_feasible_interior", "extent_nullspace_feasible"};
        out.attempts = {max_attempt, extent_attempt};
        out.selected_initializer = "";
        return out;
    }
    const FeasibleInitializationInput solve_input =
        independent_rows.size() == static_cast<std::size_t>(balance_count)
        ? input
        : input_with_conservation_rows(input, independent_rows);

    MaxMinFeasibleInitializationNlp problem(solve_input);
    FeasibleInitializationResult out;
    out.solve = solve_ipopt_nlp(problem, options);
    out.solver_ran = out.solve.solver_ran;
    if (out.solve.variables.size() >= static_cast<std::size_t>(species_count + 1)) {
        out.amounts.assign(out.solve.variables.begin(), out.solve.variables.begin() + species_count);
        const double raw_margin = out.solve.variables[static_cast<std::size_t>(species_count)];
        out.minimum_amount = *std::min_element(out.amounts.begin(), out.amounts.end());
        out.margin = std::min(raw_margin, out.minimum_amount);
        out.balance_residuals = balance_residuals(input, out.amounts);
        out.balance_inf_norm = vector_inf_norm(out.balance_residuals);
        const double active_tolerance = std::max(10.0 * options.tolerance, 1.0e-10);
        for (double amount : out.amounts) {
            if (std::abs(amount - out.margin) <= active_tolerance) {
                out.active_margin_constraint_count += 1;
            }
        }
    }

    const double raw_margin = out.solve.variables.size() >= static_cast<std::size_t>(species_count + 1)
        ? out.solve.variables[static_cast<std::size_t>(species_count)]
        : 0.0;
    const double margin_tolerance = std::max(
        std::max(100.0 * balance_tolerance, 100.0 * options.tolerance),
        1.0e-12
    );
    const bool positive_interior = out.margin > input.amount_floor
        && raw_margin - out.minimum_amount <= margin_tolerance;
    out.accepted = out.solve.accepted
        && positive_interior
        && out.balance_inf_norm <= balance_tolerance;
    out.rejection_reason = out.accepted ? "" : "initializer_solve_rejected";
    FeasibleInitializationAttempt max_attempt =
        attempt_from_result(out, profile, balance_count, input.amount_floor, balance_tolerance);
    FeasibleInitializationAttempt extent_attempt =
        solve_extent_nullspace_feasible_initialization(input, profile, balance_tolerance);
    out.attempt_order = {"max_min_feasible_interior", "extent_nullspace_feasible"};
    out.attempts = {max_attempt, extent_attempt};
    if (out.accepted) {
        out.initializer = "max_min_feasible_interior";
        out.selected_initializer = "max_min_feasible_interior";
        return out;
    }
    if (extent_attempt.accepted) {
        out.initializer = "extent_nullspace_feasible";
        out.selected_initializer = "extent_nullspace_feasible";
        out.accepted = true;
        out.solver_ran = false;
        out.rejection_reason = "";
        out.amounts = extent_attempt.amounts;
        out.margin = extent_attempt.margin;
        out.minimum_amount = extent_attempt.minimum_amount;
        out.balance_residuals = extent_attempt.balance_residuals;
        out.balance_inf_norm = extent_attempt.balance_inf_norm;
        out.active_margin_constraint_count = 0;
        out.solve = IpoptSolveResult{};
        return out;
    }
    out.selected_initializer = "";
    return out;
}

}  // namespace epcsaft::native::equilibrium_nlp
