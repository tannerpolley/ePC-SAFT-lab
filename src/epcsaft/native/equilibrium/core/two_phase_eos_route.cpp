#include "equilibrium/core/two_phase_eos_route.h"

#include "equilibrium/core/activated_equilibrium_nlp.h"
#include "equilibrium/core/activation_plan.h"
#include "equilibrium/blocks/eos_phase_block.h"
#include "eos/core_internal.h"
#include "equilibrium/solvers/ipopt_adapter.h"
#include "equilibrium/core/nlp_problem.h"
#include "equilibrium/blocks/reaction_block.h"
#include "equilibrium/core/route_metadata.h"
#include "equilibrium/core/second_order.h"
#include "equilibrium/core/variable_transform.h"

#include <algorithm>
#include <cmath>
#include <exception>
#include <limits>
#include <numeric>
#include <utility>

namespace epcsaft::native::equilibrium_nlp {

void apply_ipopt_solve_metadata(NeutralTwoPhaseEosRouteResult& out, const IpoptSolveResult& solve) {
    const RouteMetadata route_metadata = route_metadata_from_diagnostics(solve.diagnostics_string);
    if (!route_metadata.variable_model.empty()) {
        out.variable_model = route_metadata.variable_model;
    }
    if (!route_metadata.density_backend.empty()) {
        out.density_backend = route_metadata.density_backend;
    }
    if (!route_metadata.residual_families.empty()) {
        out.residual_families = route_metadata.residual_families;
    }
    if (!route_metadata.constraint_families.empty()) {
        out.constraint_families = route_metadata.constraint_families;
    }
    out.solver_feasible_point = solve.feasible_point;
    out.gradient_approximation = solve_diagnostic_string(solve, "gradient_approximation", "exact");
    out.jacobian_approximation = solve_diagnostic_string(solve, "jacobian_approximation", "exact");
    out.hessian_approximation = solve_diagnostic_string(solve, "hessian_approximation", out.hessian_approximation);
    out.hessian_backend = solve_diagnostic_string(solve, "hessian_backend", out.hessian_backend);
    out.option_profile = solve_diagnostic_string(solve, "option_profile", out.option_profile);
    out.exact_hessian_policy = solve_diagnostic_string(solve, "exact_hessian_policy", out.exact_hessian_policy);
    out.scaling_contract = solve_diagnostic_string(solve, "scaling_contract", out.scaling_contract);
    out.residual_scaling_policy =
        solve_diagnostic_string(solve, "residual_scaling_policy", out.residual_scaling_policy);
    out.linear_solver_policy = solve_diagnostic_string(solve, "linear_solver_policy", out.linear_solver_policy);
    out.barrier_policy = solve_diagnostic_string(solve, "barrier_policy", out.barrier_policy);
    out.last_callback_exception = solve_diagnostic_string(solve, "last_callback_exception", out.last_callback_exception);
    out.last_callback_failure = solve_diagnostic_string(solve, "last_callback_failure", out.last_callback_failure);
    out.scaling_method = solve_diagnostic_string(solve, "scaling_method", out.scaling_method);
    out.linear_solver_requested = solve_diagnostic_string(solve, "linear_solver_requested", out.linear_solver_requested);
    out.linear_solver_selected = solve_diagnostic_string(solve, "linear_solver_selected", out.linear_solver_selected);
    out.iteration_count = solve_diagnostic_int(solve, "iteration_count");
    out.iteration_history_limit = solve_diagnostic_int(solve, "iteration_history_limit");
    out.iteration_history_size = solve_diagnostic_int(solve, "iteration_history_size");
    out.variable_scaling_count = solve_diagnostic_int(solve, "variable_scaling_count");
    out.constraint_scaling_count = solve_diagnostic_int(solve, "constraint_scaling_count");
    out.eval_h_calls = solve_diagnostic_int(solve, "eval_h_calls");
    out.active_lower_bound_count = solve_diagnostic_int(solve, "active_lower_bound_count");
    out.active_upper_bound_count = solve_diagnostic_int(solve, "active_upper_bound_count");
    out.active_variable_bound_count = solve_diagnostic_int(solve, "active_variable_bound_count");
    out.step_trial_count_max = solve_diagnostic_int(solve, "step_trial_count_max");
    out.objective_scaling = solve_diagnostic_double(solve, "objective_scaling", out.objective_scaling);
    out.acceptable_tolerance = solve_diagnostic_double(solve, "acceptable_tolerance", out.acceptable_tolerance);
    out.constraint_violation_tolerance =
        solve_diagnostic_double(solve, "constraint_violation_tolerance", out.constraint_violation_tolerance);
    out.dual_infeasibility_tolerance =
        solve_diagnostic_double(solve, "dual_infeasibility_tolerance", out.dual_infeasibility_tolerance);
    out.complementarity_tolerance =
        solve_diagnostic_double(solve, "complementarity_tolerance", out.complementarity_tolerance);
    out.bound_push = solve_diagnostic_double(solve, "bound_push", out.bound_push);
    out.bound_frac = solve_diagnostic_double(solve, "bound_frac", out.bound_frac);
    out.variable_scaling_min = solve_diagnostic_double(solve, "variable_scaling_min", out.variable_scaling_min);
    out.variable_scaling_max = solve_diagnostic_double(solve, "variable_scaling_max", out.variable_scaling_max);
    out.constraint_scaling_min = solve_diagnostic_double(solve, "constraint_scaling_min", out.constraint_scaling_min);
    out.constraint_scaling_max = solve_diagnostic_double(solve, "constraint_scaling_max", out.constraint_scaling_max);
    out.variable_scaling_ratio = solve_diagnostic_double(solve, "variable_scaling_ratio", out.variable_scaling_ratio);
    out.constraint_scaling_ratio =
        solve_diagnostic_double(solve, "constraint_scaling_ratio", out.constraint_scaling_ratio);
    out.scaled_constraint_violation_inf_norm = solve_diagnostic_double(
        solve,
        "scaled_constraint_violation_inf_norm",
        out.scaled_constraint_violation_inf_norm
    );
    out.scaled_stationarity_inf_norm = solve_diagnostic_double(
        solve,
        "scaled_stationarity_inf_norm",
        out.scaled_stationarity_inf_norm
    );
    out.bound_complementarity_inf_norm = solve_diagnostic_double(
        solve,
        "bound_complementarity_inf_norm",
        out.bound_complementarity_inf_norm
    );
    out.barrier_parameter_final =
        solve_diagnostic_double(solve, "barrier_parameter_final", out.barrier_parameter_final);
    out.regularization_size_final =
        solve_diagnostic_double(solve, "regularization_size_final", out.regularization_size_final);
    out.regularization_size_max =
        solve_diagnostic_double(solve, "regularization_size_max", out.regularization_size_max);
    out.exact_hessian_available = solve_diagnostic_bool(solve, "exact_hessian_available");
    out.profile_exact_hessian_gate = solve_diagnostic_bool(solve, "profile_exact_hessian_gate", true);
    out.variable_scaling_quality_passed = solve_diagnostic_bool(solve, "variable_scaling_quality_passed", true);
    out.constraint_scaling_quality_passed = solve_diagnostic_bool(solve, "constraint_scaling_quality_passed", true);
    out.scaled_acceptance_passed = solve_diagnostic_bool(solve, "scaled_acceptance_passed");
    out.restoration_phase_observed = solve_diagnostic_bool(solve, "restoration_phase_observed");
    out.warm_start_requested = solve_diagnostic_bool(solve, "warm_start_requested");
    out.warm_start_used = solve_diagnostic_bool(solve, "warm_start_used");
    out.bound_lower_multipliers = solve.bound_lower_multipliers;
    out.bound_upper_multipliers = solve.bound_upper_multipliers;
    out.constraint_multipliers = solve.constraint_multipliers;
    out.iteration_history = solve.iteration_history;
}

namespace {

constexpr double kGasConstant = 8.31446261815324;
constexpr double kContractPhaseDistance = 1.0e-8;
constexpr double kCompositionFloor = 1.0e-12;
constexpr double kCandidateCompositionTolerance = 1.0e-6;
constexpr double kCandidateLogVolumeTolerance = 1.0e-5;

void apply_route_metadata(NeutralTwoPhaseEosNlpContract& out, const RouteMetadata& metadata) {
    out.variable_model = metadata.variable_model;
    out.density_backend = metadata.density_backend;
    out.residual_families = metadata.residual_families;
    out.constraint_families = metadata.constraint_families;
}

void apply_route_metadata(NeutralTwoPhaseEosPostsolve& out, const RouteMetadata& metadata) {
    out.density_backend = metadata.density_backend;
    out.residual_families = metadata.residual_families;
    out.constraint_families = metadata.constraint_families;
}

void apply_route_metadata(NeutralTwoPhaseEosRouteResult& out, const RouteMetadata& metadata) {
    out.variable_model = metadata.variable_model;
    out.density_backend = metadata.density_backend;
    out.residual_families = metadata.residual_families;
    out.constraint_families = metadata.constraint_families;
}

struct NeutralTwoPhaseEosInitialPoint {
    std::vector<std::vector<double>> phase_amounts;
    std::vector<double> volumes;
};

void require_size(const std::vector<double>& values, std::size_t expected, const std::string& label) {
    if (values.size() == expected) {
        return;
    }
    throw ValueError(label + " size does not match the neutral two-phase EOS NLP contract.");
}

void require_positive_finite(double value, const std::string& label) {
    if (std::isfinite(value) && value > 0.0) {
        return;
    }
    throw ValueError(label + " must be positive and finite.");
}

double positive_sum(const std::vector<double>& values, const std::string& label) {
    if (values.empty()) {
        throw ValueError(label + " requires at least one value.");
    }
    double total = 0.0;
    for (double value : values) {
        require_positive_finite(value, label + " value");
        total += value;
    }
    require_positive_finite(total, label + " total");
    return total;
}

std::vector<double> normalized_positive_values(const std::vector<double>& values, const std::string& label) {
    const double total = positive_sum(values, label);
    std::vector<double> normalized;
    normalized.reserve(values.size());
    for (double value : values) {
        normalized.push_back(value / total);
    }
    return normalized;
}

std::vector<double> normalized_trial_composition(const std::vector<double>& values, const std::string& label) {
    if (values.empty()) {
        throw ValueError(label + " requires at least one value.");
    }
    std::vector<double> floored;
    floored.reserve(values.size());
    double total = 0.0;
    for (double value : values) {
        if (!std::isfinite(value) || value < 0.0) {
            throw ValueError(label + " values must be finite and non-negative.");
        }
        const double floored_value = std::max(value, kCompositionFloor);
        floored.push_back(floored_value);
        total += floored_value;
    }
    require_positive_finite(total, label + " total");
    for (double& value : floored) {
        value /= total;
    }
    return floored;
}

std::vector<int> normalized_phase_kinds(const std::vector<int>& phase_kinds, const std::string& label) {
    if (phase_kinds.empty()) {
        throw ValueError(label + " requires at least one phase kind.");
    }
    std::vector<int> out;
    for (int phase_kind : phase_kinds) {
        if (phase_kind != 0 && phase_kind != 1) {
            throw ValueError(label + " phase kind must be 0/liquid or 1/vapor.");
        }
        if (std::find(out.begin(), out.end(), phase_kind) == out.end()) {
            out.push_back(phase_kind);
        }
    }
    return out;
}

std::vector<double> deterministic_composition_shift(
    const std::vector<double>& composition,
    const std::vector<double>& charges,
    const std::string& route_label,
    double shift_sign = 1.0
) {
    std::vector<double> shifted = composition;
    if (!charges.empty()) {
        require_size(charges, composition.size(), route_label + " charge");
    }
    if (composition.size() <= 1) {
        if (!charges.empty()) {
            throw ValueError(route_label + " requires at least two species.");
        }
        return shifted;
    }

    std::vector<double> positions;
    positions.reserve(composition.size());
    const double denominator = static_cast<double>(composition.size() - 1);
    for (std::size_t index = 0; index < composition.size(); ++index) {
        positions.push_back(-1.0 + 2.0 * static_cast<double>(index) / denominator);
    }
    double weighted_position = 0.0;
    for (std::size_t index = 0; index < composition.size(); ++index) {
        weighted_position += composition[index] * positions[index];
    }
    std::vector<double> direction;
    direction.reserve(composition.size());
    double max_abs_direction = 0.0;
    for (double position : positions) {
        const double value = position - weighted_position;
        direction.push_back(value);
        max_abs_direction = std::max(max_abs_direction, std::abs(value));
    }

    if (!charges.empty()) {
        double composition_charge = 0.0;
        double charge_square_weight = 0.0;
        double charge_direction = 0.0;
        for (std::size_t index = 0; index < composition.size(); ++index) {
            composition_charge += composition[index] * charges[index];
            charge_square_weight += composition[index] * charges[index] * charges[index];
            charge_direction += composition[index] * charges[index] * direction[index];
        }
        if (charge_square_weight <= 0.0) {
            throw ValueError(route_label + " requires at least one charged species.");
        }
        if (std::abs(composition_charge) > 1.0e-10) {
            throw ValueError(route_label + " feed must be charge neutral.");
        }
        const double charge_projection = charge_direction / charge_square_weight;
        max_abs_direction = 0.0;
        for (std::size_t index = 0; index < direction.size(); ++index) {
            direction[index] -= charge_projection * charges[index];
            max_abs_direction = std::max(max_abs_direction, std::abs(direction[index]));
        }
        if (max_abs_direction <= 0.0) {
            throw ValueError(route_label + " could not construct a charge-neutral initial direction.");
        }
    }

    double shifted_sum = 0.0;
    for (std::size_t index = 0; index < composition.size(); ++index) {
        const double scaled_direction = max_abs_direction > 0.0 ? direction[index] / max_abs_direction : 0.0;
        shifted[index] = composition[index] * (1.0 + 0.2 * shift_sign * scaled_direction);
        shifted_sum += shifted[index];
    }
    require_positive_finite(shifted_sum, "shifted composition sum");
    for (double& value : shifted) {
        value /= shifted_sum;
    }
    return shifted;
}

NeutralTwoPhaseEosInitialPoint build_two_phase_eos_initial_point(
    const add_args& args,
    const std::vector<double>& feed_amounts,
    const std::vector<double>& first_composition,
    double temperature,
    double target_pressure,
    const std::string& route_label,
    const std::vector<int>& phase_kinds
) {
    require_positive_finite(temperature, route_label + " temperature");
    require_positive_finite(target_pressure, route_label + " pressure");
    const double total_feed = positive_sum(feed_amounts, route_label + " feed amount");
    require_size(first_composition, feed_amounts.size(), route_label + " first phase composition");
    if (phase_kinds.size() != 2) {
        throw ValueError(route_label + " requires exactly two phase kinds.");
    }

    NeutralTwoPhaseEosInitialPoint out;
    out.phase_amounts.assign(2, std::vector<double>(feed_amounts.size(), 0.0));
    for (std::size_t index = 0; index < feed_amounts.size(); ++index) {
        out.phase_amounts[0][index] = 0.5 * total_feed * first_composition[index];
        out.phase_amounts[1][index] = feed_amounts[index] - out.phase_amounts[0][index];
        require_positive_finite(out.phase_amounts[0][index], route_label + " first phase amount");
        require_positive_finite(out.phase_amounts[1][index], route_label + " second phase amount");
    }

    out.volumes.reserve(2);
    for (std::size_t phase = 0; phase < out.phase_amounts.size(); ++phase) {
        const auto& amounts = out.phase_amounts[phase];
        const double phase_total = std::accumulate(amounts.begin(), amounts.end(), 0.0);
        require_positive_finite(phase_total, route_label + " phase amount total");
        std::vector<double> composition;
        composition.reserve(amounts.size());
        for (double amount : amounts) {
            composition.push_back(amount / phase_total);
        }
        const int phase_kind = phase_kinds[phase];
        if (phase_kind != 0 && phase_kind != 1) {
            throw ValueError(route_label + " phase kind must be 0/liquid or 1/vapor.");
        }
        const DensitySolveResult density = density_solve_report_cpp(
            temperature,
            target_pressure,
            composition,
            phase_kind,
            args
        );
        if (!density.valid || !std::isfinite(density.rho) || density.rho <= 0.0) {
            throw ValueError(route_label + " could not construct a phase-specific pressure-density root seed.");
        }
        out.volumes.push_back(phase_total / density.rho);
    }
    return out;
}

EosPhaseBlockResult evaluate_unit_phase_block_at_pressure_root(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<double>& composition,
    int phase_kind,
    const std::string& label
) {
    const std::vector<double> normalized = normalized_trial_composition(composition, label + " composition");
    const DensitySolveResult density = density_solve_report_cpp(
        temperature,
        target_pressure,
        normalized,
        phase_kind,
        args
    );
    if (!density.valid || !std::isfinite(density.rho) || density.rho <= 0.0) {
        throw ValueError(label + " could not construct a pressure-density root trial phase.");
    }
    return evaluate_eos_phase_block(args, temperature, target_pressure, normalized, 1.0 / density.rho);
}

double composition_distance_inf_norm(
    const std::vector<double>& first,
    const std::vector<double>& second
) {
    require_size(second, first.size(), "Neutral TPD candidate composition");
    double distance = 0.0;
    for (std::size_t index = 0; index < first.size(); ++index) {
        distance = std::max(distance, std::abs(first[index] - second[index]));
    }
    return distance;
}

bool duplicate_tpd_candidate(
    const NeutralTpdCandidate& first,
    const NeutralTpdCandidate& second
) {
    if (!first.valid || !second.valid || first.molar_volume <= 0.0 || second.molar_volume <= 0.0) {
        return false;
    }
    return composition_distance_inf_norm(first.composition, second.composition) < kCandidateCompositionTolerance
        && std::abs(std::log(first.molar_volume) - std::log(second.molar_volume)) < kCandidateLogVolumeTolerance;
}

void rank_tpd_candidates(NeutralPhaseDiscoveryResult& discovery) {
    for (std::size_t index = 0; index < discovery.candidates.size(); ++index) {
        discovery.candidates[index].candidate_rank = static_cast<int>(index);
        if (discovery.candidates[index].feasibility_status.empty()) {
            discovery.candidates[index].feasibility_status = "candidate_generated";
        }
    }
}

void append_unique_tpd_candidate(
    std::vector<NeutralTpdCandidate>& candidates,
    const NeutralTpdCandidate& candidate
) {
    if (!candidate.valid) {
        return;
    }
    for (NeutralTpdCandidate& existing : candidates) {
        if (!duplicate_tpd_candidate(existing, candidate)) {
            continue;
        }
        if (candidate.tpd < existing.tpd) {
            existing = candidate;
        }
        return;
    }
    candidates.push_back(candidate);
}

std::vector<std::vector<double>> neutral_tpd_trial_compositions(
    const std::vector<double>& reference
) {
    const std::vector<double> normalized = normalized_trial_composition(reference, "Neutral TPD reference");
    std::vector<std::vector<double>> out;
    out.push_back(normalized);
    if (normalized.size() > 1) {
        out.push_back(normalized_trial_composition(
            deterministic_composition_shift(normalized, {}, "Neutral TPD shifted composition", 1.0),
            "Neutral TPD shifted composition"
        ));
        out.push_back(normalized_trial_composition(
            deterministic_composition_shift(normalized, {}, "Neutral TPD shifted composition", -1.0),
            "Neutral TPD shifted composition"
        ));
    }
    if (normalized.size() == 2) {
        for (double first_fraction : {
                 1.0e-4,
                 1.0e-3,
                 1.0e-2,
                 2.0e-2,
                 5.0e-2,
                 1.0e-1,
                 2.0e-1,
                 3.5e-1,
                 5.0e-1,
                 6.5e-1,
                 8.0e-1,
                 9.0e-1,
                 9.5e-1,
                 9.8e-1,
                 9.9e-1,
                 9.99e-1}) {
            out.push_back({first_fraction, 1.0 - first_fraction});
        }
    } else if (normalized.size() > 2) {
        for (std::size_t rich = 0; rich < normalized.size(); ++rich) {
            std::vector<double> near_pure(normalized.size(), kCompositionFloor);
            near_pure[rich] = 1.0 - kCompositionFloor * static_cast<double>(normalized.size() - 1);
            out.push_back(normalized_trial_composition(near_pure, "Neutral TPD near-pure composition"));
        }
    }
    return out;
}

// AlgID: neutral_tpd_stability
void append_tpd_candidates_for_reference_block(
    const add_args& args,
    double temperature,
    double target_pressure,
    const EosPhaseBlockResult& reference,
    const std::vector<int>& trial_phase_kinds,
    const std::string& source_prefix,
    std::vector<NeutralTpdCandidate>& candidates,
    int& valid_candidate_count
) {
    const std::size_t species_count = reference.composition.size();
    if (reference.gradient.size() < species_count) {
        throw ValueError("Neutral TPD reference gradient size did not match species count.");
    }
    const std::vector<std::vector<double>> trial_compositions =
        neutral_tpd_trial_compositions(reference.composition);
    for (int phase_kind : trial_phase_kinds) {
        for (std::size_t index = 0; index < trial_compositions.size(); ++index) {
            try {
                const EosPhaseBlockResult trial = evaluate_unit_phase_block_at_pressure_root(
                    args,
                    temperature,
                    target_pressure,
                    trial_compositions[index],
                    phase_kind,
                    source_prefix
                );
                if (trial.gradient.size() < species_count) {
                    continue;
                }
                NeutralTpdCandidate candidate;
                candidate.valid = true;
                candidate.source = source_prefix + "_trial_" + std::to_string(index);
                candidate.phase_kind = phase_kind;
                candidate.composition = trial.composition;
                candidate.density = trial.density;
                candidate.molar_volume = 1.0 / trial.density;
                candidate.transformed_objective = trial.objective;
                candidate.pressure_residual_estimate = trial.pressure_consistency_residual;
                candidate.feasibility_status = "candidate_generated";
                for (std::size_t species = 0; species < species_count; ++species) {
                    candidate.tpd += trial.composition[species]
                        * (trial.gradient[species] - reference.gradient[species]);
                }
                ++valid_candidate_count;
                append_unique_tpd_candidate(candidates, candidate);
            } catch (const std::exception&) {
                continue;
            }
        }
    }
}

double candidate_pair_mass_balance_norm(
    const std::vector<double>& feed_composition,
    const std::vector<double>& first,
    const std::vector<double>& second,
    double first_fraction
) {
    require_size(first, feed_composition.size(), "Neutral TPD first candidate composition");
    require_size(second, feed_composition.size(), "Neutral TPD second candidate composition");
    double norm = 0.0;
    for (std::size_t species = 0; species < feed_composition.size(); ++species) {
        const double reconstructed = first_fraction * first[species] + (1.0 - first_fraction) * second[species];
        norm = std::max(norm, std::abs(reconstructed - feed_composition[species]));
    }
    return norm;
}

// AlgID: phase_candidate_mass_balance_selection
void select_two_phase_candidate_set(
    NeutralPhaseDiscoveryResult& discovery,
    const std::vector<double>& feed_composition,
    const std::vector<int>& phase_kinds,
    double candidate_mass_balance_tolerance
) {
    if (phase_kinds.size() != 2 || discovery.candidates.size() < 2) {
        discovery.phase_set_status = "candidate_mass_balance_incomplete";
        discovery.candidate_mass_balance_norm = std::numeric_limits<double>::infinity();
        for (NeutralTpdCandidate& candidate : discovery.candidates) {
            candidate.feasibility_status = "candidate_mass_balance_incomplete";
            candidate.selected = false;
        }
        return;
    }
    rank_tpd_candidates(discovery);
    const std::vector<double> z = normalized_trial_composition(feed_composition, "Neutral TPD feed");
    double best_norm = std::numeric_limits<double>::infinity();
    double best_fraction = 0.0;
    int best_first = -1;
    int best_second = -1;
    for (std::size_t first_index = 0; first_index < discovery.candidates.size(); ++first_index) {
        const NeutralTpdCandidate& first = discovery.candidates[first_index];
        if (first.phase_kind != phase_kinds[0]) {
            continue;
        }
        for (std::size_t second_index = 0; second_index < discovery.candidates.size(); ++second_index) {
            if (first_index == second_index) {
                continue;
            }
            const NeutralTpdCandidate& second = discovery.candidates[second_index];
            if (second.phase_kind != phase_kinds[1]) {
                continue;
            }
            double numerator = 0.0;
            double denominator = 0.0;
            for (std::size_t species = 0; species < z.size(); ++species) {
                const double direction = first.composition[species] - second.composition[species];
                numerator += (z[species] - second.composition[species]) * direction;
                denominator += direction * direction;
            }
            if (denominator <= 0.0) {
                continue;
            }
            const double fraction = numerator / denominator;
            if (!(fraction > 1.0e-10 && fraction < 1.0 - 1.0e-10)) {
                continue;
            }
            const double norm = candidate_pair_mass_balance_norm(
                z,
                first.composition,
                second.composition,
                fraction
            );
            if (norm < best_norm) {
                best_norm = norm;
                best_fraction = fraction;
                best_first = static_cast<int>(first_index);
                best_second = static_cast<int>(second_index);
            }
        }
    }
    discovery.candidate_mass_balance_norm = best_norm;
    discovery.phase_set_mass_balance_feasible = best_norm <= candidate_mass_balance_tolerance;
    discovery.candidate_completeness_accepted = discovery.phase_set_mass_balance_feasible;
    if (!discovery.phase_set_mass_balance_feasible) {
        discovery.phase_set_status = "candidate_mass_balance_incomplete";
        for (NeutralTpdCandidate& candidate : discovery.candidates) {
            candidate.feasibility_status = "candidate_mass_balance_incomplete";
            candidate.selected = false;
        }
        return;
    }
    for (NeutralTpdCandidate& candidate : discovery.candidates) {
        candidate.feasibility_status = "mass_balance_pair_unselected";
        candidate.selected = false;
    }
    discovery.candidates[static_cast<std::size_t>(best_first)].selected = true;
    discovery.candidates[static_cast<std::size_t>(best_first)].feasibility_status =
        "selected_mass_balance_feasible";
    discovery.candidates[static_cast<std::size_t>(best_second)].selected = true;
    discovery.candidates[static_cast<std::size_t>(best_second)].feasibility_status =
        "selected_mass_balance_feasible";
    discovery.selected_candidate_count = 2;
    discovery.selected_phase_fractions = {best_fraction, 1.0 - best_fraction};
    discovery.selected_phase_kinds = {phase_kinds[0], phase_kinds[1]};
    discovery.selected_phase_compositions = {
        discovery.candidates[static_cast<std::size_t>(best_first)].composition,
        discovery.candidates[static_cast<std::size_t>(best_second)].composition,
    };
    discovery.phase_set_status = "candidate_mass_balance_feasible";
}

void copy_discovery_to_postsolve(
    NeutralTwoPhaseEosPostsolve& postsolve,
    const NeutralPhaseDiscoveryResult& discovery
) {
    postsolve.stability_checked = discovery.stability_checked;
    postsolve.stability_accepted = discovery.stability_accepted;
    postsolve.candidate_completeness_accepted = discovery.candidate_completeness_accepted;
    postsolve.phase_set_mass_balance_feasible = discovery.phase_set_mass_balance_feasible;
    postsolve.phase_discovery_backend = discovery.phase_discovery_backend;
    postsolve.stability_certificate = discovery.stability_certificate;
    postsolve.phase_set_status = discovery.phase_set_status;
    postsolve.min_tpd = discovery.min_tpd;
    postsolve.candidate_mass_balance_norm = discovery.candidate_mass_balance_norm;
    postsolve.tpd_candidate_count = discovery.tpd_candidate_count;
    postsolve.unique_candidate_count = discovery.unique_candidate_count;
    postsolve.selected_candidate_count = discovery.selected_candidate_count;
    postsolve.selected_phase_fractions = discovery.selected_phase_fractions;
    postsolve.selected_phase_kinds = discovery.selected_phase_kinds;
    postsolve.selected_phase_compositions = discovery.selected_phase_compositions;
    postsolve.tpd_candidate_values.clear();
    postsolve.tpd_candidate_sources.clear();
    postsolve.tpd_candidate_phase_kinds.clear();
    postsolve.tpd_candidate_compositions.clear();
    postsolve.tpd_candidate_pressure_residuals.clear();
    postsolve.tpd_candidate_ranks.clear();
    postsolve.tpd_candidate_feasibility_statuses.clear();
    postsolve.tpd_candidate_selected.clear();
    for (const NeutralTpdCandidate& candidate : discovery.candidates) {
        postsolve.tpd_candidate_values.push_back(candidate.tpd);
        postsolve.tpd_candidate_sources.push_back(candidate.source);
        postsolve.tpd_candidate_phase_kinds.push_back(candidate.phase_kind);
        postsolve.tpd_candidate_compositions.push_back(candidate.composition);
        postsolve.tpd_candidate_pressure_residuals.push_back(candidate.pressure_residual_estimate);
        postsolve.tpd_candidate_ranks.push_back(candidate.candidate_rank);
        postsolve.tpd_candidate_feasibility_statuses.push_back(candidate.feasibility_status);
        postsolve.tpd_candidate_selected.push_back(candidate.selected);
    }
}

std::string certified_postsolve_status(const NeutralTwoPhaseEosPostsolve& postsolve) {
    if (postsolve.accepted) {
        return "production_accepted";
    }
    if (postsolve.rejection_reason == "stability_tpd") {
        return "unstable";
    }
    if (postsolve.rejection_reason == "candidate_completeness") {
        return "optimizer_converged_uncertified";
    }
    return "postsolve_rejected";
}

bool candidate_duplicates_accepted_phase(
    const NeutralTpdCandidate& candidate,
    const std::vector<EosPhaseBlockResult>& accepted_phases
) {
    for (const EosPhaseBlockResult& phase : accepted_phases) {
        if (phase.total_amount <= 0.0 || phase.volume <= 0.0) {
            continue;
        }
        NeutralTpdCandidate accepted;
        accepted.valid = true;
        accepted.composition = phase.composition;
        accepted.molar_volume = phase.volume / phase.total_amount;
        if (duplicate_tpd_candidate(candidate, accepted)) {
            return true;
        }
    }
    return false;
}

NeutralPhaseDiscoveryResult certify_neutral_phase_set(
    const add_args& args,
    double temperature,
    double target_pressure,
    const EosPhaseSystemResult& system,
    const std::vector<double>& feed_amounts,
    const std::vector<int>& phase_kinds,
    double tpd_tolerance,
    double candidate_mass_balance_tolerance
) {
    if (phase_kinds.size() != system.phase_blocks.size()) {
        throw ValueError("Neutral TPD postsolve phase kind size does not match the accepted phase set.");
    }
    NeutralPhaseDiscoveryResult out;
    out.phase_discovery_backend = "deterministic_tpd_candidate_screening";
    out.stability_certificate = "tpd_postsolve";
    const std::vector<int> trial_phase_kinds = normalized_phase_kinds(phase_kinds, "Neutral TPD postsolve");
    int valid_candidate_count = 0;
    for (std::size_t phase = 0; phase < system.phase_blocks.size(); ++phase) {
        append_tpd_candidates_for_reference_block(
            args,
            temperature,
            target_pressure,
            system.phase_blocks[phase],
            trial_phase_kinds,
            "accepted_phase_" + std::to_string(phase),
            out.candidates,
            valid_candidate_count
        );
    }
    out.tpd_candidate_count = valid_candidate_count;
    out.unique_candidate_count = static_cast<int>(out.candidates.size());
    rank_tpd_candidates(out);
    out.stability_checked = out.unique_candidate_count > 0;
    out.min_tpd = out.stability_checked ? std::numeric_limits<double>::infinity() : 0.0;
    bool negative_novel_candidate = false;
    for (const NeutralTpdCandidate& candidate : out.candidates) {
        out.min_tpd = std::min(out.min_tpd, candidate.tpd);
        if (candidate.tpd < -tpd_tolerance && !candidate_duplicates_accepted_phase(candidate, system.phase_blocks)) {
            negative_novel_candidate = true;
        }
    }
    out.stability_accepted = out.stability_checked && !negative_novel_candidate;

    const double total_feed = positive_sum(feed_amounts, "Neutral TPD postsolve feed amount");
    std::vector<double> feed_composition;
    feed_composition.reserve(feed_amounts.size());
    for (double amount : feed_amounts) {
        feed_composition.push_back(amount / total_feed);
    }
    const double phase_total = std::accumulate(
        system.phase_blocks.begin(),
        system.phase_blocks.end(),
        0.0,
        [](double total, const EosPhaseBlockResult& block) {
            return total + block.total_amount;
        }
    );
    require_positive_finite(phase_total, "Neutral TPD postsolve phase total");
    std::vector<double> fractions;
    fractions.reserve(system.phase_blocks.size());
    for (const EosPhaseBlockResult& block : system.phase_blocks) {
        fractions.push_back(block.total_amount / phase_total);
    }
    out.candidate_mass_balance_norm = 0.0;
    for (std::size_t species = 0; species < feed_composition.size(); ++species) {
        double reconstructed = 0.0;
        for (std::size_t phase = 0; phase < system.phase_blocks.size(); ++phase) {
            reconstructed += fractions[phase] * system.phase_blocks[phase].composition[species];
        }
        out.candidate_mass_balance_norm =
            std::max(out.candidate_mass_balance_norm, std::abs(reconstructed - feed_composition[species]));
    }
    out.phase_set_mass_balance_feasible = out.candidate_mass_balance_norm <= candidate_mass_balance_tolerance;
    out.candidate_completeness_accepted = out.phase_set_mass_balance_feasible && out.stability_accepted;
    out.selected_candidate_count = static_cast<int>(system.phase_blocks.size());
    out.selected_phase_fractions = fractions;
    out.selected_phase_kinds = phase_kinds;
    for (const EosPhaseBlockResult& block : system.phase_blocks) {
        out.selected_phase_compositions.push_back(block.composition);
    }
    if (!out.stability_checked) {
        out.phase_set_status = "stability_uncertified";
    } else if (!out.stability_accepted) {
        out.phase_set_status = "negative_tpd_candidate";
    } else if (!out.phase_set_mass_balance_feasible) {
        out.phase_set_status = "candidate_mass_balance_incomplete";
    } else {
        out.phase_set_status = "phase_set_certified";
    }
    return out;
}

NeutralTwoPhaseEosInitialPoint build_neutral_two_phase_eos_initial_point(
    const add_args& args,
    const std::vector<double>& feed_amounts,
    double temperature,
    double target_pressure,
    const std::string& route_label,
    const std::vector<int>& phase_kinds,
    double shift_sign = 1.0
) {
    const std::vector<double> composition = normalized_positive_values(feed_amounts, route_label + " feed amount");
    const std::vector<double> first_composition =
        deterministic_composition_shift(composition, {}, route_label + " composition", shift_sign);
    return build_two_phase_eos_initial_point(
        args,
        feed_amounts,
        first_composition,
        temperature,
        target_pressure,
        route_label,
        phase_kinds
    );
}

NeutralTwoPhaseEosInitialPoint build_two_phase_eos_initial_point_from_candidate_set(
    const add_args& args,
    const std::vector<double>& feed_amounts,
    const NeutralPhaseDiscoveryResult& discovery,
    double temperature,
    double target_pressure,
    const std::string& route_label,
    const std::vector<int>& phase_kinds
) {
    if (discovery.selected_phase_compositions.size() != 2
        || discovery.selected_phase_fractions.size() != 2
        || discovery.selected_phase_kinds.size() != 2) {
        throw ValueError(route_label + " requires a two-candidate phase-discovery seed.");
    }
    if (phase_kinds.size() != 2) {
        throw ValueError(route_label + " phase kind size does not match the neutral two-phase EOS NLP contract.");
    }
    const double total_feed = positive_sum(feed_amounts, route_label + " feed amount");
    NeutralTwoPhaseEosInitialPoint out;
    out.phase_amounts.assign(2, std::vector<double>(feed_amounts.size(), 0.0));
    out.volumes.reserve(2);
    for (std::size_t phase = 0; phase < 2; ++phase) {
        const std::vector<double> composition = normalized_trial_composition(
            discovery.selected_phase_compositions[phase],
            route_label + " phase-discovery composition"
        );
        require_size(composition, feed_amounts.size(), route_label + " phase-discovery composition");
        const double phase_fraction = discovery.selected_phase_fractions[phase];
        if (!(phase_fraction > 0.0 && phase_fraction < 1.0)) {
            throw ValueError(route_label + " phase-discovery phase fraction must be inside (0, 1).");
        }
        for (std::size_t species = 0; species < composition.size(); ++species) {
            out.phase_amounts[phase][species] = total_feed * phase_fraction * composition[species];
            require_positive_finite(out.phase_amounts[phase][species], route_label + " phase-discovery amount");
        }
        const EosPhaseBlockResult block = evaluate_unit_phase_block_at_pressure_root(
            args,
            temperature,
            target_pressure,
            composition,
            phase_kinds[phase],
            route_label + " phase-discovery seed"
        );
        out.volumes.push_back((total_feed * phase_fraction) / block.density);
    }
    return out;
}

NeutralTwoPhaseEosInitialPoint build_charge_neutral_two_phase_eos_initial_point(
    const add_args& args,
    const std::vector<double>& feed_amounts,
    const std::vector<double>& charges,
    double temperature,
    double target_pressure,
    const std::string& route_label,
    const std::vector<int>& phase_kinds,
    double shift_sign = 1.0
) {
    const std::vector<double> composition = normalized_positive_values(feed_amounts, route_label + " feed amount");
    const std::vector<double> first_composition =
        deterministic_composition_shift(composition, charges, route_label + " composition", shift_sign);
    return build_two_phase_eos_initial_point(
        args,
        feed_amounts,
        first_composition,
        temperature,
        target_pressure,
        route_label,
        phase_kinds
    );
}

struct NamedInitialVariables {
    std::string seed_name;
    std::vector<double> variables;
};

std::vector<double> neutral_two_phase_variables_from_initial(
    const NeutralTwoPhaseEosInitialPoint& initial
) {
    std::vector<double> out;
    out.reserve(initial.phase_amounts.size() * (initial.phase_amounts.front().size() + 1));
    for (std::size_t phase = 0; phase < initial.phase_amounts.size(); ++phase) {
        out.insert(out.end(), initial.phase_amounts[phase].begin(), initial.phase_amounts[phase].end());
        out.push_back(initial.volumes[phase]);
    }
    return out;
}

void append_phase_discovery_seed_candidates(
    std::vector<NamedInitialVariables>& out,
    const add_args& args,
    const std::vector<double>& feed_amounts,
    double temperature,
    double target_pressure,
    const std::string& route_label,
    const std::vector<int>& phase_kinds
) {
    try {
        const std::vector<double> feed_composition =
            normalized_positive_values(feed_amounts, route_label + " feed amount");
        const NeutralPhaseDiscoveryResult discovery = evaluate_neutral_tpd_phase_discovery(
            args,
            temperature,
            target_pressure,
            feed_composition,
            phase_kinds,
            1.0e-6,
            1.0e-6
        );
        if (!discovery.phase_set_mass_balance_feasible || discovery.selected_candidate_count != 2) {
            return;
        }
        out.push_back({
            "deterministic_tpd_candidate_pair",
            neutral_two_phase_variables_from_initial(
                build_two_phase_eos_initial_point_from_candidate_set(
                    args,
                    feed_amounts,
                    discovery,
                    temperature,
                    target_pressure,
                    route_label,
                    phase_kinds
                )
            )
        });
    } catch (const std::exception&) {
        return;
    }
}

std::vector<NamedInitialVariables> neutral_two_phase_seed_candidates(
    const add_args& args,
    const std::vector<double>& feed_amounts,
    const std::vector<double>& charges,
    double temperature,
    double target_pressure,
    const std::string& route_label,
    const std::vector<int>& phase_kinds
) {
    std::vector<NamedInitialVariables> out;
    if (charges.empty()) {
        append_phase_discovery_seed_candidates(
            out,
            args,
            feed_amounts,
            temperature,
            target_pressure,
            route_label,
            phase_kinds
        );
        const std::vector<double> feed_composition =
            normalized_positive_values(feed_amounts, route_label + " feed amount");
        out.push_back({
            "canonical_shifted_feed",
            neutral_two_phase_variables_from_initial(
                build_neutral_two_phase_eos_initial_point(
                    args,
                    feed_amounts,
                    temperature,
                    target_pressure,
                    route_label,
                    phase_kinds,
                    1.0
                )
            )
        });
        out.push_back({
            "mirrored_shifted_feed",
            neutral_two_phase_variables_from_initial(
                build_neutral_two_phase_eos_initial_point(
                    args,
                    feed_amounts,
                    temperature,
                    target_pressure,
                    route_label,
                    phase_kinds,
                    -1.0
                )
            )
        });
        if (feed_amounts.size() == 2) {
            auto append_binary_extreme = [&](int poor_component) {
                const int rich_component = 1 - poor_component;
                const double poor_fraction = std::max(
                    1.0e-6,
                    std::min(0.05, 0.5 * feed_composition[static_cast<std::size_t>(poor_component)])
                );
                std::vector<double> first_composition(2, 0.0);
                first_composition[static_cast<std::size_t>(poor_component)] = poor_fraction;
                first_composition[static_cast<std::size_t>(rich_component)] = 1.0 - poor_fraction;
                for (std::size_t species = 0; species < first_composition.size(); ++species) {
                    if (0.5 * first_composition[species] >= feed_composition[species]) {
                        return;
                    }
                }
                try {
                    out.push_back({
                        "binary_extreme_component_" + std::to_string(poor_component) + "_poor",
                        neutral_two_phase_variables_from_initial(
                            build_two_phase_eos_initial_point(
                                args,
                                feed_amounts,
                                first_composition,
                                temperature,
                                target_pressure,
                                route_label,
                                phase_kinds
                            )
                        )
                    });
                } catch (const std::exception&) {
                    return;
                }
            };
            append_binary_extreme(0);
            append_binary_extreme(1);
        }
        return out;
    }
    out.push_back({
        "canonical_shifted_feed",
        neutral_two_phase_variables_from_initial(
            build_charge_neutral_two_phase_eos_initial_point(
                args,
                feed_amounts,
                charges,
                temperature,
                target_pressure,
                route_label,
                phase_kinds,
                1.0
            )
        )
    });
    out.push_back({
        "mirrored_shifted_feed",
        neutral_two_phase_variables_from_initial(
            build_charge_neutral_two_phase_eos_initial_point(
                args,
                feed_amounts,
                charges,
                temperature,
                target_pressure,
                route_label,
                phase_kinds,
                -1.0
            )
        )
    });
    return out;
}

int neutral_route_quality(const NeutralTwoPhaseEosRouteResult& result) {
    if (result.accepted) {
        return 3;
    }
    if (result.solver_accepted) {
        return 2;
    }
    if (result.ran) {
        return 1;
    }
    return 0;
}

bool has_finite_complete_variables(const IpoptSolveResult& solve, int variable_count) {
    if (solve.variables.size() != static_cast<std::size_t>(variable_count)) {
        return false;
    }
    return std::all_of(solve.variables.begin(), solve.variables.end(), [](double value) {
        return std::isfinite(value);
    });
}

RouteSeedAttempt neutral_seed_attempt_from_result(
    const NeutralTwoPhaseEosRouteResult& result
) {
    RouteSeedAttempt out;
    out.seed_name = result.seed_name;
    out.status = result.status;
    out.solver_status = result.solver_status;
    out.application_status = result.application_status;
    out.solver_accepted = result.solver_accepted;
    out.accepted = result.accepted;
    out.stable = result.postsolve.stability_accepted;
    out.iteration_count = result.iteration_count;
    out.objective = result.objective;
    out.phase_distance = result.postsolve.phase_distance;
    out.material_balance_norm = result.postsolve.material_balance_norm;
    out.charge_balance_norm = result.postsolve.charge_balance_norm;
    out.pressure_consistency_norm = result.postsolve.pressure_consistency_norm;
    out.chemical_potential_consistency_norm = result.postsolve.chemical_potential_consistency_norm;
    out.phase_equilibrium_norm = result.postsolve.ln_fugacity_consistency_norm;
    out.min_tpd = result.postsolve.min_tpd;
    return out;
}

double vector_infinity_norm(const std::vector<double>& values, std::size_t begin, std::size_t end) {
    double norm = 0.0;
    for (std::size_t index = begin; index < end; ++index) {
        norm = std::max(norm, std::abs(values[index]));
    }
    return norm;
}

double phase_distance_inf_norm(const std::vector<double>& first, const std::vector<double>& second) {
    require_size(second, first.size(), "Neutral EOS postsolve phase composition");
    double distance = 0.0;
    for (std::size_t index = 0; index < first.size(); ++index) {
        distance = std::max(distance, std::abs(first[index] - second[index]));
    }
    return distance;
}

double phase_charge_inf_norm(
    const std::vector<std::vector<double>>& phase_amounts,
    const std::vector<double>& charges
) {
    if (charges.empty()) {
        return 0.0;
    }
    double norm = 0.0;
    for (const auto& phase : phase_amounts) {
        require_size(phase, charges.size(), "Electrolyte LLE phase charge");
        double charge = 0.0;
        for (std::size_t species = 0; species < charges.size(); ++species) {
            charge += phase[species] * charges[species];
        }
        norm = std::max(norm, std::abs(charge));
    }
    return norm;
}

double chemical_potential_inf_norm(
    const EosPhaseBlockResult& first,
    const EosPhaseBlockResult& second,
    std::size_t species_count
) {
    if (first.gradient.size() < species_count || second.gradient.size() < species_count) {
        throw ValueError("Neutral EOS postsolve phase gradient sizes did not match species count.");
    }
    double norm = 0.0;
    for (std::size_t species = 0; species < species_count; ++species) {
        norm = std::max(norm, std::abs(first.gradient[species] - second.gradient[species]));
    }
    return norm;
}

double charge_projected_difference_inf_norm(
    const std::vector<double>& first_values,
    const std::vector<double>& second_values,
    const std::vector<double>& charges,
    std::size_t species_count
) {
    if (charges.empty()) {
        double norm = 0.0;
        for (std::size_t species = 0; species < species_count; ++species) {
            norm = std::max(norm, std::abs(first_values[species] - second_values[species]));
        }
        return norm;
    }
    require_size(charges, species_count, "Electrolyte phase-equilibrium charge");
    double charge_square_norm = 0.0;
    double charge_weighted_difference = 0.0;
    std::vector<double> differences(species_count, 0.0);
    for (std::size_t species = 0; species < species_count; ++species) {
        differences[species] = first_values[species] - second_values[species];
        charge_square_norm += charges[species] * charges[species];
        charge_weighted_difference += charges[species] * differences[species];
    }
    const double charge_shift = charge_square_norm > 0.0
        ? -charge_weighted_difference / charge_square_norm
        : 0.0;
    double norm = 0.0;
    for (std::size_t species = 0; species < species_count; ++species) {
        norm = std::max(norm, std::abs(differences[species] + charge_shift * charges[species]));
    }
    return norm;
}

double electrochemical_potential_inf_norm(
    const EosPhaseBlockResult& first,
    const EosPhaseBlockResult& second,
    const std::vector<double>& charges,
    std::size_t species_count
) {
    if (first.gradient.size() < species_count || second.gradient.size() < species_count) {
        throw ValueError("Electrolyte EOS postsolve phase gradient sizes did not match species count.");
    }
    return charge_projected_difference_inf_norm(first.gradient, second.gradient, charges, species_count);
}

std::vector<double> reduced_ln_fugacity_values(
    const add_args& args,
    const EosPhaseBlockResult& block,
    std::size_t species_count
) {
    if (block.composition.size() < species_count) {
        throw ValueError("Neutral EOS postsolve phase composition size did not match species count.");
    }
    FugacityContributionResult fugacity = fugacity_coefficient_result_cpp(
        block.temperature,
        block.density,
        block.composition,
        args
    );
    if (fugacity.lnfugcoef.total.size() < species_count) {
        throw ValueError("Neutral EOS postsolve fugacity payload size did not match species count.");
    }
    std::vector<double> values;
    values.reserve(species_count);
    for (std::size_t species = 0; species < species_count; ++species) {
        require_positive_finite(block.composition[species], "Neutral EOS postsolve phase composition");
        values.push_back(std::log(block.composition[species]) + fugacity.lnfugcoef.total[species]);
    }
    return values;
}

double ln_fugacity_inf_norm(
    const add_args& args,
    const EosPhaseBlockResult& first,
    const EosPhaseBlockResult& second,
    std::size_t species_count,
    const std::vector<double>& charges = {}
) {
    const std::vector<double> first_values = reduced_ln_fugacity_values(args, first, species_count);
    const std::vector<double> second_values = reduced_ln_fugacity_values(args, second, species_count);
    return charge_projected_difference_inf_norm(first_values, second_values, charges, species_count);
}

double pairwise_chemical_potential_inf_norm(
    const std::vector<EosPhaseBlockResult>& phase_blocks,
    std::size_t species_count,
    const std::vector<double>& charges
) {
    double norm = 0.0;
    for (std::size_t first = 0; first < phase_blocks.size(); ++first) {
        for (std::size_t second = first + 1; second < phase_blocks.size(); ++second) {
            norm = std::max(
                norm,
                charges.empty()
                    ? chemical_potential_inf_norm(phase_blocks[first], phase_blocks[second], species_count)
                    : electrochemical_potential_inf_norm(
                        phase_blocks[first],
                        phase_blocks[second],
                        charges,
                        species_count
                    )
            );
        }
    }
    return norm;
}

double pairwise_ln_fugacity_inf_norm(
    const add_args& args,
    const std::vector<EosPhaseBlockResult>& phase_blocks,
    std::size_t species_count,
    const std::vector<double>& charges
) {
    double norm = 0.0;
    for (std::size_t first = 0; first < phase_blocks.size(); ++first) {
        for (std::size_t second = first + 1; second < phase_blocks.size(); ++second) {
            norm = std::max(
                norm,
                ln_fugacity_inf_norm(args, phase_blocks[first], phase_blocks[second], species_count, charges)
            );
        }
    }
    return norm;
}

double pairwise_phase_distance_inf_norm(const std::vector<std::vector<double>>& phase_compositions) {
    double norm = 0.0;
    for (std::size_t first = 0; first < phase_compositions.size(); ++first) {
        for (std::size_t second = first + 1; second < phase_compositions.size(); ++second) {
            norm = std::max(
                norm,
                composition_distance_inf_norm(phase_compositions[first], phase_compositions[second])
            );
        }
    }
    return norm;
}

std::vector<std::vector<double>> neutral_phase_amounts_from_route_variables(
    const std::vector<double>& variables,
    std::size_t species_count
) {
    const std::size_t local_variable_count = species_count + 1;
    require_size(variables, 2 * local_variable_count, "Neutral EOS route result variable");
    std::vector<std::vector<double>> phase_amounts(2, std::vector<double>(species_count, 0.0));
    for (std::size_t phase = 0; phase < 2; ++phase) {
        const std::size_t offset = phase * local_variable_count;
        for (std::size_t species = 0; species < species_count; ++species) {
            phase_amounts[phase][species] = variables[offset + species];
        }
    }
    return phase_amounts;
}

std::vector<double> neutral_phase_volumes_from_route_variables(
    const std::vector<double>& variables,
    std::size_t species_count
) {
    const std::size_t local_variable_count = species_count + 1;
    require_size(variables, 2 * local_variable_count, "Neutral EOS route result variable");
    return {variables[species_count], variables[local_variable_count + species_count]};
}

class NeutralTwoPhaseEosProblem final : public NlpProblem {
public:
    NeutralTwoPhaseEosProblem(
        add_args args,
        double temperature,
        double target_pressure,
        std::vector<std::vector<double>> phase_amounts,
        std::vector<double> volumes,
        std::vector<double> feed_amounts,
        std::vector<double> charges = {},
        std::string problem_name = "neutral_two_phase_eos",
        double minimum_phase_distance = 0.0
    )
        : args_(std::move(args)),
          temperature_(temperature),
          target_pressure_(target_pressure),
          initial_phase_amounts_(std::move(phase_amounts)),
          initial_volumes_(std::move(volumes)),
          feed_amounts_(std::move(feed_amounts)),
          charges_(std::move(charges)),
          problem_name_(std::move(problem_name)),
          minimum_phase_distance_(minimum_phase_distance) {
        phase_count_ = static_cast<int>(initial_phase_amounts_.size());
        if (phase_count_ < 2) {
            throw ValueError("Neutral EOS route builder requires at least two phases.");
        }
        if (!std::isfinite(temperature_) || temperature_ <= 0.0 || !std::isfinite(target_pressure_)) {
            throw ValueError("Neutral EOS route builder received invalid T/P specifications.");
        }
        species_count_ = static_cast<int>(feed_amounts_.size());
        if (species_count_ <= 0) {
            throw ValueError("Neutral EOS route builder requires at least one feed species.");
        }
        if (!charges_.empty()) {
            require_size(charges_, static_cast<std::size_t>(species_count_), "Neutral EOS route charge");
        }
        require_size(initial_volumes_, initial_phase_amounts_.size(), "Neutral EOS route volume");
        for (const auto& amounts : initial_phase_amounts_) {
            require_size(amounts, static_cast<std::size_t>(species_count_), "Neutral EOS route phase amount");
            for (double amount : amounts) {
                require_positive_finite(amount, "Neutral EOS route phase amount");
            }
        }
        for (double volume : initial_volumes_) {
            require_positive_finite(volume, "Neutral EOS route phase volume");
        }
        for (double amount : feed_amounts_) {
            if (!std::isfinite(amount) || amount < 0.0) {
                throw ValueError("Neutral EOS route feed amounts must be finite and non-negative.");
            }
        }
        if (minimum_phase_distance_ > 0.0) {
            if (phase_count_ != 2) {
                throw ValueError("Neutral EOS route phase-distance gating currently requires exactly two phases.");
            }
            const std::vector<double> first = phase_composition(
                initial_phase_amounts_[0],
                "Neutral EOS route first phase amount total"
            );
            const std::vector<double> second = phase_composition(
                initial_phase_amounts_[1],
                "Neutral EOS route second phase amount total"
            );
            double max_distance = 0.0;
            for (int species = 0; species < species_count_; ++species) {
                const double diff =
                    first[static_cast<std::size_t>(species)] - second[static_cast<std::size_t>(species)];
                if (std::abs(diff) > max_distance) {
                    max_distance = std::abs(diff);
                    separation_species_index_ = species;
                    separation_sign_ = diff >= 0.0 ? 1.0 : -1.0;
                }
            }
            if (max_distance <= 0.0) {
                throw ValueError("Neutral EOS route requires distinct initial phases for phase-separation gating.");
            }
        }
    }

