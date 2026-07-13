#pragma once
#include "eos/residual/internal.h"
namespace residual_association_detail {
ares_detail::AssociationDensityResponse association_density_response_cppad_cpp(
    double t,
    double rho,
    const vector<double> &x,
    const ProviderParameterAccessV1<double> &cppargs
);
ares_detail::AssociationPhaseStateResponse association_phase_state_response_cppad_cpp(
    double t,
    double rho,
    const vector<double> &x,
    const ProviderParameterAccessV1<double> &cppargs
);
ares_detail::AssociationPhaseStateResponse association_phase_state_temperature_response_cppad_cpp(
    double t,
    double rho,
    const vector<double> &x,
    const ProviderParameterAccessV1<double> &cppargs
);

inline ares_detail::AssociationDensityResponse association_density_response_cppad_cpp(
    double t, double rho, const vector<double> &x, const add_args &cppargs
) {
    const LegacyAddArgsParameterAccessV1 access(cppargs);
    return association_density_response_cppad_cpp(t, rho, x, access);
}

inline ares_detail::AssociationPhaseStateResponse association_phase_state_response_cppad_cpp(
    double t, double rho, const vector<double> &x, const add_args &cppargs
) {
    const LegacyAddArgsParameterAccessV1 access(cppargs);
    return association_phase_state_response_cppad_cpp(t, rho, x, access);
}

inline ares_detail::AssociationPhaseStateResponse association_phase_state_temperature_response_cppad_cpp(
    double t, double rho, const vector<double> &x, const add_args &cppargs
) {
    const LegacyAddArgsParameterAccessV1 access(cppargs);
    return association_phase_state_temperature_response_cppad_cpp(t, rho, x, access);
}
}  // namespace residual_association_detail
