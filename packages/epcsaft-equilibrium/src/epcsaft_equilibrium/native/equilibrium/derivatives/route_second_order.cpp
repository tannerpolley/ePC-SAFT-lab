#include "equilibrium/derivatives/route_second_order.h"

#include <exception>

#include "model/native_types.h"

#include <cstddef>

namespace epcsaft::native::equilibrium_nlp {

void require_square_block(
    const std::vector<double>& values,
    int variable_count,
    const std::string& label
) {
    const std::size_t n = static_cast<std::size_t>(variable_count);
    if (values.size() == n * n) {
        return;
    }
    throw ::ValueError(label + " size does not match the square variable block.");
}

void require_third_derivative_tensor(
    const std::vector<double>& values,
    int variable_count,
    const std::string& label
) {
    const std::size_t n = static_cast<std::size_t>(variable_count);
    if (values.size() == n * n * n) {
        return;
    }
    throw ::ValueError(label + " size does not match the third-derivative tensor.");
}

void symmetrize_square_block(std::vector<double>& values, int variable_count) {
    const std::size_t n = static_cast<std::size_t>(variable_count);
    require_square_block(values, variable_count, "symmetric square block");
    for (std::size_t row = 0; row < n; ++row) {
        for (std::size_t col = 0; col < row; ++col) {
            const double value = 0.5 * (values[row * n + col] + values[col * n + row]);
            values[row * n + col] = value;
            values[col * n + row] = value;
        }
    }
}

std::vector<int> fixed_temperature_global_indices(int phase, int local_variable_count) {
    std::vector<int> indices;
    indices.reserve(static_cast<std::size_t>(local_variable_count));
    const int offset = phase * local_variable_count;
    for (int local = 0; local < local_variable_count; ++local) {
        indices.push_back(offset + local);
    }
    return indices;
}

std::vector<int> fixed_pressure_global_indices(
    int phase,
    int local_variable_count,
    int temperature_col
) {
    std::vector<int> indices = fixed_temperature_global_indices(phase, local_variable_count);
    indices.push_back(temperature_col);
    return indices;
}

void add_local_hessian_to_dense(
    std::vector<double>& dense,
    int variable_count,
    const std::vector<int>& global_indices,
    const std::vector<double>& local_hessian,
    double scale,
    const std::string& label
) {
    const int local_variable_count = static_cast<int>(global_indices.size());
    require_square_block(local_hessian, local_variable_count, label);
    require_square_block(dense, variable_count, "dense route Hessian");
    const std::size_t n = static_cast<std::size_t>(variable_count);
    for (int local_row = 0; local_row < local_variable_count; ++local_row) {
        const int global_row = global_indices[static_cast<std::size_t>(local_row)];
        for (int local_col = 0; local_col < local_variable_count; ++local_col) {
            const int global_col = global_indices[static_cast<std::size_t>(local_col)];
            dense[static_cast<std::size_t>(global_row) * n + static_cast<std::size_t>(global_col)] +=
                scale * local_hessian[
                    static_cast<std::size_t>(local_row * local_variable_count + local_col)
                ];
        }
    }
}

void add_local_hessian_to_constraint_tensor(
    std::vector<double>& tensor,
    int constraint_row,
    int variable_count,
    const std::vector<int>& global_indices,
    const std::vector<double>& local_hessian,
    double scale,
    const std::string& label
) {
    const int local_variable_count = static_cast<int>(global_indices.size());
    require_square_block(local_hessian, local_variable_count, label);
    const std::size_t n = static_cast<std::size_t>(variable_count);
    const std::size_t row_offset = static_cast<std::size_t>(constraint_row) * n * n;
    if (tensor.size() < row_offset + n * n) {
        throw ::ValueError(label + " target tensor is smaller than the requested constraint row.");
    }
    for (int local_row = 0; local_row < local_variable_count; ++local_row) {
        const int global_row = global_indices[static_cast<std::size_t>(local_row)];
        for (int local_col = 0; local_col < local_variable_count; ++local_col) {
            const int global_col = global_indices[static_cast<std::size_t>(local_col)];
            tensor[row_offset + static_cast<std::size_t>(global_row) * n + static_cast<std::size_t>(global_col)] +=
                scale * local_hessian[
                    static_cast<std::size_t>(local_row * local_variable_count + local_col)
                ];
        }
    }
}

std::vector<double> third_derivative_slice(
    const std::vector<double>& tensor,
    int component,
    int variable_count,
    const std::string& label
) {
    require_third_derivative_tensor(tensor, variable_count, label);
    const std::size_t n = static_cast<std::size_t>(variable_count);
    const std::size_t offset = static_cast<std::size_t>(component) * n * n;
    return std::vector<double>(
        tensor.begin() + static_cast<std::ptrdiff_t>(offset),
        tensor.begin() + static_cast<std::ptrdiff_t>(offset + n * n)
    );
}

}  // namespace epcsaft::native::equilibrium_nlp
