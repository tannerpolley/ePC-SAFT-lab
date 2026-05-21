#pragma once

#include "equilibrium/core/activation_matrix.h"
#include "equilibrium/core/two_phase_eos_route.h"

#include <string>
#include <vector>

struct add_args;

namespace epcsaft::native::equilibrium {

struct SelectorInputClassification {
    bool neutral = false;
    bool nonreactive = true;
    bool nonelectrolyte = false;
    bool nonassociating = false;
};

struct SelectorRouteRequest {
    std::string route;
    bool has_temperature = false;
    bool has_pressure = false;
    double temperature = 0.0;
    double pressure = 0.0;
    std::vector<double> composition;
    std::string composition_role;
};

struct SelectorContract {
    std::string selector_family;
    std::string route;
    std::string composition_role;
    bool specified_temperature = false;
    bool specified_pressure = false;
    bool production_exposed = false;
    bool certification_required = false;
    bool density_closure_required = false;
    bool exact_derivatives_required = false;
    SelectorInputClassification input_classification;
    ProblemFamilyActivation activation;
    epcsaft::native::equilibrium_nlp::NeutralTwoPhaseEosNlpContract nlp_contract;
};

SelectorContract evaluate_selector_contract(
    const add_args& args,
    const SelectorRouteRequest& request
);

epcsaft::native::equilibrium_nlp::NeutralTwoPhaseEosRouteResult solve_selector_route(
    const add_args& args,
    const SelectorRouteRequest& request,
    const epcsaft::native::equilibrium_nlp::IpoptSolveOptions& options,
    double phase_total_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance
);

}  // namespace epcsaft::native::equilibrium
