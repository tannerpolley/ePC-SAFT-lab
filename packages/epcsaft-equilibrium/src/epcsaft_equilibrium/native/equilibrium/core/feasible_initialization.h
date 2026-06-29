#pragma once

#include "equilibrium/solvers/ipopt_adapter.h"

#include <string>
#include <vector>

namespace epcsaft::native::equilibrium_nlp {

struct FeasibleInitializationInput {
    std::vector<std::string> species_labels;
    std::vector<std::string> conservation_labels;
    std::vector<double> conservation_matrix_row_major;
    std::vector<double> conservation_totals;
    double amount_floor = 1.0e-30;
};

struct FeasibleInitializationResult {
    bool accepted = false;
    bool solver_ran = false;
    std::string rejection_reason;
    std::vector<double> amounts;
    double margin = 0.0;
    double minimum_amount = 0.0;
    std::vector<double> balance_residuals;
    double balance_inf_norm = 0.0;
    int active_margin_constraint_count = 0;
    IpoptSolveResult solve;
};

FeasibleInitializationResult solve_max_min_feasible_initialization(
    const FeasibleInitializationInput& input,
    const IpoptSolveOptions& options,
    double balance_tolerance
);

}  // namespace epcsaft::native::equilibrium_nlp
