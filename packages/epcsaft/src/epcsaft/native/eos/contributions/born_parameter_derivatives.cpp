#include "eos/contributions/contribution_internal.h"

namespace {

constexpr int kTargetDBorn = 5;
constexpr int kTargetFSolv = 9;

static void initialize_supported_result(BornDerivativeResult& result, int ncomp)
{
    result.supported = true;
    result.backend = "cppad";
    result.message = "CppAD Born parameter derivatives are available for d_born and f_solv.";
    result.ncomp = ncomp;
    result.a_born_d_d_born.assign(ncomp, 0.0);
    result.a_born_d_f_solv.assign(ncomp, 0.0);
    result.mu_res_d_d_born_row_major.assign(ncomp * ncomp, 0.0);
    result.mu_res_d_f_solv_row_major.assign(ncomp * ncomp, 0.0);
    result.lnfug_d_d_born_row_major.assign(ncomp * ncomp, 0.0);
    result.lnfug_d_f_solv_row_major.assign(ncomp * ncomp, 0.0);
    result.lngamma_d_d_born_row_major.assign(ncomp * ncomp, 0.0);
    result.lngamma_d_f_solv_row_major.assign(ncomp * ncomp, 0.0);
}

static void copy_component_parameter_column(
    const NeutralBinaryKijPhaseDerivatives& derivative,
    int parameter_index,
    int ncomp,
    vector<double>& ares_derivatives,
    vector<double>& mu_row_major,
    vector<double>& lnfug_row_major,
    vector<double>& lngamma_row_major
) {
    ares_derivatives[static_cast<size_t>(parameter_index)] = derivative.dares_dk_fixed_rho;
    if (static_cast<int>(derivative.dmu_res_dk_fixed_rho.size()) != ncomp
        || static_cast<int>(derivative.dlnphi_dk_fixed_rho.size()) != ncomp) {
        throw ValueError("Native Born parameter derivative payload has inconsistent component dimensions.");
    }
    for (int i = 0; i < ncomp; ++i) {
        const size_t offset = static_cast<size_t>(i * ncomp + parameter_index);
        mu_row_major[offset] = derivative.dmu_res_dk_fixed_rho[static_cast<size_t>(i)];
        lnfug_row_major[offset] = derivative.dlnphi_dk_fixed_rho[static_cast<size_t>(i)];
        lngamma_row_major[offset] = derivative.dmu_res_dk_fixed_rho[static_cast<size_t>(i)];
    }
}

}  // namespace

BornDerivativeResult born_parameter_derivatives_cpp(
    double t,
    double rho,
    int phase,
    vector<double> x,
    const add_args &cppargs
) {
    const int ncomp = static_cast<int>(x.size());
    BornDerivativeResult result;

    if (phase != 0) {
        throw ValueError("unsupported: Born parameter derivatives are liquid-electrolyte only.");
    }
    if (cppargs.z.empty() || cppargs.born_model != 2) {
        throw ValueError("unsupported: Born parameter derivatives require the canonical enabled Born model.");
    }
    if (cppargs.d_born.size() != x.size() || cppargs.f_solv.size() != x.size()) {
        throw ValueError("unsupported: Born parameter derivatives require aligned d_born and f_solv values.");
    }
    if (cppargs.born_eps_mode == 1) {
        throw ValueError("unsupported: Born parameter derivatives currently use mixture dielectric routing.");
    }

    initialize_supported_result(result, ncomp);
    for (int parameter_index = 0; parameter_index < ncomp; ++parameter_index) {
        const NeutralBinaryKijPhaseDerivatives d_born = generic_component_parameter_phase_derivatives_cpp(
            t,
            rho,
            x,
            cppargs,
            kTargetDBorn,
            parameter_index
        );
        copy_component_parameter_column(
            d_born,
            parameter_index,
            ncomp,
            result.a_born_d_d_born,
            result.mu_res_d_d_born_row_major,
            result.lnfug_d_d_born_row_major,
            result.lngamma_d_d_born_row_major
        );

        const NeutralBinaryKijPhaseDerivatives f_solv = generic_component_parameter_phase_derivatives_cpp(
            t,
            rho,
            x,
            cppargs,
            kTargetFSolv,
            parameter_index
        );
        copy_component_parameter_column(
            f_solv,
            parameter_index,
            ncomp,
            result.a_born_d_f_solv,
            result.mu_res_d_f_solv_row_major,
            result.lnfug_d_f_solv_row_major,
            result.lngamma_d_f_solv_row_major
        );
    }
    return result;
}
