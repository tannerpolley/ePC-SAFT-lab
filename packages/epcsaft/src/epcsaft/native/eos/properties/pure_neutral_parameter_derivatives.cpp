#include "eos/core_internal.h"

using thermo_detail::kDispersionA0;
using thermo_detail::kDispersionA1;
using thermo_detail::kDispersionA2;
using thermo_detail::kDispersionB0;
using thermo_detail::kDispersionB1;
using thermo_detail::kDispersionB2;

namespace pure_neutral_parameter_detail {

constexpr int kThetaSize = 3;

template <typename Scalar>
struct PureNeutralStateScalar {
    Scalar den = scalar_constant<Scalar>(0.0);
    Scalar d = scalar_constant<Scalar>(0.0);
    Scalar zeta0 = scalar_constant<Scalar>(0.0);
    Scalar zeta1 = scalar_constant<Scalar>(0.0);
    Scalar zeta2 = scalar_constant<Scalar>(0.0);
    Scalar zeta3 = scalar_constant<Scalar>(0.0);
    Scalar eta = scalar_constant<Scalar>(0.0);
    Scalar pair_diameter = scalar_constant<Scalar>(0.0);
    Scalar ghs = scalar_constant<Scalar>(0.0);
    Scalar ares_hs = scalar_constant<Scalar>(0.0);
    Scalar ares_hc = scalar_constant<Scalar>(0.0);
    Scalar I1 = scalar_constant<Scalar>(0.0);
    Scalar I2 = scalar_constant<Scalar>(0.0);
    Scalar dEtaI1_deta = scalar_constant<Scalar>(0.0);
    Scalar dEtaI2_deta = scalar_constant<Scalar>(0.0);
    Scalar C1 = scalar_constant<Scalar>(0.0);
    Scalar C2 = scalar_constant<Scalar>(0.0);
    Scalar m2es3 = scalar_constant<Scalar>(0.0);
    Scalar m2e2s3 = scalar_constant<Scalar>(0.0);
    Scalar ares_disp = scalar_constant<Scalar>(0.0);
    Scalar ares_total = scalar_constant<Scalar>(0.0);
    Scalar zraw_total = scalar_constant<Scalar>(0.0);
    Scalar Z = scalar_constant<Scalar>(0.0);
    Scalar pressure = scalar_constant<Scalar>(0.0);
    Scalar mures = scalar_constant<Scalar>(0.0);
    Scalar lnfug = scalar_constant<Scalar>(0.0);
};

void validate_pure_neutral_parameter_args(const add_args &base_args) {
    if (base_args.m.size() != 1 || base_args.s.size() != 1 || base_args.e.size() != 1) {
        throw ValueError("unsupported: pure-neutral m/sigma/epsilon derivatives require exactly one component.");
    }
    if (!base_args.z.empty() && (base_args.z.size() != 1 || std::abs(base_args.z[0]) > 1.0e-12)) {
        throw ValueError("unsupported: pure-neutral m/sigma/epsilon derivatives support only neutral components.");
    }
    if (!base_args.assoc_num.empty() || !base_args.assoc_matrix.empty() || !base_args.k_hb.empty() || !base_args.e_assoc.empty() || !base_args.vol_a.empty()) {
        throw ValueError("unsupported: pure-neutral m/sigma/epsilon derivatives support only nonassociating components.");
    }
}

template <typename Scalar>
PureNeutralStateScalar<Scalar> pure_neutral_state_scalar_cpp(
    double t,
    const Scalar &rho,
    const Scalar &m,
    const Scalar &s,
    const Scalar &e
) {
    PureNeutralStateScalar<Scalar> state;
    const Scalar s2 = s * s;
    const Scalar s3 = s2 * s;
    state.den = rho * (N_AV / 1.0e30);
    state.d = s * (1.0 - 0.12 * scalar_exp(-3.0 * e / t));
    const Scalar d2 = state.d * state.d;
    const Scalar d3 = d2 * state.d;

    const Scalar prefactor = PI / 6.0 * state.den * m;
    state.zeta0 = prefactor;
    state.zeta1 = prefactor * state.d;
    state.zeta2 = prefactor * d2;
    state.zeta3 = prefactor * d3;
    state.eta = state.zeta3;
    state.pair_diameter = state.d / 2.0;
    const Scalar pair_diameter2 = state.pair_diameter * state.pair_diameter;
    const Scalar zeta2_sq = state.zeta2 * state.zeta2;
    const Scalar zeta2_cu = zeta2_sq * state.zeta2;
    const Scalar zeta3_sq = state.zeta3 * state.zeta3;
    state.ghs = 1.0 / (1.0 - state.zeta3)
        + state.pair_diameter * 3.0 * state.zeta2 / scalar_pow(1.0 - state.zeta3, 2.0)
        + pair_diameter2 * 2.0 * zeta2_sq / scalar_pow(1.0 - state.zeta3, 3.0);

    state.ares_hs = 1.0 / state.zeta0 * (
        3.0 * state.zeta1 * state.zeta2 / (1.0 - state.zeta3)
        + zeta2_cu / (state.zeta3 * scalar_pow(1.0 - state.zeta3, 2.0))
        + (zeta2_cu / zeta3_sq - state.zeta0) * scalar_log(1.0 - state.zeta3)
    );
    state.ares_hc = m * state.ares_hs - (m - 1.0) * scalar_log(state.ghs);

    const Scalar c1 = (m - 1.0) / m;
    const Scalar c2 = (m - 2.0) / m;
    for (size_t i = 0; i < kDispersionA0.size(); ++i) {
        Scalar a_i = kDispersionA0[i] + c1 * kDispersionA1[i] + c1 * c2 * kDispersionA2[i];
        Scalar b_i = kDispersionB0[i] + c1 * kDispersionB1[i] + c1 * c2 * kDispersionB2[i];
        state.I1 += a_i * scalar_pow(state.eta, static_cast<int>(i));
        state.I2 += b_i * scalar_pow(state.eta, static_cast<int>(i));
        state.dEtaI1_deta += a_i * static_cast<double>(i + 1) * scalar_pow(state.eta, static_cast<int>(i));
        state.dEtaI2_deta += b_i * static_cast<double>(i + 1) * scalar_pow(state.eta, static_cast<int>(i));
    }

    state.C1 = 1.0 / (
        1.0
        + m * (8.0 * state.eta - 2.0 * state.eta * state.eta) / scalar_pow(1.0 - state.eta, 4.0)
        + (1.0 - m) * (
            20.0 * state.eta
            - 27.0 * state.eta * state.eta
            + 12.0 * scalar_pow(state.eta, 3.0)
            - 2.0 * scalar_pow(state.eta, 4.0)
        ) / scalar_pow((1.0 - state.eta) * (2.0 - state.eta), 2.0)
    );
    state.C2 = -state.C1 * state.C1 * (
        m * (-4.0 * state.eta * state.eta + 20.0 * state.eta + 8.0) / scalar_pow(1.0 - state.eta, 5.0)
        + (1.0 - m) * (
            2.0 * scalar_pow(state.eta, 3.0)
            + 12.0 * state.eta * state.eta
            - 48.0 * state.eta
            + 40.0
        ) / scalar_pow((1.0 - state.eta) * (2.0 - state.eta), 3.0)
    );

    const Scalar e_over_t = e / t;
    const Scalar e_over_t2 = e_over_t * e_over_t;
    state.m2es3 = m * m * e_over_t * s3;
    state.m2e2s3 = m * m * e_over_t2 * s3;
    state.ares_disp = -2.0 * PI * state.den * state.I1 * state.m2es3
        - PI * state.den * m * state.C1 * state.I2 * state.m2e2s3;
    state.ares_total = state.ares_hc + state.ares_disp;

    const Scalar dghs_drho = state.zeta3 / scalar_pow(1.0 - state.zeta3, 2.0)
        + state.pair_diameter * (
            3.0 * state.zeta2 / scalar_pow(1.0 - state.zeta3, 2.0)
            + 6.0 * state.zeta2 * state.zeta3 / scalar_pow(1.0 - state.zeta3, 3.0)
        )
        + pair_diameter2 * (
            4.0 * zeta2_sq / scalar_pow(1.0 - state.zeta3, 3.0)
            + 6.0 * zeta2_sq * state.zeta3 / scalar_pow(1.0 - state.zeta3, 4.0)
        );
    const Scalar dadrho_hs = state.zeta3 / (1.0 - state.zeta3)
        + 3.0 * state.zeta1 * state.zeta2 / state.zeta0 / scalar_pow(1.0 - state.zeta3, 2.0)
        + (3.0 * zeta2_cu - state.zeta3 * zeta2_cu)
            / state.zeta0 / scalar_pow(1.0 - state.zeta3, 3.0);
    const Scalar zraw_hc = m * dadrho_hs - (m - 1.0) * dghs_drho / state.ghs;
    const Scalar zraw_disp = -2.0 * PI * state.den * state.dEtaI1_deta * state.m2es3
        - PI * state.den * m * (state.C1 * state.dEtaI2_deta + state.C2 * state.eta * state.I2) * state.m2e2s3;
    state.zraw_total = zraw_hc + zraw_disp;
    state.Z = 1.0 + state.zraw_total;
    if (!(scalar_value(state.Z) > 0.0)) {
        throw ValueError("Encountered non-positive compressibility factor during pure-neutral parameter derivative evaluation.");
    }
    state.pressure = state.Z * kb * t * state.den * 1.0e30;
    state.mures = state.ares_total + state.zraw_total;
    state.lnfug = state.ares_total + state.zraw_total - scalar_log(state.Z);
    return state;
}

}  // namespace pure_neutral_parameter_detail

