#include "model/resolved_input.h"
#include "model/resolved_input_evaluator.h"

#include <algorithm>
#include <array>
#include <cctype>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <iomanip>
#include <limits>
#include <set>
#include <sstream>
#include <stdexcept>
#include <tuple>

namespace {

bool nonblank(const std::string& value) {
    return !value.empty() && std::any_of(value.begin(), value.end(), [](unsigned char character) {
        return !std::isspace(character);
    });
}

bool is_sha256(const std::string& value) {
    return value.size() == 64 && std::all_of(value.begin(), value.end(), [](unsigned char character) {
        return std::isxdigit(character) && !std::isupper(character);
    });
}

class Sha256 final {
public:
    void update(const unsigned char* data, std::size_t length) {
        for (std::size_t index = 0; index < length; ++index) {
            block_[block_length_++] = data[index];
            bit_length_ += 8;
            if (block_length_ == block_.size()) {
                transform();
                block_length_ = 0;
            }
        }
    }

    std::string finish() {
        block_[block_length_++] = 0x80;
        if (block_length_ > 56) {
            while (block_length_ < 64) block_[block_length_++] = 0;
            transform();
            block_length_ = 0;
        }
        while (block_length_ < 56) block_[block_length_++] = 0;
        for (int shift = 56; shift >= 0; shift -= 8) {
            block_[block_length_++] = static_cast<unsigned char>((bit_length_ >> shift) & 0xffU);
        }
        transform();

        std::ostringstream out;
        out << std::hex << std::setfill('0');
        for (std::uint32_t word : state_) out << std::setw(8) << word;
        return out.str();
    }

private:
    static constexpr std::array<std::uint32_t, 64> constants_ = {
        0x428a2f98U, 0x71374491U, 0xb5c0fbcfU, 0xe9b5dba5U, 0x3956c25bU, 0x59f111f1U,
        0x923f82a4U, 0xab1c5ed5U, 0xd807aa98U, 0x12835b01U, 0x243185beU, 0x550c7dc3U,
        0x72be5d74U, 0x80deb1feU, 0x9bdc06a7U, 0xc19bf174U, 0xe49b69c1U, 0xefbe4786U,
        0x0fc19dc6U, 0x240ca1ccU, 0x2de92c6fU, 0x4a7484aaU, 0x5cb0a9dcU, 0x76f988daU,
        0x983e5152U, 0xa831c66dU, 0xb00327c8U, 0xbf597fc7U, 0xc6e00bf3U, 0xd5a79147U,
        0x06ca6351U, 0x14292967U, 0x27b70a85U, 0x2e1b2138U, 0x4d2c6dfcU, 0x53380d13U,
        0x650a7354U, 0x766a0abbU, 0x81c2c92eU, 0x92722c85U, 0xa2bfe8a1U, 0xa81a664bU,
        0xc24b8b70U, 0xc76c51a3U, 0xd192e819U, 0xd6990624U, 0xf40e3585U, 0x106aa070U,
        0x19a4c116U, 0x1e376c08U, 0x2748774cU, 0x34b0bcb5U, 0x391c0cb3U, 0x4ed8aa4aU,
        0x5b9cca4fU, 0x682e6ff3U, 0x748f82eeU, 0x78a5636fU, 0x84c87814U, 0x8cc70208U,
        0x90befffaU, 0xa4506cebU, 0xbef9a3f7U, 0xc67178f2U,
    };

    static std::uint32_t rotate_right(std::uint32_t value, unsigned int count) {
        return (value >> count) | (value << (32U - count));
    }

    void transform() {
        std::array<std::uint32_t, 64> schedule{};
        for (std::size_t index = 0; index < 16; ++index) {
            const std::size_t offset = index * 4;
            schedule[index] = (static_cast<std::uint32_t>(block_[offset]) << 24U)
                | (static_cast<std::uint32_t>(block_[offset + 1]) << 16U)
                | (static_cast<std::uint32_t>(block_[offset + 2]) << 8U)
                | static_cast<std::uint32_t>(block_[offset + 3]);
        }
        for (std::size_t index = 16; index < schedule.size(); ++index) {
            const std::uint32_t s0 = rotate_right(schedule[index - 15], 7U)
                ^ rotate_right(schedule[index - 15], 18U) ^ (schedule[index - 15] >> 3U);
            const std::uint32_t s1 = rotate_right(schedule[index - 2], 17U)
                ^ rotate_right(schedule[index - 2], 19U) ^ (schedule[index - 2] >> 10U);
            schedule[index] = schedule[index - 16] + s0 + schedule[index - 7] + s1;
        }

        std::uint32_t a = state_[0];
        std::uint32_t b = state_[1];
        std::uint32_t c = state_[2];
        std::uint32_t d = state_[3];
        std::uint32_t e = state_[4];
        std::uint32_t f = state_[5];
        std::uint32_t g = state_[6];
        std::uint32_t h = state_[7];
        for (std::size_t index = 0; index < schedule.size(); ++index) {
            const std::uint32_t sigma1 = rotate_right(e, 6U) ^ rotate_right(e, 11U) ^ rotate_right(e, 25U);
            const std::uint32_t choice = (e & f) ^ ((~e) & g);
            const std::uint32_t temporary1 = h + sigma1 + choice + constants_[index] + schedule[index];
            const std::uint32_t sigma0 = rotate_right(a, 2U) ^ rotate_right(a, 13U) ^ rotate_right(a, 22U);
            const std::uint32_t majority = (a & b) ^ (a & c) ^ (b & c);
            const std::uint32_t temporary2 = sigma0 + majority;
            h = g;
            g = f;
            f = e;
            e = d + temporary1;
            d = c;
            c = b;
            b = a;
            a = temporary1 + temporary2;
        }
        state_[0] += a;
        state_[1] += b;
        state_[2] += c;
        state_[3] += d;
        state_[4] += e;
        state_[5] += f;
        state_[6] += g;
        state_[7] += h;
    }

