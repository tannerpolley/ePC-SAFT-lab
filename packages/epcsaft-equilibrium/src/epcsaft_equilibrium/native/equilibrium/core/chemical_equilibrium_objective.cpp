#include "equilibrium/core/chemical_equilibrium_objective.h"

#include "eos/core_internal.h"
#include "equilibrium/blocks/reaction_block.h"

#include <algorithm>
#include <cmath>
#include <numeric>

namespace epcsaft::native::equilibrium_nlp {

namespace {

void require_finite(double value, const std::string& label) {
    if (std::isfinite(value)) {
        return;
    }
    throw ValueError(label + " must be finite.");
}

void require_positive_finite(double value, const std::string& label) {
    if (std::isfinite(value) && value > 0.0) {
        return;
    }
    throw ValueError(label + " must be positive and finite.");
}

void require_eos_activity_input_shape(
    const ChemicalEquilibriumNlpInput& input,
    std::size_t species_count
) {
    if (
        input.eos_activity_convention != "eos_x_phi"
        && input.eos_activity_convention != "eos_x_gamma"
    ) {
        throw ValueError("chemical equilibrium EOS activity convention must be eos_x_phi or eos_x_gamma.");
    }
    require_positive_finite(input.eos_activity_temperature, "chemical equilibrium EOS activity temperature");
    require_positive_finite(input.eos_activity_pressure, "chemical equilibrium EOS activity pressure");
    if (input.eos_activity_phase_kind != 0 && input.eos_activity_phase_kind != 1) {
        throw ValueError("chemical equilibrium EOS activity reference phase must be liquid or vapor.");
    }
    if (input.eos_activity_convention == "eos_x_gamma" && input.eos_activity_phase_kind != 0) {
        throw ValueError("chemical equilibrium eos_x_gamma standard states require a liquid reference phase.");
    }
    if (!input.eos_activity_args) {
        throw ValueError("chemical equilibrium EOS activity standard states require native EOS parameters.");
    }
    if (!input.eos_activity_args->m.empty() && input.eos_activity_args->m.size() != species_count) {
        throw ValueError("chemical equilibrium EOS activity mixture component count must match CE species count.");
    }
}

void require_supported_sensitivity(
    const PhaseStateCompositionSensitivityResult& sensitivity,
    std::size_t species_count,
    const std::string& activity_convention
) {
    if (sensitivity.supported
        && sensitivity.ln_fugacity.size() == species_count
        && sensitivity.jacobian_row_major.size() == species_count * species_count) {
        return;
    }
    const std::string message = sensitivity.message.empty()
        ? "missing CppAD phase-state fugacity composition sensitivity evidence"
        : sensitivity.message;
    throw ValueError(
        "chemical equilibrium " + activity_convention
        + " objective requires supported fugacity sensitivities: " + message
    );
}

void require_eos_x_gamma_charge_groups(
    const add_args& args,
    const ChargeGroups& groups,
    std::size_t species_count
) {
    if (args.z.size() != species_count) {
        throw ValueError("chemical equilibrium eos_x_gamma requires charges aligned with CE species.");
    }
    if (args.mw.size() != species_count) {
        throw ValueError("chemical equilibrium eos_x_gamma requires molecular weights aligned with CE species.");
    }
    if (groups.cations.empty() || groups.anions.empty()) {
        throw ValueError("chemical equilibrium eos_x_gamma requires at least one cation and one anion.");
    }
    if (groups.solvents.empty()) {
        throw ValueError("chemical equilibrium eos_x_gamma requires a neutral solvent reference.");
    }
}

double solvent_fraction_sum(const std::vector<double>& mole_fractions, const ChargeGroups& groups) {
    double solvent_sum = 0.0;
    for (int solvent : groups.solvents) {
        solvent_sum += mole_fractions[static_cast<std::size_t>(solvent)];
    }
    if (solvent_sum > 0.0) {
        return solvent_sum;
    }
    throw ValueError("chemical equilibrium eos_x_gamma requires a positive solvent fraction.");
}

double reference_solvent_budget(const ChargeGroups& groups, std::size_t species_count, double eps) {
    return std::max(
        1.0 - eps * static_cast<double>(species_count - groups.solvents.size()),
        eps * static_cast<double>(groups.solvents.size())
    );
}

std::vector<double> build_eos_x_gamma_reference_composition(
    const std::vector<double>& mole_fractions,
    const ChargeGroups& groups,
    double eps
) {
    const std::size_t species_count = mole_fractions.size();
    const double solvent_sum = solvent_fraction_sum(mole_fractions, groups);
    const double solvent_budget = reference_solvent_budget(groups, species_count, eps);
    std::vector<double> reference(species_count, eps);
    for (int solvent : groups.solvents) {
        const std::size_t index = static_cast<std::size_t>(solvent);
        reference[index] = mole_fractions[index] / solvent_sum * solvent_budget;
    }
    const double reference_sum = std::accumulate(reference.begin(), reference.end(), 0.0);
    require_positive_finite(reference_sum, "chemical equilibrium eos_x_gamma reference composition sum");
    for (double& value : reference) {
        value /= reference_sum;
    }
    return reference;
}

std::vector<double> eos_x_gamma_reference_composition_jacobian(
    const std::vector<double>& mole_fractions,
    const ChargeGroups& groups,
    double eps
) {
    const std::size_t species_count = mole_fractions.size();
    const double solvent_sum = solvent_fraction_sum(mole_fractions, groups);
    const double solvent_budget = reference_solvent_budget(groups, species_count, eps);
    const double reference_sum =
        solvent_budget + eps * static_cast<double>(species_count - groups.solvents.size());
    require_positive_finite(reference_sum, "chemical equilibrium eos_x_gamma reference composition sum");

    std::vector<double> jacobian(species_count * species_count, 0.0);
    const double scale = solvent_budget / reference_sum;
    const double denominator = solvent_sum * solvent_sum;
    for (int row_index : groups.solvents) {
        const std::size_t row = static_cast<std::size_t>(row_index);
        for (int column_index : groups.solvents) {
            const std::size_t column = static_cast<std::size_t>(column_index);
            const double numerator = (row == column ? solvent_sum : 0.0) - mole_fractions[row];
            jacobian[row * species_count + column] = scale * numerator / denominator;
        }
    }
    return jacobian;
}

double composition_amount_derivative(
    const std::vector<double>& mole_fractions,
    double total_amount,
    std::size_t component,
    std::size_t amount_index
) {
    return ((component == amount_index ? 1.0 : 0.0) - mole_fractions[component]) / total_amount;
}

PhaseStateCompositionSensitivityResult evaluate_eos_activity_sensitivity(
    const ChemicalEquilibriumNlpInput& input,
    const std::vector<double>& mole_fractions
) {
    const std::size_t species_count = mole_fractions.size();
    const PhaseStateCompositionSensitivityResult current =
        phase_state_ln_fugacity_composition_sensitivity_cpp(
            input.eos_activity_temperature,
            input.eos_activity_pressure,
            mole_fractions,
            input.eos_activity_phase_kind,
            *input.eos_activity_args
        );
    require_supported_sensitivity(current, species_count, input.eos_activity_convention);
    if (input.eos_activity_convention == "eos_x_phi") {
        return current;
    }

    const double reference_eps = 1.0e-12;
    const ChargeGroups groups = collect_charge_groups(*input.eos_activity_args, species_count);
    require_eos_x_gamma_charge_groups(*input.eos_activity_args, groups, species_count);
    const std::vector<double> reference_composition =
        build_eos_x_gamma_reference_composition(mole_fractions, groups, reference_eps);
    const PhaseStateCompositionSensitivityResult reference =
        phase_state_ln_fugacity_composition_sensitivity_cpp(
            input.eos_activity_temperature,
            input.eos_activity_pressure,
            reference_composition,
            0,
            *input.eos_activity_args
        );
    require_supported_sensitivity(reference, species_count, input.eos_activity_convention);
    const std::vector<double> reference_jacobian =
        eos_x_gamma_reference_composition_jacobian(mole_fractions, groups, reference_eps);

    PhaseStateCompositionSensitivityResult activity = current;
    activity.backend = "cppad_implicit_activity_coefficient";
    activity.ln_fugacity.assign(species_count, 0.0);
    activity.jacobian_row_major.assign(species_count * species_count, 0.0);
    for (std::size_t row = 0; row < species_count; ++row) {
        activity.ln_fugacity[row] = current.ln_fugacity[row] - reference.ln_fugacity[row];
        for (std::size_t column = 0; column < species_count; ++column) {
            double reference_chain = 0.0;
            for (std::size_t ref_component = 0; ref_component < species_count; ++ref_component) {
                reference_chain += reference.jacobian_row_major[row * species_count + ref_component]
                    * reference_jacobian[ref_component * species_count + column];
            }
            activity.jacobian_row_major[row * species_count + column] =
                current.jacobian_row_major[row * species_count + column] - reference_chain;
        }
    }
    return activity;
}

HomogeneousChemicalEquilibriumBlockResult evaluate_eos_activity_objective(
    const ChemicalEquilibriumNlpInput& input,
    const std::vector<double>& amounts
) {
    HomogeneousChemicalEquilibriumBlockResult out = evaluate_homogeneous_chemical_equilibrium_block(
        amounts,
        static_cast<int>(input.reaction_labels.size()),
        input.stoichiometry_row_major,
        static_cast<int>(input.conservation_labels.size()),
        input.conservation_matrix_row_major,
        input.conservation_totals,
        input.log_equilibrium_constants
    );
    const std::size_t species_count = amounts.size();
    require_eos_activity_input_shape(input, species_count);
    const double total_amount = std::accumulate(amounts.begin(), amounts.end(), 0.0);
    require_positive_finite(total_amount, "chemical equilibrium EOS activity total amount");

    const PhaseStateCompositionSensitivityResult sensitivity =
        evaluate_eos_activity_sensitivity(input, out.mole_fractions);

    out.activity_model = input.eos_activity_convention;
    out.activity_derivative_backend = sensitivity.backend;
    out.eos_temperature = input.eos_activity_temperature;
    out.eos_pressure = input.eos_activity_pressure;
    out.eos_density = sensitivity.density;
    out.eos_phase_kind = input.eos_activity_phase_kind;
    out.eos_reference_phase = input.eos_activity_reference_phase;
    out.ln_activity_coefficients = sensitivity.ln_fugacity;
    out.activities.assign(species_count, 0.0);
    out.objective_gradient.assign(species_count, 0.0);
    out.objective_value = 0.0;
    std::vector<double> log_activities(species_count, 0.0);
    for (std::size_t species = 0; species < species_count; ++species) {
        require_positive_finite(out.mole_fractions[species], "chemical equilibrium EOS activity mole fraction");
        require_finite(
            out.ln_activity_coefficients[species],
            "chemical equilibrium EOS activity ln activity coefficient"
        );
        log_activities[species] = std::log(out.mole_fractions[species])
            + out.ln_activity_coefficients[species];
        out.activities[species] = std::exp(log_activities[species]);
        out.objective_gradient[species] = out.standard_mu_rt[species] + log_activities[species];
        out.objective_value += amounts[species] * out.objective_gradient[species];
    }

    out.hessian_row_major.assign(species_count * species_count, 0.0);
    for (std::size_t row = 0; row < species_count; ++row) {
        for (std::size_t column = 0; column < species_count; ++column) {
            double value = 0.0;
            for (std::size_t component = 0; component < species_count; ++component) {
                const double ideal_derivative =
                    row == component ? 1.0 / out.mole_fractions[row] : 0.0;
                const double activity_derivative =
                    sensitivity.jacobian_row_major[row * species_count + component];
                value += (ideal_derivative + activity_derivative)
                    * composition_amount_derivative(
                        out.mole_fractions,
                        total_amount,
                        component,
                        column
                    );
            }
            out.hessian_row_major[row * species_count + column] = value;
        }
    }
    for (std::size_t row = 0; row < species_count; ++row) {
        for (std::size_t column = 0; column < row; ++column) {
            const double symmetric = 0.5
                * (
                    out.hessian_row_major[row * species_count + column]
                    + out.hessian_row_major[column * species_count + row]
                );
            out.hessian_row_major[row * species_count + column] = symmetric;
            out.hessian_row_major[column * species_count + row] = symmetric;
        }
    }

    const int reaction_count = static_cast<int>(input.reaction_labels.size());
    out.log_q.assign(static_cast<std::size_t>(reaction_count), 0.0);
    out.reaction_residuals.assign(static_cast<std::size_t>(reaction_count), 0.0);
    out.reaction_affinities = reaction_affinities_from_gradient(
        out.objective_gradient,
        reaction_count,
        input.stoichiometry_row_major
    );
    out.affinity_jacobian_row_major.assign(static_cast<std::size_t>(reaction_count) * species_count, 0.0);
    for (int reaction = 0; reaction < reaction_count; ++reaction) {
        const std::size_t reaction_offset = static_cast<std::size_t>(reaction) * species_count;
        for (std::size_t species = 0; species < species_count; ++species) {
            const double coefficient = input.stoichiometry_row_major[reaction_offset + species];
            out.log_q[static_cast<std::size_t>(reaction)] += coefficient * log_activities[species];
            for (std::size_t amount = 0; amount < species_count; ++amount) {
                out.affinity_jacobian_row_major[reaction_offset + amount] +=
                    coefficient * out.hessian_row_major[species * species_count + amount];
            }
        }
        out.reaction_residuals[static_cast<std::size_t>(reaction)] =
            out.log_q[static_cast<std::size_t>(reaction)]
            - input.log_equilibrium_constants[static_cast<std::size_t>(reaction)];
    }
    out.objective_scaling = 1.0 / std::max(1.0, std::abs(out.objective_value));
    return out;
}

}  // namespace

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
    if (input.eos_activity_enabled) {
        return evaluate_eos_activity_objective(input, amounts);
    }
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
