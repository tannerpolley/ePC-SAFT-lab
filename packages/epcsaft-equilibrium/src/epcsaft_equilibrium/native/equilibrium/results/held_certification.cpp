#include "equilibrium/results/held_certification.h"

#include "equilibrium/results/result_builder.h"

#include <algorithm>
#include <cmath>
#include <limits>
#include <vector>

namespace epcsaft::native::equilibrium_nlp {

namespace {

constexpr double kEvidenceConsistencyTolerance = 1.0e-12;
constexpr double kCompositionNormalizationTolerance = 1.0e-8;

bool evidence_values_close(double first, double second) {
    if (!std::isfinite(first) || !std::isfinite(second)) {
        return false;
    }
    const double scale = std::max({1.0, std::abs(first), std::abs(second)});
    return std::abs(first - second) <= kEvidenceConsistencyTolerance * scale;
}

bool finite_values(const std::vector<double>& values) {
    return !values.empty()
        && std::all_of(values.begin(), values.end(), [](double value) { return std::isfinite(value); });
}

bool normalized_composition(const std::vector<double>& composition) {
    if (composition.empty()) {
        return false;
    }
    double total = 0.0;
    for (double value : composition) {
        if (!std::isfinite(value) || value < 0.0) {
            return false;
        }
        total += value;
    }
    return std::isfinite(total) && std::abs(total - 1.0) <= kCompositionNormalizationTolerance;
}

bool normalized_phase_fractions(const std::vector<double>& fractions) {
    if (fractions.size() < 2) {
        return false;
    }
    double total = 0.0;
    for (double value : fractions) {
        if (!std::isfinite(value) || value <= 0.0) {
            return false;
        }
        total += value;
    }
    return std::isfinite(total) && std::abs(total - 1.0) <= kCompositionNormalizationTolerance;
}

bool composition_vectors_equal(
    const std::vector<double>& first,
    const std::vector<double>& second
) {
    if (first.size() != second.size()) {
        return false;
    }
    for (std::size_t species = 0; species < first.size(); ++species) {
        if (!evidence_values_close(first[species], second[species])) {
            return false;
        }
    }
    return true;
}

bool composition_vectors_equal(
    const std::vector<std::vector<double>>& first,
    const std::vector<std::vector<double>>& second
) {
    if (first.size() != second.size()) {
        return false;
    }
    for (std::size_t phase = 0; phase < first.size(); ++phase) {
        if (!composition_vectors_equal(first[phase], second[phase])) {
            return false;
        }
    }
    return true;
}

bool composition_shapes_equal(
    const std::vector<std::vector<double>>& first,
    const std::vector<std::vector<double>>& second
) {
    if (first.size() != second.size()) {
        return false;
    }
    for (std::size_t phase = 0; phase < first.size(); ++phase) {
        if (first[phase].size() != second[phase].size()) {
            return false;
        }
    }
    return true;
}

bool unique_nonnegative_ranks(std::vector<int> ranks) {
    if (std::any_of(ranks.begin(), ranks.end(), [](int rank) { return rank < 0; })) {
        return false;
    }
    std::sort(ranks.begin(), ranks.end());
    return std::adjacent_find(ranks.begin(), ranks.end()) == ranks.end();
}

bool unique_nonempty_strings(const std::vector<std::string>& values) {
    if (values.empty() || std::any_of(values.begin(), values.end(), [](const std::string& value) {
            return value.empty();
        })) {
        return false;
    }
    std::vector<std::string> sorted_values = values;
    std::sort(sorted_values.begin(), sorted_values.end());
    return std::adjacent_find(sorted_values.begin(), sorted_values.end()) == sorted_values.end();
}

double phase_distance_inf_norm(const std::vector<std::vector<double>>& compositions) {
    if (compositions.size() < 2) {
        return 0.0;
    }
    const std::size_t species_count = compositions.front().size();
    double distance = 0.0;
    for (const std::vector<double>& composition : compositions) {
        if (composition.size() != species_count || !normalized_composition(composition)) {
            return std::numeric_limits<double>::infinity();
        }
    }
    for (std::size_t first = 0; first < compositions.size(); ++first) {
        for (std::size_t second = first + 1; second < compositions.size(); ++second) {
            for (std::size_t species = 0; species < species_count; ++species) {
                distance = std::max(
                    distance,
                    std::abs(compositions[first][species] - compositions[second][species])
                );
            }
        }
    }
    return distance;
}

bool held_stage_ii_bound_evidence_complete(const NeutralPhaseDiscoveryResult& discovery) {
    if (
        discovery.held_stage_ii_major_iterations <= 0
        || !std::isfinite(discovery.held_stage_ii_lower_bound)
        || !std::isfinite(discovery.held_stage_ii_upper_bound)
        || !std::isfinite(discovery.held_stage_ii_bound_gap)
        || !std::isfinite(discovery.held_stage_ii_bound_tolerance)
        || discovery.held_stage_ii_upper_bound < discovery.held_stage_ii_lower_bound
        || discovery.held_stage_ii_bound_gap < 0.0
        || discovery.held_stage_ii_bound_tolerance < 0.0
    ) {
        return false;
    }
    const double expected_gap = discovery.held_stage_ii_upper_bound - discovery.held_stage_ii_lower_bound;
    if (!evidence_values_close(discovery.held_stage_ii_bound_gap, expected_gap)) {
        return false;
    }
    const std::size_t history_size = discovery.held_stage_ii_lower_bound_history.size();
    const bool history_omitted = history_size == 0
        && discovery.held_stage_ii_upper_bound_history.empty()
        && discovery.held_stage_ii_bound_gap_history.empty();
    if (history_omitted) {
        return true;
    }
    if (
        history_size != static_cast<std::size_t>(discovery.held_stage_ii_major_iterations)
        || discovery.held_stage_ii_upper_bound_history.size() != history_size
        || discovery.held_stage_ii_bound_gap_history.size() != history_size
    ) {
        return false;
    }
    for (std::size_t index = 0; index < history_size; ++index) {
        const double lower = discovery.held_stage_ii_lower_bound_history[index];
        const double upper = discovery.held_stage_ii_upper_bound_history[index];
        const double gap = discovery.held_stage_ii_bound_gap_history[index];
        if (
            !std::isfinite(lower)
            || !std::isfinite(upper)
            || !std::isfinite(gap)
            || upper < lower
            || gap < 0.0
            || !evidence_values_close(gap, upper - lower)
        ) {
            return false;
        }
    }
    return evidence_values_close(
        discovery.held_stage_ii_lower_bound_history.back(),
        discovery.held_stage_ii_lower_bound
    ) && evidence_values_close(
        discovery.held_stage_ii_upper_bound_history.back(),
        discovery.held_stage_ii_upper_bound
    ) && evidence_values_close(
        discovery.held_stage_ii_bound_gap_history.back(),
        discovery.held_stage_ii_bound_gap
    );
}

bool held_stage_ii_replay_evidence_complete(const NeutralPhaseDiscoveryResult& discovery) {
    const std::size_t candidate_count = discovery.candidates.size();
    if (
        candidate_count < 2
        || discovery.unique_candidate_count != static_cast<int>(candidate_count)
        || discovery.held_stage_ii_candidate_count != static_cast<int>(candidate_count)
        || discovery.held_stage_ii_replay_candidate_count != static_cast<int>(candidate_count)
        || discovery.selected_candidate_count < 2
        || discovery.selected_candidate_count > static_cast<int>(candidate_count)
    ) {
        return false;
    }

    std::vector<int> candidate_ranks;
    std::vector<int> selected_ranks;
    std::vector<int> rejected_ranks;
    std::vector<const NeutralTpdCandidate*> selected_candidates;
    candidate_ranks.reserve(candidate_count);
    selected_ranks.reserve(static_cast<std::size_t>(discovery.selected_candidate_count));
    rejected_ranks.reserve(candidate_count - static_cast<std::size_t>(discovery.selected_candidate_count));
    selected_candidates.reserve(static_cast<std::size_t>(discovery.selected_candidate_count));
    for (const NeutralTpdCandidate& candidate : discovery.candidates) {
        candidate_ranks.push_back(candidate.candidate_rank);
        if (!candidate.selected) {
            rejected_ranks.push_back(candidate.candidate_rank);
            continue;
        }
        if (
            !candidate.valid
            || candidate.candidate_rank < 0
            || candidate.source.empty()
            || (candidate.phase_kind != 0 && candidate.phase_kind != 1)
            || !std::isfinite(candidate.tpd)
            || !normalized_composition(candidate.composition)
        ) {
            return false;
        }
        selected_ranks.push_back(candidate.candidate_rank);
        selected_candidates.push_back(&candidate);
    }
    if (
        selected_ranks.size() != static_cast<std::size_t>(discovery.selected_candidate_count)
        || !unique_nonnegative_ranks(candidate_ranks)
    ) {
        return false;
    }
    std::vector<int> replay_ranks = discovery.held_stage_ii_replay_candidate_ranks;
    std::sort(selected_ranks.begin(), selected_ranks.end());
    std::sort(replay_ranks.begin(), replay_ranks.end());
    if (selected_ranks != replay_ranks) {
        return false;
    }

    const std::size_t selected_count = static_cast<std::size_t>(discovery.selected_candidate_count);
    if (
        discovery.selected_phase_fractions.size() != selected_count
        || discovery.selected_phase_kinds.size() != selected_count
        || discovery.selected_phase_compositions.size() != selected_count
        || discovery.held_stage_ii_replay_phase_fractions.size() != selected_count
        || discovery.held_stage_ii_replay_phase_kinds.size() != selected_count
        || discovery.held_stage_ii_replay_phase_compositions.size() != selected_count
        || !normalized_phase_fractions(discovery.held_stage_ii_replay_phase_fractions)
        || discovery.selected_phase_kinds != discovery.held_stage_ii_replay_phase_kinds
        || !composition_vectors_equal(
            discovery.selected_phase_compositions,
            discovery.held_stage_ii_replay_phase_compositions
        )
    ) {
        return false;
    }
    std::vector<bool> matched_candidates(selected_count, false);
    for (std::size_t phase = 0; phase < selected_count; ++phase) {
        if (
            (discovery.held_stage_ii_replay_phase_kinds[phase] != 0
             && discovery.held_stage_ii_replay_phase_kinds[phase] != 1)
            || !evidence_values_close(
                discovery.selected_phase_fractions[phase],
                discovery.held_stage_ii_replay_phase_fractions[phase]
            )
            || !normalized_composition(discovery.held_stage_ii_replay_phase_compositions[phase])
        ) {
            return false;
        }
        bool matched = false;
        for (std::size_t candidate = 0; candidate < selected_count; ++candidate) {
            if (
                !matched_candidates[candidate]
                && selected_candidates[candidate]->phase_kind
                    == discovery.held_stage_ii_replay_phase_kinds[phase]
                && composition_vectors_equal(
                    selected_candidates[candidate]->composition,
                    discovery.held_stage_ii_replay_phase_compositions[phase]
                )
            ) {
                matched_candidates[candidate] = true;
                matched = true;
                break;
            }
        }
        if (!matched) {
            return false;
        }
    }

    const int rejected_count = static_cast<int>(candidate_count) - discovery.selected_candidate_count;
    std::vector<int> reported_rejected_ranks = discovery.held_stage_ii_rejected_candidate_ranks;
    std::sort(rejected_ranks.begin(), rejected_ranks.end());
    std::sort(reported_rejected_ranks.begin(), reported_rejected_ranks.end());
    return discovery.held_stage_ii_rejected_candidate_count == rejected_count
        && reported_rejected_ranks == rejected_ranks
        && discovery.held_stage_ii_rejected_candidate_reasons.size()
            == static_cast<std::size_t>(rejected_count)
        && std::all_of(
            discovery.held_stage_ii_rejected_candidate_reasons.begin(),
            discovery.held_stage_ii_rejected_candidate_reasons.end(),
            [](const std::string& reason) { return !reason.empty(); }
        );
}

}  // namespace

void certify_held_stage_i_evidence(
    NeutralPhaseDiscoveryResult& discovery,
    double tpd_tolerance,
    bool continuous_tpd_required,
    HeldStageICertificateUse certificate_use
) {
    discovery.held_stage_i_start_count = discovery.continuous_tpd_start_count;
    discovery.held_stage_i_min_tpd = discovery.continuous_tpd_min;
    const bool continuous_tpd_complete =
        discovery.continuous_tpd_status == "converged"
        || discovery.continuous_tpd_status == "complete_with_rejected_starts";
    const bool valid_tpd_evidence =
        continuous_tpd_complete
        && std::isfinite(tpd_tolerance)
        && tpd_tolerance >= 0.0
        && std::isfinite(discovery.continuous_tpd_min);
    discovery.held_stage_i_negative_tpd_found =
        continuous_tpd_required
        && valid_tpd_evidence
        && discovery.continuous_tpd_min < -tpd_tolerance;

    if (!continuous_tpd_required) {
        discovery.held_stage_i_status = "not_requested";
    } else if (discovery.continuous_tpd_solve_count == 0) {
        discovery.held_stage_i_status = "inconclusive_no_continuous_tpd_solution";
    } else if (!valid_tpd_evidence) {
        discovery.held_stage_i_status = "inconclusive_continuous_tpd_iteration_limit";
    } else if (certificate_use == HeldStageICertificateUse::Held2ConsumedEvidence) {
        discovery.held_stage_i_status = discovery.held_stage_i_negative_tpd_found
            ? "stage_i_negative_tpd_certificate_consumed"
            : "stage_i_no_negative_tpd_certificate_consumed";
    } else {
        discovery.held_stage_i_status = discovery.held_stage_i_negative_tpd_found
            ? "negative_tpd_candidate_found"
            : "no_negative_tpd_candidate_found";
    }
}

void complete_sampled_candidate_bound_audit(
    NeutralPhaseDiscoveryResult& discovery,
    bool continuous_tpd_required
) {
    discovery.held_stage_ii_replay_ready = false;
    discovery.held_stage_ii_replay_source.clear();
    discovery.held_stage_ii_replay_seed_name.clear();

    if (!continuous_tpd_required) {
        discovery.held_stage_ii_status = "not_requested";
        discovery.held_stage_ii_candidate_bound_audit_status = "not_requested";
        discovery.held_stage_ii_dual_loop_status = "not_requested";
        discovery.held_stage_ii_stopping_reason = "not_requested";
        return;
    }

    const bool continuous_tpd_complete =
        discovery.continuous_tpd_status == "converged"
        || discovery.continuous_tpd_status == "complete_with_rejected_starts";
    if (!continuous_tpd_complete) {
        discovery.held_stage_ii_status = "incomplete_stage_i_evidence";
        discovery.held_stage_ii_candidate_bound_audit_status = "incomplete_stage_i_evidence";
        discovery.held_stage_ii_dual_loop_status = "not_performed";
        discovery.held_stage_ii_stopping_reason = "stage_i_incomplete";
        return;
    }
    if (discovery.candidates.empty()) {
        discovery.held_stage_ii_status = "inconclusive_no_candidates";
        discovery.held_stage_ii_candidate_bound_audit_status = "inconclusive_no_candidates";
        discovery.held_stage_ii_dual_loop_status = "not_performed";
        discovery.held_stage_ii_stopping_reason = "no_candidates";
        return;
    }
    if (
        discovery.held_stage_ii_major_iterations <= 0
        || !std::isfinite(discovery.held_stage_ii_lower_bound)
        || !std::isfinite(discovery.held_stage_ii_upper_bound)
    ) {
        discovery.held_stage_ii_status = "inconclusive_no_finite_candidate_bound";
        discovery.held_stage_ii_candidate_bound_audit_status =
            "inconclusive_no_finite_candidate_bound";
        discovery.held_stage_ii_dual_loop_status = "not_performed";
        discovery.held_stage_ii_stopping_reason = "no_finite_candidate_bound";
        return;
    }
    if (!discovery.phase_set_mass_balance_feasible || discovery.selected_candidate_count < 2) {
        discovery.held_stage_ii_status = "candidate_simplex_mass_balance_incomplete";
        discovery.held_stage_ii_candidate_bound_audit_status =
            "candidate_simplex_mass_balance_incomplete";
        discovery.held_stage_ii_dual_loop_status = "not_performed";
        discovery.held_stage_ii_stopping_reason = "candidate_simplex_mass_balance_incomplete";
        return;
    }

    const bool bound_gap_closed = held_stage_ii_bound_evidence_complete(discovery)
        && discovery.held_stage_ii_bound_gap <= discovery.held_stage_ii_bound_tolerance;
    if (!bound_gap_closed) {
        discovery.held_stage_ii_candidate_bound_audit_status = "candidate_bound_gap_open";
        discovery.held_stage_ii_status = "sampled_candidate_audit_incomplete";
        discovery.held_stage_ii_dual_loop_status = "not_performed";
        discovery.held_stage_ii_stopping_reason = "sampled_candidate_bound_gap_open";
        return;
    }

    discovery.held_stage_ii_candidate_bound_audit_status = "candidate_bound_gap_closed";
    if (!held_stage_ii_replay_evidence_complete(discovery)) {
        discovery.held_stage_ii_status = "sampled_candidate_audit_incomplete";
        discovery.held_stage_ii_dual_loop_status = "not_performed";
        discovery.held_stage_ii_stopping_reason = "sampled_candidate_replay_metadata_incomplete";
        return;
    }
    discovery.held_stage_ii_status = "sampled_candidate_audit_complete";
    discovery.held_stage_ii_dual_loop_status = "not_performed";
    discovery.held_stage_ii_stopping_reason = "sampled_candidate_bound_gap_closed";
    discovery.held_stage_ii_replay_ready = true;
    discovery.held_stage_ii_replay_source = "sampled_candidate_audit_selected_candidates";
    discovery.held_stage_ii_replay_seed_name = discovery.selected_candidate_count == 2
        ? kSampledCandidatePairReplaySeedName
        : kSampledCandidateSetReplaySeedName;
}

bool sampled_candidate_replay_is_valid(const NeutralPhaseDiscoveryResult& discovery) {
    return discovery.held_stage_ii_replay_ready
        && discovery.held_stage_ii_status == "sampled_candidate_audit_complete"
        && discovery.held_stage_ii_candidate_bound_audit_status == "candidate_bound_gap_closed"
        && discovery.held_stage_ii_dual_loop_status == "not_performed"
        && discovery.held_stage_ii_replay_source == "sampled_candidate_audit_selected_candidates"
        && !discovery.held_stage_ii_replay_seed_name.empty()
        && held_stage_ii_bound_evidence_complete(discovery)
        && held_stage_ii_replay_evidence_complete(discovery);
}

void certify_held_stage_ii_bound_audit(
    NeutralPhaseDiscoveryResult& discovery,
    bool continuous_tpd_required
) {
    discovery.held_stage_ii_replay_ready = false;
    discovery.held_stage_ii_replay_source.clear();
    discovery.held_stage_ii_replay_seed_name.clear();

    if (!continuous_tpd_required) {
        discovery.held_stage_ii_status = "not_requested";
        discovery.held_stage_ii_candidate_bound_audit_status = "not_requested";
        discovery.held_stage_ii_dual_loop_status = "not_requested";
        discovery.held_stage_ii_stopping_reason = "not_requested";
        return;
    }

    const bool continuous_tpd_complete =
        discovery.continuous_tpd_status == "converged"
        || discovery.continuous_tpd_status == "complete_with_rejected_starts";
    if (!continuous_tpd_complete) {
        discovery.held_stage_ii_status = "incomplete_stage_i_evidence";
        discovery.held_stage_ii_candidate_bound_audit_status = "incomplete_stage_i_evidence";
        discovery.held_stage_ii_dual_loop_status = "incomplete_stage_i_evidence";
        discovery.held_stage_ii_stopping_reason = "stage_i_incomplete";
        return;
    }
    if (discovery.candidates.empty()) {
        discovery.held_stage_ii_status = "inconclusive_no_candidates";
        discovery.held_stage_ii_candidate_bound_audit_status = "inconclusive_no_candidates";
        discovery.held_stage_ii_dual_loop_status = "inconclusive_no_candidates";
        discovery.held_stage_ii_stopping_reason = "no_candidates";
        return;
    }
    if (
        discovery.held_stage_ii_major_iterations <= 0
        || !std::isfinite(discovery.held_stage_ii_lower_bound)
        || !std::isfinite(discovery.held_stage_ii_upper_bound)
    ) {
        discovery.held_stage_ii_status = "inconclusive_no_finite_candidate_bound";
        discovery.held_stage_ii_candidate_bound_audit_status =
            "inconclusive_no_finite_candidate_bound";
        discovery.held_stage_ii_dual_loop_status = "inconclusive_no_finite_candidate_bound";
        discovery.held_stage_ii_stopping_reason = "no_finite_candidate_bound";
        return;
    }
    if (!discovery.phase_set_mass_balance_feasible || discovery.selected_candidate_count < 2) {
        discovery.held_stage_ii_status = "candidate_simplex_mass_balance_incomplete";
        discovery.held_stage_ii_candidate_bound_audit_status =
            "candidate_simplex_mass_balance_incomplete";
        discovery.held_stage_ii_dual_loop_status = "candidate_simplex_mass_balance_incomplete";
        discovery.held_stage_ii_stopping_reason = "candidate_simplex_mass_balance_incomplete";
        return;
    }

    const bool bound_gap_closed = held_stage_ii_bound_evidence_complete(discovery)
        && discovery.held_stage_ii_bound_gap <= discovery.held_stage_ii_bound_tolerance;
    if (!bound_gap_closed) {
        discovery.held_stage_ii_candidate_bound_audit_status = "candidate_bound_gap_open";
        discovery.held_stage_ii_status = "dual_loop_incomplete";
        discovery.held_stage_ii_dual_loop_status = "incomplete_candidate_bound_gap_open";
        discovery.held_stage_ii_stopping_reason = "bound_gap_open";
        return;
    }

    discovery.held_stage_ii_candidate_bound_audit_status = "candidate_bound_gap_closed";
    if (!held_stage_ii_replay_evidence_complete(discovery)) {
        discovery.held_stage_ii_status = "dual_loop_incomplete";
        discovery.held_stage_ii_dual_loop_status = "incomplete_replay_metadata";
        discovery.held_stage_ii_stopping_reason = "replay_metadata_incomplete";
        return;
    }
    discovery.held_stage_ii_status = "dual_loop_verified";
    discovery.held_stage_ii_dual_loop_status = "verified";
    discovery.held_stage_ii_stopping_reason = "bound_gap_closed";
    discovery.held_stage_ii_replay_ready = true;
    discovery.held_stage_ii_replay_source = "stage_ii_dual_loop_selected_candidates";
    discovery.held_stage_ii_replay_seed_name = discovery.selected_candidate_count == 2
        ? kHeldStageIIDualLoopSeedName
        : kHeldStageIIDualLoopCandidateSetName;
}

bool held_stage_ii_replay_is_certified(const NeutralPhaseDiscoveryResult& discovery) {
    return discovery.held_stage_ii_replay_ready
        && discovery.held_stage_ii_status == "dual_loop_verified"
        && discovery.held_stage_ii_candidate_bound_audit_status == "candidate_bound_gap_closed"
        && discovery.held_stage_ii_dual_loop_status == "verified"
        && discovery.held_stage_ii_replay_source == "stage_ii_dual_loop_selected_candidates"
        && !discovery.held_stage_ii_replay_seed_name.empty()
        && held_stage_ii_bound_evidence_complete(discovery)
        && held_stage_ii_replay_evidence_complete(discovery);
}

void mark_held_stage_ii_pending(NeutralPhaseDiscoveryResult& discovery, const std::string& status) {
    discovery.held_stage_ii_status = status;
    discovery.held_stage_ii_candidate_bound_audit_status = status;
    discovery.held_stage_ii_dual_loop_status = status;
    discovery.held_stage_ii_stopping_reason = status;
    discovery.held_stage_ii_replay_ready = false;
    discovery.held_stage_ii_replay_source.clear();
    discovery.held_stage_ii_replay_seed_name.clear();
    discovery.held_stage_ii_replay_candidate_count = 0;
    discovery.held_stage_ii_replay_candidate_ranks.clear();
    discovery.held_stage_ii_replay_phase_fractions.clear();
    discovery.held_stage_ii_replay_phase_kinds.clear();
    discovery.held_stage_ii_replay_phase_compositions.clear();
    discovery.held_stage_ii_rejected_candidate_count = 0;
    discovery.held_stage_ii_rejected_candidate_ranks.clear();
    discovery.held_stage_ii_rejected_candidate_reasons.clear();
}

void certify_electrolyte_held2_phase_discovery(
    ElectrolyteHeld2PhaseDiscoveryResult& result
) {
    const bool replay_certified = held_stage_ii_replay_is_certified(result.tpd_discovery);
    result.phase_discovery_status = replay_certified ? "complete" : "incomplete";
    result.stage_iii_refinement_status = replay_certified ? "pending" : "incomplete";
    result.postsolve_certification_status = replay_certified ? "pending" : "incomplete";
    result.public_route_admission_status = "separate_public_admission_gate";
    result.stage_iii_handoff_status = replay_certified
        ? "ready_for_stage_iii_refinement"
        : "incomplete_stage_ii_replay";
}

void certify_electrolyte_stage_iii_refinement(
    ElectrolyteStageIIIRefinementResult& result
) {
    const NeutralPhaseDiscoveryResult& stage_ii = result.held2_discovery.tpd_discovery;
    const bool stage_ii_replay_certified = held_stage_ii_replay_is_certified(stage_ii)
        && result.held2_discovery.phase_discovery_status == "complete"
        && result.held2_discovery.stage_iii_handoff_status == "ready_for_stage_iii_refinement";
    result.phase_discovery_status = stage_ii_replay_certified ? "complete" : "incomplete";
    const bool solver_success =
        result.route_result.ran
        && result.route_result.solver_accepted
        && result.route_result.accepted
        && result.route_result.solver_status == "success"
        && result.route_result.application_status == "solve_succeeded"
        && finite_values(result.route_result.variables)
        && finite_values(result.route_result.constraints);
    const std::size_t phase_count = result.selected_phase_compositions.size();
    const bool replay_metadata_consistent =
        stage_ii_replay_certified
        && phase_count == 2
        && result.selected_candidate_count == stage_ii.selected_candidate_count
        && result.seed_name == stage_ii.held_stage_ii_replay_seed_name
        && !result.seed_name.empty()
        && result.selected_phase_kinds == stage_ii.held_stage_ii_replay_phase_kinds
        && composition_shapes_equal(
            result.selected_phase_compositions,
            stage_ii.held_stage_ii_replay_phase_compositions
        );
    const bool finite_compositions = replay_metadata_consistent
        && result.selected_phase_labels.size() == phase_count
        && result.selected_phase_kinds.size() == phase_count
        && result.selected_phase_fractions.size() == phase_count
        && normalized_phase_fractions(result.selected_phase_fractions)
        && unique_nonempty_strings(result.selected_phase_labels)
        && std::all_of(
            result.selected_phase_compositions.begin(),
            result.selected_phase_compositions.end(),
            [](const std::vector<double>& composition) { return normalized_composition(composition); }
        );
    double computed_residual_inf_norm = 0.0;
    bool finite_residual_values = !result.residual_values.empty();
    for (double residual : result.residual_values) {
        if (!std::isfinite(residual)) {
            finite_residual_values = false;
            break;
        }
        computed_residual_inf_norm = std::max(computed_residual_inf_norm, std::abs(residual));
    }
    const bool residuals_pass =
        finite_residual_values
        && unique_nonempty_strings(result.equation_labels)
        && result.residual_values.size() == result.equation_labels.size()
        && result.residual_scaling.size() == result.equation_labels.size()
        && std::all_of(
            result.residual_scaling.begin(),
            result.residual_scaling.end(),
            [](double scale) { return std::isfinite(scale) && scale > 0.0; }
        )
        && std::isfinite(result.residual_inf_norm)
        && result.residual_inf_norm >= 0.0
        && std::isfinite(result.residual_tolerance)
        && result.residual_tolerance > 0.0
        && evidence_values_close(result.residual_inf_norm, computed_residual_inf_norm)
        && result.residual_inf_norm <= result.residual_tolerance;
    const double computed_phase_distance = phase_distance_inf_norm(result.selected_phase_compositions);
    const bool phase_distance_pass =
        std::isfinite(result.phase_distance)
        && result.phase_distance >= 0.0
        && std::isfinite(result.phase_distance_tolerance)
        && result.phase_distance_tolerance >= 0.0
        && evidence_values_close(result.phase_distance, computed_phase_distance)
        && result.phase_distance > result.phase_distance_tolerance;
    const bool bounds_pass =
        std::isfinite(result.active_bound_violation)
        && result.active_bound_violation >= 0.0
        && std::isfinite(result.active_bound_tolerance)
        && result.active_bound_tolerance >= 0.0
        && result.active_bound_violation <= result.active_bound_tolerance;
    const bool derivative_pass =
        result.exact_reduced_jacobian_available
        && result.exact_reduced_hessian_available
        && result.route_result.exact_hessian_available
        && result.route_result.jacobian_approximation == "exact"
        && result.route_result.hessian_approximation == "exact";
    const bool accepted =
        stage_ii_replay_certified
        && solver_success
        && finite_compositions
        && residuals_pass
        && phase_distance_pass
        && bounds_pass
        && derivative_pass;
    result.status = accepted ? "complete" : "incomplete";
    result.stage_iii_refinement_status = result.status;
    result.postsolve_certification_status = accepted ? "pending" : "incomplete";
}

void certify_refined_neutral_postsolve(
    NeutralTwoPhaseEosPostsolve& postsolve,
    const NeutralPhaseDiscoveryResult& discovery,
    int refined_phase_count,
    const std::string& replay_source,
    const std::string& replay_seed_name
) {
    const bool residual_metrics_accepted = postsolve.accepted;
    const std::string residual_rejection_reason = postsolve.rejection_reason;
    const bool candidate_pair_replay_consumed =
        discovery.selected_candidate_count == 2
        && discovery.held_stage_ii_replay_seed_name == kSampledCandidatePairReplaySeedName
        && replay_source == "sampled_candidate_pair_seed"
        && replay_seed_name == kSampledCandidatePairReplaySeedName;
    const bool candidate_set_replay_consumed =
        discovery.selected_candidate_count > 2
        && discovery.held_stage_ii_replay_seed_name == kSampledCandidateSetReplaySeedName
        && replay_source == "sampled_candidate_set_seed"
        && replay_seed_name == kSampledCandidateSetReplaySeedName;
    const bool replay_metadata_consumed =
        sampled_candidate_replay_is_valid(discovery)
        && refined_phase_count == discovery.selected_candidate_count
        && (candidate_pair_replay_consumed || candidate_set_replay_consumed);
    copy_neutral_phase_discovery_evidence(postsolve, discovery);
    postsolve.held_stage_iii_status = replay_metadata_consumed
        ? "ipopt_refinement_completed_current_route"
        : "stage_ii_replay_not_consumed";
    postsolve.held_stage_iii_refined_phase_count = refined_phase_count;
    postsolve.held_stage_iii_consumed_stage_ii_replay_metadata = replay_metadata_consumed;
    postsolve.held_stage_iii_replay_source = replay_metadata_consumed ? replay_source : "";
    postsolve.held_stage_iii_replay_seed_name = replay_metadata_consumed ? replay_seed_name : "";
    postsolve.held_stage_iii_replay_candidate_count = replay_metadata_consumed
        ? discovery.held_stage_ii_replay_candidate_count
        : 0;

    if (!residual_metrics_accepted) {
        postsolve.accepted = false;
        postsolve.rejection_reason = residual_rejection_reason;
    } else if (!replay_metadata_consumed) {
        postsolve.accepted = false;
        postsolve.rejection_reason = "stage_ii_replay_not_consumed";
    } else if (!discovery.phase_set_mass_balance_feasible) {
        postsolve.accepted = false;
        postsolve.rejection_reason = "candidate_completeness";
    } else {
        postsolve.accepted = true;
        postsolve.rejection_reason = "accepted";
    }
}

}  // namespace epcsaft::native::equilibrium_nlp