    std::array<unsigned char, 64> block_{};
    std::size_t block_length_{0};
    std::uint64_t bit_length_{0};
    std::array<std::uint32_t, 8> state_{
        0x6a09e667U, 0xbb67ae85U, 0x3c6ef372U, 0xa54ff53aU,
        0x510e527fU, 0x9b05688cU, 0x1f83d9abU, 0x5be0cd19U,
    };
};

std::string sha256(const std::string& input) {
    Sha256 digest;
    digest.update(reinterpret_cast<const unsigned char*>(input.data()), input.size());
    return digest.finish();
}

std::string stable_double(double value) {
    std::ostringstream out;
    out << std::setprecision(std::numeric_limits<double>::max_digits10) << value;
    return out.str();
}

void require_domain(const NativeTemperatureDomainV1& domain, double temperature_K) {
    if (!std::isfinite(domain.minimum_K) || !std::isfinite(domain.maximum_K)
        || domain.minimum_K > domain.maximum_K || !nonblank(domain.evidence_kind)
        || !nonblank(domain.evidence_source)) {
        throw ValueError("native scientific record has an invalid sourced temperature domain");
    }
    if (temperature_K < domain.minimum_K || temperature_K > domain.maximum_K) {
        throw ValueError("temperature is outside the sourced record domain");
    }
}

void validate_dependency_signature(
    const NativeDependencySignatureV1& signature,
    const NativeCorrelationDefinitionV1& correlation
) {
    const std::set<std::string> admitted{"temperature_K", "mole_fraction"};
    if (std::set<std::string>(signature.variables.begin(), signature.variables.end()).size()
        != signature.variables.size()
        || std::any_of(signature.variables.begin(), signature.variables.end(), [&](const std::string& variable) {
            return admitted.count(variable) == 0;
        })) {
        throw ValueError("native scientific record has an unknown or duplicate dependency identity");
    }
    if (std::holds_alternative<NativeConstantCorrelationV1>(correlation)) {
        if (!signature.variables.empty() || !signature.composition_components.empty()) {
            throw ValueError("constant native correlation must have an empty dependency signature");
        }
        return;
    }
    if (const auto* composition =
        std::get_if<NativeSaltFreeWaterMoleFractionCubicPermittivityCorrelationV1>(&correlation)) {
        if (signature.variables != std::vector<std::string>{"mole_fraction"}
            || signature.composition_components
                != std::vector<std::string>{composition->water_component, composition->organic_component}) {
            throw ValueError("composition correlation dependency identity does not match its typed definition");
        }
        return;
    }
    if (signature.variables != std::vector<std::string>{"temperature_K"}
        || !signature.composition_components.empty()) {
        throw ValueError("temperature correlation dependency identity does not match its typed definition");
    }
}

void validate_formulation(const NativeFormulationV1& formulation) {
    if (!formulation.electrostatics_enabled
        && (formulation.relative_permittivity_enabled || formulation.debye_huckel_enabled
            || formulation.born_enabled || formulation.solvated_ion_diameter_enabled
            || formulation.ion_dispersion_enabled)) {
        throw ValueError("disabled electrostatics cannot carry enabled dependent formulations");
    }
    if ((formulation.debye_huckel_enabled || formulation.born_enabled)
        && !formulation.relative_permittivity_enabled) {
        throw ValueError("Debye-Huckel and Born require enabled relative permittivity");
    }
    if (formulation.relative_permittivity_rule < 0 || formulation.relative_permittivity_rule > 9
        || formulation.ion_diameter_mode < 0 || formulation.ion_diameter_mode > 2
        || formulation.born_diameter_mode < 0 || formulation.born_diameter_mode > 3
        || formulation.born_bulk_mode < 0 || formulation.born_bulk_mode > 1) {
        throw ValueError("native formulation contains an unsupported closed-vocabulary code");
    }
}

std::size_t component_index(
    const std::vector<std::string>& components,
    const std::string& component
) {
    const auto iterator = std::find(components.begin(), components.end(), component);
    if (iterator == components.end()) {
        throw ValueError("composition dependency references an unknown component");
    }
    return static_cast<std::size_t>(std::distance(components.begin(), iterator));
}

std::string native_field_for(const std::string& field) {
    static const std::map<std::string, std::string> fields{
        {"molar_mass_kg_per_mol", "mw"},
        {"segment_count", "m"},
        {"sigma_angstrom", "s"},
        {"epsilon_k_K", "e"},
        {"charge_number", "z"},
        {"association_energy_K", "e_assoc"},
        {"association_volume", "vol_a"},
        {"association_scheme", "assoc_num"},
        {"association_sites", "assoc_matrix"},
        {"relative_permittivity", "dielc"},
        {"born_diameter_angstrom", "d_born"},
        {"solvation_factor", "f_solv"},
    };
    const auto iterator = fields.find(field);
    if (iterator == fields.end()) throw ValueError("scientific record has no native field owner");
    return iterator->second;
}

std::string native_consumer_for(const std::string& field) {
    if (field == "molar_mass_kg_per_mol") return "mass-density and mass-fraction conversions";
    if (field == "segment_count" || field == "sigma_angstrom") return "hard-chain and dispersion kernels";
    if (field == "epsilon_k_K") return "dispersion kernel";
    if (field == "association_energy_K" || field == "association_volume"
        || field == "association_scheme" || field == "association_sites") {
        return "association kernel";
    }
    if (field == "charge_number" || field == "relative_permittivity") return "electrolyte kernels";
    if (field == "born_diameter_angstrom" || field == "solvation_factor") return "Born kernel";
    throw ValueError("scientific record has no native consumer owner");
}

std::vector<double>& component_vector(NativeEvaluatedInputSnapshot& snapshot, const std::string& field) {
    if (field == "molar_mass_kg_per_mol") return snapshot.mw;
    if (field == "segment_count") return snapshot.m;
    if (field == "sigma_angstrom") return snapshot.s;
    if (field == "epsilon_k_K") return snapshot.e;
    if (field == "charge_number") return snapshot.z;
    if (field == "association_energy_K") return snapshot.e_assoc;
    if (field == "association_volume") return snapshot.vol_a;
    if (field == "relative_permittivity") return snapshot.dielc;
    if (field == "born_diameter_angstrom") return snapshot.d_born;
    if (field == "solvation_factor") return snapshot.f_solv;
    throw ValueError("scientific record cannot be represented as a scalar component vector");
}

std::vector<double>& interaction_vector(NativeEvaluatedInputSnapshot& snapshot, const std::string& family) {
    if (family == "k_ij") return snapshot.k_ij;
    if (family == "l_ij") return snapshot.l_ij;
    if (family == "k_hb_ij") return snapshot.k_hb;
    throw ValueError("scientific interaction has an unknown family");
}

void initialize_parameter_store(NativeEvaluatedInputSnapshot& snapshot, std::size_t component_count) {
    const double missing = std::numeric_limits<double>::quiet_NaN();
    snapshot.m.assign(component_count, missing);
    snapshot.s.assign(component_count, missing);
    snapshot.e.assign(component_count, missing);
    snapshot.e_assoc.assign(component_count, missing);
    snapshot.vol_a.assign(component_count, missing);
    snapshot.z.assign(component_count, missing);
    snapshot.dielc.assign(component_count, missing);
    snapshot.mw.assign(component_count, missing);
    snapshot.d_born.assign(component_count, missing);
    snapshot.f_solv.assign(component_count, missing);
    snapshot.k_ij.assign(component_count * component_count, 0.0);
    snapshot.l_ij.assign(component_count * component_count, 0.0);
    snapshot.k_hb.assign(component_count * component_count, 0.0);
    snapshot.mixed_rel_perm_water_index = -1;
    snapshot.dielc_rule = snapshot.formulation.relative_permittivity_rule;
    snapshot.dielc_diff_mode = 2;
    snapshot.hc_dadx_diff_mode = 2;
    snapshot.disp_dadx_diff_mode = 2;
    snapshot.assoc_dadx_diff_mode = 3;
    snapshot.d_ion_mode = snapshot.formulation.ion_diameter_mode;
    snapshot.mu_DH_diff_mode = 2;
    snapshot.mu_DH_comp_dep_rel_perm = snapshot.formulation.debye_huckel_enabled ? 1 : 0;
    snapshot.mu_DH_include_sum_term = snapshot.formulation.debye_huckel_enabled ? 1 : 0;
    snapshot.include_born_model = snapshot.formulation.born_enabled ? 1 : 0;
    snapshot.d_born_mode = snapshot.formulation.born_diameter_mode;
    snapshot.born_solvation_shell_model = snapshot.formulation.born_solvation_shell_model ? 1 : 0;
    snapshot.born_dielectric_saturation = snapshot.formulation.born_dielectric_saturation ? 1 : 0;
    snapshot.born_bulk_mode = snapshot.formulation.born_bulk_mode;
    snapshot.mu_born_diff_mode = 2;
    snapshot.mu_born_comp_dep_rel_perm = snapshot.formulation.born_enabled ? 1 : 0;
    snapshot.mu_born_include_sum_term = snapshot.formulation.born_enabled ? 1 : 0;
    snapshot.mu_born_comp_dep_delta_d = snapshot.formulation.born_solvation_shell_model ? 1 : 0;
    snapshot.born_model = snapshot.formulation.born_enabled
        ? (snapshot.formulation.born_solvation_shell_model
            || snapshot.formulation.born_dielectric_saturation ? 2 : 1)
        : 0;
    snapshot.born_radius_model = snapshot.formulation.born_diameter_mode + 1;
    snapshot.born_diff_mode = 4;
    snapshot.born_eps_mode = snapshot.formulation.born_bulk_mode;
    snapshot.DH_model = snapshot.formulation.debye_huckel_enabled ? 1 : 0;
    snapshot.parameter_source_label = "resolved_model_input_v1";
    snapshot.parameter_provenance_status = "source_bearing_scientific_records";
    snapshot.binary_interaction_provenance_status = "source_bearing_interaction_graph";
}

void require_all_populated(const std::vector<double>& values, const std::string& field) {
    if (std::any_of(values.begin(), values.end(), [](double value) { return !std::isfinite(value); })) {
        throw ValueError("resolved native input is missing required field " + field);
    }
}

EvaluatedRecordEvidence make_evidence(
    const NativeScientificRecordV1& record,
    const NativeCorrelationJetV1& jet
) {
    return EvaluatedRecordEvidence{
        record.record_id,
        record.source_kind + ":" + record.source_locator,
        record.dependency_signature.variables,
        {jet.value},
        jet.derivative_variables,
        static_cast<int>(jet.derivative_variables.empty() ? 0 : 2),
        false,
        jet.first_derivatives,
        jet.second_derivatives_row_major,
        native_field_for(record.field),
        native_consumer_for(record.field),
    };
}

EvaluatedRecordEvidence make_evidence(
    const NativeScientificInteractionRecordV1& record,
    const NativeCorrelationJetV1& jet
) {
    return EvaluatedRecordEvidence{
        record.record_id,
        record.source_kind + ":" + record.source_locator,
        record.dependency_signature.variables,
        {jet.value},
        jet.derivative_variables,
        static_cast<int>(jet.derivative_variables.empty() ? 0 : 2),
        false,
        jet.first_derivatives,
        jet.second_derivatives_row_major,
        record.family == "k_hb_ij" ? "k_hb" : record.family,
        record.family == "k_hb_ij" ? "association kernel" : "pair combining rules",
    };
}

void record_dependency(
    NativeEvaluatedInputSnapshot& snapshot,
    const std::string& record_id,
    const NativeDependencySignatureV1& signature,
    const NativeCorrelationDefinitionV1& correlation
) {
    if (signature.variables.empty()) return;
    snapshot.state_dependent_definitions.records.push_back({record_id, signature, correlation});
    for (const std::string& variable : signature.variables) {
        snapshot.affected_record_ids[variable].push_back(record_id);
    }
}

}  // namespace

