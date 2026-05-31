#pragma once
#include "eos/properties/residual/internal.h"
namespace residual_association_detail {
ares_detail::AssociationDensityResponse association_density_response_cppad_cpp(
    double t,
    double rho,
    const vector<double> &x,
    const add_args &cppargs
);
ares_detail::AssociationPhaseStateResponse association_phase_state_response_cppad_cpp(
    double t,
    double rho,
    const vector<double> &x,
    const add_args &cppargs
);
}  // namespace residual_association_detail
