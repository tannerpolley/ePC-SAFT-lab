#include "eos/residual/internal.h"
#include <algorithm>
#include <cmath>
#include <string>
#include <vector>

#ifdef EPCSAFT_HAS_CPPAD
namespace eos_local_phase_detail {

template <typename Scalar>
Scalar local_phase_helmholtz_expression(
    double fixed_temperature,
    const vector<Scalar> &variables,
    int ncomp,
    bool include_temperature,
    const ProviderParameterAccessV1<double> &cppargs
) {
    Scalar total_amount = scalar_constant<Scalar>(0.0);
    for (int index = 0; index < ncomp; ++index) {
        total_amount += variables[static_cast<std::size_t>(index)];
    }
    const Scalar phase_volume = variables[static_cast<std::size_t>(ncomp)];
    const Scalar temperature = include_temperature
        ? variables[static_cast<std::size_t>(ncomp + 1)]
        : scalar_constant<Scalar>(fixed_temperature);
    const Scalar rho = total_amount / phase_volume;
    std::vector<Scalar> composition(static_cast<std::size_t>(ncomp));
    for (int index = 0; index < ncomp; ++index) {
        composition[static_cast<std::size_t>(index)] =
            variables[static_cast<std::size_t>(index)] / total_amount;
    }

    Scalar ideal = scalar_constant<Scalar>(0.0);
    for (int index = 0; index < ncomp; ++index) {
        const Scalar amount = variables[static_cast<std::size_t>(index)];
        ideal += amount * (CppAD::log(amount / phase_volume) - scalar_constant<Scalar>(1.0));
    }
    const auto contributions = ares_detail::ares_contributions_scalar_cpp(temperature, rho, composition, cppargs);
    const Scalar residual = total_amount
        * (contributions.hc + contributions.disp + contributions.assoc + contributions.ion + contributions.born);
    return ideal + residual;
}

}  // namespace eos_local_phase_detail
#endif

EosLocalPhaseDerivativeBundle eos_local_phase_helmholtz_derivatives_cpp(
    double t,
    const vector<double> &amounts,
    double volume,
    const ProviderParameterAccessV1<double> &cppargs,
    bool include_temperature
) {
#ifdef EPCSAFT_HAS_CPPAD
    using CppADScalar = CppAD::AD<double>;
    if (!std::isfinite(t) || t <= 0.0) {
        throw ValueError("EOS local phase Helmholtz derivatives require a positive finite temperature.");
    }
    if (!std::isfinite(volume) || volume <= 0.0) {
        throw ValueError("EOS local phase Helmholtz derivatives require a positive finite volume.");
    }
    if (!cppargs.assoc_num.empty()) {
        for (int sites : cppargs.assoc_num) {
            if (sites > 0) {
                throw ValueError("EOS local phase Helmholtz Hessian does not support active association implicit variables.");
            }
        }
    }
    const int ncomp = static_cast<int>(amounts.size());
    if (ncomp <= 0) {
        throw ValueError("EOS local phase Helmholtz derivatives require at least one species amount.");
    }
    for (double amount : amounts) {
        if (!std::isfinite(amount) || amount <= 0.0) {
            throw ValueError("EOS local phase Helmholtz derivatives require positive finite species amounts.");
        }
    }

    const int nvars = ncomp + 1 + (include_temperature ? 1 : 0);
    std::vector<CppADScalar> variables(static_cast<std::size_t>(nvars));
    for (int index = 0; index < ncomp; ++index) {
        variables[static_cast<std::size_t>(index)] = amounts[static_cast<std::size_t>(index)];
    }
    variables[static_cast<std::size_t>(ncomp)] = volume;
    if (include_temperature) {
        variables[static_cast<std::size_t>(ncomp + 1)] = t;
    }
    CppAD::Independent(variables);

    std::vector<CppADScalar> outputs(1);
    outputs[0] = eos_local_phase_detail::local_phase_helmholtz_expression(
        t,
        variables,
        ncomp,
        include_temperature,
        cppargs
    );

    CppAD::ADFun<double> function(variables, outputs);
    std::vector<double> point(amounts.begin(), amounts.end());
    point.push_back(volume);
    if (include_temperature) {
        point.push_back(t);
    }

    EosLocalPhaseDerivativeBundle bundle;
    bundle.backend = "cppad";
    bundle.variable_count = nvars;
    bundle.includes_temperature = include_temperature;
    bundle.helmholtz = function.Forward(0, point).at(0);
    bundle.gradient = function.Jacobian(point);
    bundle.hessian_row_major = function.Hessian(point, 0);
    bundle.third_derivative_tensor_row_major =
        ares_detail::scalar_function_third_derivative_tensor_cppad(function, point);
    return bundle;
#else
    (void)t;
    (void)amounts;
    (void)volume;
    (void)cppargs;
    (void)include_temperature;
    throw ValueError("EOS local phase Helmholtz derivatives require CppAD support.");
#endif
}
