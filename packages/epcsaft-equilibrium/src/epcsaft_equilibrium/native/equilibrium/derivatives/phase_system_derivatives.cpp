#include "equilibrium/derivatives/phase_system_derivatives.h"

#include <exception>

#include "model/native_types.h"

#include <cstddef>

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
) {
    const std::size_t phase_count = result.phase_blocks.size();
    const std::size_t species_count = result.feed_amounts.size();
    const std::size_t association_site_count = static_cast<std::size_t>(result.association_site_count);
    const std::size_t base_local_variable_count = species_count + 1;
    const std::size_t local_variable_count = base_local_variable_count + association_site_count;
    const std::size_t charge_constraint_count = charge_block.residuals.size();
    const std::size_t association_constraint_count = association_blocks.size() * association_site_count;
    const std::size_t constraint_count =
        species_count + phase_count + charge_constraint_count + association_constraint_count;
    const std::size_t variable_count = phase_count * local_variable_count;
    if (result.constraints.size() != constraint_count) {
        throw ::ValueError("EOS phase system derivative constraints did not match the expected constraint count.");
    }
    if (phase_amounts.size() != phase_count || volumes.size() != phase_count) {
        throw ::ValueError("EOS phase system derivative phase inputs did not match the evaluated phase count.");
    }

    result.constraint_jacobian_backend = "analytic_cppad";
    result.constraint_jacobian_rows = static_cast<int>(constraint_count);
    result.constraint_jacobian_cols = static_cast<int>(variable_count);
    result.constraint_jacobian_row_major.assign(constraint_count * variable_count, 0.0);
    result.objective_hessian_backend = "cppad_phase_blocks";
    result.objective_hessian_rows = static_cast<int>(variable_count);
    result.objective_hessian_cols = static_cast<int>(variable_count);
    result.objective_hessian_row_major.assign(variable_count * variable_count, 0.0);
    result.constraint_hessian_backend = "cppad_phase_blocks";
    result.constraint_hessian_rows = static_cast<int>(constraint_count);
    result.constraint_hessian_cols = static_cast<int>(variable_count);
    result.constraint_hessian_tensor_row_major.assign(constraint_count * variable_count * variable_count, 0.0);
    result.constraint_has_hessian.assign(constraint_count, false);
    for (std::size_t species = 0; species < species_count; ++species) {
        for (std::size_t phase = 0; phase < phase_count; ++phase) {
            result.constraint_jacobian_row_major[
                species * variable_count + phase * local_variable_count + species
            ] = 1.0;
        }
    }
    for (std::size_t phase = 0; phase < phase_count; ++phase) {
        const EosPhaseBlockResult& block = result.phase_blocks[phase];
        if (block.pressure_jacobian_row_major.size() != base_local_variable_count) {
            throw ::ValueError("EOS phase pressure Jacobian size did not match the phase variable model.");
        }
        if (block.objective_curvature_row_major.size() != base_local_variable_count * base_local_variable_count) {
            throw ::ValueError("EOS phase objective Hessian size did not match the phase variable model.");
        }
        if (block.pressure_hessian_row_major.size() != base_local_variable_count * base_local_variable_count) {
            throw ::ValueError("EOS phase pressure Hessian size did not match the phase variable model.");
        }
        const std::size_t row = species_count + phase;
        const std::size_t col_offset = phase * local_variable_count;
        for (std::size_t col = 0; col < base_local_variable_count; ++col) {
            result.constraint_jacobian_row_major[row * variable_count + col_offset + col] =
                block.pressure_jacobian_row_major[col];
        }
        result.constraint_has_hessian[row] = true;
        for (std::size_t local_row = 0; local_row < base_local_variable_count; ++local_row) {
            for (std::size_t local_col = 0; local_col < base_local_variable_count; ++local_col) {
                const std::size_t global_row = col_offset + local_row;
                const std::size_t global_col = col_offset + local_col;
                result.objective_hessian_row_major[global_row * variable_count + global_col] =
                    block.objective_curvature_row_major[local_row * base_local_variable_count + local_col];
                result.constraint_hessian_tensor_row_major[
                    row * variable_count * variable_count + global_row * variable_count + global_col
                ] = block.pressure_hessian_row_major[local_row * base_local_variable_count + local_col];
            }
        }
    }
    for (std::size_t row = 0; row < charge_constraint_count; ++row) {
        const std::size_t target_row = species_count + phase_count + row;
        for (std::size_t col = 0; col < variable_count; ++col) {
            result.constraint_jacobian_row_major[target_row * variable_count + col] =
                charge_block.jacobian_row_major[row * variable_count + col];
        }
    }
    const std::size_t association_row_offset = species_count + phase_count + charge_constraint_count;
    for (std::size_t phase = 0; phase < association_blocks.size(); ++phase) {
        const auto& block = association_blocks[phase];
        const std::size_t col_offset = phase * local_variable_count;
        const auto& amounts = phase_amounts[phase];
        const double volume = volumes[phase];
        for (std::size_t site = 0; site < association_site_count; ++site) {
            const std::size_t component_index = static_cast<std::size_t>(site_component_index[site]);
            const std::size_t amount_col = col_offset + component_index;
            const std::size_t site_col = col_offset + base_local_variable_count + site;
            const double site_fraction = association_site_fractions[phase][site];
            const double amount_site_value = 1.0 / site_fraction - 0.5;
            result.objective_hessian_row_major[amount_col * variable_count + site_col] += amount_site_value;
            result.objective_hessian_row_major[site_col * variable_count + amount_col] += amount_site_value;
            result.objective_hessian_row_major[site_col * variable_count + site_col] +=
                -amounts[component_index] / (site_fraction * site_fraction);
        }
        for (std::size_t site = 0; site < association_site_count; ++site) {
            const std::size_t target_row = association_row_offset + phase * association_site_count + site;
            const double site_fraction = association_site_fractions[phase][site];
            double amount_weighted_delta_sum = 0.0;
            for (std::size_t col = 0; col < association_site_count; ++col) {
                const std::size_t component_index = static_cast<std::size_t>(site_component_index[col]);
                const double col_fraction = association_site_fractions[phase][col];
                const double delta = association_delta_row_major[site * association_site_count + col];
                result.constraint_jacobian_row_major[
                    target_row * variable_count + col_offset + component_index
                ] += site_fraction * col_fraction * delta / volume;
                amount_weighted_delta_sum += amounts[component_index] * col_fraction * delta;
            }
            result.constraint_jacobian_row_major[
                target_row * variable_count + col_offset + species_count
            ] = -site_fraction * amount_weighted_delta_sum / (volume * volume);
            for (std::size_t col = 0; col < association_site_count; ++col) {
                result.constraint_jacobian_row_major[
                    target_row * variable_count + col_offset + base_local_variable_count + col
                ] = block.site_fraction_jacobian_row_major[site * association_site_count + col];
            }
            result.constraint_has_hessian[target_row] = true;
            for (std::size_t component = 0; component < species_count; ++component) {
                double component_delta = 0.0;
                for (std::size_t col = 0; col < association_site_count; ++col) {
                    if (static_cast<std::size_t>(site_component_index[col]) == component) {
                        component_delta += association_site_fractions[phase][col]
                            * association_delta_row_major[site * association_site_count + col];
                    }
                }
                const double amount_volume_value = -site_fraction * component_delta / (volume * volume);
                const std::size_t amount_col = col_offset + component;
                const std::size_t volume_col = col_offset + species_count;
                result.constraint_hessian_tensor_row_major[
                    target_row * variable_count * variable_count + amount_col * variable_count + volume_col
                ] = amount_volume_value;
                result.constraint_hessian_tensor_row_major[
                    target_row * variable_count * variable_count + volume_col * variable_count + amount_col
                ] = amount_volume_value;
                for (std::size_t other_site = 0; other_site < association_site_count; ++other_site) {
                    double amount_site_value = 0.0;
                    if (site == other_site) {
                        amount_site_value += component_delta / volume;
                    }
                    if (static_cast<std::size_t>(site_component_index[other_site]) == component) {
                        amount_site_value += site_fraction
                            * association_delta_row_major[site * association_site_count + other_site] / volume;
                    }
                    const std::size_t site_col = col_offset + base_local_variable_count + other_site;
                    result.constraint_hessian_tensor_row_major[
                        target_row * variable_count * variable_count + amount_col * variable_count + site_col
                    ] = amount_site_value;
                    result.constraint_hessian_tensor_row_major[
                        target_row * variable_count * variable_count + site_col * variable_count + amount_col
                    ] = amount_site_value;
                }
            }
            const std::size_t volume_col = col_offset + species_count;
            result.constraint_hessian_tensor_row_major[
                target_row * variable_count * variable_count + volume_col * variable_count + volume_col
            ] = 2.0 * site_fraction * amount_weighted_delta_sum / (volume * volume * volume);
            for (std::size_t left_site = 0; left_site < association_site_count; ++left_site) {
                const std::size_t left_col = col_offset + base_local_variable_count + left_site;
                const double volume_site_value = -(
                    (site == left_site ? amount_weighted_delta_sum : 0.0)
                    + site_fraction
                        * amounts[static_cast<std::size_t>(site_component_index[left_site])]
                        * association_delta_row_major[site * association_site_count + left_site]
                ) / (volume * volume);
                result.constraint_hessian_tensor_row_major[
                    target_row * variable_count * variable_count + volume_col * variable_count + left_col
                ] = volume_site_value;
                result.constraint_hessian_tensor_row_major[
                    target_row * variable_count * variable_count + left_col * variable_count + volume_col
                ] = volume_site_value;
                for (std::size_t right_site = 0; right_site < association_site_count; ++right_site) {
                    double site_site_value = 0.0;
                    if (site == left_site) {
                        site_site_value += amounts[static_cast<std::size_t>(site_component_index[right_site])]
                            * association_delta_row_major[site * association_site_count + right_site] / volume;
                    }
                    if (site == right_site) {
                        site_site_value += amounts[static_cast<std::size_t>(site_component_index[left_site])]
                            * association_delta_row_major[site * association_site_count + left_site] / volume;
                    }
                    const std::size_t right_col = col_offset + base_local_variable_count + right_site;
                    result.constraint_hessian_tensor_row_major[
                        target_row * variable_count * variable_count + left_col * variable_count + right_col
                    ] = site_site_value;
                }
            }
        }
    }
}

}  // namespace epcsaft::native::equilibrium_nlp