using pure_neutral_parameter_detail::kThetaSize;
using pure_neutral_parameter_detail::pure_neutral_state_scalar_cpp;
using pure_neutral_parameter_detail::validate_pure_neutral_parameter_args;

epcsaft::native::cppad_support::CppADDerivativeResult cppad_pure_neutral_parameter_derivatives_cpp(
    double t,
    double rho,
    const add_args &base_args
) {
#ifdef EPCSAFT_HAS_CPPAD
    validate_pure_neutral_parameter_args(base_args);
    if (!(t > 0.0) || !(rho > 0.0)) {
        throw ValueError("Native pure-neutral parameter derivative evaluation requires positive T and rho.");
    }

    using CppADScalar = CppAD::AD<double>;
    std::vector<CppADScalar> ax(kThetaSize);
    ax[0] = base_args.m[0];
    ax[1] = base_args.s[0];
    ax[2] = base_args.e[0];
    CppAD::Independent(ax);

    auto state = pure_neutral_state_scalar_cpp<CppADScalar>(
        t,
        CppADScalar(rho),
        ax[0],
        ax[1],
        ax[2]
    );
    std::vector<CppADScalar> ay(3);
    ay[0] = state.pressure;
    ay[1] = state.mures;
    ay[2] = state.lnfug;

    CppAD::ADFun<double> function(ax, ay);
    std::vector<double> point = {base_args.m[0], base_args.s[0], base_args.e[0]};
    auto value = function.Forward(0, point);
    auto jacobian = function.Jacobian(point);

    epcsaft::native::cppad_support::CppADDerivativeResult result;
    result.supported = true;
    result.backend = "cppad";
    result.message = "CppAD pure-neutral m/sigma/epsilon property derivatives available";
    result.value = std::move(value);
    result.jacobian_row_major = std::move(jacobian);
    result.outputs = {"pressure", "mu_res", "ln_fugacity"};
    result.variables = {"m", "sigma", "epsilon"};
    result.rows = 3;
    result.cols = kThetaSize;
    return result;
#else
    (void)t;
    (void)rho;
    (void)base_args;
    throw ValueError("unsupported: CppAD support is not enabled in this native build.");
#endif
}