    std::string name() const override {
        return problem_name_;
    }

    int variable_count() const override {
        return phase_count() * local_variable_count();
    }

    int constraint_count() const override {
        return species_count_ + phase_count() + (charges_.empty() ? 0 : phase_count())
            + separation_constraint_count();
    }

    int jacobian_nonzero_count() const override {
        const int material_nonzeros = phase_count() * species_count_;
        const int pressure_nonzeros = phase_count() * local_variable_count();
        const int charge_nonzeros = charges_.empty() ? 0 : phase_count() * species_count_;
        const int separation_nonzeros = separation_constraint_count() > 0 ? phase_count() * species_count_ : 0;
        return material_nonzeros + pressure_nonzeros + charge_nonzeros + separation_nonzeros;
    }

    NlpBounds bounds() const override {
        NlpBounds out;
        const double total_feed = std::accumulate(feed_amounts_.begin(), feed_amounts_.end(), 0.0);
        const double amount_upper = std::max(1.0, 10.0 * total_feed);
        const double volume_upper = std::max(1.0, 1.0e6 * total_feed);
        out.variable_lower.assign(static_cast<std::size_t>(variable_count()), 1.0e-14);
        out.variable_upper.reserve(static_cast<std::size_t>(variable_count()));
        for (int phase = 0; phase < phase_count(); ++phase) {
            for (int species = 0; species < species_count_; ++species) {
                out.variable_upper.push_back(amount_upper);
            }
            out.variable_upper.push_back(volume_upper);
        }
        out.constraint_lower.assign(static_cast<std::size_t>(constraint_count()), 0.0);
        out.constraint_upper.assign(static_cast<std::size_t>(constraint_count()), 0.0);
        if (separation_constraint_count() > 0) {
            out.constraint_lower.back() = minimum_phase_distance_;
            out.constraint_upper.back() = 1.0e12;
        }
        return out;
    }

