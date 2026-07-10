#pragma once

#include "equilibrium/core/two_phase_eos_route.h"

#include <string>

namespace epcsaft::native::equilibrium_nlp {

inline constexpr const char* kSampledCandidatePairReplaySeedName =
    "sampled_candidate_pair_replay";
inline constexpr const char* kSampledCandidateSetReplaySeedName =
    "sampled_candidate_set_replay";
inline constexpr const char* kHeldStageIIDualLoopSeedName =
    "held_stage_ii_dual_loop_candidate_pair";
inline constexpr const char* kHeldStageIIDualLoopCandidateSetName =
    "held_stage_ii_dual_loop_candidate_set";

enum class HeldStageICertificateUse {
    DiscoveryEvidence,
    Held2ConsumedEvidence,
};

void certify_held_stage_i_evidence(
    NeutralPhaseDiscoveryResult& discovery,
    double tpd_tolerance,
    bool continuous_tpd_required,
    HeldStageICertificateUse certificate_use = HeldStageICertificateUse::DiscoveryEvidence
);

void complete_sampled_candidate_bound_audit(
    NeutralPhaseDiscoveryResult& discovery,
    bool continuous_tpd_required
);

bool sampled_candidate_replay_is_valid(const NeutralPhaseDiscoveryResult& discovery);

void certify_held_stage_ii_bound_audit(
    NeutralPhaseDiscoveryResult& discovery,
    bool continuous_tpd_required
);

bool held_stage_ii_replay_is_certified(const NeutralPhaseDiscoveryResult& discovery);

void mark_held_stage_ii_pending(NeutralPhaseDiscoveryResult& discovery, const std::string& status);

void certify_electrolyte_held2_phase_discovery(
    ElectrolyteHeld2PhaseDiscoveryResult& result
);

void certify_electrolyte_stage_iii_refinement(
    ElectrolyteStageIIIRefinementResult& result
);

void certify_refined_neutral_postsolve(
    NeutralTwoPhaseEosPostsolve& postsolve,
    const NeutralPhaseDiscoveryResult& discovery,
    int refined_phase_count,
    const std::string& replay_source,
    const std::string& replay_seed_name
);

}  // namespace epcsaft::native::equilibrium_nlp
