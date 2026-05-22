#include "contribution_internal.h"

#include <sstream>

using thermo_detail::AssociationIntermediateState;
using thermo_detail::AssociationSolveDiagnostics;
using thermo_detail::AssociationSolveResult;
using thermo_detail::AssociationSetup;
using thermo_detail::ContributionDadxResult;
using thermo_detail::HardChainState;
using thermo_detail::MixtureState;
using thermo_detail::parameter_setup_detail::association_volume_cpp;
using thermo_detail::parameter_setup_detail::pair_diameter_cpp;

namespace assoc_detail {

static constexpr int kDefaultMaxIterations = 100;
static constexpr double kDefaultUpdateTolerance = 1.0e-15;
static constexpr double kDefaultResidualTolerance = 1.0e-10;
static constexpr double kRelaxationFactor = 0.5;
static constexpr double kSiteFractionUpperTolerance = 1.0e-12;
static const char *kRelaxationPolicy = "fixed_under_relaxation";

// EqID: x_assoc_site
static vector<double> association_site_fractions_cpp(vector<double> XA_guess, vector<double> delta_ij, double den, vector<double> x) {
    int num_sites = static_cast<int>(XA_guess.size());
    vector<double> XA = XA_guess;

    int idxij = -1;
    for (int i = 0; i < num_sites; ++i) {
        double summ = 0.0;
        for (int j = 0; j < num_sites; ++j) {
            idxij += 1;
            summ += den * x[j] * XA_guess[j] * delta_ij[idxij];
        }
        XA[i] = 1.0 / (1.0 + summ);
    }

    return XA;
}

static double initial_site_fraction_cpp(double self_delta, double den) {
    if (!std::isfinite(self_delta)) {
        throw ValueError("Association site-fraction solve received non-finite association strength.");
    }
    if (self_delta <= 0.0) {
        return 1.0;
    }
    double argument = 1.0 + 8.0 * den * self_delta;
    if (!std::isfinite(argument) || argument < 0.0) {
        throw ValueError("Association site-fraction solve generated a non-finite initial site fraction.");
    }
    double root = std::sqrt(argument);
    if (!std::isfinite(root)) {
        throw ValueError("Association site-fraction solve generated a non-finite initial site fraction.");
    }
    return 2.0 / (1.0 + root);
}

static double association_mass_action_residual_norm_cpp(
    const vector<double> &XA,
    const vector<double> &delta_ij,
    double den,
    const vector<double> &x_assoc
) {
    int num_sites = static_cast<int>(XA.size());
    double residual_norm = 0.0;
    int idxij = 0;
    for (int i = 0; i < num_sites; ++i) {
        double summ = 0.0;
        for (int j = 0; j < num_sites; ++j) {
            double delta = delta_ij[idxij];
            if (!std::isfinite(delta) || !std::isfinite(XA[j]) || !std::isfinite(x_assoc[j])) {
                return std::numeric_limits<double>::infinity();
            }
            summ += den * x_assoc[j] * XA[j] * delta;
            ++idxij;
        }
        double residual = XA[i] * (1.0 + summ) - 1.0;
        if (!std::isfinite(residual)) {
            return std::numeric_limits<double>::infinity();
        }
        residual_norm = std::max(residual_norm, std::abs(residual));
    }
    return residual_norm;
}

static void update_site_fraction_bounds_cpp(const vector<double> &XA, AssociationSolveDiagnostics &diagnostics) {
    diagnostics.min_XA = std::numeric_limits<double>::infinity();
    diagnostics.max_XA = -std::numeric_limits<double>::infinity();
    for (double value : XA) {
        diagnostics.min_XA = std::min(diagnostics.min_XA, value);
        diagnostics.max_XA = std::max(diagnostics.max_XA, value);
    }
    if (XA.empty()) {
        diagnostics.min_XA = 0.0;
        diagnostics.max_XA = 0.0;
    }
}

static bool site_fractions_are_valid_cpp(const AssociationSolveDiagnostics &diagnostics) {
    return std::isfinite(diagnostics.min_XA)
        && std::isfinite(diagnostics.max_XA)
        && diagnostics.min_XA > 0.0
        && diagnostics.max_XA <= 1.0 + kSiteFractionUpperTolerance;
}

static std::string association_solve_diagnostics_message_cpp(const AssociationSolveDiagnostics &diagnostics) {
    std::ostringstream msg;
    msg << std::boolalpha
        << "association site-fraction solve did not converge: "
        << "converged=" << diagnostics.converged
        << "; iteration_count=" << diagnostics.iteration_count
        << "; max_iterations=" << diagnostics.max_iterations
        << "; update_norm=" << diagnostics.update_norm
        << "; update_tolerance=" << diagnostics.update_tolerance
        << "; residual_norm=" << diagnostics.residual_norm
        << "; residual_tolerance=" << diagnostics.residual_tolerance
        << "; min_XA=" << diagnostics.min_XA
        << "; max_XA=" << diagnostics.max_XA
        << "; relaxation_factor=" << diagnostics.relaxation_factor
        << "; relaxation_policy=" << diagnostics.relaxation_policy;
    return msg.str();
}

static AssociationSolveResult solve_association_site_fractions_cpp(
    const vector<double> &delta_ij,
    double den,
    const vector<double> &x_assoc,
    int max_iterations,
    double update_tolerance,
    double residual_tolerance
) {
    int num_sites = static_cast<int>(x_assoc.size());
    if (num_sites == 0) {
        AssociationSolveResult empty;
        empty.diagnostics.converged = true;
        empty.diagnostics.max_iterations = max_iterations;
        empty.diagnostics.update_norm = 0.0;
        empty.diagnostics.update_tolerance = update_tolerance;
        empty.diagnostics.residual_norm = 0.0;
        empty.diagnostics.residual_tolerance = residual_tolerance;
        empty.diagnostics.min_XA = 0.0;
        empty.diagnostics.max_XA = 0.0;
        empty.diagnostics.relaxation_factor = kRelaxationFactor;
        empty.diagnostics.relaxation_policy = kRelaxationPolicy;
        return empty;
    }
    if (static_cast<int>(delta_ij.size()) != num_sites * num_sites) {
        throw ValueError("Association site-fraction solve requires a square delta_ij matrix.");
    }
    if (!std::isfinite(den) || den <= 0.0) {
        throw ValueError("Association site-fraction solve requires a positive finite molar density.");
    }
    if (max_iterations <= 0) {
        throw ValueError("Association site-fraction solve requires max_iterations > 0.");
    }
    if (!std::isfinite(update_tolerance) || update_tolerance < 0.0) {
        throw ValueError("Association site-fraction solve requires a finite non-negative update tolerance.");
    }
    if (!std::isfinite(residual_tolerance) || residual_tolerance < 0.0) {
        throw ValueError("Association site-fraction solve requires a finite non-negative residual tolerance.");
    }
    for (double value : x_assoc) {
        if (!std::isfinite(value) || value < 0.0) {
            throw ValueError("Association site-fraction solve requires finite non-negative site mole fractions.");
        }
    }

    AssociationSolveResult result;
    AssociationSolveDiagnostics &diagnostics = result.diagnostics;
    diagnostics.max_iterations = max_iterations;
    diagnostics.update_tolerance = update_tolerance;
    diagnostics.residual_tolerance = residual_tolerance;
    diagnostics.relaxation_factor = kRelaxationFactor;
    diagnostics.relaxation_policy = kRelaxationPolicy;

    vector<double> XA(num_sites, 0.0);
    for (int i = 0; i < num_sites; ++i) {
        XA[i] = initial_site_fraction_cpp(delta_ij[i * num_sites + i], den);
    }

    vector<double> XA_old = XA;
    while (diagnostics.iteration_count < max_iterations) {
        diagnostics.iteration_count += 1;
        XA = association_site_fractions_cpp(XA_old, delta_ij, den, x_assoc);
        diagnostics.update_norm = 0.0;
        for (int i = 0; i < num_sites; ++i) {
            diagnostics.update_norm += std::abs(XA[i] - XA_old[i]);
        }
        for (int i = 0; i < num_sites; ++i) {
            XA_old[i] = kRelaxationFactor * (XA[i] + XA_old[i]);
        }
        update_site_fraction_bounds_cpp(XA, diagnostics);
        diagnostics.residual_norm = association_mass_action_residual_norm_cpp(XA, delta_ij, den, x_assoc);
        bool converged_before_iteration_limit = diagnostics.iteration_count < diagnostics.max_iterations;
        diagnostics.converged = converged_before_iteration_limit
            && diagnostics.update_norm <= diagnostics.update_tolerance
            && diagnostics.residual_norm <= diagnostics.residual_tolerance
            && site_fractions_are_valid_cpp(diagnostics);
        if (diagnostics.converged) {
            result.XA = XA;
            return result;
        }
    }

    result.XA = XA;
    throw SolutionError(association_solve_diagnostics_message_cpp(diagnostics));
}

// EqID: dx_assoc_drho
static vector<double> association_site_fraction_dt_cpp(vector<double> delta_ij, double den, vector<double> XA, vector<double> ddelta_dt, vector<double> x) {
    int num_sites = static_cast<int>(XA.size());
    Eigen::MatrixXd B = Eigen::MatrixXd::Zero(num_sites, 1);
    Eigen::MatrixXd A = Eigen::MatrixXd::Zero(num_sites, num_sites);

    int ij = 0;
    for (int i = 0; i < num_sites; ++i) {
        double summ = 0.0;
        for (int j = 0; j < num_sites; ++j) {
            B(i) -= x[j] * XA[j] * ddelta_dt[ij];
            A(i, j) = x[j] * delta_ij[ij];
            summ += x[j] * XA[j] * delta_ij[ij];
            ij += 1;
        }
        A(i, i) = std::pow(1.0 + den * summ, 2.0) / den;
    }

    Eigen::MatrixXd solution = A.lu().solve(B);
    vector<double> dXA_dt(num_sites);
    for (int i = 0; i < num_sites; ++i) {
        dXA_dt[i] = solution(i);
    }
    return dXA_dt;
}

// EqID: dx_assoc_dxk
static vector<double> association_site_fraction_dx_cpp(vector<int> assoc_num, vector<double> delta_ij, double den, vector<double> XA, vector<double> ddelta_dx, vector<double> x) {
    int num_sites = static_cast<int>(XA.size());
    int ncomp = static_cast<int>(assoc_num.size());
    Eigen::MatrixXd B(num_sites * ncomp, 1);
    Eigen::MatrixXd A = Eigen::MatrixXd::Zero(num_sites * ncomp, num_sites * ncomp);

    int idx1 = 0;
    int ij = 0;
    for (int i = 0; i < ncomp; ++i) {
        for (int j = 0; j < num_sites; ++j) {
            double sum1 = 0.0;
            for (int k = 0; k < num_sites; ++k) {
                sum1 += den * x[k] * (XA[k] * ddelta_dx[i * num_sites * num_sites + j * num_sites + k]);
                A(ij, i * num_sites + k) = XA[j] * XA[j] * den * x[k] * delta_ij[j * num_sites + k];
            }

            double sum2 = 0.0;
            for (int l = 0; l < assoc_num[i]; ++l) {
                sum2 += XA[idx1 + l] * delta_ij[idx1 * num_sites + l * num_sites + j];
            }

            A(ij, ij) = A(ij, ij) + 1.0;
            B(ij) = -XA[j] * XA[j] * (sum1 + sum2);
            ij += 1;
        }
        idx1 += assoc_num[i];
    }

    Eigen::MatrixXd solution = A.lu().solve(B);
    vector<double> dXA_dx(num_sites * ncomp);
    for (int i = 0; i < num_sites * ncomp; ++i) {
        dXA_dx[i] = solution(i);
    }
    return dXA_dx;
}

}  // namespace assoc_detail