NativeCorrelationJetV1 evaluate_native_correlation_v1(
    const NativeCorrelationDefinitionV1& correlation,
    const NativeDependencySignatureV1& dependency_signature,
    double temperature_K,
    const std::vector<double>& canonical_composition,
    const std::vector<std::string>& component_order,
    double organic_relative_permittivity
) {
    NativeCorrelationJetV1 jet;
    jet.derivative_variables = dependency_signature.variables;
    if (const auto* value = std::get_if<NativeConstantCorrelationV1>(&correlation)) {
        jet.value = value->value;
    } else if (const auto* value = std::get_if<NativeReferenceTemperatureLinearCorrelationV1>(&correlation)) {
        jet.value = value->reference_value
            + value->slope_per_K * (temperature_K - value->reference_temperature_K);
        jet.first_derivatives = {value->slope_per_K};
        jet.second_derivatives_row_major = {0.0};
    } else if (const auto* value = std::get_if<NativeLogTemperatureCorrelationV1>(&correlation)) {
        if (temperature_K <= 0.0) throw ValueError("logarithmic correlation requires positive temperature");
        jet.value = value->intercept
            + value->coefficient * std::log(temperature_K / value->reference_temperature_K);
        jet.first_derivatives = {value->coefficient / temperature_K};
        jet.second_derivatives_row_major = {-value->coefficient / (temperature_K * temperature_K)};
    } else if (const auto* value = std::get_if<NativeConstantPlusExponentialTermsCorrelationV1>(&correlation)) {
        jet.value = value->constant;
        double first = 0.0;
        double second = 0.0;
        for (const NativeExponentialTermV1& term : value->terms) {
            const double contribution = term.coefficient
                * std::exp(term.temperature_coefficient_per_K * temperature_K);
            jet.value += contribution;
            first += contribution * term.temperature_coefficient_per_K;
            second += contribution * term.temperature_coefficient_per_K * term.temperature_coefficient_per_K;
        }
        jet.first_derivatives = {first};
        jet.second_derivatives_row_major = {second};
    } else if (const auto* value = std::get_if<NativePiecewiseQuadraticTemperatureCorrelationV1>(&correlation)) {
        const NativeQuadraticCoefficientsV1& branch = temperature_K <= value->transition_temperature_K
            ? value->lower : value->upper;
        jet.value = branch.quadratic * temperature_K * temperature_K
            + branch.linear * temperature_K + branch.constant;
        jet.first_derivatives = {2.0 * branch.quadratic * temperature_K + branch.linear};
        jet.second_derivatives_row_major = {2.0 * branch.quadratic};
    } else if (const auto* value =
        std::get_if<NativeSaltFreeWaterMoleFractionCubicPermittivityCorrelationV1>(&correlation)) {
        const std::size_t water = component_index(component_order, value->water_component);
        const std::size_t organic = component_index(component_order, value->organic_component);
        const double denominator = canonical_composition[water] + canonical_composition[organic];
        if (!(denominator > 0.0)) {
            throw ValueError("salt-free solvent composition requires positive water-plus-organic fraction");
        }
        const double fraction = canonical_composition[water] / denominator;
        jet.value = organic_relative_permittivity + value->coefficient_a * fraction * fraction * fraction
            + value->coefficient_b * fraction * fraction + value->coefficient_c * fraction;
        jet.first_derivatives = {
            3.0 * value->coefficient_a * fraction * fraction
                + 2.0 * value->coefficient_b * fraction + value->coefficient_c,
        };
        jet.second_derivatives_row_major = {
            6.0 * value->coefficient_a * fraction + 2.0 * value->coefficient_b,
        };
    }
    if (!std::isfinite(jet.value)) throw ValueError("native scientific correlation produced a nonfinite value");
    return jet;
}

