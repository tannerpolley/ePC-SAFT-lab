#pragma once
#include "eos/properties/residual_scalar_state.h"

namespace ares_detail {
inline std::vector<double> vector_output_component_hessian_cppad(
    CppAD::ADFun<double>& function,
    const std::vector<double>& point,
    std::size_t output_index
) {
    return function.Hessian(point, output_index);
}

inline std::vector<double> scalar_function_third_derivative_tensor_cppad(
    const CppAD::ADFun<double>& function,
    const std::vector<double>& point
) {
    using ADScalar = CppAD::AD<double>;
    const std::size_t nvar = point.size();
    std::vector<ADScalar> ax(nvar);
    for (std::size_t i = 0; i < nvar; ++i) {
        ax[i] = point[i];
    }
    CppAD::Independent(ax);
    CppAD::ADFun<ADScalar, double> af(function.base2ad());
    std::vector<ADScalar> ay = af.Forward(0, ax);
    if (ay.size() != 1) {
        throw ValueError("Third-derivative tensor helper requires a scalar recorded function.");
    }
    std::vector<ADScalar> aw(1);
    aw[0] = ADScalar(1.0);
    std::vector<ADScalar> agrad = af.Reverse(1, aw);
    CppAD::ADFun<double> grad_fun(ax, agrad);
    std::vector<double> tensor(nvar * nvar * nvar, 0.0);
    for (std::size_t component = 0; component < nvar; ++component) {
        const std::vector<double> hessian = grad_fun.Hessian(point, component);
        for (std::size_t row = 0; row < nvar; ++row) {
            for (std::size_t col = 0; col < nvar; ++col) {
                tensor[component * nvar * nvar + row * nvar + col] =
                    hessian[row * nvar + col];
            }
        }
    }
    return tensor;
}

}  // namespace ares_detail