AssociationSolveResult association_site_fraction_solve_result_cpp(
    const vector<double> &delta_ij,
    double den,
    const vector<double> &x_assoc,
    int max_iterations,
    double update_tolerance,
    double residual_tolerance
) {
    return assoc_detail::solve_association_site_fractions_cpp(
        delta_ij,
        den,
        x_assoc,
        max_iterations,
        update_tolerance,
        residual_tolerance
    );
}

// EqID: rho_j_assoc
// EqID: delta_assoc
AssociationSetup association_setup_cpp(const vector<double> &x, const add_args &cppargs, const vector<double> &s_ij, const vector<double> &ghs, double t) {
    int ncomp = static_cast<int>(x.size());
    AssociationSetup setup;
    setup.site_component_index.reserve(ncomp);
    setup.x_assoc.reserve(ncomp);

    for (std::vector<int>::const_iterator it = cppargs.assoc_num.begin(); it != cppargs.assoc_num.end(); ++it) {
        for (int i = 0; i < *it; ++i) {
            setup.site_component_index.push_back(static_cast<int>(it - cppargs.assoc_num.begin()));
            setup.x_assoc.push_back(x[setup.site_component_index.back()]);
        }
    }

    int num_sites = static_cast<int>(setup.site_component_index.size());
    setup.delta_ij.assign(static_cast<size_t>(num_sites * num_sites), 0.0);

    int idxa = 0;
    for (int i = 0; i < num_sites; ++i) {
        int comp_i = setup.site_component_index[i];
        for (int j = 0; j < num_sites; ++j) {
            int comp_j = setup.site_component_index[j];
            if (cppargs.assoc_matrix[idxa] != 0) {
                double eABij = 0.5 * (cppargs.e_assoc[comp_i] + cppargs.e_assoc[comp_j]);
                double volABij = association_volume_cpp(comp_i, comp_j, ncomp, s_ij, cppargs);
                setup.delta_ij[idxa] = ghs[comp_i * ncomp + comp_j] * (std::exp(eABij / t) - 1.0)
                    * std::pow(s_ij[comp_i * ncomp + comp_j], 3.0) * volABij;
            }
            ++idxa;
        }
    }

    return setup;
}

