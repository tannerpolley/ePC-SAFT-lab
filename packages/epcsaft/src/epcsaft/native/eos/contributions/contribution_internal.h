#pragma once

#include "eos/core_internal.h"

namespace thermo_detail {

struct HardChainState {
    vector<double> zeta;
    vector<double> ghs;
    double eta = 0.0;
};

#ifdef EPCSAFT_HAS_CPPAD
struct CppADHardChainState {
    vector<CppADScalar> zeta;
    vector<CppADScalar> ghs;
    CppADScalar eta = make_cppad_scalar(0.0);
};
#endif

struct ContributionDadxResult {
    vector<double> dadx;
    double ares = 0.0;
    double z = 0.0;
    double sum_x_dadx = 0.0;
};

struct AssociationSolveDiagnostics {
    bool converged = false;
    int iteration_count = 0;
    int max_iterations = 0;
    double update_norm = std::numeric_limits<double>::infinity();
    double update_tolerance = 0.0;
    double residual_norm = std::numeric_limits<double>::infinity();
    double residual_tolerance = 0.0;
    double min_XA = std::numeric_limits<double>::infinity();
    double max_XA = -std::numeric_limits<double>::infinity();
    double relaxation_factor = 0.0;
    std::string relaxation_policy;
};

struct AssociationSolveResult {
    vector<double> XA;
    AssociationSolveDiagnostics diagnostics;
};

struct AssociationIntermediateState {
    bool active = false;
    AssociationSetup setup;
    vector<double> XA;
    vector<double> dXA_dt;
    vector<double> dXA_dx;
    AssociationSolveDiagnostics solve_diagnostics;
};

struct IonIntermediateState {
    bool active = false;
    DielectricState dielectric;
    double charge_square_sum = 0.0;
    double kappa = 0.0;
    vector<double> chi;
    vector<double> sigma_k;
    double chi_sum = 0.0;
    double sigma_sum = 0.0;
    vector<double> dkappa_dx;
    vector<double> dchi_sum_dx;
};

struct BornIntermediateState {
    int model = 0;
    double eps_value = 0.0;
    vector<double> deps_dx;
    double charge_radius_sum = 0.0;
    double charge_radius_sum_dt = 0.0;
    BornGeometryData shell;
};

}  // namespace thermo_detail

using thermo_detail::HardChainState;
#ifdef EPCSAFT_HAS_CPPAD
using thermo_detail::CppADHardChainState;
#endif
using thermo_detail::AssociationIntermediateState;
using thermo_detail::AssociationSolveDiagnostics;
using thermo_detail::AssociationSolveResult;
using thermo_detail::BornIntermediateState;
using thermo_detail::ContributionDadxResult;
using thermo_detail::IonIntermediateState;

HardChainState hard_chain_state_cpp(const MixtureState &thermo, const vector<double> &x, const ProviderParameterAccessV1<double> &cppargs);
#ifdef EPCSAFT_HAS_CPPAD
CppADHardChainState hard_chain_state_cppad_cpp(double den, const vector<double> &d, const vector<CppADScalar> &x, const ProviderParameterAccessV1<double> &cppargs);
#endif
double hs_contact_value_cpp(double pair_diameter, double zeta2, double zeta3);

AssociationIntermediateState association_intermediate_state_cpp(
    const MixtureState &thermo,
    const HardChainState &hc_state,
    double t,
    const vector<double> &x,
    const ProviderParameterAccessV1<double> &cppargs,
    bool include_dt,
    bool include_dx,
    const vector<double> *dghs_dt = nullptr
);
AssociationSolveResult association_site_fraction_solve_result_cpp(
    const vector<double> &delta_ij,
    double den,
    const vector<double> &x_assoc,
    int max_iterations = 100,
    double update_tolerance = 1.0e-15,
    double residual_tolerance = 1.0e-10
);

