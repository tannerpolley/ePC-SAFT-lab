#pragma once
#include "eos/residual/cppad/hard_chain_dispersion.h"
#include "eos/residual/cppad/association.h"
#include "eos/residual/cppad/ionic.h"
#include "eos/residual/cppad/born.h"

namespace ares_detail {
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