namespace assoc_detail {

// EqID: ddelta_assoc_drho
static vector<double> association_site_fraction_density_terms_cpp(
    const vector<double> &delta_ij,
    double den,
    const vector<double> &XA,
    const vector<double> &ddelta_weighted,
    const vector<double> &x_assoc
) {
    int num_sites = static_cast<int>(XA.size());
    Eigen::MatrixXd B = Eigen::MatrixXd::Zero(num_sites, 1);
    Eigen::MatrixXd A = Eigen::MatrixXd::Zero(num_sites, num_sites);

    int ij = 0;
    for (int i = 0; i < num_sites; ++i) {
        double summ = 0.0;
        for (int j = 0; j < num_sites; ++j) {
            B(i) -= x_assoc[j] * XA[j] * ddelta_weighted[ij];
            A(i, j) = x_assoc[j] * delta_ij[ij];
            summ += x_assoc[j] * XA[j] * delta_ij[ij];
            ++ij;
        }
        B(i) -= summ;
        A(i, i) = std::pow(1.0 + den * summ, 2.0) / den;
    }

    Eigen::MatrixXd solution = A.lu().solve(B);
    vector<double> dXA_weighted(num_sites, 0.0);
    for (int i = 0; i < num_sites; ++i) {
        dXA_weighted[i] = solution(i);
    }
    return dXA_weighted;
}

// EqID: ddelta_assoc_dxk
static vector<double> association_site_fraction_composition_terms_cpp(
    const vector<double> &delta_ij,
    double den,
    const vector<double> &XA,
    const vector<double> &ddelta_dx,
    const vector<int> &site_component_index,
    const vector<double> &x_assoc,
    int ncomp
) {
    int num_sites = static_cast<int>(XA.size());
    vector<double> dXA_dx(ncomp * num_sites, 0.0);

    for (int k = 0; k < ncomp; ++k) {
        Eigen::MatrixXd B = Eigen::MatrixXd::Zero(num_sites, 1);
        Eigen::MatrixXd A = Eigen::MatrixXd::Zero(num_sites, num_sites);

        int ij = 0;
        for (int i = 0; i < num_sites; ++i) {
            double direct_sum = 0.0;
            double delta_sum = 0.0;
            for (int j = 0; j < num_sites; ++j) {
                if (site_component_index[j] == k) {
                    direct_sum += XA[j] * delta_ij[ij];
                }
                delta_sum += x_assoc[j] * XA[j] * ddelta_dx[k * num_sites * num_sites + ij];
                A(i, j) = x_assoc[j] * delta_ij[ij];
                ++ij;
            }
            B(i) = -(direct_sum + delta_sum);
            A(i, i) += 1.0 / (den * XA[i] * XA[i]);
        }

        Eigen::MatrixXd solution = A.lu().solve(B);
        for (int i = 0; i < num_sites; ++i) {
            dXA_dx[k * num_sites + i] = solution(i);
        }
    }

    return dXA_dx;
}

}  // namespace assoc_detail

