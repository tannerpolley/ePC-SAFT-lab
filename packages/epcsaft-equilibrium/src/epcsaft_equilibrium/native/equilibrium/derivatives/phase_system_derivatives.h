#pragma once

#include "equilibrium/blocks/association_block.h"
#include "equilibrium/blocks/eos_phase_block.h"
#include "equilibrium/blocks/electrolyte_block.h"

#include <vector>

namespace epcsaft::native::equilibrium_nlp {

void populate_eos_phase_system_derivatives(
    EosPhaseSystemResult& result,
    const std::vector<std::vector<double>>& phase_amounts,
    const std::vector<double>& volumes,
    const PhaseChargeBlockResult& charge_block,
    const std::vector<AssociationMassActionBlockResult>& association_blocks,
    const std::vector<int>& site_component_index,
    const std::vector<std::vector<double>>& association_site_fractions,
    const std::vector<double>& association_delta_row_major
);

}  // namespace epcsaft::native::equilibrium_nlp
