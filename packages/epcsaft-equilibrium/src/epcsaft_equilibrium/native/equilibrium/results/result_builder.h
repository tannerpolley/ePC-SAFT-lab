#pragma once

#include "equilibrium/core/two_phase_eos_route.h"

#include <string>

namespace epcsaft::native::equilibrium_nlp {

enum class NeutralRouteCertificationLevel {
    LocalPostsolve,
    PhaseSetCertified,
};

enum class NeutralPhaseDiscoveryAcceptancePolicy {
    CandidateMassBalanceOnly,
    GeneralizedFeed,
    AcceptedPhaseSet,
    ElectrolyteDeterministic,
    ElectrolyteContinuous,
    ElectrolyteHeld2,
};

struct NeutralPostsolveAcceptanceCriteria {
    double material_tolerance = 0.0;
    double pressure_tolerance = 0.0;
    double chemical_potential_tolerance = 0.0;
    double phase_distance_tolerance = 0.0;
    double charge_tolerance = 0.0;
    double fixed_composition_tolerance = 0.0;
    double phase_amount_total_tolerance = 0.0;
    bool charged_system = false;
    bool phase_distance_required = false;
    bool phase_distance_strictly_greater = false;
    bool charge_balance_required = false;
    bool fixed_composition_required = false;
    bool phase_amount_total_required = false;
    bool stability_evidence_pending = false;
    bool stability_certification_required = false;
    bool stability_certification_unsupported = false;
    bool ln_fugacity_consistency_required = true;
};

struct NeutralRouteAcceptablePointCriteria {
    bool enabled = false;
    double scaled_constraint_violation_limit = 0.0;
    double scaled_stationarity_limit = 0.0;
    double scaled_complementarity_limit = 0.0;
};

void mark_neutral_route_ipopt_dependency_required(NeutralTwoPhaseEosRouteResult& out);

void mark_neutral_route_derivative_preflight_failed(
    NeutralTwoPhaseEosRouteResult& out,
    const NlpProblem& problem,
    const std::string& message
);

bool apply_neutral_route_solve_result(
    NeutralTwoPhaseEosRouteResult& out,
    const IpoptSolveResult& solve
);

bool apply_neutral_route_solve_result(
    NeutralTwoPhaseEosRouteResult& out,
    const IpoptSolveResult& solve,
    const NeutralRouteAcceptablePointCriteria& acceptable_point
);

void apply_neutral_route_postsolve(
    NeutralTwoPhaseEosRouteResult& out,
    NeutralTwoPhaseEosPostsolve postsolve,
    NeutralRouteCertificationLevel certification_level
);

void certify_neutral_phase_discovery(
    NeutralPhaseDiscoveryResult& discovery,
    NeutralPhaseDiscoveryAcceptancePolicy policy,
    double tpd_tolerance,
    double candidate_mass_balance_tolerance,
    bool negative_novel_candidate = false
);

void copy_neutral_phase_discovery_evidence(
    NeutralTwoPhaseEosPostsolve& postsolve,
    const NeutralPhaseDiscoveryResult& discovery
);

void certify_neutral_postsolve(
    NeutralTwoPhaseEosPostsolve& postsolve,
    const NeutralPostsolveAcceptanceCriteria& criteria
);

void reject_neutral_postsolve(NeutralTwoPhaseEosPostsolve& postsolve, const std::string& reason);

void certify_electrolyte_postsolve(ElectrolytePostsolveCertificationResult& result);

int neutral_route_quality(const NeutralTwoPhaseEosRouteResult& result);

bool neutral_route_strict_ipopt_success(const NeutralTwoPhaseEosRouteResult& result);

int neutral_boundary_route_quality(const NeutralTwoPhaseEosRouteResult& result);

RouteSeedAttempt neutral_seed_attempt_from_result(const NeutralTwoPhaseEosRouteResult& result);

RoutePhysicalEvidence build_neutral_route_physical_evidence(const NeutralTwoPhaseEosRouteResult& result);

}  // namespace epcsaft::native::equilibrium_nlp