AssociationIntermediateState association_intermediate_state_cpp(
    const MixtureState &thermo,
    const HardChainState &hc_state,
    double t,
    const vector<double> &x,
    const add_args &cppargs,
    bool include_dt,
    bool include_dx,
    const vector<double> *dghs_dt
) {
    AssociationIntermediateState state;
    if (cppargs.e_assoc.empty()) {
        return state;
    }
    state.active = true;
    state.setup = association_setup_cpp(x, cppargs, thermo.s_ij, hc_state.ghs, t);
    const vector<int> &site_component_index = state.setup.site_component_index;
    const vector<double> &x_assoc = state.setup.x_assoc;
    const vector<double> &delta_ij = state.setup.delta_ij;
    int ncomp = static_cast<int>(x.size());
    int num_sites = static_cast<int>(site_component_index.size());

    AssociationSolveResult solve_result = association_site_fraction_solve_result_cpp(
        delta_ij,
        thermo.den,
        x_assoc,
        assoc_detail::kDefaultMaxIterations,
        assoc_detail::kDefaultUpdateTolerance,
        assoc_detail::kDefaultResidualTolerance
    );
    state.XA = solve_result.XA;
    state.solve_diagnostics = solve_result.diagnostics;

    if (include_dt) {
        vector<double> ddelta_dt(num_sites * num_sites, 0.0);
        if (dghs_dt == nullptr) {
            throw ValueError("Association temperature derivatives require externally provided hard-sphere contact time derivatives.");
        }

        for (int i = 0; i < num_sites; ++i) {
            for (int j = 0; j < num_sites; ++j) {
                if (cppargs.assoc_matrix[i * num_sites + j] != 0) {
                    double eABij = 0.5 * (cppargs.e_assoc[site_component_index[i]] + cppargs.e_assoc[site_component_index[j]]);
                    double volABij = association_volume_cpp(site_component_index[i], site_component_index[j], ncomp, thermo.s_ij, cppargs);
                    double pair_diameter = pair_diameter_cpp(
                        thermo.d[site_component_index[i]],
                        thermo.d[site_component_index[j]]
                    );
                    ddelta_dt[i * num_sites + j] = std::pow(pair_diameter, 3) * volABij * (
                        -eABij / std::pow(t, 2) * std::exp(eABij / t) * hc_state.ghs[site_component_index[i] * ncomp + site_component_index[j]]
                        + (*dghs_dt)[site_component_index[i] * ncomp + site_component_index[j]] * (std::exp(eABij / t) - 1.0)
                    );
                }
            }
        }

        state.dXA_dt = assoc_detail::association_site_fraction_dt_cpp(delta_ij, thermo.den, state.XA, ddelta_dt, x_assoc);
    }

    if (include_dx) {
        vector<double> ddelta_dx(num_sites * num_sites * ncomp, 0.0);
        int idx_ddelta = 0;
        for (int k = 0; k < ncomp; ++k) {
            for (int i = 0; i < num_sites; ++i) {
                for (int j = 0; j < num_sites; ++j) {
                    if (cppargs.assoc_matrix[i * num_sites + j] != 0) {
                        double pair_diameter = pair_diameter_cpp(thermo.d[site_component_index[i]], thermo.d[site_component_index[j]]);
                        double dzeta2_dx = PI / 6.0 * thermo.den * cppargs.m[k] * std::pow(thermo.d[k], 2);
                        double dzeta3_dx = PI / 6.0 * thermo.den * cppargs.m[k] * std::pow(thermo.d[k], 3);
                        double dghsd_dx = hs_contact_composition_derivative_cpp(
                            pair_diameter,
                            hc_state.zeta[2],
                            hc_state.zeta[3],
                            dzeta2_dx,
                            dzeta3_dx
                        );
                        double eABij = 0.5 * (cppargs.e_assoc[site_component_index[i]] + cppargs.e_assoc[site_component_index[j]]);
                        double volABij = association_volume_cpp(site_component_index[i], site_component_index[j], ncomp, thermo.s_ij, cppargs);
                        ddelta_dx[idx_ddelta] = dghsd_dx * (std::exp(eABij / t) - 1.0)
                            * std::pow(thermo.s_ij[site_component_index[i] * ncomp + site_component_index[j]], 3) * volABij;
                    }
                    ++idx_ddelta;
                }
            }
        }

        state.dXA_dx = assoc_detail::association_site_fraction_dx_cpp(cppargs.assoc_num, delta_ij, thermo.den, state.XA, ddelta_dx, x_assoc);
    }

    return state;
}