IonIntermediateState ion_intermediate_state_cpp(
    const MixtureState &thermo,
    double t,
    const vector<double> &x,
    const ProviderParameterAccessV1<double> &cppargs,
    bool include_dx
);

BornIntermediateState born_intermediate_state_cpp(
    double t,
    const vector<double> &x,
    const ProviderParameterAccessV1<double> &cppargs,
    bool include_dt
);

vector<double> dzeta_dt_cpp(const MixtureState &thermo, const vector<double> &x, const ProviderParameterAccessV1<double> &cppargs);
double hs_contact_density_derivative_cpp(double pair_diameter, double zeta2, double zeta3);
double hs_contact_time_derivative_cpp(
    double pair_diameter,
    double pair_diameter_dt,
    double zeta2,
    double zeta3,
    double dzeta2_dt,
    double dzeta3_dt
);
double hs_contact_composition_derivative_cpp(
    double pair_diameter,
    double zeta2,
    double zeta3,
    double dzeta2_dx,
    double dzeta3_dx
);
vector<double> hc_contact_time_terms_cpp(const MixtureState &thermo, const HardChainState &hc_state, const vector<double> &dzeta_dt);
double dadrho_hc_cpp(const MixtureState &thermo, const HardChainState &hc_state, const vector<double> &x, const ProviderParameterAccessV1<double> &cppargs);
double dadt_hc_cpp(
    const MixtureState &thermo,
    const HardChainState &hc_state,
    const vector<double> &dzeta_dt,
    const vector<double> &x,
    const ProviderParameterAccessV1<double> &cppargs
);
ContributionDadxResult dadx_hc_cpp(
    const MixtureState &thermo,
    const HardChainState &hc_state,
    double t,
    double rho,
    const vector<double> &x,
    const ProviderParameterAccessV1<double> &cppargs
);

double dadrho_disp_cpp(const MixtureState &thermo, const HardChainState &hc_state, const DispersionPolynomialState &dispersion);
double dadt_disp_cpp(const MixtureState &thermo, double deta_dt, double t, const DispersionPolynomialState &dispersion);
ContributionDadxResult dadx_disp_cpp(
    const MixtureState &thermo,
    const HardChainState &hc_state,
    const DispersionPolynomialState &dispersion,
    double t,
    double rho,
    const vector<double> &x,
    const ProviderParameterAccessV1<double> &cppargs
);

double dadrho_assoc_cpp(
    const MixtureState &thermo,
    const HardChainState &hc_state,
    const AssociationIntermediateState &assoc_state,
    const vector<double> &x,
    const ProviderParameterAccessV1<double> &cppargs,
    double t
);
double dadt_assoc_cpp(const AssociationIntermediateState &assoc_state, const vector<double> &x);
ContributionDadxResult dadx_assoc_cpp(
    const MixtureState &thermo,
    const HardChainState &hc_state,
    const AssociationIntermediateState &assoc_state,
    double t,
    double rho,
    const vector<double> &x,
    const ProviderParameterAccessV1<double> &cppargs
);

double dadrho_ion_cpp(double t, const IonIntermediateState &ion_state);
double dadt_ion_cpp(const IonIntermediateState &ion_state, double t, const vector<double> &x, const ProviderParameterAccessV1<double> &cppargs);
ContributionDadxResult dadx_ion_cpp(
    const IonIntermediateState &ion_state,
    double t,
    double rho,
    const vector<double> &x,
    const ProviderParameterAccessV1<double> &cppargs
);

double dadrho_born_cpp();
double dadt_born_cpp(double t, const BornIntermediateState &born_state);
ContributionDadxResult dadx_born_cpp(
    const BornIntermediateState &born_state,
    double t,
    double rho,
    const vector<double> &x,
    const ProviderParameterAccessV1<double> &cppargs
);

vector<double> contribution_dadx_cppad_cpp(
    AresContributionKind kind,
    double t,
    double rho,
    const vector<double> &x,
    const ProviderParameterAccessV1<double> &cppargs
);
