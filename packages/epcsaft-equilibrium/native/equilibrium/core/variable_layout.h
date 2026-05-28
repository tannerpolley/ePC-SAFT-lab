#pragma once

#include "equilibrium/core/activation_plan.h"

#include <string>
#include <vector>

namespace epcsaft::native::equilibrium {

struct VariableBlockLayout {
    std::string name;
    int offset = 0;
    int size = 0;
    int stride = 0;
};

struct VariableLayout {
    std::string family_key;
    std::string route;
    std::string variable_model;
    std::string physical_basis = "true_species_phase_amounts_and_phase_volumes";
    std::string solver_coordinate_basis = "physical_variables";
    std::string lift_policy = "identity_true_species_lift";
    std::string back_lift_policy = "phase_amount_volume_back_lift";
    std::string transform_policy = "identity_physical_coordinates";
    int phase_count = 0;
    int species_count = 0;
    int variable_count = 0;
    std::vector<std::string> phase_keys;
    std::vector<std::string> phase_kinds;
    std::vector<std::string> physical_variable_order;
    std::vector<VariableBlockLayout> variable_blocks;
    std::vector<std::vector<int>> phase_amount_indices;
    std::vector<int> phase_volume_indices;

    int phase_amount_index(int phase, int species) const;
    int phase_volume_index(int phase) const;
};

VariableLayout build_variable_layout(
    const ActivationPlan& plan,
    int species_count
);

}  // namespace epcsaft::native::equilibrium
