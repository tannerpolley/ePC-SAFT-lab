#pragma once

#include "equilibrium/blocks/eos_phase_block.h"

#include <vector>

struct add_args;

namespace epcsaft::native::equilibrium_nlp {

struct TemperatureRoutePhaseBlock {
    EosPhaseBlockResult block;
    std::vector<double> gradient;
    std::vector<double> objective_hessian_row_major;
    std::vector<double> objective_third_derivative_tensor_row_major;
    std::vector<double> pressure_jacobian_row_major;
    std::vector<double> pressure_hessian_row_major;
};

void populate_eos_phase_block_derivatives(
    EosPhaseBlockResult& result,
    const ::add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<double>& amounts,
    double volume
);

TemperatureRoutePhaseBlock evaluate_temperature_route_phase_block(
    const ::add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<double>& amounts,
    double volume
);

}  // namespace epcsaft::native::equilibrium_nlp
