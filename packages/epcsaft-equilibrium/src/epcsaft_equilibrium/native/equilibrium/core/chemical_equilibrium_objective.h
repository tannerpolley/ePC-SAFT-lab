#pragma once

#include "equilibrium/blocks/chemical_equilibrium_block.h"
#include "equilibrium/core/chemical_equilibrium_nlp.h"

#include <vector>

namespace epcsaft::native::equilibrium_nlp {

ChemicalEquilibriumNlpInput chemical_equilibrium_input_with_log_k_lambda(
    const ChemicalEquilibriumNlpInput& input,
    double log_equilibrium_constants_lambda
);

HomogeneousChemicalEquilibriumBlockResult evaluate_chemical_equilibrium_objective(
    const ChemicalEquilibriumNlpInput& input,
    const std::vector<double>& amounts
);

}  // namespace epcsaft::native::equilibrium_nlp
