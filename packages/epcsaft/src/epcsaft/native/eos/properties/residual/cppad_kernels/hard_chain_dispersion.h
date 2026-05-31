#pragma once
#include "eos/properties/residual/cppad_kernels/state.h"

namespace ares_detail {
template <typename Scalar>
static Scalar hs_contact_value_scalar_cpp(const Scalar &pair_diameter, const Scalar &zeta2, const Scalar &zeta3) {
    const Scalar one = scalar_constant<Scalar>(1.0);
    return one / (one - zeta3)
        + pair_diameter * 3.0 * zeta2 / scalar_pow(one - zeta3, 2)
        + scalar_pow(pair_diameter, 2.0) * 2.0 * zeta2 * zeta2 / scalar_pow(one - zeta3, 3);
}

template <typename Scalar>
static HardChainStateScalar<Scalar> hard_chain_state_scalar_cpp(const MixtureStateScalar<Scalar> &thermo, const vector<Scalar> &x, const add_args &cppargs) {
    HardChainStateScalar<Scalar> state;
    int ncomp = static_cast<int>(x.size());
    state.zeta.assign(4, scalar_constant<Scalar>(0.0));
    state.ghs.assign(ncomp * ncomp, scalar_constant<Scalar>(0.0));
    for (int k = 0; k < 4; ++k) {
        Scalar summ = scalar_constant<Scalar>(0.0);
        for (int j = 0; j < ncomp; ++j) {
            summ += x[j] * cppargs.m[j] * scalar_pow(thermo.d[j], k);
        }
        state.zeta[k] = PI / 6.0 * thermo.den * summ;
    }
    state.eta = state.zeta[3];

    int idx = -1;
    for (int i = 0; i < ncomp; ++i) {
        for (int j = 0; j < ncomp; ++j) {
            ++idx;
            Scalar pair_diameter = thermo.d[i] * thermo.d[j] / (thermo.d[i] + thermo.d[j]);
            state.ghs[idx] = hs_contact_value_scalar_cpp(pair_diameter, state.zeta[2], state.zeta[3]);
        }
    }
    return state;
}

template <typename Scalar>
static DispersionPolynomialStateScalar<Scalar> dispersion_polynomials_scalar_cpp(const Scalar &m_avg, const Scalar &eta) {
    DispersionPolynomialStateScalar<Scalar> state;
    Scalar c1 = (m_avg - 1.0) / m_avg;
    Scalar c2 = (m_avg - 2.0) / m_avg;
    for (size_t i = 0; i < state.a.size(); ++i) {
        state.a[i] = thermo_detail::kDispersionA0[i] + c1 * thermo_detail::kDispersionA1[i] + c1 * c2 * thermo_detail::kDispersionA2[i];
        state.b[i] = thermo_detail::kDispersionB0[i] + c1 * thermo_detail::kDispersionB1[i] + c1 * c2 * thermo_detail::kDispersionB2[i];
        state.I1 += state.a[i] * scalar_pow(eta, static_cast<int>(i));
        state.I2 += state.b[i] * scalar_pow(eta, static_cast<int>(i));
        state.dEtaI1_deta += state.a[i] * static_cast<double>(i + 1) * scalar_pow(eta, static_cast<int>(i));
        state.dEtaI2_deta += state.b[i] * static_cast<double>(i + 1) * scalar_pow(eta, static_cast<int>(i));
    }
    const Scalar one = scalar_constant<Scalar>(1.0);
    state.C1 = one / (one
        + m_avg * (8.0 * eta - 2.0 * eta * eta) / scalar_pow(one - eta, 4)
        + (one - m_avg) * (20.0 * eta - 27.0 * eta * eta + 12.0 * scalar_pow(eta, 3) - 2.0 * scalar_pow(eta, 4))
            / scalar_pow((one - eta) * (2.0 - eta), 2));
    state.C2 = -state.C1 * state.C1 * (
        m_avg * (-4.0 * eta * eta + 20.0 * eta + 8.0) / scalar_pow(one - eta, 5)
        + (one - m_avg) * (2.0 * scalar_pow(eta, 3) + 12.0 * eta * eta - 48.0 * eta + 40.0)
            / scalar_pow((one - eta) * (2.0 - eta), 3));
    return state;
}

// EqID: ares_hs
template <typename Scalar>
static Scalar ares_hs_scalar_cpp(const HardChainStateScalar<Scalar> &hc_state) {
    const auto &zeta = hc_state.zeta;
    return 1.0 / zeta[0] * (
        3.0 * zeta[1] * zeta[2] / (1.0 - zeta[3])
        + scalar_pow(zeta[2], 3) / (zeta[3] * scalar_pow(1.0 - zeta[3], 2))
        + (scalar_pow(zeta[2], 3) / scalar_pow(zeta[3], 2) - zeta[0]) * scalar_log(1.0 - zeta[3])
    );
}

// EqID: ares_hc
template <typename Scalar>
static Scalar ares_hc_scalar_cpp(const MixtureStateScalar<Scalar> &thermo, const HardChainStateScalar<Scalar> &hc_state, const vector<Scalar> &x, const add_args &cppargs) {
    int ncomp = static_cast<int>(x.size());
    Scalar summ = scalar_constant<Scalar>(0.0);
    for (int i = 0; i < ncomp; ++i) {
        summ += x[i] * (cppargs.m[i] - 1.0) * scalar_log(hc_state.ghs[i * ncomp + i]);
    }
    return thermo.m_avg * ares_hs_scalar_cpp(hc_state) - summ;
}

// EqID: ares_disp
template <typename Scalar>
static Scalar ares_disp_scalar_cpp(const MixtureStateScalar<Scalar> &thermo, const DispersionPolynomialStateScalar<Scalar> &dispersion) {
    return -2.0 * PI * thermo.den * dispersion.I1 * thermo.m2es3
        - PI * thermo.den * thermo.m_avg * dispersion.C1 * dispersion.I2 * thermo.m2e2s3;
}

inline double ares_hc_cpp(const MixtureState &thermo, const HardChainState &hc_state, const vector<double> &x, const add_args &cppargs) {
    MixtureStateScalar<double> scalar_thermo;
    scalar_thermo.d = thermo.d;
    scalar_thermo.e_ij = thermo.e_ij;
    scalar_thermo.s_ij = thermo.s_ij;
    scalar_thermo.den = thermo.den;
    scalar_thermo.m_avg = thermo.m_avg;
    scalar_thermo.m2es3 = thermo.m2es3;
    scalar_thermo.m2e2s3 = thermo.m2e2s3;

    HardChainStateScalar<double> scalar_hc;
    scalar_hc.zeta = hc_state.zeta;
    scalar_hc.ghs = hc_state.ghs;
    scalar_hc.eta = hc_state.eta;
    return ares_hc_scalar_cpp(scalar_thermo, scalar_hc, x, cppargs);
}

inline double ares_disp_cpp(const MixtureState &thermo, const DispersionPolynomialState &dispersion) {
    MixtureStateScalar<double> scalar_thermo;
    scalar_thermo.d = thermo.d;
    scalar_thermo.e_ij = thermo.e_ij;
    scalar_thermo.s_ij = thermo.s_ij;
    scalar_thermo.den = thermo.den;
    scalar_thermo.m_avg = thermo.m_avg;
    scalar_thermo.m2es3 = thermo.m2es3;
    scalar_thermo.m2e2s3 = thermo.m2e2s3;

    DispersionPolynomialStateScalar<double> scalar_dispersion;
    for (size_t i = 0; i < scalar_dispersion.a.size(); ++i) {
        scalar_dispersion.a[i] = dispersion.a[i];
        scalar_dispersion.b[i] = dispersion.b[i];
    }
    scalar_dispersion.I1 = dispersion.I1;
    scalar_dispersion.I2 = dispersion.I2;
    scalar_dispersion.dEtaI1_deta = dispersion.dEtaI1_deta;
    scalar_dispersion.dEtaI2_deta = dispersion.dEtaI2_deta;
    scalar_dispersion.C1 = dispersion.C1;
    scalar_dispersion.C2 = dispersion.C2;
    return ares_disp_scalar_cpp(scalar_thermo, scalar_dispersion);
}

}  // namespace ares_detail
