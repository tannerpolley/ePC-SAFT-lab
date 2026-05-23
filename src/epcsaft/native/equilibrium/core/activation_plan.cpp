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

ActivationPlan build_two_phase_amount_volume_plan(
    const add_args& args,
    const std::string& family_key,
    const std::string& route,
    const std::vector<std::string>& phase_keys,
    const std::vector<std::string>& phase_kinds,
    const std::vector<std::string>& postsolve_blocks,
    double temperature,
    double pressure,
    const std::vector<double>& feed_composition
) {
    require_positive_finite(temperature, "temperature");
    require_positive_finite(pressure, "pressure");

    const ProblemFamilyActivation& activation = activation_row_for_key(family_key);
    if (!activation.production_exposed || activation.exposure_status != "production_exposed") {
        throw ValueError("activation-plan-ineligible: " + family_key + " is not production exposed.");
    }

    ActivationPlan out;
    out.family_key = activation.key;
    out.route = route;
    out.phase_keys = phase_keys;
    out.phase_kinds = phase_kinds;
    out.variable_blocks = {"phase_species_amounts", "phase_volumes"};
    out.constraint_blocks = activation.constraint_families;
    out.residual_blocks = activation.residual_families;
    out.postsolve_blocks = postsolve_blocks;
    out.variable_model = activation.variable_model;
    out.density_backend = activation.density_backend;
    out.feed_composition = normalized_positive_composition(args, feed_composition);
    out.temperature = temperature;
    out.pressure = pressure;
    return out;
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
    return build_two_phase_amount_volume_plan(
        args,
        "neutral_tp_flash",
        "neutral_tp_flash",
        {"liquid", "vapor"},
        {"liquid", "vapor"},
        {
            "material_balance",
            "phase_pressure_consistency",
            "phase_equilibrium",
            "phase_distance",
            "phase_volume_gap",
        },
        temperature,
        pressure,
        feed_composition
    );
}

ActivationPlan build_neutral_lle_activation_plan(
    const add_args& args,
    double temperature,
    double pressure,
    const std::vector<double>& feed_composition
) {
    return build_two_phase_amount_volume_plan(
        args,
        "neutral_lle",
        "neutral_lle",
        {"liquid1", "liquid2"},
        {"liquid", "liquid"},
        {
            "material_balance",
            "phase_pressure_consistency",
            "phase_equilibrium",
            "phase_distance",
        },
        temperature,
        pressure,
        feed_composition
    );
}

ActivationPlan build_activation_plan(
    const add_args& args,
    const SelectorRouteRequest& raw_request
) {
    const std::string route = normalized_token(raw_request.route);
    const std::string composition_role = normalized_token(raw_request.composition_role);
    if (route != "neutral_tp_flash" && route != "neutral_lle") {
        throw ValueError(
            "activation-plan-ineligible: activation-plan slice supports only neutral_tp_flash and neutral_lle."
        );
    }
    if (!raw_request.has_temperature) {
        throw ValueError("activation-plan-ineligible: " + route + " requires temperature.");
    }
    if (!raw_request.has_pressure) {
        throw ValueError("activation-plan-ineligible: " + route + " requires pressure.");
    }
    if (composition_role != "feed") {
        throw ValueError("activation-plan-ineligible: " + route + " requires composition_role='feed'.");
    }
    if (route == "neutral_lle") {
        return build_neutral_lle_activation_plan(
            args,
            raw_request.temperature,
            raw_request.pressure,
            raw_request.composition
        );
    }
    return build_neutral_tp_flash_activation_plan(
        args,
        raw_request.temperature,
        raw_request.pressure,
        raw_request.composition
    );
}

}  // namespace epcsaft::native::equilibrium