// EqID: assoc_ares_dadrho
double dadrho_assoc_cpp(
    const MixtureState &thermo,
    const HardChainState &hc_state,
    const AssociationIntermediateState &assoc_state,
    const vector<double> &x,
    const add_args &cppargs,
    double t
) {
    if (!assoc_state.active) {
        return 0.0;
    }

    const vector<int> &site_component_index = assoc_state.setup.site_component_index;
    const vector<double> &x_assoc = assoc_state.setup.x_assoc;
    const vector<double> &delta_ij = assoc_state.setup.delta_ij;
    int ncomp = static_cast<int>(x.size());
    int num_sites = static_cast<int>(site_component_index.size());
    vector<double> ddelta_weighted(num_sites * num_sites, 0.0);

    int ij = 0;
    for (int i = 0; i < num_sites; ++i) {
        int comp_i = site_component_index[i];
        for (int j = 0; j < num_sites; ++j) {
            int comp_j = site_component_index[j];
            if (cppargs.assoc_matrix[ij] != 0) {
                double pair_diameter = pair_diameter_cpp(thermo.d[comp_i], thermo.d[comp_j]);
                double eABij = 0.5 * (cppargs.e_assoc[comp_i] + cppargs.e_assoc[comp_j]);
                double volABij = association_volume_cpp(comp_i, comp_j, ncomp, thermo.s_ij, cppargs);
                ddelta_weighted[ij] = hs_contact_density_derivative_cpp(pair_diameter, hc_state.zeta[2], hc_state.zeta[3])
                    * (std::exp(eABij / t) - 1.0)
                    * std::pow(thermo.s_ij[comp_i * ncomp + comp_j], 3.0)
                    * volABij;
            }
            ++ij;
        }
    }

    vector<double> dXA_weighted = assoc_detail::association_site_fraction_density_terms_cpp(
        delta_ij, thermo.den, assoc_state.XA, ddelta_weighted, x_assoc
    );

    double value = 0.0;
    for (int i = 0; i < num_sites; ++i) {
        int component_index = site_component_index[i];
        value += x[component_index] * (1.0 / assoc_state.XA[i] - 0.5) * dXA_weighted[i];
    }
    return value;
}

