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

struct SelectorContract {
    std::string selector_family;
    std::string route;
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
    const std::string& route,
    double scalar,
    const std::vector<double>& composition
);

epcsaft::native::equilibrium_nlp::NeutralTwoPhaseEosRouteResult solve_selector_route(
    const add_args& args,
    const std::string& route,
    double scalar,
    const std::vector<double>& composition,
    const epcsaft::native::equilibrium_nlp::IpoptSolveOptions& options,
    double phase_total_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance
);

}  // namespace epcsaft::native::equilibrium
