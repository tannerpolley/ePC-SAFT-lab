#include "eos/properties/residual_helmholtz_internal.h"
#include "eos/properties/residual_association_sensitivities.h"
#include "eos/properties/residual_backend_helpers.h"
#include <algorithm>
#include <cmath>
#include <string>
#include <vector>

void eos_phase_objective_derivatives_cpp(
    double t,
    double target_pressure,
    const vector<double> &amounts,
    double volume,
    const add_args &cppargs,
    double *objective,
    vector<double> *gradient,
    vector<double> *hessian_row_major,
    vector<double> *third_derivative_tensor_row_major
) {
#ifdef EPCSAFT_HAS_CPPAD
    using CppADScalar = CppAD::AD<double>;
    if (!objective || !gradient || !hessian_row_major) {
        throw ValueError("EOS phase objective derivative output buffers must be valid.");
    }
    if (!cppargs.assoc_num.empty()) {
        for (int sites : cppargs.assoc_num) {
            if (sites > 0) {
                throw ValueError("unsupported: EOS phase objective Hessian requires association implicit variables.");
            }
        }
    }
    if (!cppargs.z.empty() && cppargs.born_model > 1) {
        throw ValueError("unsupported: EOS phase objective Hessian supports direct Born model=1 formulas only.");
    }
    const int ncomp = static_cast<int>(amounts.size());
    const int nvars = ncomp + 1;
    std::vector<CppADScalar> variables(static_cast<std::size_t>(nvars));
    for (int index = 0; index < ncomp; ++index) {
        variables[static_cast<std::size_t>(index)] = amounts[static_cast<std::size_t>(index)];
    }
    variables[static_cast<std::size_t>(ncomp)] = volume;
    CppAD::Independent(variables);

    CppADScalar total_amount = scalar_constant<CppADScalar>(0.0);
    for (int index = 0; index < ncomp; ++index) {
        total_amount += variables[static_cast<std::size_t>(index)];
    }
    const CppADScalar phase_volume = variables[static_cast<std::size_t>(ncomp)];
    const CppADScalar rho = total_amount / phase_volume;
    std::vector<CppADScalar> composition(static_cast<std::size_t>(ncomp));
    for (int index = 0; index < ncomp; ++index) {
        composition[static_cast<std::size_t>(index)] = variables[static_cast<std::size_t>(index)] / total_amount;
    }

    CppADScalar ideal = scalar_constant<CppADScalar>(0.0);
    for (int index = 0; index < ncomp; ++index) {
        const CppADScalar amount = variables[static_cast<std::size_t>(index)];
        ideal += amount * (CppAD::log(amount / phase_volume) - scalar_constant<CppADScalar>(1.0));
    }
    const auto contributions = ares_detail::ares_contributions_scalar_cpp(t, rho, composition, cppargs);
    const CppADScalar residual = total_amount
        * (contributions.hc + contributions.disp + contributions.assoc + contributions.ion + contributions.born);
    const CppADScalar pressure_work = target_pressure * phase_volume / (kb * N_AV * t);
    std::vector<CppADScalar> outputs(1);
    outputs[0] = ideal + residual + pressure_work;

    CppAD::ADFun<double> function(variables, outputs);
    std::vector<double> point(amounts.begin(), amounts.end());
    point.push_back(volume);
    auto value = function.Forward(0, point);
    auto jacobian = function.Jacobian(point);
    auto hessian = function.Hessian(point, 0);
    if (third_derivative_tensor_row_major) {
        *third_derivative_tensor_row_major =
            ares_detail::scalar_function_third_derivative_tensor_cppad(function, point);
    }

    *objective = value.at(0);
    *gradient = std::move(jacobian);
    *hessian_row_major = std::move(hessian);
#else
    (void)t;
    (void)target_pressure;
    (void)amounts;
    (void)volume;
    (void)cppargs;
    (void)objective;
    (void)gradient;
    (void)hessian_row_major;
    (void)third_derivative_tensor_row_major;
    throw ValueError("EOS phase objective Hessian requires CppAD support.");
#endif
}

