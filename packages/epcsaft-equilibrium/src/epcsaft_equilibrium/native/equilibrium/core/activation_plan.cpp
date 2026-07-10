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

ActivationPlan build_amount_volume_plan(
    const add_args& args,
    const std::string& family_key,
    const std::string& route,
    const std::vector<std::string>& phase_keys,
    const std::vector<std::string>& phase_kinds,
    const std::vector<std::string>& postsolve_blocks,
    double temperature,
    double pressure,
    const std::vector<double>& feed_composition,
    bool require_production_exposed
) {
    require_positive_finite(temperature, "temperature");
    require_positive_finite(pressure, "pressure");
    if (phase_keys.size() != phase_kinds.size() || phase_keys.size() < 2) {
        throw ValueError("activation-plan-ineligible: amount-volume plans require at least two aligned phases.");
    }

    const ProblemFamilyActivation& activation = activation_row_for_key(family_key);
    if (require_production_exposed
        && (!activation.production_exposed || activation.exposure_status != "production_exposed")) {
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

std::vector<std::string> normalized_phase_kind_tokens(const std::vector<std::string>& phase_kinds) {
    if (phase_kinds.size() < 2) {
        throw ValueError("activation-plan-ineligible: phase_kinds must contain at least two phases.");
    }
    std::vector<std::string> out;
    out.reserve(phase_kinds.size());
    for (const std::string& phase_kind : phase_kinds) {
        const std::string normalized = normalized_token(phase_kind);
        if (normalized != "liquid" && normalized != "vapor") {
            throw ValueError("activation-plan-ineligible: unsupported phase kind in phase_kinds.");
        }
        out.push_back(normalized);
    }
    return out;
}

std::vector<std::string> phase_keys_for_kinds(const std::vector<std::string>& phase_kinds) {
    const std::vector<std::string> normalized = normalized_phase_kind_tokens(phase_kinds);
    const int liquid_count = static_cast<int>(std::count(normalized.begin(), normalized.end(), "liquid"));
    const int vapor_count = static_cast<int>(std::count(normalized.begin(), normalized.end(), "vapor"));
    int liquid_index = 0;
    int vapor_index = 0;
    std::vector<std::string> out;
    out.reserve(normalized.size());
    for (const std::string& phase_kind : normalized) {
        if (phase_kind == "liquid") {
            ++liquid_index;
            out.push_back(liquid_count > 1 ? "liquid" + std::to_string(liquid_index) : "liquid");
            continue;
        }
        ++vapor_index;
        out.push_back(vapor_count > 1 ? "vapor" + std::to_string(vapor_index) : "vapor");
    }
    return out;
}

const ProblemFamilyActivation& activation_row_for_key(std::string_view key) {
    const auto& matrix = problem_family_activation_matrix();
    const auto found = std::find_if(
        matrix.begin(),
        matrix.end(),
        [&](const ProblemFamilyActivation& row) { return row.key == key; }
    );
    if (found == matrix.end()) {
        throw ValueError(
            "activation-plan-ineligible: activation row is missing for " + std::string(key) + "."
        );
    }
    return *found;
}

ActivationPlan build_neutral_tp_flash_activation_plan(
    const add_args& args,
    double temperature,
    double pressure,
    const std::vector<double>& feed_composition
) {
    return build_amount_volume_plan(
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
        feed_composition,
        true
    );
}

ActivationPlan build_neutral_lle_activation_plan(
    const add_args& args,
    double temperature,
    double pressure,
    const std::vector<double>& feed_composition
) {
    return build_amount_volume_plan(
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
        feed_composition,
        true
    );
}

ActivationPlan build_neutral_multiphase_nonassoc_activation_plan(
    const add_args& args,
    double temperature,
    double pressure,
    const std::vector<double>& feed_composition,
    const std::vector<std::string>& phase_kinds
) {
    const std::vector<std::string> normalized_kinds = normalized_phase_kind_tokens(phase_kinds);
    if (normalized_kinds.size() < 3) {
        throw ValueError(
            "activation-plan-ineligible: neutral_multiphase_nonassoc requires at least three requested phases."
        );
    }
    return build_amount_volume_plan(
        args,
        "neutral_multiphase_nonassoc",
        "neutral_multiphase_nonassoc",
        phase_keys_for_kinds(normalized_kinds),
        normalized_kinds,
        {
            "material_balance",
            "phase_pressure_consistency",
            "phase_equilibrium",
        },
        temperature,
        pressure,
        feed_composition,
        false
    );
}

ActivationPlan build_reactive_speciation_activation_plan(int species_count) {
    if (species_count <= 0) {
        throw ValueError("activation-plan-ineligible: reactive_speciation requires at least one species.");
    }
    const ProblemFamilyActivation& activation = activation_row_for_key("reactive_speciation");
    ActivationPlan out;
    out.family_key = activation.key;
    out.route = "reactive_speciation";
    out.phase_keys = {"homogeneous"};
    out.phase_kinds = {"homogeneous"};
    out.variable_blocks = {"species_amounts"};
    out.constraint_blocks = activation.constraint_families;
    out.residual_blocks = activation.residual_families;
    out.postsolve_blocks = {"conserved_balance", "reaction_stationarity"};
    out.variable_model = activation.variable_model;
    out.density_backend = activation.density_backend;
    return out;
}

ActivationPlan build_activation_plan(
    const add_args& args,
    const SelectorRouteRequest& raw_request
) {
    const std::string route = normalized_token(raw_request.route);
    const std::string composition_role = normalized_token(raw_request.composition_role);
    if (route != "neutral_tp_flash" && route != "neutral_lle" && route != "neutral_multiphase_nonassoc") {
        throw ValueError(
            "activation-plan-ineligible: activation-plan slice supports only neutral_tp_flash, neutral_lle, "
            "and neutral_multiphase_nonassoc."
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
    if (route == "neutral_multiphase_nonassoc") {
        return build_neutral_multiphase_nonassoc_activation_plan(
            args,
            raw_request.temperature,
            raw_request.pressure,
            raw_request.composition,
            raw_request.phase_kinds
        );
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
