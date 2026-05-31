#pragma once
#include "eos/properties/residual_scalar_state.h"

namespace ares_detail {
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

}  // namespace ares_detail
