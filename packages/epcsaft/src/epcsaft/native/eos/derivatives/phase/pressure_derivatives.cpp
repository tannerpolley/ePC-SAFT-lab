#include "eos/residual/internal.h"
#include "eos/residual/implicit_association/sensitivities.h"
#include "eos/derivatives/backend_labels.h"
#include <algorithm>
#include <cmath>
#include <string>
#include <vector>

// Equilibrium pressure-consistency constraints consume this as the pressure
// Jacobian over phase amounts plus volume.
EosPhasePressureDerivativeResult eos_phase_pressure_derivatives_cpp(
    double t,
    const vector<double> &amounts,
    double volume,
    const ProviderParameterAccessV1<double> &cppargs
) {
    EosPhasePressureDerivativeResult out;
    using CppADScalar = CppAD::AD<double>;
    if (!(std::isfinite(t) && t > 0.0) || !(std::isfinite(volume) && volume > 0.0)) {
        out.message = "EOS phase pressure derivatives require positive finite temperature and volume.";
        return out;
    }
    const int ncomp = static_cast<int>(amounts.size());
    if (ncomp <= 0) {
        out.message = "EOS phase pressure derivatives require at least one species amount.";
        return out;
    }
    double total_amount = 0.0;
    for (double amount : amounts) {
        if (!(std::isfinite(amount) && amount > 0.0)) {
            out.message = "EOS phase pressure derivatives require positive finite species amounts.";
            return out;
        }
        total_amount += amount;
    }
    if (!(std::isfinite(total_amount) && total_amount > 0.0)) {
        out.message = "EOS phase pressure derivatives require a positive finite total amount.";
        return out;
    }

    const double rho = total_amount / volume;
    vector<double> x(static_cast<size_t>(ncomp), 0.0);
    for (int i = 0; i < ncomp; ++i) {
        x[static_cast<size_t>(i)] = amounts[static_cast<size_t>(i)] / total_amount;
    }

    const int var_count = ncomp + 1;
    std::vector<CppADScalar> avars(static_cast<size_t>(var_count));
    avars[0] = rho;
    for (int i = 0; i < ncomp; ++i) {
        avars[static_cast<size_t>(1 + i)] = x[static_cast<size_t>(i)];
    }
    CppAD::Independent(avars);

    std::vector<CppADScalar> ax(static_cast<size_t>(ncomp));
    for (int i = 0; i < ncomp; ++i) {
        ax[static_cast<size_t>(i)] = avars[static_cast<size_t>(1 + i)];
    }
    const bool active_association = derivative_backend_detail::has_association_sites(cppargs);
    const AssociationDisabledParameterAccessV1 recording_args(cppargs);
    auto contributions = ares_detail::ares_contributions_scalar_cpp(t, avars[0], ax, recording_args);
    std::vector<CppADScalar> ay(1);
    ay[0] = contributions.hc + contributions.disp + contributions.assoc + contributions.ion + contributions.born;

    CppAD::ADFun<double> function(avars, ay);
    std::vector<double> point(static_cast<size_t>(var_count), 0.0);
    point[0] = rho;
    for (int i = 0; i < ncomp; ++i) {
        point[static_cast<size_t>(1 + i)] = x[static_cast<size_t>(i)];
    }
    auto jacobian = function.Jacobian(point);
    auto hessian = function.Hessian(point, 0);
    const auto h = [&](int row, int col) {
        return hessian[static_cast<size_t>(row * var_count + col)];
    };

    ares_detail::AssociationPhaseStateResponse association_response;
    if (active_association) {
        association_response = residual_association_detail::association_phase_state_response_cppad_cpp(t, rho, x, cppargs);
        if (!association_response.active) {
            out.message =
                "Association pressure derivative expected active association but received no active site fractions.";
            return out;
        }
    }

    const double da_drho = jacobian[0];
    const double association_zraw = active_association ? association_response.zraw : 0.0;
    const double z_raw = rho * da_drho + association_zraw;
    const double z = 1.0 + z_raw;
    if (!(std::isfinite(z) && z > 0.0)) {
        out.message = "EOS phase pressure derivatives produced a non-positive compressibility factor.";
        return out;
    }

    const auto base_dzraw_dvar = [&](int var_index) {
        double value = rho * h(0, var_index);
        if (var_index == 0) {
            value += da_drho;
        }
        return value;
    };
    const auto dzraw_dvar = [&](int var_index) {
        double value = base_dzraw_dvar(var_index);
        if (active_association) {
            value += association_response.dzraw_dvar[static_cast<size_t>(var_index)];
        }
        return value;
    };
    const auto pressure_dvar = [&](int var_index) {
        const double dzraw = dzraw_dvar(var_index);
        double value = rho * dzraw;
        if (var_index == 0) {
            value += z;
        }
        return kb * t * N_AV * value;
    };

    const double dp_drho = pressure_dvar(0);
    if (!(std::isfinite(dp_drho) && std::abs(dp_drho) > 1.0e-30)) {
        out.message = "EOS phase pressure derivatives produced a singular pressure-density derivative.";
        return out;
    }

    vector<double> dpdx_fixed(static_cast<size_t>(ncomp), 0.0);
    double sum_x_dpdx = 0.0;
    for (int i = 0; i < ncomp; ++i) {
        dpdx_fixed[static_cast<size_t>(i)] = pressure_dvar(1 + i);
        if (!std::isfinite(dpdx_fixed[static_cast<size_t>(i)])) {
            out.message = "EOS phase pressure composition derivative was not finite.";
            return out;
        }
        sum_x_dpdx += x[static_cast<size_t>(i)] * dpdx_fixed[static_cast<size_t>(i)];
    }

    out.pressure_jacobian_row_major.assign(static_cast<size_t>(ncomp + 1), 0.0);
    for (int species = 0; species < ncomp; ++species) {
        out.pressure_jacobian_row_major[static_cast<size_t>(species)] =
            dp_drho / volume
            + (dpdx_fixed[static_cast<size_t>(species)] - sum_x_dpdx) / total_amount;
    }
    out.pressure_jacobian_row_major[static_cast<size_t>(ncomp)] = -dp_drho * rho / volume;
    for (double value : out.pressure_jacobian_row_major) {
        if (!std::isfinite(value)) {
            out.message = "EOS phase pressure amount-volume derivative was not finite.";
            return out;
        }
    }
    out.supported = true;
    out.backend = active_association ? "cppad_implicit" : "cppad";
    out.message = active_association
        ? "CppAD pressure derivatives with implicit association sensitivities are available."
        : "CppAD pressure derivatives are available.";
    out.pressure_density_derivative = dp_drho;
    return out;
}
