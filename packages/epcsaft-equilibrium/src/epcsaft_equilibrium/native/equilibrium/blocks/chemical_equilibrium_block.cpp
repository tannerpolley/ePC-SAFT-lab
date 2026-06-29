#include "equilibrium/blocks/chemical_equilibrium_block.h"

#include "equilibrium/blocks/gibbs_blocks.h"
#include "equilibrium/blocks/reaction_block.h"
#include "model/native_types.h"

#include <algorithm>
#include <cmath>
#include <numeric>

namespace epcsaft::native::equilibrium_nlp {

namespace {

void validate_conservation_inputs(
    std::size_t species_count,
    int conservation_row_count,
    const std::vector<double>& conservation_matrix_row_major,
    const std::vector<double>& conservation_totals
) {
    if (conservation_row_count <= 0) {
        throw ValueError("Homogeneous chemical equilibrium block requires at least one conservation row.");
    }
    const std::size_t rows = static_cast<std::size_t>(conservation_row_count);
    if (conservation_totals.size() != rows) {
        throw ValueError("Homogeneous chemical equilibrium block requires one conservation total per row.");
    }
    if (conservation_matrix_row_major.size() != rows * species_count) {
        throw ValueError("Homogeneous chemical equilibrium conservation matrix must be row-major rows by species.");
    }
    for (double coefficient : conservation_matrix_row_major) {
        if (!std::isfinite(coefficient)) {
            throw ValueError("Homogeneous chemical equilibrium conservation matrix must be finite.");
        }
    }
    for (double total : conservation_totals) {
        if (!std::isfinite(total)) {
            throw ValueError("Homogeneous chemical equilibrium conservation totals must be finite.");
        }
    }
}

std::vector<double> conservation_residuals(
    const std::vector<double>& amounts,
    int conservation_row_count,
    const std::vector<double>& conservation_matrix_row_major,
    const std::vector<double>& conservation_totals
) {
    const std::size_t species = amounts.size();
    std::vector<double> residuals(static_cast<std::size_t>(conservation_row_count), 0.0);
    for (int row = 0; row < conservation_row_count; ++row) {
        const std::size_t row_offset = static_cast<std::size_t>(row) * species;
        double balance = 0.0;
        for (std::size_t species_index = 0; species_index < species; ++species_index) {
            balance += conservation_matrix_row_major[row_offset + species_index] * amounts[species_index];
        }
        residuals[static_cast<std::size_t>(row)] = balance - conservation_totals[static_cast<std::size_t>(row)];
    }
    return residuals;
}

std::vector<double> variable_scaling_for(const std::vector<double>& amounts) {
    std::vector<double> scaling(amounts.size(), 1.0);
    for (std::size_t index = 0; index < amounts.size(); ++index) {
        scaling[index] = 1.0 / std::max(1.0, std::abs(amounts[index]));
    }
    return scaling;
}

std::vector<double> balance_scaling_for(const std::vector<double>& conservation_totals) {
    std::vector<double> scaling(conservation_totals.size(), 1.0);
    for (std::size_t index = 0; index < conservation_totals.size(); ++index) {
        scaling[index] = 1.0 / std::max(1.0, std::abs(conservation_totals[index]));
    }
    return scaling;
}

}  // namespace

HomogeneousChemicalEquilibriumBlockResult evaluate_homogeneous_chemical_equilibrium_block(
    const std::vector<double>& amounts,
    int reaction_count,
    const std::vector<double>& stoichiometry_row_major,
    int conservation_row_count,
    const std::vector<double>& conservation_matrix_row_major,
    const std::vector<double>& conservation_totals,
    const std::vector<double>& log_equilibrium_constants
) {
    if (amounts.empty()) {
        throw ValueError("Homogeneous chemical equilibrium block requires at least one species.");
    }
    for (double amount : amounts) {
        if (!(std::isfinite(amount) && amount > 0.0)) {
            throw ValueError("Homogeneous chemical equilibrium species amounts must be positive and finite.");
        }
    }
    validate_conservation_inputs(
        amounts.size(),
        conservation_row_count,
        conservation_matrix_row_major,
        conservation_totals
    );

    const auto species_count = static_cast<int>(amounts.size());
    const std::vector<double> standard_mu_rt = standard_mu_rt_from_reactions(
        species_count,
        reaction_count,
        stoichiometry_row_major,
        log_equilibrium_constants
    );
    const IdealReducedGibbsResult gibbs = evaluate_ideal_reduced_gibbs(amounts, standard_mu_rt, true);
    const IdealReactionQuotientResult reactions = evaluate_ideal_reaction_quotients(
        amounts,
        reaction_count,
        stoichiometry_row_major,
        log_equilibrium_constants
    );

    HomogeneousChemicalEquilibriumBlockResult out;
    out.species_count = species_count;
    out.reaction_count = reaction_count;
    out.constraint_count = conservation_row_count;
    out.objective_value = gibbs.value;
    out.amounts = amounts;
    out.mole_fractions = gibbs.mole_fractions;
    out.activities = gibbs.mole_fractions;
    out.ln_activity_coefficients.assign(amounts.size(), 0.0);
    out.standard_mu_rt = standard_mu_rt;
    out.objective_gradient = gibbs.gradient;
    out.hessian_row_major = gibbs.hessian_row_major;
    out.balance_residuals = conservation_residuals(
        amounts,
        conservation_row_count,
        conservation_matrix_row_major,
        conservation_totals
    );
    out.balance_jacobian_row_major = conservation_matrix_row_major;
    out.log_q = reactions.log_q;
    out.reaction_residuals = reactions.residuals;
    out.reaction_affinities = reaction_affinities_from_gradient(
        gibbs.gradient,
        reaction_count,
        stoichiometry_row_major
    );
    out.affinity_jacobian_row_major = reactions.jacobian_row_major;
    out.variable_scaling = variable_scaling_for(amounts);
    out.balance_scaling = balance_scaling_for(conservation_totals);
    out.affinity_scaling.assign(static_cast<std::size_t>(reaction_count), 1.0);
    out.objective_scaling = 1.0 / std::max(1.0, std::abs(gibbs.value));
    out.minimum_amount = *std::min_element(amounts.begin(), amounts.end());
    out.amount_lower_margin = out.minimum_amount;
    out.total_amount = std::accumulate(amounts.begin(), amounts.end(), 0.0);
    return out;
}

}  // namespace epcsaft::native::equilibrium_nlp
