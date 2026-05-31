#include "eos/residual/internal.h"

#include "eos/derivatives/backend_labels.h"

#include <utility>
#include <vector>

DadrhoResult dadrho_result_cpp(double t, double rho, vector<double> x, const add_args &cppargs) {
    MixtureState thermo = mixture_state_cpp(t, rho, x, cppargs, false);
    HardChainState hc_state = hard_chain_state_cpp(thermo, x, cppargs);
    DispersionPolynomialState dispersion = dispersion_polynomials_cpp(thermo.m_avg, hc_state.eta);
    AssociationIntermediateState assoc_state = association_intermediate_state_cpp(
        thermo,
        hc_state,
        t,
        x,
        cppargs,
        false,
        false
    );
    IonIntermediateState ion_state = ion_intermediate_state_cpp(thermo, t, x, cppargs, false);

    double hc = dadrho_hc_cpp(thermo, hc_state, x, cppargs);
    double disp = dadrho_disp_cpp(thermo, hc_state, dispersion);
    double assoc = dadrho_assoc_cpp(thermo, hc_state, assoc_state, x, cppargs, t);
    double ion = dadrho_ion_cpp(t, ion_state);
    double born = dadrho_born_cpp();
    double total = hc + disp + assoc + ion + born;

    ScalarContributionTerms raw_terms = make_scalar_terms(hc, disp, assoc, ion, born, total);
    DadrhoResult result;
    result.raw = raw_terms;
    result.terms = normalized_dadrho_terms_cpp(raw_terms);
    return result;
}

// EqID: dares_dT
ScalarContributionTerms temperature_derivative_residual_helmholtz_result_cpp(
    double t,
    double rho,
    vector<double> x,
    const add_args &cppargs
) {
    MixtureState thermo = mixture_state_cpp(t, rho, x, cppargs, true);
    HardChainState hc_state = hard_chain_state_cpp(thermo, x, cppargs);
    vector<double> dzeta_dt = dzeta_dt_cpp(thermo, x, cppargs);
    vector<double> dghs_dt = hc_contact_time_terms_cpp(thermo, hc_state, dzeta_dt);
    DispersionPolynomialState dispersion = dispersion_polynomials_cpp(thermo.m_avg, hc_state.eta);
    AssociationIntermediateState assoc_state = association_intermediate_state_cpp(
        thermo,
        hc_state,
        t,
        x,
        cppargs,
        true,
        false,
        &dghs_dt
    );
    IonIntermediateState ion_state = ion_intermediate_state_cpp(thermo, t, x, cppargs, false);
    BornIntermediateState born_state = born_intermediate_state_cpp(t, x, cppargs, true);

    double hc = dadt_hc_cpp(thermo, hc_state, dzeta_dt, x, cppargs);
    double disp = dadt_disp_cpp(thermo, dzeta_dt[3], t, dispersion);
    double assoc = dadt_assoc_cpp(assoc_state, x);
    double ion = dadt_ion_cpp(ion_state, t, x, cppargs);
    double born = dadt_born_cpp(t, born_state);
    double total = hc + disp + assoc + ion + born;
    return make_scalar_terms(hc, disp, assoc, ion, born, total);
}

double dadt_cpp(double t, double rho, vector<double> x, const add_args &cppargs) {
    return temperature_derivative_residual_helmholtz_result_cpp(t, rho, std::move(x), cppargs).total;
}

CompositionContributionResult composition_derivative_residual_helmholtz_result_cpp(
    double t,
    double rho,
    vector<double> x,
    const add_args &cppargs
) {
    int ncomp = static_cast<int>(x.size());
    MixtureState thermo = mixture_state_cpp(t, rho, x, cppargs, false);
    HardChainState hc_state = hard_chain_state_cpp(thermo, x, cppargs);
    DadrhoResult dadrho_result = dadrho_result_cpp(t, rho, x, cppargs);
    const ScalarContributionTerms &z_raw_terms = dadrho_result.raw;
    ScalarContributionTerms z_terms = compressibility_terms_from_dadrho_cpp(dadrho_result);

    DispersionPolynomialState dispersion = dispersion_polynomials_cpp(thermo.m_avg, hc_state.eta);
    AssociationIntermediateState assoc_state = association_intermediate_state_cpp(
        thermo,
        hc_state,
        t,
        x,
        cppargs,
        false,
        false
    );
    IonIntermediateState ion_state = ion_intermediate_state_cpp(thermo, t, x, cppargs, true);
    BornIntermediateState born_state = born_intermediate_state_cpp(t, x, cppargs, false);

    ContributionDadxResult hc = dadx_hc_cpp(thermo, hc_state, t, rho, x, cppargs);
    ContributionDadxResult disp = dadx_disp_cpp(thermo, hc_state, dispersion, t, rho, x, cppargs);
    ContributionDadxResult assoc = dadx_assoc_cpp(thermo, hc_state, assoc_state, t, rho, x, cppargs);
    ContributionDadxResult ion = dadx_ion_cpp(ion_state, t, rho, x, cppargs);
    ContributionDadxResult born = dadx_born_cpp(born_state, t, rho, x, cppargs);

    CompositionContributionResult result;
    result.dadx = make_vector_terms(hc.dadx, disp.dadx, assoc.dadx, ion.dadx, born.dadx, vector<double>());
    result.ares = make_scalar_terms(
        hc.ares,
        disp.ares,
        assoc.ares,
        ion.ares,
        born.ares,
        hc.ares + disp.ares + assoc.ares + ion.ares + born.ares
    );
    result.sum_x_dadx = make_scalar_terms(
        hc.sum_x_dadx,
        disp.sum_x_dadx,
        assoc.sum_x_dadx,
        ion.sum_x_dadx,
        born.sum_x_dadx,
        hc.sum_x_dadx + disp.sum_x_dadx + assoc.sum_x_dadx + ion.sum_x_dadx + born.sum_x_dadx
    );
    result.z_raw = z_raw_terms;
    result.z = z_terms;

    vector<double> total(ncomp, 0.0);
    for (int i = 0; i < ncomp; ++i) {
        total[i] = hc.dadx[i] + disp.dadx[i] + assoc.dadx[i] + ion.dadx[i] + born.dadx[i];
    }
    result.dadx.total = total;
    result.derivative_backend = derivative_backend_detail::composition_derivative_backend_map(cppargs);
    result.derivative_available = true;
    for (const auto& item : result.derivative_backend) {
        if (item.second == "unsupported") {
            result.derivative_available = false;
            break;
        }
    }
    return result;
}