    std::vector<double> initial_point() const override {
        std::vector<double> out;
        out.reserve(static_cast<std::size_t>(variable_count()));
        for (std::size_t phase = 0; phase < initial_phase_amounts_.size(); ++phase) {
            out.insert(out.end(), initial_phase_amounts_[phase].begin(), initial_phase_amounts_[phase].end());
            out.push_back(initial_volumes_[phase]);
        }
        return out;
    }

    double objective(const std::vector<double>& variables) const override {
        return phase_system(variables).objective;
    }

    std::vector<double> objective_gradient(const std::vector<double>& variables) const override {
        return phase_system(variables).gradient;
    }

    std::vector<double> constraints(const std::vector<double>& variables) const override {
        std::vector<double> out = phase_system(variables).constraints;
        if (separation_constraint_count() > 0) {
            out.push_back(phase_separation(phase_amounts_from_variables(variables)));
        }
        return out;
    }

    NlpJacobianStructure jacobian_structure() const override {
        NlpJacobianStructure out;
        out.rows.reserve(static_cast<std::size_t>(jacobian_nonzero_count()));
        out.cols.reserve(static_cast<std::size_t>(jacobian_nonzero_count()));
        for (int species = 0; species < species_count_; ++species) {
            for (int phase = 0; phase < phase_count(); ++phase) {
                out.rows.push_back(species);
                out.cols.push_back(phase * local_variable_count() + species);
            }
        }
        const int pressure_row_start = species_count_;
        for (int phase = 0; phase < phase_count(); ++phase) {
            const int row = pressure_row_start + phase;
            const int phase_offset = phase * local_variable_count();
            for (int col = 0; col < local_variable_count(); ++col) {
                out.rows.push_back(row);
                out.cols.push_back(phase_offset + col);
            }
        }
        if (!charges_.empty()) {
            const int charge_row_start = pressure_row_start + phase_count();
            for (int phase = 0; phase < phase_count(); ++phase) {
                const int row = charge_row_start + phase;
                const int phase_offset = phase * local_variable_count();
                for (int species = 0; species < species_count_; ++species) {
                    out.rows.push_back(row);
                    out.cols.push_back(phase_offset + species);
                }
            }
        }
        if (separation_constraint_count() > 0) {
            const int row = constraint_count() - 1;
            for (int phase = 0; phase < phase_count(); ++phase) {
                const int phase_offset = phase * local_variable_count();
                for (int species = 0; species < species_count_; ++species) {
                    out.rows.push_back(row);
                    out.cols.push_back(phase_offset + species);
                }
            }
        }
        return out;
    }

