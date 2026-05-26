#include "equilibrium/core/variable_layout.h"

#include "model/native_types.h"

#include <cstddef>

namespace epcsaft::native::equilibrium {

int VariableLayout::phase_amount_index(int phase, int species) const {
    if (phase < 0 || phase >= phase_count || species < 0 || species >= species_count) {
        throw ValueError("activation-layout-ineligible: phase amount index is out of range.");
    }
    return phase_amount_indices[static_cast<std::size_t>(phase)][static_cast<std::size_t>(species)];
}

int VariableLayout::phase_volume_index(int phase) const {
    if (phase < 0 || phase >= phase_count) {
        throw ValueError("activation-layout-ineligible: phase volume index is out of range.");
    }
    return phase_volume_indices[static_cast<std::size_t>(phase)];
}

VariableLayout build_variable_layout(
    const ActivationPlan& plan,
    int species_count
) {
    if (plan.variable_model != "phase_species_amounts_plus_phase_volume") {
        throw ValueError("activation-layout-ineligible: unsupported variable model for activation layout.");
    }
    if (plan.variable_blocks != std::vector<std::string>{"phase_species_amounts", "phase_volumes"}) {
        throw ValueError("activation-layout-ineligible: unsupported variable blocks for activation layout.");
    }
    if (static_cast<int>(plan.phase_keys.size()) < 2 || species_count <= 0) {
        throw ValueError("activation-layout-ineligible: amount-volume layout requires at least two phases and species.");
    }

    VariableLayout out;
    out.family_key = plan.family_key;
    out.route = plan.route;
    out.variable_model = plan.variable_model;
    out.phase_count = static_cast<int>(plan.phase_keys.size());
    out.species_count = species_count;
    const int local_variable_count = species_count + 1;
    out.variable_count = out.phase_count * local_variable_count;
    out.variable_blocks = {
        {"phase_species_amounts", 0, out.phase_count * out.species_count, local_variable_count},
        {"phase_volumes", out.species_count, out.phase_count, local_variable_count},
    };
    out.phase_amount_indices.assign(
        static_cast<std::size_t>(out.phase_count),
        std::vector<int>(static_cast<std::size_t>(out.species_count), 0)
    );
    out.phase_volume_indices.assign(static_cast<std::size_t>(out.phase_count), 0);
    for (int phase = 0; phase < out.phase_count; ++phase) {
        const int offset = phase * local_variable_count;
        for (int species = 0; species < out.species_count; ++species) {
            out.phase_amount_indices[static_cast<std::size_t>(phase)][static_cast<std::size_t>(species)] =
                offset + species;
        }
        out.phase_volume_indices[static_cast<std::size_t>(phase)] = offset + out.species_count;
    }
    return out;
}

}  // namespace epcsaft::native::equilibrium
