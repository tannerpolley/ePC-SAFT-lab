#pragma once
#include "eos/residual/cppad/state.h"

namespace ares_detail {
// EqID: ares_assoc
template <typename Scalar>
static Scalar ares_assoc_scalar_cpp(const vector<Scalar> &x, const add_args &cppargs) {
    (void)x;
    if (!cppargs.assoc_num.empty()) {
        for (int sites : cppargs.assoc_num) {
            if (sites > 0) {
                throw ValueError("unsupported: CppAD association recording requires implicit site-fraction sensitivities.");
            }
        }
    }
    return scalar_constant<Scalar>(0.0);
}

inline double ares_assoc_cpp(const AssociationIntermediateState &assoc_state, const vector<double> &x) {
    if (!assoc_state.active) {
        return 0.0;
    }
    double value = 0.0;
    for (int i = 0; i < static_cast<int>(assoc_state.setup.site_component_index.size()); ++i) {
        int component_index = assoc_state.setup.site_component_index[i];
        value += x[component_index] * (std::log(assoc_state.XA[i]) - 0.5 * assoc_state.XA[i] + 0.5);
    }
    return value;
}

template <typename Scalar>
static Scalar hs_contact_density_derivative_scalar_cpp(const Scalar &pair_diameter, const Scalar &zeta2, const Scalar &zeta3) {
    return zeta3 / scalar_pow(1.0 - zeta3, 2.0)
        + pair_diameter * (
            3.0 * zeta2 / scalar_pow(1.0 - zeta3, 2.0)
            + 6.0 * zeta2 * zeta3 / scalar_pow(1.0 - zeta3, 3.0)
        )
        + scalar_pow(pair_diameter, 2.0) * (
            4.0 * zeta2 * zeta2 / scalar_pow(1.0 - zeta3, 3.0)
            + 6.0 * zeta2 * zeta2 * zeta3 / scalar_pow(1.0 - zeta3, 4.0)
        );
}

template <typename Scalar>
static Scalar hs_contact_composition_derivative_scalar_cpp(
    const Scalar &pair_diameter,
    const Scalar &zeta2,
    const Scalar &zeta3,
    const Scalar &dzeta2_dx,
    const Scalar &dzeta3_dx
) {
    return dzeta3_dx / scalar_pow(1.0 - zeta3, 2.0)
        + pair_diameter * (
            3.0 * dzeta2_dx / scalar_pow(1.0 - zeta3, 2.0)
            + 6.0 * zeta2 * dzeta3_dx / scalar_pow(1.0 - zeta3, 3.0)
        )
        + scalar_pow(pair_diameter, 2.0) * (
            4.0 * zeta2 * dzeta2_dx / scalar_pow(1.0 - zeta3, 3.0)
            + 6.0 * zeta2 * zeta2 * dzeta3_dx / scalar_pow(1.0 - zeta3, 4.0)
        );
}

template <typename Scalar>
static Scalar association_volume_scalar_cpp(
    int comp_i,
    int comp_j,
    int ncomp,
    const vector<Scalar> &s_ij,
    const add_args &cppargs,
    int component_target_kind = -1,
    int component_target_index = -1,
    const Scalar *component_target_value = nullptr,
    int k_hb_override_index = -1,
    const Scalar *k_hb_override_value = nullptr
) {
    const int idxi = comp_i * ncomp + comp_i;
    const int idxj = comp_j * ncomp + comp_j;
    const Scalar vol_i = scalar_component_parameter_cpp(
        kGenericTargetVolALocal,
        component_target_index,
        comp_i,
        cppargs.vol_a[static_cast<size_t>(comp_i)],
        component_target_kind == kGenericTargetVolALocal ? component_target_value : nullptr
    );
    const Scalar vol_j = scalar_component_parameter_cpp(
        kGenericTargetVolALocal,
        component_target_index,
        comp_j,
        cppargs.vol_a[static_cast<size_t>(comp_j)],
        component_target_kind == kGenericTargetVolALocal ? component_target_value : nullptr
    );
    Scalar volume = scalar_sqrt(vol_i * vol_j)
        * scalar_pow(
            scalar_sqrt(s_ij[static_cast<size_t>(idxi)] * s_ij[static_cast<size_t>(idxj)])
                / (0.5 * (s_ij[static_cast<size_t>(idxi)] + s_ij[static_cast<size_t>(idxj)])),
            3.0
        );
    if (!cppargs.k_hb.empty()) {
        const int pair_index = comp_i * ncomp + comp_j;
        const Scalar k_hb = (k_hb_override_value != nullptr && k_hb_override_index == pair_index)
            ? *k_hb_override_value
            : scalar_constant<Scalar>(cppargs.k_hb[static_cast<size_t>(pair_index)]);
        volume *= (1.0 - k_hb);
    }
    return volume;
}

template <typename Scalar>
static vector<Scalar> solve_linear_system_scalar_cpp(vector<Scalar> matrix, vector<Scalar> rhs, int n) {
    for (int col = 0; col < n; ++col) {
        int pivot = col;
        double pivot_abs = std::abs(scalar_value(matrix[static_cast<size_t>(col * n + col)]));
        for (int row = col + 1; row < n; ++row) {
            const double candidate_abs = std::abs(scalar_value(matrix[static_cast<size_t>(row * n + col)]));
            if (candidate_abs > pivot_abs) {
                pivot = row;
                pivot_abs = candidate_abs;
            }
        }
        if (pivot_abs <= 1.0e-30) {
            throw ValueError("Association implicit sensitivity matrix is singular.");
        }
        if (pivot != col) {
            for (int j = col; j < n; ++j) {
                std::swap(matrix[static_cast<size_t>(col * n + j)], matrix[static_cast<size_t>(pivot * n + j)]);
            }
            std::swap(rhs[static_cast<size_t>(col)], rhs[static_cast<size_t>(pivot)]);
        }
        const Scalar pivot_value = matrix[static_cast<size_t>(col * n + col)];
        for (int row = col + 1; row < n; ++row) {
            const Scalar factor = matrix[static_cast<size_t>(row * n + col)] / pivot_value;
            matrix[static_cast<size_t>(row * n + col)] = scalar_constant<Scalar>(0.0);
            for (int j = col + 1; j < n; ++j) {
                matrix[static_cast<size_t>(row * n + j)] -= factor * matrix[static_cast<size_t>(col * n + j)];
            }
            rhs[static_cast<size_t>(row)] -= factor * rhs[static_cast<size_t>(col)];
        }
    }

    vector<Scalar> out(static_cast<size_t>(n), scalar_constant<Scalar>(0.0));
    for (int row = n - 1; row >= 0; --row) {
        Scalar accum = rhs[static_cast<size_t>(row)];
        for (int col = row + 1; col < n; ++col) {
            accum -= matrix[static_cast<size_t>(row * n + col)] * out[static_cast<size_t>(col)];
        }
        out[static_cast<size_t>(row)] = accum / matrix[static_cast<size_t>(row * n + row)];
    }
    return out;
}

template <typename Scalar>
static vector<Scalar> association_site_fraction_density_terms_scalar_cpp(
    const vector<Scalar> &delta_ij,
    const Scalar &den,
    const vector<Scalar> &XA,
    const vector<Scalar> &ddelta_weighted,
    const vector<Scalar> &x_assoc
) {
    const int num_sites = static_cast<int>(XA.size());
    vector<Scalar> matrix(static_cast<size_t>(num_sites * num_sites), scalar_constant<Scalar>(0.0));
    vector<Scalar> rhs(static_cast<size_t>(num_sites), scalar_constant<Scalar>(0.0));

    int ij = 0;
    for (int i = 0; i < num_sites; ++i) {
        Scalar summ = scalar_constant<Scalar>(0.0);
        for (int j = 0; j < num_sites; ++j) {
            rhs[static_cast<size_t>(i)] -= x_assoc[static_cast<size_t>(j)] * XA[static_cast<size_t>(j)] * ddelta_weighted[static_cast<size_t>(ij)];
            matrix[static_cast<size_t>(i * num_sites + j)] = x_assoc[static_cast<size_t>(j)] * delta_ij[static_cast<size_t>(ij)];
            summ += x_assoc[static_cast<size_t>(j)] * XA[static_cast<size_t>(j)] * delta_ij[static_cast<size_t>(ij)];
            ++ij;
        }
        rhs[static_cast<size_t>(i)] -= summ;
        matrix[static_cast<size_t>(i * num_sites + i)] = scalar_pow(1.0 + den * summ, 2.0) / den;
    }

    return solve_linear_system_scalar_cpp(matrix, rhs, num_sites);
}

template <typename Scalar>
static vector<Scalar> association_site_fraction_composition_terms_scalar_cpp(
    const vector<Scalar> &delta_ij,
    const Scalar &den,
    const vector<Scalar> &XA,
    const vector<Scalar> &ddelta_dx,
    const vector<int> &site_component_index,
    const vector<Scalar> &x_assoc,
    int ncomp
) {
    const int num_sites = static_cast<int>(XA.size());
    vector<Scalar> dXA_dx(static_cast<size_t>(ncomp * num_sites), scalar_constant<Scalar>(0.0));

    for (int k = 0; k < ncomp; ++k) {
        vector<Scalar> matrix(static_cast<size_t>(num_sites * num_sites), scalar_constant<Scalar>(0.0));
        vector<Scalar> rhs(static_cast<size_t>(num_sites), scalar_constant<Scalar>(0.0));

        int ij = 0;
        for (int i = 0; i < num_sites; ++i) {
            Scalar direct_sum = scalar_constant<Scalar>(0.0);
            Scalar delta_sum = scalar_constant<Scalar>(0.0);
            for (int j = 0; j < num_sites; ++j) {
                if (site_component_index[static_cast<size_t>(j)] == k) {
                    direct_sum += XA[static_cast<size_t>(j)] * delta_ij[static_cast<size_t>(ij)];
                }
                delta_sum += x_assoc[static_cast<size_t>(j)] * XA[static_cast<size_t>(j)]
                    * ddelta_dx[static_cast<size_t>(k * num_sites * num_sites + ij)];
                matrix[static_cast<size_t>(i * num_sites + j)] = x_assoc[static_cast<size_t>(j)] * delta_ij[static_cast<size_t>(ij)];
                ++ij;
            }
            rhs[static_cast<size_t>(i)] = -(direct_sum + delta_sum);
            matrix[static_cast<size_t>(i * num_sites + i)] += 1.0 / (den * XA[static_cast<size_t>(i)] * XA[static_cast<size_t>(i)]);
        }

        vector<Scalar> solution = solve_linear_system_scalar_cpp(matrix, rhs, num_sites);
        for (int i = 0; i < num_sites; ++i) {
            dXA_dx[static_cast<size_t>(k * num_sites + i)] = solution[static_cast<size_t>(i)];
        }
    }

    return dXA_dx;
}

template <typename Scalar, typename TemperatureScalar>
static AssociationImplicitTermsScalar<Scalar> association_implicit_terms_scalar_cpp(
    const MixtureStateScalar<Scalar> &thermo,
    const HardChainStateScalar<Scalar> &hc_state,
    const TemperatureScalar &t,
    const vector<Scalar> &x,
    const add_args &cppargs,
    const vector<Scalar> &XA,
    int component_target_kind = -1,
    int component_target_index = -1,
    const Scalar *component_target_value = nullptr,
    int k_hb_override_index = -1,
    const Scalar *k_hb_override_value = nullptr
) {
    const int ncomp = static_cast<int>(x.size());
    AssociationImplicitTermsScalar<Scalar> out;
    out.dadx.assign(static_cast<size_t>(ncomp), scalar_constant<Scalar>(0.0));
    out.mu.assign(static_cast<size_t>(ncomp), scalar_constant<Scalar>(0.0));

    for (int comp = 0; comp < static_cast<int>(cppargs.assoc_num.size()); ++comp) {
        for (int site = 0; site < cppargs.assoc_num[static_cast<size_t>(comp)]; ++site) {
            out.site_component_index.push_back(comp);
            out.x_assoc.push_back(x[static_cast<size_t>(comp)]);
        }
    }

    const int num_sites = static_cast<int>(out.site_component_index.size());
    out.delta_ij.assign(static_cast<size_t>(num_sites * num_sites), scalar_constant<Scalar>(0.0));
    out.residuals.assign(static_cast<size_t>(num_sites), scalar_constant<Scalar>(0.0));
    if (num_sites == 0) {
        return out;
    }
    if (static_cast<int>(XA.size()) != num_sites) {
        throw ValueError("Association implicit sensitivity received a site-fraction vector with the wrong size.");
    }

    int idxa = 0;
    for (int i = 0; i < num_sites; ++i) {
        const int comp_i = out.site_component_index[static_cast<size_t>(i)];
        for (int j = 0; j < num_sites; ++j) {
            const int comp_j = out.site_component_index[static_cast<size_t>(j)];
            if (cppargs.assoc_matrix[static_cast<size_t>(idxa)] != 0) {
                const Scalar e_i = scalar_component_parameter_cpp(
                    kGenericTargetEAssocLocal,
                    component_target_index,
                    comp_i,
                    cppargs.e_assoc[static_cast<size_t>(comp_i)],
                    component_target_kind == kGenericTargetEAssocLocal ? component_target_value : nullptr
                );
                const Scalar e_j = scalar_component_parameter_cpp(
                    kGenericTargetEAssocLocal,
                    component_target_index,
                    comp_j,
                    cppargs.e_assoc[static_cast<size_t>(comp_j)],
                    component_target_kind == kGenericTargetEAssocLocal ? component_target_value : nullptr
                );
                const Scalar eABij = 0.5 * (e_i + e_j);
                const Scalar volABij = association_volume_scalar_cpp(
                    comp_i,
                    comp_j,
                    ncomp,
                    thermo.s_ij,
                    cppargs,
                    component_target_kind,
                    component_target_index,
                    component_target_value,
                    k_hb_override_index,
                    k_hb_override_value
                );
                out.delta_ij[static_cast<size_t>(idxa)] =
                    hc_state.ghs[static_cast<size_t>(comp_i * ncomp + comp_j)]
                    * (scalar_exp(eABij / t) - 1.0)
                    * scalar_pow(thermo.s_ij[static_cast<size_t>(comp_i * ncomp + comp_j)], 3.0)
                    * volABij;
            }
            ++idxa;
        }
    }

    for (int i = 0; i < num_sites; ++i) {
        Scalar summ = scalar_constant<Scalar>(0.0);
        for (int j = 0; j < num_sites; ++j) {
            summ += out.x_assoc[static_cast<size_t>(j)] * XA[static_cast<size_t>(j)]
                * out.delta_ij[static_cast<size_t>(i * num_sites + j)];
        }
        out.residuals[static_cast<size_t>(i)] = XA[static_cast<size_t>(i)] * (1.0 + thermo.den * summ) - 1.0;
        const int component_index = out.site_component_index[static_cast<size_t>(i)];
        out.ares += x[static_cast<size_t>(component_index)] * (
            scalar_log(XA[static_cast<size_t>(i)]) - 0.5 * XA[static_cast<size_t>(i)] + 0.5
        );
    }

    vector<Scalar> ddelta_weighted(static_cast<size_t>(num_sites * num_sites), scalar_constant<Scalar>(0.0));
    idxa = 0;
    for (int i = 0; i < num_sites; ++i) {
        const int comp_i = out.site_component_index[static_cast<size_t>(i)];
        for (int j = 0; j < num_sites; ++j) {
            const int comp_j = out.site_component_index[static_cast<size_t>(j)];
            if (cppargs.assoc_matrix[static_cast<size_t>(idxa)] != 0) {
                const Scalar pair_diameter = thermo.d[static_cast<size_t>(comp_i)] * thermo.d[static_cast<size_t>(comp_j)]
                    / (thermo.d[static_cast<size_t>(comp_i)] + thermo.d[static_cast<size_t>(comp_j)]);
                const Scalar e_i = scalar_component_parameter_cpp(
                    kGenericTargetEAssocLocal,
                    component_target_index,
                    comp_i,
                    cppargs.e_assoc[static_cast<size_t>(comp_i)],
                    component_target_kind == kGenericTargetEAssocLocal ? component_target_value : nullptr
                );
                const Scalar e_j = scalar_component_parameter_cpp(
                    kGenericTargetEAssocLocal,
                    component_target_index,
                    comp_j,
                    cppargs.e_assoc[static_cast<size_t>(comp_j)],
                    component_target_kind == kGenericTargetEAssocLocal ? component_target_value : nullptr
                );
                const Scalar eABij = 0.5 * (e_i + e_j);
                const Scalar volABij = association_volume_scalar_cpp(
                    comp_i,
                    comp_j,
                    ncomp,
                    thermo.s_ij,
                    cppargs,
                    component_target_kind,
                    component_target_index,
                    component_target_value,
                    k_hb_override_index,
                    k_hb_override_value
                );
                ddelta_weighted[static_cast<size_t>(idxa)] =
                    hs_contact_density_derivative_scalar_cpp(pair_diameter, hc_state.zeta[2], hc_state.zeta[3])
                    * (scalar_exp(eABij / t) - 1.0)
                    * scalar_pow(thermo.s_ij[static_cast<size_t>(comp_i * ncomp + comp_j)], 3.0)
                    * volABij;
            }
            ++idxa;
        }
    }

    vector<Scalar> dXA_density = association_site_fraction_density_terms_scalar_cpp(
        out.delta_ij, thermo.den, XA, ddelta_weighted, out.x_assoc
    );
    for (int i = 0; i < num_sites; ++i) {
        const int component_index = out.site_component_index[static_cast<size_t>(i)];
        out.zraw += x[static_cast<size_t>(component_index)] * (1.0 / XA[static_cast<size_t>(i)] - 0.5)
            * dXA_density[static_cast<size_t>(i)];
    }

    vector<Scalar> ddelta_dx(static_cast<size_t>(num_sites * num_sites * ncomp), scalar_constant<Scalar>(0.0));
    int idx_ddelta = 0;
    for (int k = 0; k < ncomp; ++k) {
        for (int i = 0; i < num_sites; ++i) {
            const int comp_i = out.site_component_index[static_cast<size_t>(i)];
            for (int j = 0; j < num_sites; ++j) {
                const int comp_j = out.site_component_index[static_cast<size_t>(j)];
                if (cppargs.assoc_matrix[static_cast<size_t>(i * num_sites + j)] != 0) {
                    const Scalar pair_diameter = thermo.d[static_cast<size_t>(comp_i)] * thermo.d[static_cast<size_t>(comp_j)]
                        / (thermo.d[static_cast<size_t>(comp_i)] + thermo.d[static_cast<size_t>(comp_j)]);
                    const Scalar dzeta2_dx = scalar_constant<Scalar>(PI / 6.0 * cppargs.m[static_cast<size_t>(k)])
                        * thermo.den
                        * scalar_pow(thermo.d[static_cast<size_t>(k)], 2.0);
                    const Scalar dzeta3_dx = scalar_constant<Scalar>(PI / 6.0 * cppargs.m[static_cast<size_t>(k)])
                        * thermo.den
                        * scalar_pow(thermo.d[static_cast<size_t>(k)], 3.0);
                    const Scalar e_i = scalar_component_parameter_cpp(
                        kGenericTargetEAssocLocal,
                        component_target_index,
                        comp_i,
                        cppargs.e_assoc[static_cast<size_t>(comp_i)],
                        component_target_kind == kGenericTargetEAssocLocal ? component_target_value : nullptr
                    );
                    const Scalar e_j = scalar_component_parameter_cpp(
                        kGenericTargetEAssocLocal,
                        component_target_index,
                        comp_j,
                        cppargs.e_assoc[static_cast<size_t>(comp_j)],
                        component_target_kind == kGenericTargetEAssocLocal ? component_target_value : nullptr
                    );
                    const Scalar eABij = 0.5 * (e_i + e_j);
                    const Scalar volABij = association_volume_scalar_cpp(
                        comp_i,
                        comp_j,
                        ncomp,
                        thermo.s_ij,
                        cppargs,
                        component_target_kind,
                        component_target_index,
                        component_target_value,
                        k_hb_override_index,
                        k_hb_override_value
                    );
                    ddelta_dx[static_cast<size_t>(idx_ddelta)] =
                        hs_contact_composition_derivative_scalar_cpp(pair_diameter, hc_state.zeta[2], hc_state.zeta[3], dzeta2_dx, dzeta3_dx)
                        * (scalar_exp(eABij / t) - 1.0)
                        * scalar_pow(thermo.s_ij[static_cast<size_t>(comp_i * ncomp + comp_j)], 3.0)
                        * volABij;
                }
                ++idx_ddelta;
            }
        }
    }

    vector<Scalar> dXA_dx = association_site_fraction_composition_terms_scalar_cpp(
        out.delta_ij,
        thermo.den,
        XA,
        ddelta_dx,
        out.site_component_index,
        out.x_assoc,
        ncomp
    );
    for (int i = 0; i < ncomp; ++i) {
        for (int j = 0; j < num_sites; ++j) {
            out.dadx[static_cast<size_t>(i)] += x[static_cast<size_t>(out.site_component_index[static_cast<size_t>(j)])]
                * dXA_dx[static_cast<size_t>(i * num_sites + j)] * (1.0 / XA[static_cast<size_t>(j)] - 0.5);
        }
    }
    for (int i = 0; i < num_sites; ++i) {
        const int component_index = out.site_component_index[static_cast<size_t>(i)];
        out.dadx[static_cast<size_t>(component_index)] += scalar_log(XA[static_cast<size_t>(i)])
            - 0.5 * XA[static_cast<size_t>(i)] + 0.5;
    }
    for (int i = 0; i < ncomp; ++i) {
        out.sum_x_dadx += x[static_cast<size_t>(i)] * out.dadx[static_cast<size_t>(i)];
    }
    for (int i = 0; i < ncomp; ++i) {
        out.mu[static_cast<size_t>(i)] = out.ares + out.zraw + out.dadx[static_cast<size_t>(i)] - out.sum_x_dadx;
    }
    return out;
}

}  // namespace ares_detail
