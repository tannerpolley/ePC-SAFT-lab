#include "equilibrium/core/chemical_equilibrium_objective.h"

#include "model/native_types.h"

#include <cmath>

namespace epcsaft::native::equilibrium_nlp {

ChemicalEquilibriumNlpInput chemical_equilibrium_input_with_log_k_lambda(
    const ChemicalEquilibriumNlpInput& input,
    double log_equilibrium_constants_lambda
) {
    if (!std::isfinite(log_equilibrium_constants_lambda)) {
        throw ValueError("chemical equilibrium log-K homotopy lambda must be finite.");
    }
    ChemicalEquilibriumNlpInput out = input;
    out.log_equilibrium_constants_lambda = log_equilibrium_constants_lambda;
    out.log_equilibrium_constants.clear();
    out.log_equilibrium_constants.reserve(input.log_equilibrium_constants.size());
    for (double value : input.log_equilibrium_constants) {
        out.log_equilibrium_constants.push_back(log_equilibrium_constants_lambda * value);
    }
    return out;
}

HomogeneousChemicalEquilibriumBlockResult evaluate_chemical_equilibrium_objective(
    const ChemicalEquilibriumNlpInput& input,
    const std::vector<double>& amounts
) {
    return evaluate_homogeneous_chemical_equilibrium_block(
        amounts,
        static_cast<int>(input.reaction_labels.size()),
        input.stoichiometry_row_major,
        static_cast<int>(input.conservation_labels.size()),
        input.conservation_matrix_row_major,
        input.conservation_totals,
        input.log_equilibrium_constants
    );
}

}  // namespace epcsaft::native::equilibrium_nlp
