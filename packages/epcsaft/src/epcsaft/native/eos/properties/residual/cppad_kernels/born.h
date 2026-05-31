#pragma once
#include "eos/properties/residual/cppad_kernels/state.h"

namespace ares_detail {
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

}  // namespace ares_detail