ResolvedNativeInput make_resolved_native_input_v1(
    std::string definition_fingerprint_sha256,
    std::vector<std::string> component_order,
    NativeFormulationV1 formulation,
    std::vector<NativeScientificRecordV1> records,
    std::vector<NativeScientificInteractionRecordV1> interactions,
    std::vector<StructuralZeroEvidence> structural_zeros
) {
    if (!is_sha256(definition_fingerprint_sha256)) {
        throw ValueError("resolved native input requires a lowercase SHA-256 definition fingerprint");
    }
    if (component_order.empty() || std::set<std::string>(component_order.begin(), component_order.end()).size()
        != component_order.size()) {
        throw ValueError("resolved native input requires a unique nonempty component order");
    }
    validate_formulation(formulation);
    std::set<std::string> record_ids;
    std::set<std::pair<std::size_t, std::string>> component_fields;
    for (const NativeScientificRecordV1& record : records) {
        if (!nonblank(record.record_id) || record.component_index >= component_order.size()
            || component_order[record.component_index] != record.component
            || !nonblank(record.source_kind) || !nonblank(record.source_locator)
            || !record_ids.insert(record.record_id).second
            || !component_fields.insert({record.component_index, record.field}).second) {
            throw ValueError("resolved native input contains an invalid or duplicate scientific record");
        }
        native_field_for(record.field);
        validate_dependency_signature(record.dependency_signature, record.correlation);
    }
    const std::vector<std::string> required_fields{
        "molar_mass_kg_per_mol",
        "segment_count",
        "sigma_angstrom",
        "epsilon_k_K",
        "charge_number",
        "association_energy_K",
        "association_volume",
    };
    for (std::size_t index = 0; index < component_order.size(); ++index) {
        for (const std::string& field : required_fields) {
            if (component_fields.count({index, field}) == 0) {
                throw ValueError("resolved native input is missing a required component scientific record");
            }
        }
    }
    std::set<std::tuple<std::string, std::size_t, std::size_t>> interaction_coverage;
    for (const NativeScientificInteractionRecordV1& record : interactions) {
        if (!nonblank(record.record_id) || record.component_i >= record.component_j
            || record.component_j >= component_order.size() || !record_ids.insert(record.record_id).second
            || !interaction_coverage.insert({record.family, record.component_i, record.component_j}).second
            || !nonblank(record.source_kind) || !nonblank(record.source_locator)) {
            throw ValueError("resolved native input contains an invalid or duplicate interaction record");
        }
        if (record.family != "k_ij" && record.family != "l_ij" && record.family != "k_hb_ij") {
            throw ValueError("scientific interaction has an unknown family");
        }
        validate_dependency_signature(record.dependency_signature, record.correlation);
    }
    for (const StructuralZeroEvidence& record : structural_zeros) {
        if (!nonblank(record.record_id) || record.component_i >= record.component_j
            || record.component_j >= component_order.size() || !record_ids.insert(record.record_id).second
            || !interaction_coverage.insert({record.family, record.component_i, record.component_j}).second
            || record.scientific_source_id.rfind("model_structural_zero:", 0) != 0) {
            throw ValueError("resolved native input contains invalid or duplicate structural-zero evidence");
        }
    }
    for (std::size_t left = 0; left < component_order.size(); ++left) {
        for (std::size_t right = left + 1; right < component_order.size(); ++right) {
            for (const char* family : {"k_ij", "l_ij", "k_hb_ij"}) {
                if (interaction_coverage.count({family, left, right}) == 0) {
                    throw ValueError("resolved native input is missing explicit interaction evidence");
                }
            }
        }
    }
    return ResolvedNativeInput{
        "provider_resolved_input_definition_v1",
        "epcsaft.resolved-model-input",
        1,
        std::move(definition_fingerprint_sha256),
        std::move(component_order),
        formulation,
        std::move(records),
        std::move(interactions),
        std::move(structural_zeros),
    };
}

