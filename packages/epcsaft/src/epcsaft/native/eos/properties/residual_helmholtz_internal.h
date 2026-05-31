#pragma once
#include "eos/core_internal.h"
#include "eos/contributions/contribution_internal.h"
#include "autodiff/implicit_sensitivity.h"

#include <cppad/cppad.hpp>

#include <algorithm>
#include <map>
#include <numeric>
#include <string>

using thermo_detail::AresContributionKind;
using thermo_detail::AresContributions;
using thermo_detail::AssociationIntermediateState;
using thermo_detail::BornIntermediateState;
using thermo_detail::DadrhoResult;
using thermo_detail::DispersionPolynomialState;
using thermo_detail::HardChainState;
using thermo_detail::IonIntermediateState;
using thermo_detail::MixtureState;

namespace ares_detail {

constexpr int kGenericTargetSLocal = 1;
constexpr int kGenericTargetELocal = 2;
constexpr int kGenericTargetEAssocLocal = 3;
constexpr int kGenericTargetVolALocal = 4;
constexpr int kGenericTargetDBornLocal = 5;
constexpr int kGenericTargetLIJLocal = 7;
constexpr int kGenericTargetKHBLocal = 8;
constexpr int kGenericTargetFSolvLocal = 9;
constexpr int kGenericTargetDielcLocal = 10;

template <typename Scalar>
struct MixtureStateScalar {
    vector<Scalar> d;
    vector<Scalar> e_ij;
    vector<Scalar> s_ij;
    Scalar den = scalar_constant<Scalar>(0.0);
    Scalar m_avg = scalar_constant<Scalar>(0.0);
    Scalar m2es3 = scalar_constant<Scalar>(0.0);
    Scalar m2e2s3 = scalar_constant<Scalar>(0.0);
};

template <typename Scalar>
struct HardChainStateScalar {
    vector<Scalar> zeta;
    vector<Scalar> ghs;
    Scalar eta = scalar_constant<Scalar>(0.0);
};

template <typename Scalar>
struct DispersionPolynomialStateScalar {
    std::array<Scalar, 7> a{};
    std::array<Scalar, 7> b{};
    Scalar I1 = scalar_constant<Scalar>(0.0);
    Scalar I2 = scalar_constant<Scalar>(0.0);
    Scalar dEtaI1_deta = scalar_constant<Scalar>(0.0);
    Scalar dEtaI2_deta = scalar_constant<Scalar>(0.0);
    Scalar C1 = scalar_constant<Scalar>(0.0);
    Scalar C2 = scalar_constant<Scalar>(0.0);
};

template <typename Scalar>
struct AresContributionsScalar {
    Scalar hc = scalar_constant<Scalar>(0.0);
    Scalar disp = scalar_constant<Scalar>(0.0);
    Scalar assoc = scalar_constant<Scalar>(0.0);
    Scalar ion = scalar_constant<Scalar>(0.0);
    Scalar born = scalar_constant<Scalar>(0.0);
};

template <typename Scalar>
struct AssociationImplicitTermsScalar {
    vector<int> site_component_index;
    vector<Scalar> x_assoc;
    vector<Scalar> delta_ij;
    vector<Scalar> residuals;
    Scalar ares = scalar_constant<Scalar>(0.0);
    Scalar zraw = scalar_constant<Scalar>(0.0);
    vector<Scalar> dadx;
    Scalar sum_x_dadx = scalar_constant<Scalar>(0.0);
    vector<Scalar> mu;
};

struct AssociationDensityResponse {
    std::string backend = "cppad_implicit_association";
    std::string helper = "association_implicit_sensitivity";
    int site_count = 0;
    double zraw = 0.0;
    vector<double> mu;
    double dzraw_drho = 0.0;
    vector<double> dmu_drho;
    vector<double> site_sensitivity_row_major;
};

struct AssociationPhaseStateResponse {
    bool active = false;
    int ncomp = 0;
    int base_var_count = 0;
    std::string backend = "cppad_implicit_association";
    std::string helper = "association_implicit_sensitivity";
    int site_count = 0;
    double zraw = 0.0;
    vector<double> mu;
    vector<double> site_sensitivity_row_major;
    vector<double> site_second_sensitivity_tensor_row_major;
    vector<double> dzraw_dvar;
    vector<double> dmu_dvar_row_major;
    vector<double> d2zraw_dvar2_row_major;
    vector<double> d2mu_dvar2_tensor_row_major;
};

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

template <typename Scalar>
static Scalar scalar_component_parameter_cpp(
    int target_kind,
    int target_index,
    int component_index,
    double base_value,
    const Scalar *target_value
) {
    if (target_value != nullptr && target_index == component_index && target_kind >= 0) {
        return *target_value;
    }
    return scalar_constant<Scalar>(base_value);
}

template <typename Scalar>
static Scalar scalar_dielc_parameter_cpp(
    int target_kind,
    int target_index,
    int component_index,
    double base_value,
    const Scalar *target_value
) {
    return scalar_component_parameter_cpp(
        target_kind,
        target_index,
        component_index,
        base_value,
        target_kind == kGenericTargetDielcLocal ? target_value : nullptr
    );
}

template <typename Scalar, typename TemperatureScalar>
static Scalar ion_diameter_scalar_cpp(
    int i,
    const TemperatureScalar &t,
    const add_args &cppargs,
    const Scalar &sigma_i,
    const Scalar &epsilon_i
) {
    if (!is_ion_species(cppargs, i)) {
        return sigma_i;
    }
    int mode = cppargs.d_ion_mode;
    if (mode == 0) {
        return sigma_i;
    }
    if (mode == 1) {
        return sigma_i * 0.88;
    }
    if (mode == 2) {
        return sigma_i * (1.0 - 0.12 * scalar_exp(-3.0 * epsilon_i / t));
    }
    throw ValueError("Unknown d_ion_mode. Supported values are 0, 1, 2.");
}

template <typename Scalar, typename TemperatureScalar>
static Scalar ion_born_radius_scalar_cpp(
    int i,
    const TemperatureScalar &t,
    const add_args &cppargs,
    const Scalar &sigma_i,
    const Scalar &epsilon_i,
    int target_kind,
    int target_index,
    const Scalar *target_value
) {
    if (!is_ion_species(cppargs, i)) {
        return sigma_i;
    }
    int mode = cppargs.d_born_mode;
    if (mode == 0) {
        return sigma_i;
    }
    if (mode == 1) {
        return sigma_i * 0.88;
    }
    if (mode == 2) {
        return sigma_i * (1.0 - 0.12 * scalar_exp(-3.0 * epsilon_i / t));
    }
    if (mode == 3) {
        if (cppargs.d_born.size() <= static_cast<size_t>(i) || cppargs.d_born[i] <= 0.0) {
            throw ValueError("d_Born_mode=fitted_param requires positive ionic params['d_born'] values.");
        }
        return scalar_component_parameter_cpp(
            target_kind,
            target_index,
            i,
            cppargs.d_born[i],
            target_kind == kGenericTargetDBornLocal ? target_value : nullptr
        );
    }
    throw ValueError("Unknown d_Born_mode. Supported values are 0, 1, 2, 3.");
}

template <typename Scalar, typename TemperatureScalar>
static MixtureStateScalar<Scalar> mixture_state_scalar_cpp(
    const TemperatureScalar &t,
    const Scalar &rho,
    const vector<Scalar> &x,
    const add_args &cppargs,
    int k_override_index = -1,
    const Scalar *k_override_value = nullptr,
    int l_override_index = -1,
    const Scalar *l_override_value = nullptr,
    int component_target_kind = -1,
    int component_target_index = -1,
    const Scalar *component_target_value = nullptr
) {
    MixtureStateScalar<Scalar> state;
    int ncomp = static_cast<int>(x.size());
    state.d.assign(ncomp, scalar_constant<Scalar>(0.0));
    state.e_ij.assign(ncomp * ncomp, 0.0);
    state.s_ij.assign(ncomp * ncomp, scalar_constant<Scalar>(0.0));
    state.den = rho * N_AV / 1.0e30;

    for (int i = 0; i < ncomp; ++i) {
        Scalar sigma_i = scalar_component_parameter_cpp(
            component_target_kind,
            component_target_index,
            i,
            cppargs.s[i],
            component_target_kind == kGenericTargetSLocal ? component_target_value : nullptr
        );
        Scalar epsilon_i = scalar_component_parameter_cpp(
            component_target_kind,
            component_target_index,
            i,
            cppargs.e[i],
            component_target_kind == kGenericTargetELocal ? component_target_value : nullptr
        );
        state.d[i] = sigma_i * (1.0 - 0.12 * scalar_exp(-3.0 * epsilon_i / t));
        if (!cppargs.z.empty() && std::abs(cppargs.z[i]) > 1e-12) {
            state.d[i] = ion_diameter_scalar_cpp(i, t, cppargs, sigma_i, epsilon_i);
        }
        state.m_avg += x[i] * scalar_constant<Scalar>(cppargs.m[i]);
    }

    int idx = -1;
    for (int i = 0; i < ncomp; ++i) {
        for (int j = 0; j < ncomp; ++j) {
            ++idx;
            if (l_override_value != nullptr && l_override_index >= 0) {
                Scalar sigma_i = scalar_component_parameter_cpp(
                    component_target_kind,
                    component_target_index,
                    i,
                    cppargs.s[i],
                    component_target_kind == kGenericTargetSLocal ? component_target_value : nullptr
                );
                Scalar sigma_j = scalar_component_parameter_cpp(
                    component_target_kind,
                    component_target_index,
                    j,
                    cppargs.s[j],
                    component_target_kind == kGenericTargetSLocal ? component_target_value : nullptr
                );
                state.s_ij[idx] = 0.5 * (sigma_i + sigma_j);
                if (idx == l_override_index) {
                    state.s_ij[idx] *= (1.0 - *l_override_value);
                } else if (!cppargs.l_ij.empty()) {
                    state.s_ij[idx] *= (1.0 - cppargs.l_ij[static_cast<size_t>(idx)]);
                }
            } else {
                Scalar sigma_i = scalar_component_parameter_cpp(
                    component_target_kind,
                    component_target_index,
                    i,
                    cppargs.s[i],
                    component_target_kind == kGenericTargetSLocal ? component_target_value : nullptr
                );
                Scalar sigma_j = scalar_component_parameter_cpp(
                    component_target_kind,
                    component_target_index,
                    j,
                    cppargs.s[j],
                    component_target_kind == kGenericTargetSLocal ? component_target_value : nullptr
                );
                state.s_ij[idx] = 0.5 * (sigma_i + sigma_j);
                if (!cppargs.l_ij.empty()) {
                    state.s_ij[idx] *= (1.0 - cppargs.l_ij[static_cast<size_t>(idx)]);
                }
            }
            Scalar epsilon_i = scalar_component_parameter_cpp(
                component_target_kind,
                component_target_index,
                i,
                cppargs.e[i],
                component_target_kind == kGenericTargetELocal ? component_target_value : nullptr
            );
            Scalar epsilon_j = scalar_component_parameter_cpp(
                component_target_kind,
                component_target_index,
                j,
                cppargs.e[j],
                component_target_kind == kGenericTargetELocal ? component_target_value : nullptr
            );
            Scalar epsilon = scalar_sqrt(epsilon_i * epsilon_j);
            if (!cppargs.z.empty() && cppargs.z[i] * cppargs.z[j] > 0.0) {
                epsilon = scalar_constant<Scalar>(0.0);
            } else if (k_override_value != nullptr && k_override_index >= 0) {
                if (idx == k_override_index) {
                    epsilon *= (1.0 - *k_override_value);
                } else if (!cppargs.k_ij.empty()) {
                    epsilon *= (1.0 - cppargs.k_ij[static_cast<size_t>(idx)]);
                }
            } else if (!cppargs.k_ij.empty()) {
                epsilon *= (1.0 - cppargs.k_ij[static_cast<size_t>(idx)]);
            }
            state.e_ij[idx] = epsilon;
            state.m2es3 += x[i] * x[j] * cppargs.m[i] * cppargs.m[j] * state.e_ij[idx] / t * scalar_pow(state.s_ij[idx], 3);
            state.m2e2s3 += x[i] * x[j] * cppargs.m[i] * cppargs.m[j] * scalar_pow(state.e_ij[idx] / t, 2) * scalar_pow(state.s_ij[idx], 3);
        }
    }
    return state;
}

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

// EqID: ares_assoc
template <typename Scalar>
static Scalar ares_assoc_scalar_cpp(const vector<Scalar> &x, const add_args &cppargs) {
    (void)x;
    if (!cppargs.assoc_num.empty()) {
        for (int sites : cppargs.assoc_num) {
            if (sites > 0) {
                throw ValueError("unsupported: CppAD association recording requires implicit site-fraction sensitivities.");
            }
        }
    }
    return scalar_constant<Scalar>(0.0);
}

inline double ares_assoc_cpp(const AssociationIntermediateState &assoc_state, const vector<double> &x) {
    if (!assoc_state.active) {
        return 0.0;
    }
    double value = 0.0;
    for (int i = 0; i < static_cast<int>(assoc_state.setup.site_component_index.size()); ++i) {
        int component_index = assoc_state.setup.site_component_index[i];
        value += x[component_index] * (std::log(assoc_state.XA[i]) - 0.5 * assoc_state.XA[i] + 0.5);
    }
    return value;
}

template <typename Scalar>
static Scalar hs_contact_density_derivative_scalar_cpp(const Scalar &pair_diameter, const Scalar &zeta2, const Scalar &zeta3) {
    return zeta3 / scalar_pow(1.0 - zeta3, 2.0)
        + pair_diameter * (
            3.0 * zeta2 / scalar_pow(1.0 - zeta3, 2.0)
            + 6.0 * zeta2 * zeta3 / scalar_pow(1.0 - zeta3, 3.0)
        )
        + scalar_pow(pair_diameter, 2.0) * (
            4.0 * zeta2 * zeta2 / scalar_pow(1.0 - zeta3, 3.0)
            + 6.0 * zeta2 * zeta2 * zeta3 / scalar_pow(1.0 - zeta3, 4.0)
        );
}

template <typename Scalar>
static Scalar hs_contact_composition_derivative_scalar_cpp(
    const Scalar &pair_diameter,
    const Scalar &zeta2,
    const Scalar &zeta3,
    const Scalar &dzeta2_dx,
    const Scalar &dzeta3_dx
) {
    return dzeta3_dx / scalar_pow(1.0 - zeta3, 2.0)
        + pair_diameter * (
            3.0 * dzeta2_dx / scalar_pow(1.0 - zeta3, 2.0)
            + 6.0 * zeta2 * dzeta3_dx / scalar_pow(1.0 - zeta3, 3.0)
        )
        + scalar_pow(pair_diameter, 2.0) * (
            4.0 * zeta2 * dzeta2_dx / scalar_pow(1.0 - zeta3, 3.0)
            + 6.0 * zeta2 * zeta2 * dzeta3_dx / scalar_pow(1.0 - zeta3, 4.0)
        );
}

template <typename Scalar>
static Scalar association_volume_scalar_cpp(
    int comp_i,
    int comp_j,
    int ncomp,
    const vector<Scalar> &s_ij,
    const add_args &cppargs,
    int component_target_kind = -1,
    int component_target_index = -1,
    const Scalar *component_target_value = nullptr,
    int k_hb_override_index = -1,
    const Scalar *k_hb_override_value = nullptr
) {
    const int idxi = comp_i * ncomp + comp_i;
    const int idxj = comp_j * ncomp + comp_j;
    const Scalar vol_i = scalar_component_parameter_cpp(
        kGenericTargetVolALocal,
        component_target_index,
        comp_i,
        cppargs.vol_a[static_cast<size_t>(comp_i)],
        component_target_kind == kGenericTargetVolALocal ? component_target_value : nullptr
    );
    const Scalar vol_j = scalar_component_parameter_cpp(
        kGenericTargetVolALocal,
        component_target_index,
        comp_j,
        cppargs.vol_a[static_cast<size_t>(comp_j)],
        component_target_kind == kGenericTargetVolALocal ? component_target_value : nullptr
    );
    Scalar volume = scalar_sqrt(vol_i * vol_j)
        * scalar_pow(
            scalar_sqrt(s_ij[static_cast<size_t>(idxi)] * s_ij[static_cast<size_t>(idxj)])
                / (0.5 * (s_ij[static_cast<size_t>(idxi)] + s_ij[static_cast<size_t>(idxj)])),
            3.0
        );
    if (!cppargs.k_hb.empty()) {
        const int pair_index = comp_i * ncomp + comp_j;
        const Scalar k_hb = (k_hb_override_value != nullptr && k_hb_override_index == pair_index)
            ? *k_hb_override_value
            : scalar_constant<Scalar>(cppargs.k_hb[static_cast<size_t>(pair_index)]);
        volume *= (1.0 - k_hb);
    }
    return volume;
}

template <typename Scalar>
static vector<Scalar> solve_linear_system_scalar_cpp(vector<Scalar> matrix, vector<Scalar> rhs, int n) {
    for (int col = 0; col < n; ++col) {
        int pivot = col;
        double pivot_abs = std::abs(scalar_value(matrix[static_cast<size_t>(col * n + col)]));
        for (int row = col + 1; row < n; ++row) {
            const double candidate_abs = std::abs(scalar_value(matrix[static_cast<size_t>(row * n + col)]));
            if (candidate_abs > pivot_abs) {
                pivot = row;
                pivot_abs = candidate_abs;
            }
        }
        if (pivot_abs <= 1.0e-30) {
            throw ValueError("Association implicit sensitivity matrix is singular.");
        }
        if (pivot != col) {
            for (int j = col; j < n; ++j) {
                std::swap(matrix[static_cast<size_t>(col * n + j)], matrix[static_cast<size_t>(pivot * n + j)]);
            }
            std::swap(rhs[static_cast<size_t>(col)], rhs[static_cast<size_t>(pivot)]);
        }
        const Scalar pivot_value = matrix[static_cast<size_t>(col * n + col)];
        for (int row = col + 1; row < n; ++row) {
            const Scalar factor = matrix[static_cast<size_t>(row * n + col)] / pivot_value;
            matrix[static_cast<size_t>(row * n + col)] = scalar_constant<Scalar>(0.0);
            for (int j = col + 1; j < n; ++j) {
                matrix[static_cast<size_t>(row * n + j)] -= factor * matrix[static_cast<size_t>(col * n + j)];
            }
            rhs[static_cast<size_t>(row)] -= factor * rhs[static_cast<size_t>(col)];
        }
    }

    vector<Scalar> out(static_cast<size_t>(n), scalar_constant<Scalar>(0.0));
    for (int row = n - 1; row >= 0; --row) {
        Scalar accum = rhs[static_cast<size_t>(row)];
        for (int col = row + 1; col < n; ++col) {
            accum -= matrix[static_cast<size_t>(row * n + col)] * out[static_cast<size_t>(col)];
        }
        out[static_cast<size_t>(row)] = accum / matrix[static_cast<size_t>(row * n + row)];
    }
    return out;
}

template <typename Scalar>
static vector<Scalar> association_site_fraction_density_terms_scalar_cpp(
    const vector<Scalar> &delta_ij,
    const Scalar &den,
    const vector<Scalar> &XA,
    const vector<Scalar> &ddelta_weighted,
    const vector<Scalar> &x_assoc
) {
    const int num_sites = static_cast<int>(XA.size());
    vector<Scalar> matrix(static_cast<size_t>(num_sites * num_sites), scalar_constant<Scalar>(0.0));
    vector<Scalar> rhs(static_cast<size_t>(num_sites), scalar_constant<Scalar>(0.0));

    int ij = 0;
    for (int i = 0; i < num_sites; ++i) {
        Scalar summ = scalar_constant<Scalar>(0.0);
        for (int j = 0; j < num_sites; ++j) {
            rhs[static_cast<size_t>(i)] -= x_assoc[static_cast<size_t>(j)] * XA[static_cast<size_t>(j)] * ddelta_weighted[static_cast<size_t>(ij)];
            matrix[static_cast<size_t>(i * num_sites + j)] = x_assoc[static_cast<size_t>(j)] * delta_ij[static_cast<size_t>(ij)];
            summ += x_assoc[static_cast<size_t>(j)] * XA[static_cast<size_t>(j)] * delta_ij[static_cast<size_t>(ij)];
            ++ij;
        }
        rhs[static_cast<size_t>(i)] -= summ;
        matrix[static_cast<size_t>(i * num_sites + i)] = scalar_pow(1.0 + den * summ, 2.0) / den;
    }

    return solve_linear_system_scalar_cpp(matrix, rhs, num_sites);
}

template <typename Scalar>
static vector<Scalar> association_site_fraction_composition_terms_scalar_cpp(
    const vector<Scalar> &delta_ij,
    const Scalar &den,
    const vector<Scalar> &XA,
    const vector<Scalar> &ddelta_dx,
    const vector<int> &site_component_index,
    const vector<Scalar> &x_assoc,
    int ncomp
) {
    const int num_sites = static_cast<int>(XA.size());
    vector<Scalar> dXA_dx(static_cast<size_t>(ncomp * num_sites), scalar_constant<Scalar>(0.0));

    for (int k = 0; k < ncomp; ++k) {
        vector<Scalar> matrix(static_cast<size_t>(num_sites * num_sites), scalar_constant<Scalar>(0.0));
        vector<Scalar> rhs(static_cast<size_t>(num_sites), scalar_constant<Scalar>(0.0));

        int ij = 0;
        for (int i = 0; i < num_sites; ++i) {
            Scalar direct_sum = scalar_constant<Scalar>(0.0);
            Scalar delta_sum = scalar_constant<Scalar>(0.0);
            for (int j = 0; j < num_sites; ++j) {
                if (site_component_index[static_cast<size_t>(j)] == k) {
                    direct_sum += XA[static_cast<size_t>(j)] * delta_ij[static_cast<size_t>(ij)];
                }
                delta_sum += x_assoc[static_cast<size_t>(j)] * XA[static_cast<size_t>(j)]
                    * ddelta_dx[static_cast<size_t>(k * num_sites * num_sites + ij)];
                matrix[static_cast<size_t>(i * num_sites + j)] = x_assoc[static_cast<size_t>(j)] * delta_ij[static_cast<size_t>(ij)];
                ++ij;
            }
            rhs[static_cast<size_t>(i)] = -(direct_sum + delta_sum);
            matrix[static_cast<size_t>(i * num_sites + i)] += 1.0 / (den * XA[static_cast<size_t>(i)] * XA[static_cast<size_t>(i)]);
        }

        vector<Scalar> solution = solve_linear_system_scalar_cpp(matrix, rhs, num_sites);
        for (int i = 0; i < num_sites; ++i) {
            dXA_dx[static_cast<size_t>(k * num_sites + i)] = solution[static_cast<size_t>(i)];
        }
    }

    return dXA_dx;
}

template <typename Scalar>
static AssociationImplicitTermsScalar<Scalar> association_implicit_terms_scalar_cpp(
    const MixtureStateScalar<Scalar> &thermo,
    const HardChainStateScalar<Scalar> &hc_state,
    double t,
    const vector<Scalar> &x,
    const add_args &cppargs,
    const vector<Scalar> &XA,
    int component_target_kind = -1,
    int component_target_index = -1,
    const Scalar *component_target_value = nullptr,
    int k_hb_override_index = -1,
    const Scalar *k_hb_override_value = nullptr
) {
    const int ncomp = static_cast<int>(x.size());
    AssociationImplicitTermsScalar<Scalar> out;
    out.dadx.assign(static_cast<size_t>(ncomp), scalar_constant<Scalar>(0.0));
    out.mu.assign(static_cast<size_t>(ncomp), scalar_constant<Scalar>(0.0));

    for (int comp = 0; comp < static_cast<int>(cppargs.assoc_num.size()); ++comp) {
        for (int site = 0; site < cppargs.assoc_num[static_cast<size_t>(comp)]; ++site) {
            out.site_component_index.push_back(comp);
            out.x_assoc.push_back(x[static_cast<size_t>(comp)]);
        }
    }

    const int num_sites = static_cast<int>(out.site_component_index.size());
    out.delta_ij.assign(static_cast<size_t>(num_sites * num_sites), scalar_constant<Scalar>(0.0));
    out.residuals.assign(static_cast<size_t>(num_sites), scalar_constant<Scalar>(0.0));
    if (num_sites == 0) {
        return out;
    }
    if (static_cast<int>(XA.size()) != num_sites) {
        throw ValueError("Association implicit sensitivity received a site-fraction vector with the wrong size.");
    }

    int idxa = 0;
    for (int i = 0; i < num_sites; ++i) {
        const int comp_i = out.site_component_index[static_cast<size_t>(i)];
        for (int j = 0; j < num_sites; ++j) {
            const int comp_j = out.site_component_index[static_cast<size_t>(j)];
            if (cppargs.assoc_matrix[static_cast<size_t>(idxa)] != 0) {
                const Scalar e_i = scalar_component_parameter_cpp(
                    kGenericTargetEAssocLocal,
                    component_target_index,
                    comp_i,
                    cppargs.e_assoc[static_cast<size_t>(comp_i)],
                    component_target_kind == kGenericTargetEAssocLocal ? component_target_value : nullptr
                );
                const Scalar e_j = scalar_component_parameter_cpp(
                    kGenericTargetEAssocLocal,
                    component_target_index,
                    comp_j,
                    cppargs.e_assoc[static_cast<size_t>(comp_j)],
                    component_target_kind == kGenericTargetEAssocLocal ? component_target_value : nullptr
                );
                const Scalar eABij = 0.5 * (e_i + e_j);
                const Scalar volABij = association_volume_scalar_cpp(
                    comp_i,
                    comp_j,
                    ncomp,
                    thermo.s_ij,
                    cppargs,
                    component_target_kind,
                    component_target_index,
                    component_target_value,
                    k_hb_override_index,
                    k_hb_override_value
                );
                out.delta_ij[static_cast<size_t>(idxa)] =
                    hc_state.ghs[static_cast<size_t>(comp_i * ncomp + comp_j)]
                    * (scalar_exp(eABij / t) - 1.0)
                    * scalar_pow(thermo.s_ij[static_cast<size_t>(comp_i * ncomp + comp_j)], 3.0)
                    * volABij;
            }
            ++idxa;
        }
    }

    for (int i = 0; i < num_sites; ++i) {
        Scalar summ = scalar_constant<Scalar>(0.0);
        for (int j = 0; j < num_sites; ++j) {
            summ += out.x_assoc[static_cast<size_t>(j)] * XA[static_cast<size_t>(j)]
                * out.delta_ij[static_cast<size_t>(i * num_sites + j)];
        }
        out.residuals[static_cast<size_t>(i)] = XA[static_cast<size_t>(i)] * (1.0 + thermo.den * summ) - 1.0;
        const int component_index = out.site_component_index[static_cast<size_t>(i)];
        out.ares += x[static_cast<size_t>(component_index)] * (
            scalar_log(XA[static_cast<size_t>(i)]) - 0.5 * XA[static_cast<size_t>(i)] + 0.5
        );
    }

    vector<Scalar> ddelta_weighted(static_cast<size_t>(num_sites * num_sites), scalar_constant<Scalar>(0.0));
    idxa = 0;
    for (int i = 0; i < num_sites; ++i) {
        const int comp_i = out.site_component_index[static_cast<size_t>(i)];
        for (int j = 0; j < num_sites; ++j) {
            const int comp_j = out.site_component_index[static_cast<size_t>(j)];
            if (cppargs.assoc_matrix[static_cast<size_t>(idxa)] != 0) {
                const Scalar pair_diameter = thermo.d[static_cast<size_t>(comp_i)] * thermo.d[static_cast<size_t>(comp_j)]
                    / (thermo.d[static_cast<size_t>(comp_i)] + thermo.d[static_cast<size_t>(comp_j)]);
                const Scalar e_i = scalar_component_parameter_cpp(
                    kGenericTargetEAssocLocal,
                    component_target_index,
                    comp_i,
                    cppargs.e_assoc[static_cast<size_t>(comp_i)],
                    component_target_kind == kGenericTargetEAssocLocal ? component_target_value : nullptr
                );
                const Scalar e_j = scalar_component_parameter_cpp(
                    kGenericTargetEAssocLocal,
                    component_target_index,
                    comp_j,
                    cppargs.e_assoc[static_cast<size_t>(comp_j)],
                    component_target_kind == kGenericTargetEAssocLocal ? component_target_value : nullptr
                );
                const Scalar eABij = 0.5 * (e_i + e_j);
                const Scalar volABij = association_volume_scalar_cpp(
                    comp_i,
                    comp_j,
                    ncomp,
                    thermo.s_ij,
                    cppargs,
                    component_target_kind,
                    component_target_index,
                    component_target_value,
                    k_hb_override_index,
                    k_hb_override_value
                );
                ddelta_weighted[static_cast<size_t>(idxa)] =
                    hs_contact_density_derivative_scalar_cpp(pair_diameter, hc_state.zeta[2], hc_state.zeta[3])
                    * (scalar_exp(eABij / t) - 1.0)
                    * scalar_pow(thermo.s_ij[static_cast<size_t>(comp_i * ncomp + comp_j)], 3.0)
                    * volABij;
            }
            ++idxa;
        }
    }

    vector<Scalar> dXA_density = association_site_fraction_density_terms_scalar_cpp(
        out.delta_ij, thermo.den, XA, ddelta_weighted, out.x_assoc
    );
    for (int i = 0; i < num_sites; ++i) {
        const int component_index = out.site_component_index[static_cast<size_t>(i)];
        out.zraw += x[static_cast<size_t>(component_index)] * (1.0 / XA[static_cast<size_t>(i)] - 0.5)
            * dXA_density[static_cast<size_t>(i)];
    }

    vector<Scalar> ddelta_dx(static_cast<size_t>(num_sites * num_sites * ncomp), scalar_constant<Scalar>(0.0));
    int idx_ddelta = 0;
    for (int k = 0; k < ncomp; ++k) {
        for (int i = 0; i < num_sites; ++i) {
            const int comp_i = out.site_component_index[static_cast<size_t>(i)];
            for (int j = 0; j < num_sites; ++j) {
                const int comp_j = out.site_component_index[static_cast<size_t>(j)];
                if (cppargs.assoc_matrix[static_cast<size_t>(i * num_sites + j)] != 0) {
                    const Scalar pair_diameter = thermo.d[static_cast<size_t>(comp_i)] * thermo.d[static_cast<size_t>(comp_j)]
                        / (thermo.d[static_cast<size_t>(comp_i)] + thermo.d[static_cast<size_t>(comp_j)]);
                    const Scalar dzeta2_dx = scalar_constant<Scalar>(PI / 6.0 * cppargs.m[static_cast<size_t>(k)])
                        * thermo.den
                        * scalar_pow(thermo.d[static_cast<size_t>(k)], 2.0);
                    const Scalar dzeta3_dx = scalar_constant<Scalar>(PI / 6.0 * cppargs.m[static_cast<size_t>(k)])
                        * thermo.den
                        * scalar_pow(thermo.d[static_cast<size_t>(k)], 3.0);
                    const Scalar e_i = scalar_component_parameter_cpp(
                        kGenericTargetEAssocLocal,
                        component_target_index,
                        comp_i,
                        cppargs.e_assoc[static_cast<size_t>(comp_i)],
                        component_target_kind == kGenericTargetEAssocLocal ? component_target_value : nullptr
                    );
                    const Scalar e_j = scalar_component_parameter_cpp(
                        kGenericTargetEAssocLocal,
                        component_target_index,
                        comp_j,
                        cppargs.e_assoc[static_cast<size_t>(comp_j)],
                        component_target_kind == kGenericTargetEAssocLocal ? component_target_value : nullptr
                    );
                    const Scalar eABij = 0.5 * (e_i + e_j);
                    const Scalar volABij = association_volume_scalar_cpp(
                        comp_i,
                        comp_j,
                        ncomp,
                        thermo.s_ij,
                        cppargs,
                        component_target_kind,
                        component_target_index,
                        component_target_value,
                        k_hb_override_index,
                        k_hb_override_value
                    );
                    ddelta_dx[static_cast<size_t>(idx_ddelta)] =
                        hs_contact_composition_derivative_scalar_cpp(pair_diameter, hc_state.zeta[2], hc_state.zeta[3], dzeta2_dx, dzeta3_dx)
                        * (scalar_exp(eABij / t) - 1.0)
                        * scalar_pow(thermo.s_ij[static_cast<size_t>(comp_i * ncomp + comp_j)], 3.0)
                        * volABij;
                }
                ++idx_ddelta;
            }
        }
    }

    vector<Scalar> dXA_dx = association_site_fraction_composition_terms_scalar_cpp(
        out.delta_ij,
        thermo.den,
        XA,
        ddelta_dx,
        out.site_component_index,
        out.x_assoc,
        ncomp
    );
    for (int i = 0; i < ncomp; ++i) {
        for (int j = 0; j < num_sites; ++j) {
            out.dadx[static_cast<size_t>(i)] += x[static_cast<size_t>(out.site_component_index[static_cast<size_t>(j)])]
                * dXA_dx[static_cast<size_t>(i * num_sites + j)] * (1.0 / XA[static_cast<size_t>(j)] - 0.5);
        }
    }
    for (int i = 0; i < num_sites; ++i) {
        const int component_index = out.site_component_index[static_cast<size_t>(i)];
        out.dadx[static_cast<size_t>(component_index)] += scalar_log(XA[static_cast<size_t>(i)])
            - 0.5 * XA[static_cast<size_t>(i)] + 0.5;
    }
    for (int i = 0; i < ncomp; ++i) {
        out.sum_x_dadx += x[static_cast<size_t>(i)] * out.dadx[static_cast<size_t>(i)];
    }
    for (int i = 0; i < ncomp; ++i) {
        out.mu[static_cast<size_t>(i)] = out.ares + out.zraw + out.dadx[static_cast<size_t>(i)] - out.sum_x_dadx;
    }
    return out;
}

// EqID: ares_dh
template <typename Scalar, typename TemperatureScalar>
static Scalar ares_ion_scalar_cpp(
    const TemperatureScalar &t,
    const MixtureStateScalar<Scalar> &thermo,
    const vector<Scalar> &x,
    const add_args &cppargs,
    int component_target_kind = -1,
    int component_target_index = -1,
    const Scalar *component_target_value = nullptr
) {
    if (cppargs.z.empty()) {
        return scalar_constant<Scalar>(0.0);
    }
    bool has_charge = false;
    for (double charge : cppargs.z) {
        if (std::abs(charge) > 1.0e-12) {
            has_charge = true;
            break;
        }
    }
    if (!has_charge) {
        return scalar_constant<Scalar>(0.0);
    }
    Scalar q2_sum = scalar_constant<Scalar>(0.0);
    for (int i = 0; i < static_cast<int>(x.size()); ++i) {
        q2_sum += x[i] * cppargs.z[i] * cppargs.z[i];
    }
    Scalar eps = scalar_constant<Scalar>(0.0);
    if (cppargs.dielc_rule == 0) {
        if (component_target_kind == kGenericTargetDielcLocal) {
            throw ValueError("unsupported: CppAD ionic dielectric-parameter recording requires dielc_rule=1.");
        }
        eps = scalar_constant<Scalar>(*std::max_element(cppargs.dielc.begin(), cppargs.dielc.end()));
    } else if (cppargs.dielc_rule == 1) {
        for (int i = 0; i < static_cast<int>(x.size()); ++i) {
            eps += x[i] * scalar_dielc_parameter_cpp(
                component_target_kind,
                component_target_index,
                i,
                cppargs.dielc[i],
                component_target_value
            );
        }
    } else {
        if (component_target_kind == kGenericTargetDielcLocal) {
            throw ValueError("unsupported: CppAD ionic dielectric-parameter recording requires dielc_rule=1.");
        }
#ifdef EPCSAFT_HAS_CPPAD
        eps = dielectric_constant_rule_cppad_cpp(cppargs.dielc_rule, x, cppargs);
#else
        throw ValueError("CppAD ionic recording requires CppAD support for composition-dependent dielectric rules.");
#endif
    }
    Scalar kappa = scalar_sqrt(thermo.den * E_CHRG * E_CHRG / kb / t / (eps * perm_vac) * q2_sum);
    Scalar chi_sum = scalar_constant<Scalar>(0.0);
    for (int i = 0; i < static_cast<int>(x.size()); ++i) {
        Scalar ka = kappa * thermo.d[i];
        Scalar chi = 3.0 / scalar_pow(ka, 3) * (1.5 + scalar_log(1.0 + ka) - 2.0 * (1.0 + ka) + 0.5 * scalar_pow(1.0 + ka, 2));
        chi_sum += x[i] * cppargs.z[i] * cppargs.z[i] * chi;
    }
    Scalar K0 = scalar_constant<Scalar>(E_CHRG * E_CHRG / (12.0 * PI * kb * perm_vac)) / t;
    return -K0 * kappa / eps * chi_sum;
}

inline double ares_ion_cpp(double t, const IonIntermediateState &ion_state) {
    if (!ion_state.active) {
        return 0.0;
    }
    double K0 = E_CHRG * E_CHRG / (12.0 * PI * kb * t * perm_vac);
    return -K0 * ion_state.kappa / ion_state.dielectric.eps * ion_state.chi_sum;
}

// EqID: ares_born
template <typename Scalar, typename TemperatureScalar>
static Scalar ares_born_scalar_cpp(
    const TemperatureScalar &t,
    const vector<Scalar> &x,
    const add_args &cppargs,
    int component_target_kind = -1,
    int component_target_index = -1,
    const Scalar *component_target_value = nullptr
) {
    if (cppargs.z.empty() || cppargs.born_model == 0) {
        return scalar_constant<Scalar>(0.0);
    }
    bool has_charge = false;
    for (double charge : cppargs.z) {
        if (std::abs(charge) > 1.0e-12) {
            has_charge = true;
            break;
        }
    }
    if (!has_charge) {
        return scalar_constant<Scalar>(0.0);
    }
    if (cppargs.born_model != 1) {
        if (cppargs.born_model != 2) {
            throw ValueError("Unknown born_model. Supported values are 0, 1, 2.");
        }
    }
    Scalar eps = scalar_constant<Scalar>(0.0);
    if (cppargs.dielc_rule == 0) {
        if (component_target_kind == kGenericTargetDielcLocal) {
            throw ValueError("unsupported: CppAD Born dielectric-parameter recording requires dielc_rule=1.");
        }
        eps = scalar_constant<Scalar>(*std::max_element(cppargs.dielc.begin(), cppargs.dielc.end()));
    } else if (cppargs.dielc_rule == 1) {
        for (int i = 0; i < static_cast<int>(x.size()); ++i) {
            eps += x[i] * scalar_dielc_parameter_cpp(
                component_target_kind,
                component_target_index,
                i,
                cppargs.dielc[i],
                component_target_value
            );
        }
    } else {
        if (component_target_kind == kGenericTargetDielcLocal) {
            throw ValueError("unsupported: CppAD Born dielectric-parameter recording requires dielc_rule=1.");
        }
#ifdef EPCSAFT_HAS_CPPAD
        eps = dielectric_constant_rule_cppad_cpp(cppargs.dielc_rule, x, cppargs);
#else
        throw ValueError("CppAD Born recording requires CppAD support for composition-dependent dielectric rules.");
#endif
    }
    if (cppargs.born_eps_mode == 1) {
        throw ValueError("unsupported: CppAD Born reference-solvent dielectric routing requires a tape route.");
    }
    if (cppargs.born_model == 1) {
        Scalar charge_radius_sum = scalar_constant<Scalar>(0.0);
        for (int i = 0; i < static_cast<int>(x.size()); ++i) {
            if (!is_ion_species(cppargs, i)) {
                continue;
            }
            Scalar sigma_i = scalar_component_parameter_cpp(
                component_target_kind,
                component_target_index,
                i,
                cppargs.s[i],
                component_target_kind == kGenericTargetSLocal ? component_target_value : nullptr
            );
            Scalar epsilon_i = scalar_component_parameter_cpp(
                component_target_kind,
                component_target_index,
                i,
                cppargs.e[i],
                component_target_kind == kGenericTargetELocal ? component_target_value : nullptr
            );
            Scalar d_born_i = ion_born_radius_scalar_cpp(
                i,
                t,
                cppargs,
                sigma_i,
                epsilon_i,
                component_target_kind,
                component_target_index,
                component_target_value
            );
            charge_radius_sum += x[i] * cppargs.z[i] * cppargs.z[i] / d_born_i;
        }
        Scalar Kborn = scalar_constant<Scalar>(E_CHRG * E_CHRG / (4.0 * PI * kb * perm_vac)) / t;
        return -Kborn * (1.0 - 1.0 / eps) * charge_radius_sum;
    }

    const bool use_ssm = (cppargs.born_solvation_shell_model != 0);
    const bool use_ds = (cppargs.born_dielectric_saturation != 0);
    const Scalar eps_ion = scalar_constant<Scalar>(8.0);
    Scalar f_mix = scalar_constant<Scalar>(0.0);
    for (int i = 0; i < static_cast<int>(x.size()); ++i) {
        Scalar f_i = scalar_constant<Scalar>(1.0);
        if (!is_ion_species(cppargs, i) && cppargs.f_solv.size() > static_cast<size_t>(i)) {
            f_i = scalar_component_parameter_cpp(
                component_target_kind,
                component_target_index,
                i,
                cppargs.f_solv[i],
                component_target_kind == kGenericTargetFSolvLocal ? component_target_value : nullptr
            );
        }
        f_mix += x[i] * f_i;
    }

    Scalar sum_bracket = scalar_constant<Scalar>(0.0);
    for (int i = 0; i < static_cast<int>(x.size()); ++i) {
        if (!is_ion_species(cppargs, i)) {
            continue;
        }
        Scalar sigma_i = scalar_component_parameter_cpp(
            component_target_kind,
            component_target_index,
            i,
            cppargs.s[i],
            component_target_kind == kGenericTargetSLocal ? component_target_value : nullptr
        );
        Scalar epsilon_i = scalar_component_parameter_cpp(
            component_target_kind,
            component_target_index,
            i,
            cppargs.e[i],
            component_target_kind == kGenericTargetELocal ? component_target_value : nullptr
        );
        Scalar d_born_i = ion_born_radius_scalar_cpp(
            i,
            t,
            cppargs,
            sigma_i,
            epsilon_i,
            component_target_kind,
            component_target_index,
            component_target_value
        );
        const double absz = std::abs(cppargs.z[i]);
        const double z2 = cppargs.z[i] * cppargs.z[i];
        Scalar delta_di = use_ssm ? ((f_mix - 1.0) * d_born_i / absz) : scalar_constant<Scalar>(0.0);
        Scalar D_i = d_born_i + delta_di;
        if (scalar_value(D_i) <= 0.0) {
            throw ValueError("Born model generated a non-positive d_born + Delta d.");
        }
        Scalar invD = 1.0 / D_i;
        Scalar gap = 1.0 / d_born_i - invD;
        Scalar base_term = (1.0 - 1.0 / eps) * invD;
        Scalar ds_term = use_ds ? ((1.0 - 1.0 / eps_ion) * gap) : scalar_constant<Scalar>(0.0);
        sum_bracket += x[i] * z2 * (base_term + ds_term);
    }
    Scalar Kborn = scalar_constant<Scalar>(E_CHRG * E_CHRG / (4.0 * PI * kb * perm_vac)) / t;
    return -Kborn * sum_bracket;
}

inline double ares_born_cpp(double t, const BornIntermediateState &born_state) {
    if (born_state.model == 0) {
        return 0.0;
    }
    if (born_state.model == 1) {
        return -E_CHRG * E_CHRG / (4.0 * PI * kb * t * perm_vac) * (1.0 - 1.0 / born_state.eps_value) * born_state.charge_radius_sum;
    }
    if (born_state.model == 2) {
        const double Kborn = E_CHRG * E_CHRG / (4.0 * PI * kb * t * perm_vac);
        return -Kborn * born_state.shell.sum_bracket;
    }
    throw ValueError("Unknown born_model. Supported values are 0, 1, 2.");
}

template <typename Scalar, typename TemperatureScalar>
static AresContributionsScalar<Scalar> ares_contributions_scalar_cpp(
    const TemperatureScalar &t,
    const Scalar &rho,
    const vector<Scalar> &x,
    const add_args &cppargs,
    int k_override_index = -1,
    const Scalar *k_override_value = nullptr,
    int l_override_index = -1,
    const Scalar *l_override_value = nullptr,
    int component_target_kind = -1,
    int component_target_index = -1,
    const Scalar *component_target_value = nullptr
) {
    AresContributionsScalar<Scalar> out;
    MixtureStateScalar<Scalar> thermo = mixture_state_scalar_cpp(
        t,
        rho,
        x,
        cppargs,
        k_override_index,
        k_override_value,
        l_override_index,
        l_override_value,
        component_target_kind,
        component_target_index,
        component_target_value
    );
    HardChainStateScalar<Scalar> hc_state = hard_chain_state_scalar_cpp(thermo, x, cppargs);
    DispersionPolynomialStateScalar<Scalar> dispersion = dispersion_polynomials_scalar_cpp(thermo.m_avg, hc_state.eta);
    out.hc = ares_hc_scalar_cpp(thermo, hc_state, x, cppargs);
    out.disp = ares_disp_scalar_cpp(thermo, dispersion);
    out.assoc = ares_assoc_scalar_cpp(x, cppargs);
    out.ion = ares_ion_scalar_cpp(
        t,
        thermo,
        x,
        cppargs,
        component_target_kind,
        component_target_index,
        component_target_value
    );
    out.born = ares_born_scalar_cpp(t, x, cppargs, component_target_kind, component_target_index, component_target_value);
    return out;
}

}  // namespace ares_detail
