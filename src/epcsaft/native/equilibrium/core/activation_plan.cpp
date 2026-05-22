#include "equilibrium/core/activation_plan.h"

#include "equilibrium/core/selector_core.h"
#include "model/native_types.h"

#include <algorithm>
#include <cmath>
#include <cctype>
#include <numeric>

namespace epcsaft::native::equilibrium {
namespace {

std::string normalized_token(std::string value) {
    std::transform(value.begin(), value.end(), value.begin(), [](unsigned char ch) {
        return static_cast<char>(std::tolower(ch));
    });
    return value;
}

void require_positive_finite(double value, const std::string& label) {
    if (std::isfinite(value) && value > 0.0) {
        return;
    }
    throw ValueError("activation-plan-ineligible: " + label + " must be positive and finite.");
}

std::vector<double> normalized_positive_composition(
    const add_args& args,
    const std::vector<double>& composition
) {
    const std::size_t expected = args.m.size();
    if (composition.size() != expected) {
        throw ValueError("activation-plan-ineligible: feed composition length must match mixture component count.");
    }
    double total = 0.0;
    for (double value : composition) {
        require_positive_finite(value, "feed composition value");
        total += value;
    }
    require_positive_finite(total, "feed composition total");
    std::vector<double> normalized;
    normalized.reserve(composition.size());
    for (double value : composition) {
        normalized.push_back(value / total);
    }
    return normalized;
}

}  // namespace

const ProblemFamilyActivation& activation_row_for_key(const std::string& key) {
    const auto& matrix = problem_family_activation_matrix();
    const auto found = std::find_if(
        matrix.begin(),
        matrix.end(),
        [&](const ProblemFamilyActivation& row) { return row.key == key; }
    );
    if (found == matrix.end()) {
        throw ValueError("activation-plan-ineligible: activation row is missing for " + key + ".");
    }
    return *found;
}

ActivationPlan build_neutral_tp_flash_activation_plan(
    const add_args& args,
    double temperature,
    double pressure,
    const std::vector<double>& feed_composition
) {
    require_positive_finite(temperature, "temperature");
    require_positive_finite(pressure, "pressure");

    const ProblemFamilyActivation& activation = activation_row_for_key("neutral_tp_flash");
    if (!activation.production_exposed || activation.exposure_status != "production_exposed") {
        throw ValueError("activation-plan-ineligible: neutral_tp_flash is not production exposed.");
    }

    ActivationPlan out;
    out.family_key = activation.key;
    out.route = "neutral_tp_flash";
    out.phase_keys = {"liquid", "vapor"};
    out.phase_kinds = {"liquid", "vapor"};
    out.variable_blocks = {"phase_species_amounts", "phase_volumes"};
    out.constraint_blocks = activation.constraint_families;
    out.residual_blocks = activation.residual_families;
    out.postsolve_blocks = {
        "material_balance",
        "phase_pressure_consistency",
        "phase_equilibrium",
        "phase_distance",
        "phase_volume_gap",
    };
    out.variable_model = activation.variable_model;
    out.density_backend = activation.density_backend;
    out.feed_composition = normalized_positive_composition(args, feed_composition);
    out.temperature = temperature;
    out.pressure = pressure;
    return out;
}

ActivationPlan build_activation_plan(
    const add_args& args,
    const SelectorRouteRequest& raw_request
) {
    const std::string route = normalized_token(raw_request.route);
    const std::string composition_role = normalized_token(raw_request.composition_role);
    if (route != "neutral_tp_flash") {
        throw ValueError(
            "activation-plan-ineligible: first activation-plan slice supports only neutral_tp_flash."
        );
    }
    if (!raw_request.has_temperature) {
        throw ValueError("activation-plan-ineligible: neutral_tp_flash requires temperature.");
    }
    if (!raw_request.has_pressure) {
        throw ValueError("activation-plan-ineligible: neutral_tp_flash requires pressure.");
    }
    if (composition_role != "feed") {
        throw ValueError("activation-plan-ineligible: neutral_tp_flash requires composition_role='feed'.");
    }
    return build_neutral_tp_flash_activation_plan(
        args,
        raw_request.temperature,
        raw_request.pressure,
        raw_request.composition
    );
}

}  // namespace epcsaft::native::equilibrium
