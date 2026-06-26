#pragma once

#include <vector>

namespace epcsaft::native::equilibrium_nlp {

struct HomogeneousChemicalEquilibriumBlockResult {
    int species_count = 0;
    int reaction_count = 0;
    int constraint_count = 0;
    double objective_value = 0.0;
    std::vector<double> amounts;
    std::vector<double> mole_fractions;
    std::vector<double> standard_mu_rt;
    std::vector<double> objective_gradient;
    std::vector<double> hessian_row_major;
    std::vector<double> balance_residuals;
    std::vector<double> balance_jacobian_row_major;
    std::vector<double> log_q;
    std::vector<double> reaction_residuals;
    std::vector<double> reaction_affinities;
    std::vector<double> affinity_jacobian_row_major;
    std::vector<double> variable_scaling;
    std::vector<double> balance_scaling;
    std::vector<double> affinity_scaling;
    double objective_scaling = 1.0;
    double minimum_amount = 0.0;
    double amount_lower_margin = 0.0;
    double total_amount = 0.0;
};

HomogeneousChemicalEquilibriumBlockResult evaluate_homogeneous_chemical_equilibrium_block(
    const std::vector<double>& amounts,
    int reaction_count,
    const std::vector<double>& stoichiometry_row_major,
    int conservation_row_count,
    const std::vector<double>& conservation_matrix_row_major,
    const std::vector<double>& conservation_totals,
    const std::vector<double>& log_equilibrium_constants
);

}  // namespace epcsaft::native::equilibrium_nlp
