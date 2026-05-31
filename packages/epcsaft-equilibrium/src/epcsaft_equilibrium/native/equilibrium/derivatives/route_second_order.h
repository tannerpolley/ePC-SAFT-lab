#pragma once

#include <string>
#include <vector>

namespace epcsaft::native::equilibrium_nlp {

void require_square_block(
    const std::vector<double>& values,
    int variable_count,
    const std::string& label
);

void require_third_derivative_tensor(
    const std::vector<double>& values,
    int variable_count,
    const std::string& label
);

void symmetrize_square_block(std::vector<double>& values, int variable_count);

std::vector<int> fixed_temperature_global_indices(int phase, int local_variable_count);

std::vector<int> fixed_pressure_global_indices(
    int phase,
    int local_variable_count,
    int temperature_col
);

void add_local_hessian_to_dense(
    std::vector<double>& dense,
    int variable_count,
    const std::vector<int>& global_indices,
    const std::vector<double>& local_hessian,
    double scale,
    const std::string& label
);

void add_local_hessian_to_constraint_tensor(
    std::vector<double>& tensor,
    int constraint_row,
    int variable_count,
    const std::vector<int>& global_indices,
    const std::vector<double>& local_hessian,
    double scale,
    const std::string& label
);

std::vector<double> third_derivative_slice(
    const std::vector<double>& tensor,
    int component,
    int variable_count,
    const std::string& label
);

}  // namespace epcsaft::native::equilibrium_nlp
