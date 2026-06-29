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

int row_rank(
    std::vector<double> matrix,
    int rows,
    int columns
) {
    const double tolerance = 1.0e-12 * std::max(1.0, matrix_abs_max(matrix));
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
        }
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
    return rank;
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
    if (row_rank(input.conservation_matrix_row_major, balance_count, species_count) < balance_count) {
        return rejected_without_solve("rank_deficient_conservation_constraints");
    }

    MaxMinFeasibleInitializationNlp problem(input);
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
    return out;
}

}  // namespace epcsaft::native::equilibrium_nlp