    std::vector<double> jacobian_values(const std::vector<double>& variables) const override {
        const EosPhaseSystemResult system = phase_system(variables);
        std::vector<double> out;
        out.reserve(static_cast<std::size_t>(jacobian_nonzero_count()));
        const int dense_cols = variable_count();
        for (int species = 0; species < species_count_; ++species) {
            for (int phase = 0; phase < phase_count(); ++phase) {
                out.push_back(
                    system.constraint_jacobian_row_major[
                        static_cast<std::size_t>(species) * static_cast<std::size_t>(dense_cols)
                        + static_cast<std::size_t>(phase * local_variable_count() + species)
                    ]
                );
            }
        }
        const int pressure_row_start = species_count_;
        for (int phase = 0; phase < phase_count(); ++phase) {
            const int row = pressure_row_start + phase;
            const int phase_offset = phase * local_variable_count();
            for (int col = 0; col < local_variable_count(); ++col) {
                out.push_back(
                    system.constraint_jacobian_row_major[
                        static_cast<std::size_t>(row) * static_cast<std::size_t>(dense_cols)
                        + static_cast<std::size_t>(phase_offset + col)
                    ]
                );
            }
        }
        if (!charges_.empty()) {
            const int charge_row_start = pressure_row_start + phase_count();
            for (int phase = 0; phase < phase_count(); ++phase) {
                const int row = charge_row_start + phase;
                const int phase_offset = phase * local_variable_count();
                for (int species = 0; species < species_count_; ++species) {
                    out.push_back(
                        system.constraint_jacobian_row_major[
                            static_cast<std::size_t>(row) * static_cast<std::size_t>(dense_cols)
                            + static_cast<std::size_t>(phase_offset + species)
                        ]
                    );
                }
            }
        }
        if (separation_constraint_count() > 0) {
            const std::vector<double> row = phase_separation_jacobian(phase_amounts_from_variables(variables));
            for (int phase = 0; phase < phase_count(); ++phase) {
                const int phase_offset = phase * local_variable_count();
                for (int species = 0; species < species_count_; ++species) {
                    out.push_back(row[static_cast<std::size_t>(phase_offset + species)]);
                }
            }
        }
        return out;
    }

