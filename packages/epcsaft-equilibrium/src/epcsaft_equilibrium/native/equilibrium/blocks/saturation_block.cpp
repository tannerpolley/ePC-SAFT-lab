#include "equilibrium/blocks/saturation_block.h"

#include "eos/core_internal.h"

#include <algorithm>
#include <cmath>
#include <string>
#include <utility>

namespace epcsaft::native::equilibrium_nlp {

namespace {

void require_finite_value(double value, const std::string& label) {
    if (std::isfinite(value)) {
        return;
    }
    throw ValueError(label + " must be finite.");
}

void require_positive_finite_value(double value, const std::string& label) {
    if (std::isfinite(value) && value > 0.0) {
        return;
    }
    throw ValueError(label + " must be positive and finite.");
}

void require_single_component(const add_args& args) {
    if (args.m.size() == 1) {
        return;
    }
    throw ValueError("single-component VLE block requires exactly one component.");
}

double phase_reduced_chemical_potential(const EosPhaseBlockResult& block) {
    if (block.gradient.size() != 2) {
        throw ValueError("single-component VLE phase gradient shape did not match one component plus volume.");
    }
    return block.gradient[0];
}

double phase_reduced_chemical_potential_log_density_derivative(const EosPhaseBlockResult& block) {
    if (block.objective_curvature_rows != 2
        || block.objective_curvature_cols != 2
        || block.objective_curvature_row_major.size() != 4) {
        throw ValueError(
            "single-component VLE phase curvature shape did not match one component plus volume."
        );
    }
    const double species_volume_curvature = block.objective_curvature_row_major[1];
    return -block.volume * species_volume_curvature;
}

double pressure_scale(double pressure) {
    return 1.0 / std::max(std::abs(pressure), 1.0e5);
}

}  // namespace

SingleComponentVleBlockResult evaluate_single_component_vle_block(
    const add_args& args,
    double temperature,
    double log_vapor_density,
    double log_liquid_density,
    double log_saturation_pressure
) {
    require_single_component(args);
    require_positive_finite_value(temperature, "single-component VLE temperature");
    require_finite_value(log_vapor_density, "single-component VLE vapor log-density");
    require_finite_value(log_liquid_density, "single-component VLE liquid log-density");
    require_finite_value(log_saturation_pressure, "single-component VLE saturation log-pressure");

    const double vapor_density = std::exp(log_vapor_density);
    const double liquid_density = std::exp(log_liquid_density);
    const double p_sat = std::exp(log_saturation_pressure);
    require_positive_finite_value(vapor_density, "single-component VLE vapor density");
    require_positive_finite_value(liquid_density, "single-component VLE liquid density");
    require_positive_finite_value(p_sat, "single-component VLE saturation pressure");

    EosPhaseBlockResult vapor_block = evaluate_eos_phase_block(
        args,
        temperature,
        p_sat,
        {1.0},
        1.0 / vapor_density
    );
    EosPhaseBlockResult liquid_block = evaluate_eos_phase_block(
        args,
        temperature,
        p_sat,
        {1.0},
        1.0 / liquid_density
    );
    const double vapor_mu = phase_reduced_chemical_potential(vapor_block);
    const double liquid_mu = phase_reduced_chemical_potential(liquid_block);
    const double vapor_mu_log_density_derivative =
        phase_reduced_chemical_potential_log_density_derivative(vapor_block);
    const double liquid_mu_log_density_derivative =
        phase_reduced_chemical_potential_log_density_derivative(liquid_block);

    SingleComponentVleBlockResult result;
    result.block = "single_component_vle";
    result.derivative_backend = "analytic_cppad";
    result.jacobian_backend = "cppad_phase_blocks";
    result.variable_names = {"log_rho_v", "log_rho_l", "log_p_sat"};
    result.constraint_names = {
        "vapor_pressure_consistency",
        "liquid_pressure_consistency",
        "chemical_potential_equality",
    };
    result.temperature = temperature;
    result.vapor_density = vapor_density;
    result.liquid_density = liquid_density;
    result.p_sat = p_sat;
    result.vapor_pressure = vapor_block.eos_pressure;
    result.liquid_pressure = liquid_block.eos_pressure;
    result.vapor_reduced_chemical_potential = vapor_mu;
    result.liquid_reduced_chemical_potential = liquid_mu;
    result.vapor_pressure_density_derivative = vapor_block.pressure_density_derivative;
    result.liquid_pressure_density_derivative = liquid_block.pressure_density_derivative;
    result.residuals = {
        result.vapor_pressure - p_sat,
        result.liquid_pressure - p_sat,
        vapor_mu - liquid_mu,
    };
    result.jacobian_rows = 3;
    result.jacobian_cols = 3;
    result.jacobian_row_major = {
        result.vapor_pressure_density_derivative * vapor_density,
        0.0,
        -p_sat,
        0.0,
        result.liquid_pressure_density_derivative * liquid_density,
        -p_sat,
        vapor_mu_log_density_derivative,
        -liquid_mu_log_density_derivative,
        0.0,
    };
    result.constraint_scaling = {pressure_scale(p_sat), pressure_scale(p_sat), 1.0};
    result.vapor_phase_block = std::move(vapor_block);
    result.liquid_phase_block = std::move(liquid_block);
    return result;
}

}  // namespace epcsaft::native::equilibrium_nlp
