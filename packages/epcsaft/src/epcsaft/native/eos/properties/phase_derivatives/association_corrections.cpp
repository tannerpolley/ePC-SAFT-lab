#include "eos/properties/residual/internal.h"
#include "eos/properties/residual/implicit_association/sensitivities.h"
#include "eos/properties/residual/backend_helpers.h"
#include <algorithm>
#include <cmath>
#include <string>
#include <vector>

// Adds implicit-association Hessian terms that are not present on the base
// residual tape when site fractions are solved outside the CppAD recording.
EosPhaseAssociationDerivativeCorrectionResult eos_phase_association_derivative_corrections_cpp(
    double t,
    const vector<double> &amounts,
    double volume,
    const add_args &cppargs
) {
    EosPhaseAssociationDerivativeCorrectionResult out;
    out.backend = "cppad_implicit_association";
    if (!residual_backend_detail::has_association_sites(cppargs)) {
        out.message = "No active association sites were present.";
        return out;
    }
    if (!(std::isfinite(t) && t > 0.0) || !(std::isfinite(volume) && volume > 0.0)) {
        out.message = "Association derivative corrections require positive finite temperature and volume.";
        return out;
    }
    const int ncomp = static_cast<int>(amounts.size());
    if (ncomp <= 0) {
        out.message = "Association derivative corrections require at least one species amount.";
        return out;
    }
    double total_amount = 0.0;
    for (double amount : amounts) {
        if (!(std::isfinite(amount) && amount > 0.0)) {
            out.message = "Association derivative corrections require positive finite species amounts.";
            return out;
        }
        total_amount += amount;
    }
    if (!(std::isfinite(total_amount) && total_amount > 0.0)) {
        out.message = "Association derivative corrections require a positive finite total amount.";
        return out;
    }

    const double rho = total_amount / volume;
    vector<double> x(static_cast<size_t>(ncomp), 0.0);
    for (int i = 0; i < ncomp; ++i) {
        x[static_cast<size_t>(i)] = amounts[static_cast<size_t>(i)] / total_amount;
    }

    const int base_var_count = ncomp + 1;  // [rho, x_0, ..., x_n]
    const int phase_var_count = ncomp + 1;  // [n_0, ..., n_n, V]
    const auto association_response = residual_association_detail::association_phase_state_response_cppad_cpp(t, rho, x, cppargs);
    if (!association_response.active) {
        out.message = "Association derivative corrections expected active site fractions.";
        return out;
    }
    if (association_response.base_var_count != base_var_count) {
        out.message = "Association derivative correction variable count did not match the phase model.";
        return out;
    }

    std::vector<double> q_first(static_cast<size_t>(base_var_count * phase_var_count), 0.0);
    std::vector<double> q_second(
        static_cast<size_t>(base_var_count * phase_var_count * phase_var_count),
        0.0
    );
    const auto q1 = [&](int q, int y) -> double& {
        return q_first[static_cast<size_t>(q * phase_var_count + y)];
    };
    const auto q2 = [&](int q, int y0, int y1) -> double& {
        return q_second[
            static_cast<size_t>(q * phase_var_count * phase_var_count + y0 * phase_var_count + y1)
        ];
    };
    const auto q1_value = [&](int q, int y) {
        return q_first[static_cast<size_t>(q * phase_var_count + y)];
    };
    const auto q2_value = [&](int q, int y0, int y1) {
        return q_second[
            static_cast<size_t>(q * phase_var_count * phase_var_count + y0 * phase_var_count + y1)
        ];
    };

    for (int species = 0; species < ncomp; ++species) {
        q1(0, species) = 1.0 / volume;
        q2(0, species, ncomp) = -1.0 / (volume * volume);
        q2(0, ncomp, species) = -1.0 / (volume * volume);
    }
    q1(0, ncomp) = -rho / volume;
    q2(0, ncomp, ncomp) = 2.0 * rho / (volume * volume);

    for (int component = 0; component < ncomp; ++component) {
        const int q_index = 1 + component;
        for (int species = 0; species < ncomp; ++species) {
            const double indicator = component == species ? 1.0 : 0.0;
            q1(q_index, species) = (indicator - x[static_cast<size_t>(component)]) / total_amount;
        }
        for (int first = 0; first < ncomp; ++first) {
            for (int second = 0; second < ncomp; ++second) {
                const double first_indicator = component == first ? 1.0 : 0.0;
                const double second_indicator = component == second ? 1.0 : 0.0;
                q2(q_index, first, second) =
                    (2.0 * x[static_cast<size_t>(component)] - first_indicator - second_indicator)
                    / (total_amount * total_amount);
            }
        }
    }

    const auto z_first = [&](int q) {
        return association_response.dzraw_dvar[static_cast<size_t>(q)];
    };
    const auto z_second = [&](int q0, int q1_index) {
        return association_response.d2zraw_dvar2_row_major[
            static_cast<size_t>(q0 * base_var_count + q1_index)
        ];
    };
    const auto mu_first = [&](int component, int q) {
        return association_response.dmu_dvar_row_major[
            static_cast<size_t>(component * base_var_count + q)
        ];
    };
    const auto pressure_reduced_first = [&](int q) {
        double value = rho * z_first(q);
        if (q == 0) {
            value += association_response.zraw;
        }
        return value;
    };
    const auto pressure_reduced_second = [&](int q0, int q1_index) {
        double value = rho * z_second(q0, q1_index);
        if (q0 == 0) {
            value += z_first(q1_index);
        }
        if (q1_index == 0) {
            value += z_first(q0);
        }
        return value;
    };

    out.variable_count = phase_var_count;
    out.objective_hessian_row_major.assign(static_cast<size_t>(phase_var_count * phase_var_count), 0.0);
    out.pressure_hessian_row_major.assign(static_cast<size_t>(phase_var_count * phase_var_count), 0.0);

    for (int row = 0; row < ncomp; ++row) {
        for (int col = 0; col < phase_var_count; ++col) {
            double value = 0.0;
            for (int q = 0; q < base_var_count; ++q) {
                value += mu_first(row, q) * q1_value(q, col);
            }
            out.objective_hessian_row_major[static_cast<size_t>(row * phase_var_count + col)] = value;
        }
    }
    for (int col = 0; col < phase_var_count; ++col) {
        double value = 0.0;
        for (int q = 0; q < base_var_count; ++q) {
            value -= pressure_reduced_first(q) * q1_value(q, col);
        }
        out.objective_hessian_row_major[static_cast<size_t>(ncomp * phase_var_count + col)] = value;
    }
    for (int row = 0; row < phase_var_count; ++row) {
        for (int col = 0; col < row; ++col) {
            const double symmetric = 0.5 * (
                out.objective_hessian_row_major[static_cast<size_t>(row * phase_var_count + col)]
                + out.objective_hessian_row_major[static_cast<size_t>(col * phase_var_count + row)]
            );
            out.objective_hessian_row_major[static_cast<size_t>(row * phase_var_count + col)] = symmetric;
            out.objective_hessian_row_major[static_cast<size_t>(col * phase_var_count + row)] = symmetric;
        }
    }

    const double rt = kb * N_AV * t;
    for (int first = 0; first < phase_var_count; ++first) {
        for (int second = 0; second < phase_var_count; ++second) {
            double value = 0.0;
            for (int q0 = 0; q0 < base_var_count; ++q0) {
                value += pressure_reduced_first(q0) * q2_value(q0, first, second);
                for (int q1_index = 0; q1_index < base_var_count; ++q1_index) {
                    value += pressure_reduced_second(q0, q1_index)
                        * q1_value(q0, first)
                        * q1_value(q1_index, second);
                }
            }
            out.pressure_hessian_row_major[static_cast<size_t>(first * phase_var_count + second)] =
                rt * value;
        }
    }
    for (int row = 0; row < phase_var_count; ++row) {
        for (int col = 0; col < row; ++col) {
            const double symmetric = 0.5 * (
                out.pressure_hessian_row_major[static_cast<size_t>(row * phase_var_count + col)]
                + out.pressure_hessian_row_major[static_cast<size_t>(col * phase_var_count + row)]
            );
            out.pressure_hessian_row_major[static_cast<size_t>(row * phase_var_count + col)] = symmetric;
            out.pressure_hessian_row_major[static_cast<size_t>(col * phase_var_count + row)] = symmetric;
        }
    }

    for (double value : out.objective_hessian_row_major) {
        if (!std::isfinite(value)) {
            out.message = "Association objective Hessian correction was not finite.";
            return out;
        }
    }
    for (double value : out.pressure_hessian_row_major) {
        if (!std::isfinite(value)) {
            out.message = "Association pressure Hessian correction was not finite.";
            return out;
        }
    }
    out.active = true;
    out.message = "Association implicit objective and pressure Hessian corrections are available.";
    return out;
}
