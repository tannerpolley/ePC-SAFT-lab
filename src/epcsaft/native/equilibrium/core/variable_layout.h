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
    int phase_count = 0;
    int species_count = 0;
    int variable_count = 0;
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
