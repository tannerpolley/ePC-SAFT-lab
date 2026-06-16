#pragma once

#include <string>
#include <vector>

struct add_args;

namespace epcsaft::native::equilibrium_nlp {

struct PhaseEquilibriumResidualBlockResult {
    std::string block;
    std::string derivative_backend;
    int phase_count = 0;
    int species_count = 0;
    int variable_count = 0;
    int constraint_count = 0;
    int residual_count = 0;
    int full_square_constraint_count = 0;
    std::vector<double> reduced_ln_fugacity_values;
    std::vector<double> residuals;
    std::vector<double> jacobian_row_major;
    std::vector<double> hessian_tensor_row_major;
    std::vector<std::string> residual_names;
    bool exact_jacobian_available = false;
    bool exact_hessian_available = false;
    int local_jacobian_rows = 0;
    int local_jacobian_cols = 0;
    int local_hessian_rows = 0;
    int local_hessian_cols = 0;
    int local_hessian_depth = 0;
    int global_jacobian_rows = 0;
    int global_jacobian_cols = 0;
    int global_hessian_rows = 0;
    int global_hessian_cols = 0;
    int global_hessian_depth = 0;
    int residual_jacobian_nonzero_count = 0;
    int residual_hessian_nonzero_count = 0;
    std::vector<double> density_amount_jacobian;
    std::vector<double> composition_amount_jacobian;
    std::vector<double> phase_minimum_compositions;
};

PhaseEquilibriumResidualBlockResult evaluate_phase_equilibrium_residual_block(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<std::vector<double>>& phase_amounts,
    const std::vector<double>& volumes
);

}  // namespace epcsaft::native::equilibrium_nlp
