#pragma once

#include <string>
#include <vector>

namespace epcsaft::native::implicit_sensitivity {

struct ImplicitSensitivityProblem {
    int explicit_variable_count = 0;
    int solved_variable_count = 0;
    int output_count = 0;
    int residual_row0 = 0;
    std::string backend = "cppad_implicit";
    std::string helper_name = "implicit_sensitivity";
    std::vector<double> values;
    std::vector<double> jacobian_row_major;
    std::vector<double> hessian_tensor_row_major;
};

struct ImplicitSensitivityResult {
    std::string backend;
    std::string helper_name;
    int explicit_variable_count = 0;
    int solved_variable_count = 0;
    int output_count = 0;
    std::vector<double> output_values;
    std::vector<double> solved_first_row_major;
    std::vector<double> solved_second_tensor_row_major;
    std::vector<double> output_first_row_major;
    std::vector<double> output_second_tensor_row_major;
};

ImplicitSensitivityResult solve_implicit_sensitivity(
    const ImplicitSensitivityProblem& problem,
    bool include_second_order
);

}  // namespace epcsaft::native::implicit_sensitivity