std::shared_ptr<ProviderResolvedInputHandleV1> evaluate_resolved_native_input_v1(
    const ResolvedNativeInput& input,
    double temperature_K,
    const std::vector<double>& canonical_composition
) {
    if (!std::isfinite(temperature_K) || temperature_K <= 0.0) {
        throw ValueError("temperature must be finite and positive");
    }
    if (canonical_composition.size() != input.component_order.size()) {
        throw ValueError("canonical composition length must match component order");
    }
    double composition_sum = 0.0;
    for (double value : canonical_composition) {
        if (!std::isfinite(value) || value < 0.0) {
            throw ValueError("canonical composition must contain finite non-negative values");
        }
        composition_sum += value;
    }
    if (std::abs(composition_sum - 1.0) > 1.0e-12) {
        throw ValueError("canonical composition must sum to one without normalization");
    }

    auto mutable_snapshot = std::make_shared<NativeEvaluatedInputSnapshot>();
    NativeEvaluatedInputSnapshot& snapshot = *mutable_snapshot;
    snapshot.definition_fingerprint_sha256 = input.definition_fingerprint_sha256;
    snapshot.component_order = input.component_order;
    snapshot.temperature_K = temperature_K;
    snapshot.canonical_composition = canonical_composition;
    snapshot.structural_zeros = input.structural_zeros;
    snapshot.formulation = input.formulation;
    initialize_parameter_store(snapshot, input.component_order.size());

    std::vector<const NativeScientificRecordV1*> deferred_composition_records;
    for (const NativeScientificRecordV1& record : input.records) {
        require_domain(record.temperature_domain, temperature_K);
        if (std::holds_alternative<NativeSaltFreeWaterMoleFractionCubicPermittivityCorrelationV1>(
                record.correlation)) {
            deferred_composition_records.push_back(&record);
            continue;
        }
        const NativeCorrelationJetV1 jet = evaluate_native_correlation_v1(
            record.correlation,
            record.dependency_signature,
            temperature_K,
            canonical_composition,
            input.component_order,
            0.0
        );
        if (record.field == "association_scheme" || record.field == "association_sites") {
            throw ValueError("association topology requires a typed discrete record, not a scalar correlation");
        }
        component_vector(snapshot, record.field)[record.component_index] = jet.value;
        snapshot.evaluated_records.push_back(make_evidence(record, jet));
        snapshot.parameter_provenance_fields.push_back(record.record_id);
        snapshot.native_mapping[record.record_id] = {
            native_field_for(record.field), native_consumer_for(record.field),
        };
        record_dependency(snapshot, record.record_id, record.dependency_signature, record.correlation);
    }

    for (const NativeScientificRecordV1* record : deferred_composition_records) {
        const auto& definition =
            std::get<NativeSaltFreeWaterMoleFractionCubicPermittivityCorrelationV1>(record->correlation);
        const std::size_t organic_index = component_index(input.component_order, definition.organic_component);
        const double organic_relative_permittivity = snapshot.dielc[organic_index];
        if (!std::isfinite(organic_relative_permittivity)) {
            throw ValueError("composition-dependent permittivity requires a separate organic permittivity record");
        }
        const NativeCorrelationJetV1 jet = evaluate_native_correlation_v1(
            record->correlation,
            record->dependency_signature,
            temperature_K,
            canonical_composition,
            input.component_order,
            organic_relative_permittivity
        );
        component_vector(snapshot, record->field)[record->component_index] = jet.value;
        snapshot.evaluated_records.push_back(make_evidence(*record, jet));
        snapshot.parameter_provenance_fields.push_back(record->record_id);
        snapshot.native_mapping[record->record_id] = {
            native_field_for(record->field), native_consumer_for(record->field),
        };
        record_dependency(snapshot, record->record_id, record->dependency_signature, record->correlation);
    }

    const std::size_t component_count = input.component_order.size();
    for (const NativeScientificInteractionRecordV1& record : input.interactions) {
        require_domain(record.temperature_domain, temperature_K);
        const NativeCorrelationJetV1 jet = evaluate_native_correlation_v1(
            record.correlation,
            record.dependency_signature,
            temperature_K,
            canonical_composition,
            input.component_order,
            0.0
        );
        std::vector<double>& matrix = interaction_vector(snapshot, record.family);
        matrix[record.component_i * component_count + record.component_j] = jet.value;
        matrix[record.component_j * component_count + record.component_i] = jet.value;
        snapshot.evaluated_records.push_back(make_evidence(record, jet));
        snapshot.parameter_provenance_fields.push_back(record.record_id);
        snapshot.native_mapping[record.record_id] = {
            record.family == "k_hb_ij" ? "k_hb" : record.family,
            record.family == "k_hb_ij" ? "association kernel" : "pair combining rules",
        };
        record_dependency(snapshot, record.record_id, record.dependency_signature, record.correlation);
    }
    for (const StructuralZeroEvidence& zero : input.structural_zeros) {
        std::vector<double>& matrix = interaction_vector(snapshot, zero.family);
        matrix[zero.component_i * component_count + zero.component_j] = 0.0;
        matrix[zero.component_j * component_count + zero.component_i] = 0.0;
        snapshot.parameter_provenance_fields.push_back(zero.record_id);
        snapshot.native_mapping[zero.record_id] = {
            zero.family == "k_hb_ij" ? "k_hb" : zero.family,
            "source-backed structural-zero policy",
        };
    }

    for (const auto& item : {
        std::pair<const std::vector<double>*, const char*>{&snapshot.mw, "mw"},
        {&snapshot.m, "m"}, {&snapshot.s, "s"}, {&snapshot.e, "e"},
        {&snapshot.z, "z"}, {&snapshot.e_assoc, "e_assoc"}, {&snapshot.vol_a, "vol_a"},
    }) {
        require_all_populated(*item.first, item.second);
    }
    const bool association_parameters_active =
        std::any_of(
            snapshot.e_assoc.begin(),
            snapshot.e_assoc.end(),
            [](double value) { return value > 0.0; }
        )
        || std::any_of(
            snapshot.vol_a.begin(),
            snapshot.vol_a.end(),
            [](double value) { return value > 0.0; }
        );
    if (association_parameters_active) {
        throw ValueError(
            "active association parameters require a typed discrete association-topology record"
        );
    }
    if (snapshot.formulation.relative_permittivity_enabled) {
        require_all_populated(snapshot.dielc, "dielc");
    } else {
        std::replace_if(snapshot.dielc.begin(), snapshot.dielc.end(),
            [](double value) { return !std::isfinite(value); }, 1.0);
    }
    if (snapshot.formulation.born_enabled) {
        require_all_populated(snapshot.d_born, "d_born");
        require_all_populated(snapshot.f_solv, "f_solv");
    } else {
        std::replace_if(snapshot.d_born.begin(), snapshot.d_born.end(),
            [](double value) { return !std::isfinite(value); }, 0.0);
        std::replace_if(snapshot.f_solv.begin(), snapshot.f_solv.end(),
            [](double value) { return !std::isfinite(value); }, 1.0);
    }

    snapshot.trial_phase_composition_invariant = snapshot.affected_record_ids.count("mole_fraction") == 0;
    snapshot.active_residual_families = {"hard_chain", "dispersion"};
    for (std::size_t index = 0; index < snapshot.z.size(); ++index) {
        if (std::abs(snapshot.z[index]) > 1.0e-12) snapshot.ionic_component_indices.push_back(static_cast<int>(index));
    }
    if (!snapshot.ionic_component_indices.empty() && snapshot.formulation.debye_huckel_enabled) {
        snapshot.active_residual_families.push_back("ion");
    }
    if (!snapshot.ionic_component_indices.empty() && snapshot.formulation.born_enabled) {
        snapshot.active_residual_families.push_back("born");
    }

    std::set<std::string> source_classifications;
    for (const NativeScientificRecordV1& record : input.records) source_classifications.insert(record.source_kind);
    for (const NativeScientificInteractionRecordV1& record : input.interactions) {
        source_classifications.insert(record.source_kind);
    }
    for (const StructuralZeroEvidence& record : input.structural_zeros) {
        const std::size_t separator = record.scientific_source_id.find(':');
        source_classifications.insert(record.scientific_source_id.substr(0, separator));
    }
    snapshot.scientific_source_classifications.assign(
        source_classifications.begin(), source_classifications.end()
    );

    std::ostringstream topology;
    topology << "association-topology-v1|components=";
    for (const std::string& component : input.component_order) topology << component << ',';
    topology << '|';
    for (const NativeScientificRecordV1& record : input.records) {
        if (record.field.rfind("association_", 0) == 0) {
            topology << record.record_id << ':' << record.component_index << ':' << record.field << '|';
        }
    }
    for (const StructuralZeroEvidence& zero : input.structural_zeros) {
        if (zero.family == "k_hb_ij") {
            topology << zero.record_id << ':' << zero.component_i << ':' << zero.component_j
                     << ':' << zero.reason << ':' << zero.scientific_source_id << '|';
        }
    }
    snapshot.association_topology_fingerprint_sha256 = sha256(topology.str());

    std::ostringstream snapshot_identity;
    snapshot_identity << input.definition_fingerprint_sha256 << "|T=" << stable_double(temperature_K) << "|x=";
    for (double value : canonical_composition) snapshot_identity << stable_double(value) << ',';
    snapshot.snapshot_fingerprint_sha256 = sha256(snapshot_identity.str());
    snapshot.mixed_relative_permittivity = {
        snapshot.mixed_rel_perm_a,
        snapshot.mixed_rel_perm_b,
        snapshot.mixed_rel_perm_c,
        snapshot.mixed_rel_perm_mask,
        snapshot.mixed_rel_perm_water_index,
    };
    snapshot.assoc_num.assign(component_count, 0);
    snapshot.assoc_matrix.clear();

    std::shared_ptr<const NativeEvaluatedInputSnapshot> const_snapshot = mutable_snapshot;
    return std::make_shared<ProviderResolvedInputHandleV1>(std::move(const_snapshot));
}

