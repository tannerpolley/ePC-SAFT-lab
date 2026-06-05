#pragma once

#include <string>
#include <vector>

#include "equilibrium/blocks/eos_phase_block.h"

struct add_args;

namespace epcsaft::native::equilibrium_nlp {

struct SingleComponentVleBlockResult {
    std::string block;
    std::string derivative_backend;
    std::string jacobian_backend;
    std::vector<std::string> variable_names;
    std::vector<std::string> constraint_names;
    double temperature = 0.0;
    double vapor_density = 0.0;
    double liquid_density = 0.0;
    double p_sat = 0.0;
    double vapor_pressure = 0.0;
    double liquid_pressure = 0.0;
    double vapor_reduced_chemical_potential = 0.0;
    double liquid_reduced_chemical_potential = 0.0;
    double vapor_pressure_density_derivative = 0.0;
    double liquid_pressure_density_derivative = 0.0;
    std::vector<double> residuals;
    int jacobian_rows = 0;
    int jacobian_cols = 0;
    std::vector<double> jacobian_row_major;
    std::vector<double> constraint_scaling;
    EosPhaseBlockResult vapor_phase_block;
    EosPhaseBlockResult liquid_phase_block;
};

SingleComponentVleBlockResult evaluate_single_component_vle_block(
    const add_args& args,
    double temperature,
    double log_vapor_density,
    double log_liquid_density,
    double log_saturation_pressure
);

}  // namespace epcsaft::native::equilibrium_nlp
