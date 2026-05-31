#include "eos/properties/residual_helmholtz_internal.h"
double ares_contribution_value_cpp(const AresContributions &terms, AresContributionKind kind) {
    switch (kind) {
        case AresContributionKind::HC:
            return terms.hc;
        case AresContributionKind::DISP:
            return terms.disp;
        case AresContributionKind::ASSOC:
            return terms.assoc;
        case AresContributionKind::ION:
            return terms.ion;
        case AresContributionKind::BORN:
            return terms.born;
    }
    throw ValueError("Unknown AresContributionKind.");
}

// EqID: ares_total
AresContributions ares_contributions_cpp(double t, double rho, const vector<double> &x, const add_args &cppargs) {
    AresContributions out;
    MixtureState thermo = mixture_state_cpp(t, rho, x, cppargs, false);
    HardChainState hc_state = hard_chain_state_cpp(thermo, x, cppargs);
    DispersionPolynomialState dispersion = dispersion_polynomials_cpp(thermo.m_avg, hc_state.eta);
    AssociationIntermediateState assoc_state = association_intermediate_state_cpp(thermo, hc_state, t, x, cppargs, false, false);
    IonIntermediateState ion_state = ion_intermediate_state_cpp(thermo, t, x, cppargs, false);
    BornIntermediateState born_state = born_intermediate_state_cpp(t, x, cppargs, false);

    out.hc = ares_detail::ares_hc_cpp(thermo, hc_state, x, cppargs);
    out.disp = ares_detail::ares_disp_cpp(thermo, dispersion);
    out.assoc = ares_detail::ares_assoc_cpp(assoc_state, x);
    out.ion = ares_detail::ares_ion_cpp(t, ion_state);
    out.born = ares_detail::ares_born_cpp(t, born_state);
    return out;
}

ScalarContributionTerms residual_helmholtz_result_cpp(double t, double rho, vector<double> x, const add_args &cppargs) {
    AresContributions contributions = ares_contributions_cpp(t, rho, x, cppargs);
    double ares = contributions.hc + contributions.disp + contributions.assoc + contributions.ion + contributions.born;
    return make_scalar_terms(
        contributions.hc,
        contributions.disp,
        contributions.assoc,
        contributions.ion,
        contributions.born,
        ares
    );
}

double ares_cpp(double t, double rho, vector<double> x, const add_args &cppargs) {
    AresContributions contributions = ares_contributions_cpp(t, rho, x, cppargs);
    return contributions.hc + contributions.disp + contributions.assoc + contributions.ion + contributions.born;
}

epcsaft::native::cppad_support::CppADDerivativeResult cppad_eos_contribution_derivatives_cpp(
    double t,
    double rho,
    const vector<double> &x,
    const add_args &cppargs
) {
    using CppADScalar = CppAD::AD<double>;
    if (!cppargs.assoc_num.empty()) {
        for (int sites : cppargs.assoc_num) {
            if (sites > 0) {
                throw ValueError("unsupported: CppAD association recording requires implicit site-fraction sensitivities.");
            }
        }
    }
    int ncomp = static_cast<int>(x.size());
    std::vector<CppADScalar> ax(ncomp);
    for (int i = 0; i < ncomp; ++i) {
        ax[i] = x[i];
    }
    CppAD::Independent(ax);

    CppADScalar arho = rho;
    auto contributions = ares_detail::ares_contributions_scalar_cpp(t, arho, ax, cppargs);
    std::vector<CppADScalar> ay(6);
    ay[0] = contributions.hc;
    ay[1] = contributions.disp;
    ay[2] = contributions.assoc;
    ay[3] = contributions.ion;
    ay[4] = contributions.born;
    ay[5] = contributions.hc + contributions.disp + contributions.assoc + contributions.ion + contributions.born;

    CppAD::ADFun<double> function(ax, ay);
    std::vector<double> point(x.begin(), x.end());
    auto value = function.Forward(0, point);
    auto jacobian = function.Jacobian(point);

    epcsaft::native::cppad_support::CppADDerivativeResult result;
    result.supported = true;
    result.backend = "cppad";
    result.message = "CppAD EOS contribution composition derivatives available";
    result.value = std::move(value);
    result.jacobian_row_major = std::move(jacobian);
    result.outputs = {"hc", "disp", "assoc", "ion", "born", "total"};
    result.variables.reserve(static_cast<size_t>(ncomp));
    for (int i = 0; i < ncomp; ++i) {
        result.variables.push_back("x_" + std::to_string(i));
    }
    result.rows = 6;
    result.cols = ncomp;
    return result;
}