    bool has_exact_hessian() const override {
        return args_.z.empty() || args_.born_model <= 1;
    }

    int hessian_nonzero_count() const override {
        return LagrangianHessianAssembler(variable_count()).nonzero_count();
    }

    NlpHessianStructure hessian_structure() const override {
        return LagrangianHessianAssembler(variable_count()).structure();
    }

    std::vector<double> hessian_values(
        const std::vector<double>& variables,
        double objective_factor,
        const std::vector<double>& constraint_multipliers
    ) const override {
        if (!has_exact_hessian()) {
            throw ValueError("Neutral EOS route exact Hessian requires direct or absent Born phase blocks.");
        }
        if (constraint_multipliers.size() != static_cast<std::size_t>(constraint_count())) {
            throw ValueError("Neutral EOS route Hessian multiplier vector size does not match the constraint count.");
        }
        const EosPhaseSystemResult system = phase_system(variables);
        if (system.objective_hessian_row_major.size()
            != static_cast<std::size_t>(variable_count() * variable_count())) {
            throw ValueError("Neutral EOS route objective Hessian shape did not match the NLP variable count.");
        }

        ObjectiveSecondOrderData objective;
        objective.variable_count = variable_count();
        objective.value = system.objective;
        objective.gradient = system.gradient;
        objective.hessian_row_major = system.objective_hessian_row_major;
        objective.backend = system.objective_hessian_backend;

        ConstraintSecondOrderData constraints;
        constraints.constraint_count = constraint_count();
        constraints.variable_count = variable_count();
        constraints.values = system.constraints;
        constraints.jacobian_row_major = system.constraint_jacobian_row_major;
        constraints.hessian_tensor_row_major.assign(
            static_cast<std::size_t>(constraint_count() * variable_count() * variable_count()),
            0.0
        );
        constraints.has_hessian.assign(static_cast<std::size_t>(constraint_count()), false);
        constraints.backend = system.constraint_hessian_backend;
        if (system.constraint_hessian_tensor_row_major.size()
            != static_cast<std::size_t>(
                system.constraint_jacobian_rows * variable_count() * variable_count()
            )) {
            throw ValueError("Neutral EOS route constraint Hessian tensor shape did not match the system constraints.");
        }
        for (int row = 0; row < system.constraint_jacobian_rows; ++row) {
            if (row >= constraint_count()) {
                throw ValueError("Neutral EOS route system constraint count exceeded the NLP constraint count.");
            }
            constraints.has_hessian[static_cast<std::size_t>(row)] =
                row < static_cast<int>(system.constraint_has_hessian.size())
                && system.constraint_has_hessian[static_cast<std::size_t>(row)];
            const std::size_t source_offset =
                static_cast<std::size_t>(row * variable_count() * variable_count());
            std::copy(
                system.constraint_hessian_tensor_row_major.begin() + static_cast<std::ptrdiff_t>(source_offset),
                system.constraint_hessian_tensor_row_major.begin()
                    + static_cast<std::ptrdiff_t>(source_offset + variable_count() * variable_count()),
                constraints.hessian_tensor_row_major.begin() + static_cast<std::ptrdiff_t>(source_offset)
            );
        }
        if (separation_constraint_count() > 0) {
            constraints.has_hessian.back() = true;
            const std::vector<double> separation_hessian =
                phase_separation_hessian(phase_amounts_from_variables(variables));
            const std::size_t offset = static_cast<std::size_t>(
                (constraint_count() - 1) * variable_count() * variable_count()
            );
            std::copy(
                separation_hessian.begin(),
                separation_hessian.end(),
                constraints.hessian_tensor_row_major.begin() + static_cast<std::ptrdiff_t>(offset)
            );
        }
        return LagrangianHessianAssembler(variable_count()).values(
            objective_factor,
            objective,
            constraints,
            constraint_multipliers
        );
    }

