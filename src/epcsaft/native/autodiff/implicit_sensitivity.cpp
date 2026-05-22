#include "autodiff/implicit_sensitivity.h"

#include <algorithm>
#include <cmath>
#include <cstddef>

#include "model/native_types.h"

namespace epcsaft::native::implicit_sensitivity {

namespace {

void require_positive_count(int value, const std::string& label) {
    if (value <= 0) {
        throw ValueError("Implicit sensitivity helper requires positive " + label + ".");
    }
}

void require_size(const std::vector<double>& values, std::size_t expected, const std::string& label) {
    if (values.size() != expected) {
        throw ValueError("Implicit sensitivity helper received invalid " + label + " size.");
    }
    for (double value : values) {
        if (!std::isfinite(value)) {
            throw ValueError("Implicit sensitivity helper received non-finite " + label + ".");
        }
    }
}

std::vector<double> solve_linear_system(std::vector<double> matrix, std::vector<double> rhs, int n) {
    require_size(matrix, static_cast<std::size_t>(n * n), "matrix");
    require_size(rhs, static_cast<std::size_t>(n), "right-hand side");

    for (int col = 0; col < n; ++col) {
        int pivot = col;
        double pivot_abs = std::abs(matrix[static_cast<std::size_t>(col * n + col)]);
        for (int row = col + 1; row < n; ++row) {
            const double candidate_abs = std::abs(matrix[static_cast<std::size_t>(row * n + col)]);
            if (candidate_abs > pivot_abs) {
                pivot = row;
                pivot_abs = candidate_abs;
            }
        }
        if (pivot_abs <= 1.0e-30) {
            throw ValueError("Implicit sensitivity helper matrix is singular.");
        }
        if (pivot != col) {
            for (int j = col; j < n; ++j) {
                std::swap(matrix[static_cast<std::size_t>(col * n + j)], matrix[static_cast<std::size_t>(pivot * n + j)]);
            }
            std::swap(rhs[static_cast<std::size_t>(col)], rhs[static_cast<std::size_t>(pivot)]);
        }
        const double pivot_value = matrix[static_cast<std::size_t>(col * n + col)];
        for (int row = col + 1; row < n; ++row) {
            const double factor = matrix[static_cast<std::size_t>(row * n + col)] / pivot_value;
            matrix[static_cast<std::size_t>(row * n + col)] = 0.0;
            for (int j = col + 1; j < n; ++j) {
                matrix[static_cast<std::size_t>(row * n + j)] -= factor * matrix[static_cast<std::size_t>(col * n + j)];
            }
            rhs[static_cast<std::size_t>(row)] -= factor * rhs[static_cast<std::size_t>(col)];
        }
    }

    std::vector<double> out(static_cast<std::size_t>(n), 0.0);
    for (int row = n - 1; row >= 0; --row) {
        double accum = rhs[static_cast<std::size_t>(row)];
        for (int col = row + 1; col < n; ++col) {
            accum -= matrix[static_cast<std::size_t>(row * n + col)] * out[static_cast<std::size_t>(col)];
        }
        out[static_cast<std::size_t>(row)] = accum / matrix[static_cast<std::size_t>(row * n + row)];
    }
    return out;
}

void require_result_finite(const std::vector<double>& values, const std::string& label) {
    for (double value : values) {
        if (!std::isfinite(value)) {
            throw ValueError("Implicit sensitivity helper produced non-finite " + label + ".");
        }
    }
}

}  // namespace

ImplicitSensitivityResult solve_implicit_sensitivity(
    const ImplicitSensitivityProblem& problem,
    bool include_second_order
) {
    require_positive_count(problem.explicit_variable_count, "explicit variable count");
    require_positive_count(problem.solved_variable_count, "solved variable count");
    require_positive_count(problem.output_count, "output count");
    if (problem.residual_row0 < problem.output_count) {
        throw ValueError("Implicit sensitivity helper residual rows overlap output rows.");
    }

    const int explicit_count = problem.explicit_variable_count;
    const int solved_count = problem.solved_variable_count;
    const int output_count = problem.output_count;
    const int variable_count = explicit_count + solved_count;
    const int row_count = problem.residual_row0 + solved_count;

    require_size(problem.values, static_cast<std::size_t>(row_count), "value vector");
    require_size(
        problem.jacobian_row_major,
        static_cast<std::size_t>(row_count * variable_count),
        "Jacobian"
    );
    if (include_second_order) {
        require_size(
            problem.hessian_tensor_row_major,
            static_cast<std::size_t>(row_count * variable_count * variable_count),
            "Hessian tensor"
        );
    }

    const auto jac = [&](int row, int col) {
        return problem.jacobian_row_major[static_cast<std::size_t>(row * variable_count + col)];
    };
    const auto hess = [&](int output, int row, int col) {
        return problem.hessian_tensor_row_major[
            static_cast<std::size_t>(output * variable_count * variable_count + row * variable_count + col)
        ];
    };

    std::vector<double> residual_matrix(static_cast<std::size_t>(solved_count * solved_count), 0.0);
    for (int residual = 0; residual < solved_count; ++residual) {
        for (int site = 0; site < solved_count; ++site) {
            residual_matrix[static_cast<std::size_t>(residual * solved_count + site)] =
                jac(problem.residual_row0 + residual, explicit_count + site);
        }
    }

    ImplicitSensitivityResult out;
    out.backend = problem.backend;
    out.helper_name = problem.helper_name;
    out.explicit_variable_count = explicit_count;
    out.solved_variable_count = solved_count;
    out.output_count = output_count;
    out.output_values.assign(problem.values.begin(), problem.values.begin() + output_count);
    out.solved_first_row_major.assign(static_cast<std::size_t>(explicit_count * solved_count), 0.0);
    out.output_first_row_major.assign(static_cast<std::size_t>(output_count * explicit_count), 0.0);

    for (int var = 0; var < explicit_count; ++var) {
        std::vector<double> rhs(static_cast<std::size_t>(solved_count), 0.0);
        for (int residual = 0; residual < solved_count; ++residual) {
            rhs[static_cast<std::size_t>(residual)] = -jac(problem.residual_row0 + residual, var);
        }
        const std::vector<double> solved_first = solve_linear_system(residual_matrix, rhs, solved_count);
        for (int site = 0; site < solved_count; ++site) {
            out.solved_first_row_major[static_cast<std::size_t>(var * solved_count + site)] =
                solved_first[static_cast<std::size_t>(site)];
        }
        for (int output = 0; output < output_count; ++output) {
            double value = jac(output, var);
            for (int site = 0; site < solved_count; ++site) {
                value += jac(output, explicit_count + site) * solved_first[static_cast<std::size_t>(site)];
            }
            out.output_first_row_major[static_cast<std::size_t>(output * explicit_count + var)] = value;
        }
    }

    if (include_second_order) {
        out.solved_second_tensor_row_major.assign(
            static_cast<std::size_t>(explicit_count * explicit_count * solved_count),
            0.0
        );
        out.output_second_tensor_row_major.assign(
            static_cast<std::size_t>(output_count * explicit_count * explicit_count),
            0.0
        );
        for (int first = 0; first < explicit_count; ++first) {
            for (int second = 0; second < explicit_count; ++second) {
                std::vector<double> rhs(static_cast<std::size_t>(solved_count), 0.0);
                for (int residual = 0; residual < solved_count; ++residual) {
                    double value = -hess(problem.residual_row0 + residual, first, second);
                    for (int site = 0; site < solved_count; ++site) {
                        const double dy_second = out.solved_first_row_major[
                            static_cast<std::size_t>(second * solved_count + site)
                        ];
                        const double dy_first = out.solved_first_row_major[
                            static_cast<std::size_t>(first * solved_count + site)
                        ];
                        value -= hess(problem.residual_row0 + residual, first, explicit_count + site) * dy_second;
                        value -= hess(problem.residual_row0 + residual, second, explicit_count + site) * dy_first;
                    }
                    for (int site_i = 0; site_i < solved_count; ++site_i) {
                        const double dy_first = out.solved_first_row_major[
                            static_cast<std::size_t>(first * solved_count + site_i)
                        ];
                        for (int site_j = 0; site_j < solved_count; ++site_j) {
                            value -= hess(
                                problem.residual_row0 + residual,
                                explicit_count + site_i,
                                explicit_count + site_j
                            ) * dy_first * out.solved_first_row_major[
                                static_cast<std::size_t>(second * solved_count + site_j)
                            ];
                        }
                    }
                    rhs[static_cast<std::size_t>(residual)] = value;
                }
                const std::vector<double> solved_second = solve_linear_system(residual_matrix, rhs, solved_count);
                for (int site = 0; site < solved_count; ++site) {
                    out.solved_second_tensor_row_major[
                        static_cast<std::size_t>(first * explicit_count * solved_count + second * solved_count + site)
                    ] = solved_second[static_cast<std::size_t>(site)];
                }

                for (int output = 0; output < output_count; ++output) {
                    double value = hess(output, first, second);
                    for (int site = 0; site < solved_count; ++site) {
                        const double dy_second = out.solved_first_row_major[
                            static_cast<std::size_t>(second * solved_count + site)
                        ];
                        const double dy_first = out.solved_first_row_major[
                            static_cast<std::size_t>(first * solved_count + site)
                        ];
                        value += hess(output, first, explicit_count + site) * dy_second;
                        value += hess(output, second, explicit_count + site) * dy_first;
                        value += jac(output, explicit_count + site) * solved_second[static_cast<std::size_t>(site)];
                    }
                    for (int site_i = 0; site_i < solved_count; ++site_i) {
                        const double dy_first = out.solved_first_row_major[
                            static_cast<std::size_t>(first * solved_count + site_i)
                        ];
                        for (int site_j = 0; site_j < solved_count; ++site_j) {
                            value += hess(output, explicit_count + site_i, explicit_count + site_j)
                                * dy_first
                                * out.solved_first_row_major[
                                    static_cast<std::size_t>(second * solved_count + site_j)
                                ];
                        }
                    }
                    out.output_second_tensor_row_major[
                        static_cast<std::size_t>(output * explicit_count * explicit_count + first * explicit_count + second)
                    ] = value;
                }
            }
        }
    }

    require_result_finite(out.output_values, "output values");
    require_result_finite(out.solved_first_row_major, "solved first sensitivities");
    require_result_finite(out.output_first_row_major, "output first sensitivities");
    require_result_finite(out.solved_second_tensor_row_major, "solved second sensitivities");
    require_result_finite(out.output_second_tensor_row_major, "output second sensitivities");
    return out;
}

}  // namespace epcsaft::native::implicit_sensitivity
