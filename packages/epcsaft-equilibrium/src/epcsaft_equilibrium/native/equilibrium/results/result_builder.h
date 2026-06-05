#pragma once

#include "equilibrium/core/two_phase_eos_route.h"

#include <string>
#include <vector>

struct add_args;

namespace epcsaft::native::equilibrium_nlp {

struct NeutralTwoPhaseEosPhasePayload {
    std::string label;
    std::vector<double> composition;
    std::vector<double> ln_fugacity_coefficient;
    std::vector<double> fugacity_coefficient;
    double density = 0.0;
    double temperature = 0.0;
    double pressure = 0.0;
    double phase_fraction = 0.0;
    double amount_total = 0.0;
    double volume = 0.0;
    double eos_pressure = 0.0;
    double pressure_consistency_residual = 0.0;
    double compressibility_factor = 0.0;
};

struct NeutralTwoPhaseEosResultPayload {
    bool accepted = false;
    bool stable = false;
    bool split_detected = false;
    std::string backend = "native_equilibrium_nlp";
    std::string problem_kind = "neutral_two_phase_eos";
    std::string derivative_backend;
    std::string rejection_reason;
    double objective = 0.0;
    double material_balance_norm = 0.0;
    double pressure_consistency_norm = 0.0;
    double chemical_potential_consistency_norm = 0.0;
    double ln_fugacity_consistency_norm = 0.0;
    double phase_distance = 0.0;
    std::vector<double> feed_amounts;
    std::vector<double> constraints;
    std::vector<NeutralTwoPhaseEosPhasePayload> phases;
};

enum class NeutralRouteCertificationLevel {
    LocalPostsolve,
    PhaseSetCertified,
};

void mark_neutral_route_ipopt_dependency_required(NeutralTwoPhaseEosRouteResult& out);

bool apply_neutral_route_solve_result(
    NeutralTwoPhaseEosRouteResult& out,
    const IpoptSolveResult& solve
);

void apply_neutral_route_postsolve(
    NeutralTwoPhaseEosRouteResult& out,
    NeutralTwoPhaseEosPostsolve postsolve,
    NeutralRouteCertificationLevel certification_level
);

int neutral_route_quality(const NeutralTwoPhaseEosRouteResult& result);

bool neutral_route_strict_ipopt_success(const NeutralTwoPhaseEosRouteResult& result);

int neutral_boundary_route_quality(const NeutralTwoPhaseEosRouteResult& result);

RouteSeedAttempt neutral_seed_attempt_from_result(const NeutralTwoPhaseEosRouteResult& result);

RoutePhysicalEvidence build_neutral_route_physical_evidence(const NeutralTwoPhaseEosRouteResult& result);

NeutralTwoPhaseEosResultPayload build_neutral_two_phase_eos_result(
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
    bool phase_distance_constraint = true
);

}  // namespace epcsaft::native::equilibrium_nlp