    std::string hessian_backend() const override {
        return "cppad_phase_system";
    }

    NlpScaling scaling() const override {
        const double total_feed = std::accumulate(feed_amounts_.begin(), feed_amounts_.end(), 0.0);
        const double amount_scale = std::max(1.0, total_feed);
        NlpScaling out;
        out.objective = 1.0 / amount_scale;
        out.variables.assign(static_cast<std::size_t>(variable_count()), 1.0 / amount_scale);
        out.constraints.assign(static_cast<std::size_t>(constraint_count()), 1.0 / amount_scale);
        if (separation_constraint_count() > 0) {
            out.constraints.back() = 1.0;
        }
        return out;
    }

    std::map<std::string, std::string> diagnostics() const override {
        return route_metadata_diagnostics(
            phase_amount_volume_route_metadata(!charges_.empty(), separation_constraint_count() > 0)
        );
    }

    int species_count() const {
        return species_count_;
    }

    int phase_count() const {
        return phase_count_;
    }

private:
    int local_variable_count() const {
        return species_count_ + 1;
    }

    int separation_constraint_count() const {
        return minimum_phase_distance_ > 0.0 ? 1 : 0;
    }

    std::vector<double> phase_composition(
        const std::vector<double>& amounts,
        const std::string& total_label
    ) const {
        require_size(amounts, static_cast<std::size_t>(species_count_), "Neutral EOS route phase amount");
        const double total = std::accumulate(amounts.begin(), amounts.end(), 0.0);
        require_positive_finite(total, total_label);
        std::vector<double> composition;
        composition.reserve(amounts.size());
        for (double amount : amounts) {
            composition.push_back(amount / total);
        }
        return composition;
    }

    double phase_separation(const std::vector<std::vector<double>>& phase_amounts) const {
        const std::vector<double> first = phase_composition(
            phase_amounts[0],
            "Neutral EOS route first phase amount total"
        );
        const std::vector<double> second = phase_composition(
            phase_amounts[1],
            "Neutral EOS route second phase amount total"
        );
        const std::size_t species = static_cast<std::size_t>(separation_species_index_);
        return separation_sign_ * (first[species] - second[species]);
    }

    std::vector<double> phase_separation_jacobian(
        const std::vector<std::vector<double>>& phase_amounts
    ) const {
        const std::vector<double> first = phase_composition(
            phase_amounts[0],
            "Neutral EOS route first phase amount total"
        );
        const std::vector<double> second = phase_composition(
            phase_amounts[1],
            "Neutral EOS route second phase amount total"
        );
        const double first_total = std::accumulate(phase_amounts[0].begin(), phase_amounts[0].end(), 0.0);
        const double second_total = std::accumulate(phase_amounts[1].begin(), phase_amounts[1].end(), 0.0);
        require_positive_finite(first_total, "Neutral EOS route first phase amount total");
        require_positive_finite(second_total, "Neutral EOS route second phase amount total");

        std::vector<double> row(static_cast<std::size_t>(variable_count()), 0.0);
        const std::size_t selected = static_cast<std::size_t>(separation_species_index_);
        for (int species = 0; species < species_count_; ++species) {
            const std::size_t index = static_cast<std::size_t>(species);
            const double first_indicator = index == selected ? 1.0 : 0.0;
            row[index] = separation_sign_ * (first_indicator - first[selected]) / first_total;

            const std::size_t second_offset = static_cast<std::size_t>(local_variable_count() + species);
            const double second_indicator = index == selected ? 1.0 : 0.0;
            row[second_offset] = -separation_sign_ * (second_indicator - second[selected]) / second_total;
        }
        return row;
    }

    std::vector<double> phase_separation_hessian(
        const std::vector<std::vector<double>>& phase_amounts
    ) const {
        if (phase_amounts.size() != static_cast<std::size_t>(phase_count())) {
            throw ValueError("Neutral EOS route phase amount phase count does not match the NLP model.");
        }
        std::vector<double> hessian(static_cast<std::size_t>(variable_count() * variable_count()), 0.0);
        const std::size_t selected = static_cast<std::size_t>(separation_species_index_);
        for (int phase = 0; phase < phase_count(); ++phase) {
            const std::vector<double> composition = phase_composition(
                phase_amounts[static_cast<std::size_t>(phase)],
                "Neutral EOS route phase amount total"
            );
            const double total = std::accumulate(
                phase_amounts[static_cast<std::size_t>(phase)].begin(),
                phase_amounts[static_cast<std::size_t>(phase)].end(),
                0.0
            );
            require_positive_finite(total, "Neutral EOS route phase amount total");
            const double phase_sign = phase == 0 ? separation_sign_ : -separation_sign_;
            const std::size_t phase_offset = static_cast<std::size_t>(phase * local_variable_count());
            for (int first = 0; first < species_count_; ++first) {
                for (int second = 0; second < species_count_; ++second) {
                    const double first_indicator =
                        static_cast<std::size_t>(first) == selected ? 1.0 : 0.0;
                    const double second_indicator =
                        static_cast<std::size_t>(second) == selected ? 1.0 : 0.0;
                    const double value = phase_sign
                        * (2.0 * composition[selected] - first_indicator - second_indicator)
                        / (total * total);
                    const std::size_t row = phase_offset + static_cast<std::size_t>(first);
                    const std::size_t col = phase_offset + static_cast<std::size_t>(second);
                    hessian[row * static_cast<std::size_t>(variable_count()) + col] = value;
                }
            }
        }
        return hessian;
    }

    std::vector<std::vector<double>> phase_amounts_from_variables(const std::vector<double>& variables) const {
        require_size(variables, static_cast<std::size_t>(variable_count()), "Neutral EOS route variable");
        std::vector<std::vector<double>> phase_amounts(
            static_cast<std::size_t>(phase_count()),
            std::vector<double>(static_cast<std::size_t>(species_count_), 0.0)
        );
        for (int phase = 0; phase < phase_count(); ++phase) {
            const std::size_t offset = static_cast<std::size_t>(phase * local_variable_count());
            for (int species = 0; species < species_count_; ++species) {
                phase_amounts[static_cast<std::size_t>(phase)][static_cast<std::size_t>(species)] =
                    variables[offset + static_cast<std::size_t>(species)];
            }
        }
        return phase_amounts;
    }

    std::vector<double> volumes_from_variables(const std::vector<double>& variables) const {
        require_size(variables, static_cast<std::size_t>(variable_count()), "Neutral EOS route variable");
        std::vector<double> volumes(static_cast<std::size_t>(phase_count()), 0.0);
        for (int phase = 0; phase < phase_count(); ++phase) {
            const std::size_t volume_index = static_cast<std::size_t>(
                phase * local_variable_count() + species_count_
            );
            volumes[static_cast<std::size_t>(phase)] = variables[volume_index];
        }
        return volumes;
    }

    EosPhaseSystemResult phase_system(const std::vector<double>& variables) const {
        return evaluate_eos_phase_system(
            args_,
            temperature_,
            target_pressure_,
            phase_amounts_from_variables(variables),
            volumes_from_variables(variables),
            feed_amounts_,
            charges_
        );
    }