// EqID: assoc_ares_dT
double dadt_assoc_cpp(const AssociationIntermediateState &assoc_state, const vector<double> &x) {
    if (!assoc_state.active) {
        return 0.0;
    }
    double value = 0.0;
    for (int i = 0; i < static_cast<int>(assoc_state.setup.site_component_index.size()); ++i) {
        value += x[assoc_state.setup.site_component_index[i]] * (1.0 / assoc_state.XA[i] - 0.5) * assoc_state.dXA_dt[i];
    }
    return value;
}

// EqID: assoc_ares_dxk
ContributionDadxResult dadx_assoc_cpp(const MixtureState &thermo, const HardChainState &hc_state, const AssociationIntermediateState &assoc_state, double t, double rho, const vector<double> &x, const add_args &cppargs) {
    int ncomp = static_cast<int>(x.size());
    ContributionDadxResult result;
    result.dadx.assign(ncomp, 0.0);
    if (!assoc_state.active) {
        return result;
    }

    int num_sites = static_cast<int>(assoc_state.setup.site_component_index.size());
    vector<double> ddelta_dx(num_sites * num_sites * ncomp, 0.0);
    int idx_ddelta = 0;
    for (int k = 0; k < ncomp; ++k) {
        for (int i = 0; i < num_sites; ++i) {
            int comp_i = assoc_state.setup.site_component_index[i];
            for (int j = 0; j < num_sites; ++j) {
                int comp_j = assoc_state.setup.site_component_index[j];
                if (cppargs.assoc_matrix[i * num_sites + j] != 0) {
                    double pair_diameter = pair_diameter_cpp(thermo.d[comp_i], thermo.d[comp_j]);
                    double dzeta2_dx = PI / 6.0 * thermo.den * cppargs.m[k] * std::pow(thermo.d[k], 2);
                    double dzeta3_dx = PI / 6.0 * thermo.den * cppargs.m[k] * std::pow(thermo.d[k], 3);
                    double dghsd_dx = hs_contact_composition_derivative_cpp(
                        pair_diameter,
                        hc_state.zeta[2],
                        hc_state.zeta[3],
                        dzeta2_dx,
                        dzeta3_dx
                    );
                    double eABij = 0.5 * (cppargs.e_assoc[comp_i] + cppargs.e_assoc[comp_j]);
                    double volABij = association_volume_cpp(comp_i, comp_j, ncomp, thermo.s_ij, cppargs);
                    ddelta_dx[idx_ddelta] = dghsd_dx * (std::exp(eABij / t) - 1.0)
                        * std::pow(thermo.s_ij[comp_i * ncomp + comp_j], 3.0) * volABij;
                }
                ++idx_ddelta;
            }
        }
    }

    vector<double> dXA_dx = assoc_detail::association_site_fraction_composition_terms_cpp(
        assoc_state.setup.delta_ij,
        thermo.den,
        assoc_state.XA,
        ddelta_dx,
        assoc_state.setup.site_component_index,
        assoc_state.setup.x_assoc,
        ncomp
    );

    for (int i = 0; i < ncomp; ++i) {
        for (int j = 0; j < num_sites; ++j) {
            result.dadx[i] += x[assoc_state.setup.site_component_index[j]] * dXA_dx[i * num_sites + j] * (1.0 / assoc_state.XA[j] - 0.5);
        }
    }

    for (int i = 0; i < num_sites; ++i) {
        int component_index = assoc_state.setup.site_component_index[i];
        result.dadx[component_index] += std::log(assoc_state.XA[i]) - 0.5 * assoc_state.XA[i] + 0.5;
        result.ares += x[component_index] * (std::log(assoc_state.XA[i]) - 0.5 * assoc_state.XA[i] + 0.5);
    }

    if (cppargs.assoc_dadx_diff_mode == 1) {
        throw ValueError("unsupported: association composition derivative backend is not enabled.");
    } else if (cppargs.assoc_dadx_diff_mode == 2) {
        result.dadx = contribution_dadx_cppad_cpp(AresContributionKind::ASSOC, t, rho, x, cppargs);
    }

    for (int i = 0; i < ncomp; ++i) {
        result.sum_x_dadx += x[i] * result.dadx[i];
    }
    return result;
}
