#pragma once

#include "equilibrium/core/activation_matrix.h"

#include <string>
#include <vector>

struct add_args;

namespace epcsaft::native::equilibrium {

struct SelectorRouteRequest;

struct ActivationPlan {
    std::string family_key;
    std::string route;
    std::vector<std::string> phase_keys;
    std::vector<std::string> phase_kinds;
    std::vector<std::string> variable_blocks;
    std::vector<std::string> constraint_blocks;
    std::vector<std::string> residual_blocks;
    std::vector<std::string> postsolve_blocks;
    std::string variable_model;
    std::string density_backend;
    std::vector<double> feed_composition;
    double temperature = 0.0;
    double pressure = 0.0;
};

const ProblemFamilyActivation& activation_row_for_key(const std::string& key);

ActivationPlan build_activation_plan(
    const add_args& args,
    const SelectorRouteRequest& request
);

ActivationPlan build_neutral_tp_flash_activation_plan(
    const add_args& args,
    double temperature,
    double pressure,
    const std::vector<double>& feed_composition
);

ActivationPlan build_neutral_lle_activation_plan(
    const add_args& args,
    double temperature,
    double pressure,
    const std::vector<double>& feed_composition
);

}  // namespace epcsaft::native::equilibrium