    add_args args_;
    double temperature_ = 0.0;
    double target_pressure_ = 0.0;
    std::vector<std::vector<double>> initial_phase_amounts_;
    std::vector<double> initial_volumes_;
    std::vector<double> feed_amounts_;
    std::vector<double> charges_;
    std::string problem_name_;
    double minimum_phase_distance_ = 0.0;
    int separation_species_index_ = 0;
    double separation_sign_ = 1.0;
    int phase_count_ = 0;
    int species_count_ = 0;
};

NeutralTwoPhaseEosNlpContract make_nlp_contract(
    const NlpProblem& problem,
    int phase_count,
    int species_count
) {
    validate_nlp_problem_shape(problem);

    const std::vector<double> initial = problem.initial_point();
    const NlpBounds bounds = problem.bounds();
    const NlpJacobianStructure structure = problem.jacobian_structure();
    const NlpHessianStructure hessian_structure = problem.hessian_structure();
    const NlpScaling scaling = problem.scaling();
    const std::vector<double> constraints = problem.constraints(initial);
    const IdentityVariableTransform transform(problem.variable_count());
    const VariableTransformEvaluation transform_evaluation = transform.evaluate(initial);

    NeutralTwoPhaseEosNlpContract out;
    out.problem_name = problem.name();
    out.derivative_backend = "analytic_cppad";
    apply_route_metadata(out, route_metadata_from_diagnostics(problem.diagnostics()));
    out.phase_count = phase_count;
    out.species_count = species_count;
    out.variable_count = problem.variable_count();
    out.constraint_count = problem.constraint_count();
    out.jacobian_nonzero_count = problem.jacobian_nonzero_count();
    out.exact_hessian_available = problem.has_exact_hessian();
    out.hessian_nonzero_count = problem.hessian_nonzero_count();
    out.hessian_backend = problem.hessian_backend();
    out.initial_point = initial;
    out.variable_lower_bounds = bounds.variable_lower;
    out.variable_upper_bounds = bounds.variable_upper;
    out.constraint_lower_bounds = bounds.constraint_lower;
    out.constraint_upper_bounds = bounds.constraint_upper;
    out.objective_at_initial = problem.objective(initial);
    out.gradient_at_initial = problem.objective_gradient(initial);
    out.constraints_at_initial = constraints;
    out.jacobian_rows = structure.rows;
    out.jacobian_cols = structure.cols;
    out.jacobian_values_at_initial = problem.jacobian_values(initial);
    out.hessian_rows = hessian_structure.rows;
    out.hessian_cols = hessian_structure.cols;
    if (problem.has_exact_hessian()) {
        out.hessian_values_at_initial = problem.hessian_values(
            initial,
            1.0,
            std::vector<double>(static_cast<std::size_t>(problem.constraint_count()), 0.0)
        );
    }
    out.objective_scaling = scaling.objective;
    out.variable_scaling = scaling.variables;
    out.constraint_scaling = scaling.constraints;
    out.transform_policy = transform_evaluation.transform_policy;
    out.transform_backend = transform_evaluation.backend;
    out.transform_input_variable_count = transform_evaluation.input_variable_count;
    out.transform_output_variable_count = transform_evaluation.output_variable_count;
    out.transform_jacobian_value_count = static_cast<int>(transform_evaluation.jacobian_row_major.size());
    out.transform_hessian_value_count =
        static_cast<int>(transform_evaluation.output_hessian_tensor_row_major.size());
    out.initial_variable_lower_margin = std::numeric_limits<double>::infinity();
    out.initial_variable_upper_margin = std::numeric_limits<double>::infinity();
    out.initial_amount_lower_margin = std::numeric_limits<double>::infinity();
    out.initial_volume_lower_margin = std::numeric_limits<double>::infinity();
    for (int index = 0; index < problem.variable_count(); ++index) {
        const std::size_t i = static_cast<std::size_t>(index);
        const double lower_margin = initial[i] - bounds.variable_lower[i];
        const double upper_margin = bounds.variable_upper[i] - initial[i];
        out.initial_variable_lower_margin = std::min(out.initial_variable_lower_margin, lower_margin);
        out.initial_variable_upper_margin = std::min(out.initial_variable_upper_margin, upper_margin);
        const bool is_volume = species_count > 0 && (index % (species_count + 1)) == species_count;
        if (is_volume) {
            out.initial_volume_lower_margin = std::min(out.initial_volume_lower_margin, lower_margin);
        } else {
            out.initial_amount_lower_margin = std::min(out.initial_amount_lower_margin, lower_margin);
        }
    }
    out.initial_variable_bound_margin =
        std::min(out.initial_variable_lower_margin, out.initial_variable_upper_margin);
    out.initial_constraint_bound_violation = 0.0;
    for (int index = 0; index < problem.constraint_count(); ++index) {
        const std::size_t i = static_cast<std::size_t>(index);
        if (constraints[i] < bounds.constraint_lower[i]) {
            out.initial_constraint_bound_violation =
                std::max(out.initial_constraint_bound_violation, bounds.constraint_lower[i] - constraints[i]);
        }
        if (constraints[i] > bounds.constraint_upper[i]) {
            out.initial_constraint_bound_violation =
                std::max(out.initial_constraint_bound_violation, constraints[i] - bounds.constraint_upper[i]);
        }
    }
    if (!std::isfinite(out.initial_amount_lower_margin)) {
        out.initial_amount_lower_margin = 0.0;
    }
    if (!std::isfinite(out.initial_volume_lower_margin)) {
        out.initial_volume_lower_margin = 0.0;
    }
    return out;
}

}  // namespace

// AlgID: neutral_deterministic_phase_candidate_screening
NeutralPhaseDiscoveryResult evaluate_neutral_tpd_phase_discovery(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<double>& feed_composition,
    const std::vector<int>& phase_kinds,
    double tpd_tolerance,
    double candidate_mass_balance_tolerance
) {
    require_positive_finite(tpd_tolerance, "Neutral TPD tolerance");
    require_positive_finite(candidate_mass_balance_tolerance, "Neutral TPD candidate mass-balance tolerance");
    const std::vector<double> feed =
        normalized_trial_composition(feed_composition, "Neutral TPD feed composition");
    const std::vector<int> trial_phase_kinds = normalized_phase_kinds(phase_kinds, "Neutral TPD discovery");

    NeutralPhaseDiscoveryResult out;
    int valid_candidate_count = 0;
    for (int phase_kind : trial_phase_kinds) {
        try {
            const EosPhaseBlockResult reference = evaluate_unit_phase_block_at_pressure_root(
                args,
                temperature,
                target_pressure,
                feed,
                phase_kind,
                "Neutral TPD feed reference"
            );
            append_tpd_candidates_for_reference_block(
                args,
                temperature,
                target_pressure,
                reference,
                trial_phase_kinds,
                "feed_phase_kind_" + std::to_string(phase_kind),
                out.candidates,
                valid_candidate_count
            );
        } catch (const std::exception&) {
            continue;
        }
    }
    out.tpd_candidate_count = valid_candidate_count;
    out.unique_candidate_count = static_cast<int>(out.candidates.size());
    rank_tpd_candidates(out);
    out.stability_checked = out.unique_candidate_count > 0;
    out.min_tpd = out.stability_checked ? std::numeric_limits<double>::infinity() : 0.0;
    for (const NeutralTpdCandidate& candidate : out.candidates) {
        out.min_tpd = std::min(out.min_tpd, candidate.tpd);
    }
    out.stability_accepted = out.stability_checked && out.min_tpd >= -tpd_tolerance;
    select_two_phase_candidate_set(out, feed, phase_kinds, candidate_mass_balance_tolerance);
    if (!out.stability_checked) {
        out.phase_set_status = "stability_uncertified";
    } else if (!out.phase_set_mass_balance_feasible) {
        out.phase_set_status = "candidate_mass_balance_incomplete";
    } else if (out.stability_accepted) {
        out.phase_set_status = "single_phase_stable_candidate_set";
    }
    return out;
}

NeutralTwoPhaseEosNlpContract evaluate_neutral_two_phase_eos_nlp_contract(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<std::vector<double>>& phase_amounts,
    const std::vector<double>& volumes,
    const std::vector<double>& feed_amounts
) {
    NeutralTwoPhaseEosProblem problem(args, temperature, target_pressure, phase_amounts, volumes, feed_amounts);
    return make_nlp_contract(problem, problem.phase_count(), problem.species_count());
}

NeutralTwoPhaseEosNlpContract evaluate_neutral_multiphase_eos_nlp_contract(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<std::vector<double>>& phase_amounts,
    const std::vector<double>& volumes,
    const std::vector<double>& feed_amounts
) {
    NeutralTwoPhaseEosProblem problem(
        args,
        temperature,
        target_pressure,
        phase_amounts,
        volumes,
        feed_amounts,
        std::vector<double>{},
        "neutral_multiphase_eos"
    );
    return make_nlp_contract(problem, problem.phase_count(), problem.species_count());
}

std::unique_ptr<NlpProblem> make_neutral_two_phase_eos_problem(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<std::vector<double>>& phase_amounts,
    const std::vector<double>& volumes,
    const std::vector<double>& feed_amounts,
    const std::string& problem_name,
    double minimum_phase_distance
) {
    return std::make_unique<NeutralTwoPhaseEosProblem>(
        args,
        temperature,
        target_pressure,
        phase_amounts,
        volumes,
        feed_amounts,
        std::vector<double>{},
        problem_name,
        minimum_phase_distance
    );
}

std::unique_ptr<NlpProblem> make_neutral_two_phase_eos_problem_from_feed(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<double>& feed_composition,
    const std::vector<int>& phase_kinds,
    const std::string& problem_name,
    double minimum_phase_distance
) {
    const std::vector<double> feed_amounts =
        normalized_positive_values(feed_composition, problem_name + " feed composition");
    const NeutralTwoPhaseEosInitialPoint initial = build_neutral_two_phase_eos_initial_point(
        args,
        feed_amounts,
        temperature,
        target_pressure,
        problem_name,
        phase_kinds
    );
    return make_neutral_two_phase_eos_problem(
        args,
        temperature,
        target_pressure,
        initial.phase_amounts,
        initial.volumes,
        feed_amounts,
        problem_name,
        minimum_phase_distance
    );
}

IpoptSolveResult solve_neutral_two_phase_eos_ipopt(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<std::vector<double>>& phase_amounts,
    const std::vector<double>& volumes,
    const std::vector<double>& feed_amounts,
    const IpoptSolveOptions& options,
    const std::vector<double>& charges,
    const std::string& problem_name,
    double minimum_phase_distance
) {
    NeutralTwoPhaseEosProblem problem(
        args,
        temperature,
        target_pressure,
        phase_amounts,
        volumes,
        feed_amounts,
        charges,
        problem_name,
        minimum_phase_distance
    );
    return solve_ipopt_nlp(problem, options);
}

// AlgID: postsolve_tpd_certification
NeutralTwoPhaseEosPostsolve evaluate_neutral_two_phase_eos_postsolve(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<std::vector<double>>& phase_amounts,
    const std::vector<double>& volumes,
    const std::vector<double>& feed_amounts,
    double material_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance,
    const std::vector<double>& charges,
    bool phase_distance_constraint,
    bool stability_certification_required,
    std::vector<int> phase_kinds
) {
    require_positive_finite(material_tolerance, "Neutral EOS postsolve material tolerance");
    require_positive_finite(pressure_tolerance, "Neutral EOS postsolve pressure tolerance");
    require_positive_finite(
        chemical_potential_tolerance,
        "Neutral EOS postsolve chemical-potential tolerance"
    );
    require_positive_finite(phase_distance_tolerance, "Neutral EOS postsolve phase-distance tolerance");

    const EosPhaseSystemResult system = evaluate_eos_phase_system(
        args,
        temperature,
        target_pressure,
        phase_amounts,
        volumes,
        feed_amounts,
        charges
    );
    if (system.phase_count < 2) {
        throw ValueError("Neutral EOS postsolve requires at least two phases.");
    }
    if (phase_distance_constraint && system.phase_count != 2) {
        throw ValueError("Neutral EOS postsolve phase-distance constraint currently requires exactly two phases.");
    }

    NeutralTwoPhaseEosPostsolve out;
    out.derivative_backend = system.derivative_backend;
    apply_route_metadata(out, phase_amount_volume_route_metadata(!charges.empty(), phase_distance_constraint));
    out.phase_count = system.phase_count;
    out.species_count = system.species_count;
    out.objective = system.objective;
    out.constraints = system.constraints;
    out.phase_volumes = volumes;
    out.phase_amount_totals.reserve(system.phase_blocks.size());
    out.phase_compositions.reserve(system.phase_blocks.size());
    for (const EosPhaseBlockResult& block : system.phase_blocks) {
        out.phase_amount_totals.push_back(block.total_amount);
        out.phase_compositions.push_back(block.composition);
    }

    const std::size_t species_count = static_cast<std::size_t>(system.species_count);
    out.material_balance_norm = vector_infinity_norm(system.constraints, 0, species_count);
    out.pressure_consistency_norm = vector_infinity_norm(
        system.constraints,
        species_count,
        species_count + static_cast<std::size_t>(system.phase_count)
    );
    out.chemical_potential_consistency_norm =
        pairwise_chemical_potential_inf_norm(system.phase_blocks, species_count, charges);
    out.ln_fugacity_consistency_norm =
        pairwise_ln_fugacity_inf_norm(args, system.phase_blocks, species_count, charges);
    out.phase_distance = pairwise_phase_distance_inf_norm(out.phase_compositions);
    out.stability_checked = false;
    out.stability_accepted = !stability_certification_required;
    out.candidate_completeness_accepted = !stability_certification_required;
    out.phase_set_mass_balance_feasible = !stability_certification_required;
    out.phase_discovery_backend = stability_certification_required
        ? "deterministic_tpd_candidate_screening"
        : "deterministic_seed_sweep";
    out.stability_certificate = stability_certification_required
        ? "tpd_postsolve"
        : "postsolve_local_only";
    out.phase_set_status = stability_certification_required ? "not_checked" : "not_required";

    const double effective_chemical_tolerance = charges.empty()
        ? chemical_potential_tolerance
        : std::max(chemical_potential_tolerance, 2.0 * std::sqrt(chemical_potential_tolerance));
    out.accepted = out.material_balance_norm <= material_tolerance
        && out.pressure_consistency_norm <= pressure_tolerance
        && out.chemical_potential_consistency_norm <= effective_chemical_tolerance
        && out.ln_fugacity_consistency_norm <= effective_chemical_tolerance
        && (!phase_distance_constraint || out.phase_distance >= phase_distance_tolerance);
    if (out.accepted) {
        out.rejection_reason = "accepted";
    } else if (out.material_balance_norm > material_tolerance) {
        out.rejection_reason = "material_balance";
    } else if (out.pressure_consistency_norm > pressure_tolerance) {
        out.rejection_reason = "pressure_consistency";
    } else if (out.chemical_potential_consistency_norm > effective_chemical_tolerance) {
        out.rejection_reason = "chemical_potential_consistency";
    } else if (out.ln_fugacity_consistency_norm > effective_chemical_tolerance) {
        out.rejection_reason = "ln_fugacity_consistency";
    } else if (phase_distance_constraint) {
        out.rejection_reason = "phase_distance";
    } else {
        out.rejection_reason = "phase_set_not_certified";
    }
    if (out.accepted && stability_certification_required) {
        if (!charges.empty()) {
            out.accepted = false;
            out.rejection_reason = "stability_tpd";
            out.phase_set_status = "neutral_tpd_not_valid_for_charged_system";
            return out;
        }
        if (phase_kinds.empty()) {
            phase_kinds.assign(static_cast<std::size_t>(system.phase_count), 0);
        }
        if (phase_kinds.size() != static_cast<std::size_t>(system.phase_count)) {
            throw ValueError("Neutral EOS postsolve phase kind size does not match the accepted phase set.");
        }
        const double tpd_tolerance = std::max(1.0e-6, 100.0 * chemical_potential_tolerance);
        const double candidate_mass_balance_tolerance = std::max(1.0e-8, 10.0 * material_tolerance);
        const NeutralPhaseDiscoveryResult discovery = certify_neutral_phase_set(
            args,
            temperature,
            target_pressure,
            system,
            feed_amounts,
            phase_kinds,
            tpd_tolerance,
            candidate_mass_balance_tolerance
        );
        copy_discovery_to_postsolve(out, discovery);
        if (!out.stability_checked) {
            out.accepted = false;
            out.rejection_reason = "candidate_completeness";
        } else if (!out.stability_accepted) {
            out.accepted = false;
            out.rejection_reason = "stability_tpd";
        } else if (!out.candidate_completeness_accepted) {
            out.accepted = false;
            out.rejection_reason = "candidate_completeness";
        } else {
            out.rejection_reason = "accepted";
        }
    }
    return out;
}

NeutralTwoPhaseEosPostsolve evaluate_neutral_multiphase_eos_postsolve(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<std::vector<double>>& phase_amounts,
    const std::vector<double>& volumes,
    const std::vector<double>& feed_amounts,
    double material_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance,
    const std::vector<int>& phase_kinds
) {
    return evaluate_neutral_two_phase_eos_postsolve(
        args,
        temperature,
        target_pressure,
        phase_amounts,
        volumes,
        feed_amounts,
        material_tolerance,
        pressure_tolerance,
        chemical_potential_tolerance,
        phase_distance_tolerance,
        {},
        false,
        true,
        phase_kinds
    );
}

NeutralTwoPhaseEosRouteResult solve_neutral_two_phase_eos_route(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<std::vector<double>>& phase_amounts,
    const std::vector<double>& volumes,
    const std::vector<double>& feed_amounts,
    const IpoptSolveOptions& options,
    double material_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance,
    double minimum_phase_distance,
    const std::vector<double>& charges,
    const std::string& problem_name,
    double charge_tolerance
) {
    if (!charges.empty()) {
        require_positive_finite(charge_tolerance, problem_name + " charge tolerance");
    }
    const IpoptAdapterInfo adapter = native_ipopt_adapter_info();
    NeutralTwoPhaseEosRouteResult out;
    out.compiled = adapter.compiled;
    out.adapter_available = adapter.adapter_available;
    out.adapter_kind = adapter.adapter_kind;
    out.exact_gradient_required = adapter.exact_gradient_required;
    out.exact_jacobian_required = adapter.exact_jacobian_required;
    out.problem_name = problem_name;
    apply_route_metadata(out, phase_amount_volume_route_metadata(!charges.empty(), minimum_phase_distance > 0.0));
    if (!adapter.compiled) {
        out.status = "ipopt_dependency_required";
        return out;
    }

    const IpoptSolveResult solve = solve_neutral_two_phase_eos_ipopt(
        args,
        temperature,
        target_pressure,
        phase_amounts,
        volumes,
        feed_amounts,
        options,
        charges,
        problem_name,
        minimum_phase_distance
    );
    out.ran = solve.solver_ran;
    out.solver_accepted = solve.accepted;
    out.solver_status = solve.solver_status;
    out.application_status = solve.application_status;
    apply_ipopt_solve_metadata(out, solve);
    const auto last_exception = solve.diagnostics_string.find("last_callback_exception");
    if (last_exception != solve.diagnostics_string.end()) {
        out.last_callback_exception = last_exception->second;
    }
    out.objective = solve.objective;
    out.variables = solve.variables;
    out.constraints = solve.constraints;
    if (!solve.accepted) {
        out.status = "solver_rejected";
        return out;
    }

    const std::size_t species_count = feed_amounts.size();
    out.phase_amounts = neutral_phase_amounts_from_route_variables(solve.variables, species_count);
    out.phase_volumes = neutral_phase_volumes_from_route_variables(solve.variables, species_count);
    out.postsolve = evaluate_neutral_two_phase_eos_postsolve(
        args,
        temperature,
        target_pressure,
        out.phase_amounts,
        out.phase_volumes,
        feed_amounts,
        material_tolerance,
        pressure_tolerance,
        chemical_potential_tolerance,
        phase_distance_tolerance,
        charges,
        minimum_phase_distance > 0.0
    );
    if (!charges.empty()) {
        out.postsolve.charge_balance_norm = phase_charge_inf_norm(out.phase_amounts, charges);
        out.postsolve.accepted = out.postsolve.accepted && out.postsolve.charge_balance_norm <= charge_tolerance;
        if (out.postsolve.charge_balance_norm > charge_tolerance) {
            out.postsolve.rejection_reason = "charge_balance";
        }
    }
    out.accepted = out.postsolve.accepted;
    out.status = out.accepted ? "accepted" : "postsolve_rejected";
    return out;
}

// AlgID: neutral_lle_ipopt
NeutralTwoPhaseEosRouteResult solve_activated_neutral_lle_eos_route(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<double>& feed_composition,
    const IpoptSolveOptions& options,
    double material_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance
) {
    const std::string problem_name = "neutral_lle_eos";
    const epcsaft::native::equilibrium::ActivationPlan plan =
        epcsaft::native::equilibrium::build_neutral_lle_activation_plan(
            args,
            temperature,
            target_pressure,
            feed_composition
        );
    const epcsaft::native::equilibrium::VariableLayout layout =
        epcsaft::native::equilibrium::build_variable_layout(
            plan,
            static_cast<int>(plan.feed_composition.size())
        );
    const IpoptAdapterInfo adapter = native_ipopt_adapter_info();
    NeutralTwoPhaseEosRouteResult best;
    best.compiled = adapter.compiled;
    best.adapter_available = adapter.adapter_available;
    best.adapter_kind = adapter.adapter_kind;
    best.exact_gradient_required = adapter.exact_gradient_required;
    best.exact_jacobian_required = adapter.exact_jacobian_required;
    best.problem_name = problem_name;
    best.activation_compiler = "activation_plan";
    apply_route_metadata(best, phase_amount_volume_route_metadata(false, true));
    if (!adapter.compiled) {
        best.status = "ipopt_dependency_required";
        return best;
    }

    const std::vector<double>& normalized_feed = plan.feed_composition;
    const std::vector<double> feed_amounts = normalized_feed;
    const std::vector<NamedInitialVariables> seeds = neutral_two_phase_seed_candidates(
        args,
        feed_amounts,
        {},
        temperature,
        target_pressure,
        problem_name,
        {0, 0}
    );
    bool have_best = false;
    std::vector<RouteSeedAttempt> attempts;
    attempts.reserve(seeds.size() + (options.initial_variables.empty() ? 0 : 1));

    auto run_attempt = [&](const std::string& seed_name, const IpoptSolveOptions& attempt_options) {
        ActivatedEquilibriumNlp problem(args, plan, layout);
        const IpoptSolveResult solve = solve_ipopt_nlp(problem, attempt_options);
        NeutralTwoPhaseEosRouteResult result;
        result.compiled = adapter.compiled;
        result.adapter_available = adapter.adapter_available;
        result.adapter_kind = adapter.adapter_kind;
        result.exact_gradient_required = adapter.exact_gradient_required;
        result.exact_jacobian_required = adapter.exact_jacobian_required;
        result.problem_name = problem_name;
        result.activation_compiler = "activation_plan";
        result.initial_point_strategy = "deterministic_seed_sweep";
        result.seed_name = seed_name;
        result.ran = solve.solver_ran;
        const bool can_postsolve =
            solve.accepted || solve.feasible_point || has_finite_complete_variables(solve, problem.variable_count());
        result.solver_accepted = can_postsolve;
        result.solver_feasible_point = solve.feasible_point;
        result.solver_status = solve.solver_status;
        result.application_status = solve.application_status;
        apply_ipopt_solve_metadata(result, solve);
        result.objective = solve.objective;
        result.variables = solve.variables;
        result.constraints = solve.constraints;
        apply_route_metadata(result, phase_amount_volume_route_metadata(false, true));
        if (!can_postsolve) {
            result.status = "solver_rejected";
            attempts.push_back(neutral_seed_attempt_from_result(result));
            if (!have_best || neutral_route_quality(result) > neutral_route_quality(best)) {
                best = result;
                have_best = true;
            }
            return result;
        }

        result.phase_amounts = neutral_phase_amounts_from_route_variables(
            solve.variables,
            static_cast<std::size_t>(layout.species_count)
        );
        result.phase_volumes = neutral_phase_volumes_from_route_variables(
            solve.variables,
            static_cast<std::size_t>(layout.species_count)
        );
        result.postsolve = evaluate_neutral_two_phase_eos_postsolve(
            args,
            temperature,
            target_pressure,
            result.phase_amounts,
            result.phase_volumes,
            feed_amounts,
            material_tolerance,
            pressure_tolerance,
            chemical_potential_tolerance,
            phase_distance_tolerance,
            {},
            true,
            true,
            {0, 0}
        );
        result.accepted = result.postsolve.accepted;
        result.status = certified_postsolve_status(result.postsolve);
        attempts.push_back(neutral_seed_attempt_from_result(result));
        if (!have_best || neutral_route_quality(result) > neutral_route_quality(best)) {
            best = result;
            have_best = true;
        }
        return result;
    };

    if (!options.initial_variables.empty()) {
        const NeutralTwoPhaseEosRouteResult continuation = run_attempt("continuation_state", options);
        if (continuation.accepted) {
            best.seed_attempts = attempts;
            return best;
        }
    }

    if (seeds.empty()) {
        throw ValueError(problem_name + " could not construct a deterministic LLE seed.");
    }
    for (const auto& seed : seeds) {
        IpoptSolveOptions attempt_options = options;
        attempt_options.initial_variables = seed.variables;
        attempt_options.initial_bound_lower_multipliers.clear();
        attempt_options.initial_bound_upper_multipliers.clear();
        attempt_options.initial_constraint_multipliers.clear();
        const NeutralTwoPhaseEosRouteResult attempt = run_attempt(seed.seed_name, attempt_options);
        if (attempt.accepted) {
            break;
        }
    }

    best.initial_point_strategy = "deterministic_seed_sweep";
    best.seed_attempts = attempts;
    return best;
}

}  // namespace epcsaft::native::equilibrium_nlp