void eos_phase_temperature_variable_derivatives_cpp(
    double t,
    double target_pressure,
    const vector<double> &amounts,
    double volume,
    const add_args &cppargs,
    double *objective,
    vector<double> *gradient,
    vector<double> *hessian_row_major,
    vector<double> *third_derivative_tensor_row_major
) {
#ifdef EPCSAFT_HAS_CPPAD
    using CppADScalar = CppAD::AD<double>;
    if (!objective || !gradient || !hessian_row_major) {
        throw ValueError("EOS phase variable-temperature derivative output buffers must be valid.");
    }
    if (!cppargs.assoc_num.empty()) {
        for (int sites : cppargs.assoc_num) {
            if (sites > 0) {
                throw ValueError("unsupported: EOS phase temperature route Hessian requires association implicit variables.");
            }
        }
    }
    if (!cppargs.z.empty() && cppargs.born_model > 1) {
        throw ValueError("unsupported: EOS phase temperature route Hessian supports direct Born model=1 formulas only.");
    }
    const int ncomp = static_cast<int>(amounts.size());
    const int nvars = ncomp + 2;
    std::vector<CppADScalar> variables(static_cast<std::size_t>(nvars));
    for (int index = 0; index < ncomp; ++index) {
        variables[static_cast<std::size_t>(index)] = amounts[static_cast<std::size_t>(index)];
    }
    variables[static_cast<std::size_t>(ncomp)] = volume;
    variables[static_cast<std::size_t>(ncomp + 1)] = t;
    CppAD::Independent(variables);

    CppADScalar total_amount = scalar_constant<CppADScalar>(0.0);
    for (int index = 0; index < ncomp; ++index) {
        total_amount += variables[static_cast<std::size_t>(index)];
    }
    const CppADScalar phase_volume = variables[static_cast<std::size_t>(ncomp)];
    const CppADScalar temperature = variables[static_cast<std::size_t>(ncomp + 1)];
    const CppADScalar rho = total_amount / phase_volume;
    std::vector<CppADScalar> composition(static_cast<std::size_t>(ncomp));
    for (int index = 0; index < ncomp; ++index) {
        composition[static_cast<std::size_t>(index)] = variables[static_cast<std::size_t>(index)] / total_amount;
    }

    CppADScalar ideal = scalar_constant<CppADScalar>(0.0);
    for (int index = 0; index < ncomp; ++index) {
        const CppADScalar amount = variables[static_cast<std::size_t>(index)];
        ideal += amount * (CppAD::log(amount / phase_volume) - scalar_constant<CppADScalar>(1.0));
    }
    const auto contributions = ares_detail::ares_contributions_scalar_cpp(temperature, rho, composition, cppargs);
    const CppADScalar residual = total_amount
        * (contributions.hc + contributions.disp + contributions.assoc + contributions.ion + contributions.born);
    const CppADScalar pressure_work = target_pressure * phase_volume / (kb * N_AV * temperature);
    std::vector<CppADScalar> outputs(1);
    outputs[0] = ideal + residual + pressure_work;

    CppAD::ADFun<double> function(variables, outputs);
    std::vector<double> point(amounts.begin(), amounts.end());
    point.push_back(volume);
    point.push_back(t);
    auto value = function.Forward(0, point);
    auto jacobian = function.Jacobian(point);
    auto hessian = function.Hessian(point, 0);
    if (third_derivative_tensor_row_major) {
        *third_derivative_tensor_row_major =
            ares_detail::scalar_function_third_derivative_tensor_cppad(function, point);
    }

    *objective = value.at(0);
    *gradient = std::move(jacobian);
    *hessian_row_major = std::move(hessian);
#else
    (void)t;
    (void)target_pressure;
    (void)amounts;
    (void)volume;
    (void)cppargs;
    (void)objective;
    (void)gradient;
    (void)hessian_row_major;
    (void)third_derivative_tensor_row_major;
    throw ValueError("EOS phase variable-temperature Hessian requires CppAD support.");
#endif
}
