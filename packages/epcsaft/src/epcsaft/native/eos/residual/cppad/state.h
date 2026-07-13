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
    const ProviderParameterAccessV1<double> &cppargs,
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
    const ProviderParameterAccessV1<double> &cppargs,
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
    const ProviderParameterAccessV1<double> &cppargs,
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

}  // namespace ares_detail
