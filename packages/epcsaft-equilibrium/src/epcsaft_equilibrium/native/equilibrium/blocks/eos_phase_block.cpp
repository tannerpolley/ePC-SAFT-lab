#include "equilibrium/blocks/eos_phase_block.h"

#include "equilibrium/blocks/association_block.h"
#include "equilibrium/blocks/electrolyte_block.h"
#include "equilibrium/derivatives/phase_block_derivatives.h"
#include "equilibrium/derivatives/phase_system_derivatives.h"
#include "eos/core_internal.h"

#include <cmath>
#include <numeric>
#include <sstream>

namespace epcsaft::native::equilibrium_nlp {

namespace {

void require_positive_finite(double value, const std::string& label) {
    if (std::isfinite(value) && value > 0.0) {
        return;
    }
    throw ValueError(label + " must be positive and finite.");
}

void validate_amounts(const std::vector<double>& amounts) {
    if (amounts.empty()) {
        throw ValueError("EOS phase block requires at least one species amount.");
    }
    for (double amount : amounts) {
        require_positive_finite(amount, "EOS phase species amount");
    }
}

std::vector<std::string> amount_variable_names(std::size_t count) {
    std::vector<std::string> names;
    names.reserve(count + 1);
    for (std::size_t index = 0; index < count; ++index) {
        names.push_back("n_" + std::to_string(index));
    }
    names.push_back("volume");
    return names;
}

std::vector<std::string> phase_system_variable_names(
    std::size_t phase_count,
    std::size_t species_count,
    std::size_t association_site_count
) {
    std::vector<std::string> names;
    names.reserve(phase_count * (species_count + 1 + association_site_count));
    for (std::size_t phase = 0; phase < phase_count; ++phase) {
        for (std::size_t species = 0; species < species_count; ++species) {
            names.push_back("phase_" + std::to_string(phase) + ".n_" + std::to_string(species));
        }
        names.push_back("phase_" + std::to_string(phase) + ".volume");
        for (std::size_t site = 0; site < association_site_count; ++site) {
            names.push_back("phase_" + std::to_string(phase) + ".association_site_" + std::to_string(site));
        }
    }
    return names;
}

std::vector<std::string> phase_system_constraint_names(std::size_t phase_count, std::size_t species_count) {
    std::vector<std::string> names;
    names.reserve(species_count + phase_count);
    for (std::size_t species = 0; species < species_count; ++species) {
        names.push_back("material_balance_" + std::to_string(species));
    }
    for (std::size_t phase = 0; phase < phase_count; ++phase) {
        names.push_back("phase_" + std::to_string(phase) + ".pressure_consistency");
    }
    return names;
}

std::vector<double> composition_from_amounts(const std::vector<double>& amounts, double total_amount) {
    std::vector<double> composition;
    composition.reserve(amounts.size());
    for (double amount : amounts) {
        composition.push_back(amount / total_amount);
    }
    return composition;
}

double ideal_helmholtz_amount_volume_term(const std::vector<double>& amounts, double volume) {
    double value = 0.0;
    for (double amount : amounts) {
        value += amount * (std::log(amount / volume) - 1.0);
    }
    return value;
}

void require_finite_nonnegative(double value, const std::string& label) {
    if (std::isfinite(value) && value >= 0.0) {
        return;
    }
    throw ValueError(label + " must be finite and non-negative.");
}

bool association_block_enabled(
    const std::vector<std::vector<double>>& association_site_fractions,
    const std::vector<double>& association_delta_row_major
) {
    if (association_site_fractions.empty() && association_delta_row_major.empty()) {
        return false;
    }
    if (association_site_fractions.empty() || association_delta_row_major.empty()) {
        throw ValueError("EOS phase system association variables require site fractions and a delta matrix.");
    }
    return true;
}

std::vector<int> association_site_component_index(const add_args& args, std::size_t species_count) {
    if (args.assoc_num.size() != species_count) {
        throw ValueError("EOS phase system association topology must include one assoc_num entry per species.");
    }
    std::vector<int> site_component_index;
    for (std::size_t component = 0; component < args.assoc_num.size(); ++component) {
        const int site_count = args.assoc_num[component];
        if (site_count < 0) {
            throw ValueError("EOS phase system association topology cannot contain negative site counts.");
        }
        for (int site = 0; site < site_count; ++site) {
            site_component_index.push_back(static_cast<int>(component));
        }
    }
    return site_component_index;
}

add_args without_solved_association(add_args args) {
    args.e_assoc.clear();
    args.vol_a.clear();
    args.assoc_num.clear();
    args.assoc_matrix.clear();
    args.k_hb.clear();
    return args;
}

}  // namespace

EosPhaseBlockResult evaluate_eos_phase_block(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<double>& amounts,
    double volume
) {
    require_positive_finite(temperature, "EOS phase temperature");
    if (!std::isfinite(target_pressure)) {
        throw ValueError("EOS phase target pressure must be finite.");
    }
    require_positive_finite(volume, "EOS phase volume");
    validate_amounts(amounts);

    const double total_amount = std::accumulate(amounts.begin(), amounts.end(), 0.0);
    require_positive_finite(total_amount, "EOS phase total amount");
    const std::vector<double> composition = composition_from_amounts(amounts, total_amount);
    if (!args.m.empty() && args.m.size() != composition.size()) {
        std::ostringstream msg;
        msg << "EOS phase block composition size " << composition.size()
            << " does not match parameter size " << args.m.size() << ".";
        throw ValueError(msg.str());
    }

    const double density = total_amount / volume;
    require_positive_finite(density, "EOS phase molar density");
    const double rt = kb * N_AV * temperature;
    const ScalarContributionTerms helmholtz = residual_helmholtz_result_cpp(
        temperature,
        density,
        composition,
        args
    );
    const CompressibilityFactorResult z = compressibility_factor_result_cpp(
        temperature,
        density,
        composition,
        args
    );
    const ResidualChemicalPotentialResult mu = residual_chemical_potential_result_cpp(
        temperature,
        density,
        composition,
        args
    );
    if (mu.mu.total.size() != amounts.size()) {
        throw ValueError("EOS phase residual chemical potential size did not match species count.");
    }
    const double eos_pressure = p_cpp(temperature, density, composition, args);

    EosPhaseBlockResult result;
    result.block = "eos_phase";
    result.derivative_backend = "analytic";
    result.variable_names = amount_variable_names(amounts.size());
    result.constraint_names = {"pressure_consistency"};
    result.temperature = temperature;
    result.target_pressure = target_pressure;
    result.gas_constant_temperature = rt;
    result.total_amount = total_amount;
    result.volume = volume;
    result.density = density;
    result.composition = composition;
    result.residual_helmholtz = helmholtz.total;
    result.eos_pressure = eos_pressure;
    result.compressibility_factor = z.terms.total;
    result.ideal_helmholtz = ideal_helmholtz_amount_volume_term(amounts, volume);
    result.residual_helmholtz_term = total_amount * helmholtz.total;
    result.pressure_work = target_pressure * volume / rt;
    result.electrolyte_contribution = evaluate_electrolyte_contribution_block(
        args,
        temperature,
        density,
        composition,
        amounts
    );
    result.objective = result.ideal_helmholtz + result.residual_helmholtz_term + result.pressure_work;
    result.pressure_consistency_residual = eos_pressure - target_pressure;
    result.gradient.reserve(amounts.size() + 1);
    for (std::size_t index = 0; index < amounts.size(); ++index) {
        result.gradient.push_back(std::log(amounts[index] / volume) + mu.mu.total[index]);
    }
    result.gradient.push_back((target_pressure - eos_pressure) / rt);
    populate_eos_phase_block_derivatives(result, args, temperature, target_pressure, amounts, volume);
    return result;
}

EosPhaseSystemResult evaluate_eos_phase_system(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<std::vector<double>>& phase_amounts,
    const std::vector<double>& volumes,
    const std::vector<double>& feed_amounts,
    const std::vector<double>& charges,
    const std::vector<std::vector<double>>& association_site_fractions,
    const std::vector<double>& association_delta_row_major
) {
    if (phase_amounts.empty()) {
        throw ValueError("EOS phase system requires at least one phase.");
    }
    const std::size_t phase_count = phase_amounts.size();
    const std::size_t species_count = feed_amounts.size();
    if (species_count == 0) {
        throw ValueError("EOS phase system requires at least one feed species amount.");
    }
    if (volumes.size() != phase_count) {
        throw ValueError("EOS phase system volume count must match phase count.");
    }
    for (double amount : feed_amounts) {
        require_finite_nonnegative(amount, "EOS phase system feed amount");
    }
    const bool include_association = association_block_enabled(
        association_site_fractions,
        association_delta_row_major
    );
    const std::vector<int> site_component_index =
        include_association ? association_site_component_index(args, species_count) : std::vector<int>{};
    const std::size_t association_site_count = site_component_index.size();
    if (include_association) {
        if (association_site_count == 0) {
            throw ValueError("EOS phase system association variables require active association topology.");
        }
        if (association_site_fractions.size() != phase_count) {
            throw ValueError("EOS phase system association site-fraction phase count must match phase count.");
        }
        if (association_delta_row_major.size() != association_site_count * association_site_count) {
            throw ValueError("EOS phase system association delta matrix must be square over the association site count.");
        }
        for (const auto& fractions : association_site_fractions) {
            if (fractions.size() != association_site_count) {
                throw ValueError("EOS phase system association site-fraction size must match association site count.");
            }
        }
    }

    EosPhaseSystemResult result;
    result.block = "eos_phase_system";
    result.derivative_backend = "analytic_cppad";
    result.phase_count = static_cast<int>(phase_count);
    result.species_count = static_cast<int>(species_count);
    result.association_site_count = static_cast<int>(association_site_count);
    result.association_site_component_index = site_component_index;
    result.variable_names = phase_system_variable_names(phase_count, species_count, association_site_count);
    result.constraint_names = phase_system_constraint_names(phase_count, species_count);
    result.temperature = temperature;
    result.target_pressure = target_pressure;
    result.feed_amounts = feed_amounts;
    result.phase_blocks.reserve(phase_count);

    const std::size_t base_local_variable_count = species_count + 1;
    const std::size_t local_variable_count = base_local_variable_count + association_site_count;
    const add_args phase_block_args = include_association ? without_solved_association(args) : args;
    result.gradient.reserve(phase_count * local_variable_count);
    for (std::size_t phase = 0; phase < phase_count; ++phase) {
        if (phase_amounts[phase].size() != species_count) {
            throw ValueError("EOS phase system phase amount sizes must match feed species count.");
        }
        result.phase_blocks.push_back(
            evaluate_eos_phase_block(phase_block_args, temperature, target_pressure, phase_amounts[phase], volumes[phase])
        );
        const EosPhaseBlockResult& block = result.phase_blocks.back();
        if (block.gradient.size() != base_local_variable_count) {
            throw ValueError("EOS phase block derivative size did not match the phase system variables.");
        }
        if (block.pressure_jacobian_row_major.size() != base_local_variable_count) {
            throw ValueError("EOS phase block pressure derivative size did not match the phase system variables.");
        }
        result.objective += block.objective;
        result.gradient.insert(result.gradient.end(), block.gradient.begin(), block.gradient.end());
        result.gradient.insert(result.gradient.end(), association_site_count, 0.0);
    }

    if (!charges.empty() && charges.size() != species_count) {
        throw ValueError("EOS phase system charge count must match feed species count.");
    }
    const PhaseChargeBlockResult charge_block = charges.empty()
        ? PhaseChargeBlockResult{}
        : evaluate_phase_charge_block(phase_amounts, charges, static_cast<int>(local_variable_count));
    const std::size_t charge_constraint_count = charge_block.residuals.size();
    std::vector<AssociationMassActionBlockResult> association_blocks;
    association_blocks.reserve(include_association ? phase_count : 0);
    for (std::size_t phase = 0; phase < phase_count && include_association; ++phase) {
        std::vector<double> site_composition;
        site_composition.reserve(association_site_count);
        for (int component_index : site_component_index) {
            site_composition.push_back(result.phase_blocks[phase].composition[static_cast<std::size_t>(component_index)]);
        }
        association_blocks.push_back(
            evaluate_association_mass_action_block(
                result.phase_blocks[phase].density,
                association_site_fractions[phase],
                site_composition,
                association_delta_row_major
            )
        );
        const auto& block = association_blocks.back();
        if (block.residuals.size() != association_site_count
            || block.site_fraction_jacobian_row_major.size() != association_site_count * association_site_count) {
            throw ValueError("EOS phase system association block size did not match the phase variable model.");
        }
        double phase_association_objective = 0.0;
        const std::size_t col_offset = phase * local_variable_count;
        for (std::size_t site = 0; site < association_site_count; ++site) {
            const double site_fraction = association_site_fractions[phase][site];
            const std::size_t component_index = static_cast<std::size_t>(site_component_index[site]);
            const double amount = phase_amounts[phase][component_index];
            const double site_objective = std::log(site_fraction) - 0.5 * site_fraction + 0.5;
            phase_association_objective += amount * site_objective;
            result.gradient[col_offset + component_index] += site_objective;
            result.gradient[col_offset + base_local_variable_count + site] += amount * (1.0 / site_fraction - 0.5);
        }
        result.phase_association_objectives.push_back(phase_association_objective);
        result.association_objective += phase_association_objective;
        result.objective += phase_association_objective;
    }
    const std::size_t association_constraint_count = association_blocks.size() * association_site_count;
    const std::size_t constraint_count =
        species_count + phase_count + charge_constraint_count + association_constraint_count;
    result.constraints.assign(constraint_count, 0.0);
    for (std::size_t species = 0; species < species_count; ++species) {
        result.constraints[species] = -feed_amounts[species];
        for (std::size_t phase = 0; phase < phase_count; ++phase) {
            result.constraints[species] += phase_amounts[phase][species];
        }
    }
    for (std::size_t phase = 0; phase < phase_count; ++phase) {
        result.constraints[species_count + phase] = result.phase_blocks[phase].pressure_consistency_residual;
    }
    for (std::size_t row = 0; row < charge_constraint_count; ++row) {
        result.constraint_names.push_back(charge_block.constraint_names[row]);
        result.constraints[species_count + phase_count + row] = charge_block.residuals[row];
    }
    result.phase_charge_residuals = charge_block.residuals;
    const std::size_t association_row_offset = species_count + phase_count + charge_constraint_count;
    for (std::size_t phase = 0; phase < association_blocks.size(); ++phase) {
        const auto& block = association_blocks[phase];
        for (std::size_t site = 0; site < association_site_count; ++site) {
            const std::size_t target_row = association_row_offset + phase * association_site_count + site;
            result.constraint_names.push_back(
                "phase_" + std::to_string(phase) + "." + block.constraint_names[site]
            );
            result.constraints[target_row] = block.residuals[site];
            result.phase_association_residuals.push_back(block.residuals[site]);
        }
    }

    populate_eos_phase_system_derivatives(
        result,
        phase_amounts,
        volumes,
        charge_block,
        association_blocks,
        site_component_index,
        association_site_fractions,
        association_delta_row_major
    );
    return result;
}

}  // namespace epcsaft::native::equilibrium_nlp