ProviderResolvedInputHandleV1::ProviderResolvedInputHandleV1(
    std::shared_ptr<const NativeEvaluatedInputSnapshot> snapshot
) : snapshot_(std::move(snapshot)) {
    if (!snapshot_) throw ValueError("provider resolved-input handle requires a snapshot");
}

const NativeEvaluatedInputSnapshot& ProviderResolvedInputHandleV1::snapshot() const {
    return *snapshot_;
}

std::shared_ptr<const NativeEvaluatedInputSnapshot> ProviderResolvedInputHandleV1::shared_snapshot() const {
    return snapshot_;
}

std::map<std::string, std::string> resolved_input_field_accounting_v1() {
    return {
        {"m", "snapshot.segment_count"},
        {"s", "snapshot.sigma_angstrom"},
        {"e", "snapshot.epsilon_k_K"},
        {"k_ij", "snapshot.k_ij_row_major"},
        {"e_assoc", "snapshot.association_energy_K"},
        {"vol_a", "snapshot.association_volume"},
        {"z", "snapshot.charge_number"},
        {"dielc", "snapshot.pure_relative_permittivity"},
        {"mw", "snapshot.molecular_weight_kg_per_mol"},
        {"mixed_rel_perm_a", "snapshot.mixed_relative_permittivity.coefficient_a"},
        {"mixed_rel_perm_b", "snapshot.mixed_relative_permittivity.coefficient_b"},
        {"mixed_rel_perm_c", "snapshot.mixed_relative_permittivity.coefficient_c"},
        {"mixed_rel_perm_mask", "snapshot.mixed_relative_permittivity.mask"},
        {"mixed_rel_perm_water_index", "snapshot.mixed_relative_permittivity.water_component_index"},
        {"dielc_rule", "snapshot.formulation.relative_permittivity_rule"},
        {"dielc_diff_mode", "snapshot.formulation.relative_permittivity_derivative_mode"},
        {"hc_dadx_diff_mode", "snapshot.formulation.hard_chain_derivative_mode"},
        {"disp_dadx_diff_mode", "snapshot.formulation.dispersion_derivative_mode"},
        {"assoc_dadx_diff_mode", "snapshot.formulation.association_derivative_mode"},
        {"d_ion_mode", "snapshot.formulation.ion_diameter_mode"},
        {"mu_DH_diff_mode", "snapshot.formulation.debye_huckel_derivative_mode"},
        {"mu_DH_comp_dep_rel_perm", "snapshot.formulation.debye_huckel_composition_permittivity"},
        {"mu_DH_include_sum_term", "snapshot.formulation.debye_huckel_sum_term"},
        {"include_born_model", "snapshot.formulation.born_enabled"},
        {"d_born_mode", "snapshot.formulation.born_diameter_mode"},
        {"born_solvation_shell_model", "snapshot.formulation.born_solvation_shell_model"},
        {"born_dielectric_saturation", "snapshot.formulation.born_dielectric_saturation"},
        {"born_bulk_mode", "snapshot.formulation.born_bulk_mode"},
        {"mu_born_diff_mode", "snapshot.formulation.born_derivative_mode"},
        {"mu_born_comp_dep_rel_perm", "snapshot.formulation.born_composition_permittivity"},
        {"mu_born_include_sum_term", "snapshot.formulation.born_sum_term"},
        {"mu_born_comp_dep_delta_d", "snapshot.formulation.born_composition_shell_delta"},
        {"d_born", "snapshot.born_diameter_angstrom"},
        {"f_solv", "snapshot.solvation_factor"},
        {"born_model", "snapshot.formulation.born_model"},
        {"born_radius_model", "snapshot.formulation.born_radius_model"},
        {"born_diff_mode", "snapshot.formulation.born_composition_derivative_mode"},
        {"born_eps_mode", "snapshot.formulation.born_permittivity_basis"},
        {"DH_model", "snapshot.formulation.debye_huckel_model"},
        {"assoc_num", "snapshot.association_site_count"},
        {"assoc_matrix", "snapshot.association_site_matrix"},
        {"k_hb", "snapshot.k_hb_ij_row_major"},
        {"l_ij", "snapshot.l_ij_row_major"},
        {"parameter_source_label", "snapshot.source_identity.label"},
        {"parameter_provenance_status", "snapshot.source_identity.parameter_status"},
        {"binary_interaction_provenance_status", "snapshot.source_identity.interaction_status"},
        {"parameter_provenance_fields", "snapshot.source_identity.record_ids"},
    };
}
