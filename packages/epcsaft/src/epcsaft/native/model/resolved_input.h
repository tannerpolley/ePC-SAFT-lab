#pragma once

#include "model/native_types.h"

#include <map>
#include <memory>
#include <string>
#include <variant>
#include <vector>

struct NativeDependencySignatureV1 {
    std::vector<std::string> variables;
    std::vector<std::string> composition_components;
};

struct NativeTemperatureDomainV1 {
    double minimum_K;
    double maximum_K;
    std::string evidence_kind;
    std::string evidence_source;
};

struct NativeConstantCorrelationV1 {
    double value;
};

struct NativeReferenceTemperatureLinearCorrelationV1 {
    double reference_temperature_K;
    double reference_value;
    double slope_per_K;
};

struct NativeLogTemperatureCorrelationV1 {
    double coefficient;
    double intercept;
    double reference_temperature_K;
};

struct NativeExponentialTermV1 {
    double coefficient;
    double temperature_coefficient_per_K;
};

struct NativeConstantPlusExponentialTermsCorrelationV1 {
    double constant;
    std::vector<NativeExponentialTermV1> terms;
};

struct NativeQuadraticCoefficientsV1 {
    double quadratic;
    double linear;
    double constant;
};

struct NativePiecewiseQuadraticTemperatureCorrelationV1 {
    double transition_temperature_K;
    NativeQuadraticCoefficientsV1 lower;
    NativeQuadraticCoefficientsV1 upper;
};

struct NativeSaltFreeWaterMoleFractionCubicPermittivityCorrelationV1 {
    std::string water_component;
    std::string organic_component;
    double coefficient_a;
    double coefficient_b;
    double coefficient_c;
};

using NativeCorrelationDefinitionV1 = std::variant<
    NativeConstantCorrelationV1,
    NativeReferenceTemperatureLinearCorrelationV1,
    NativeLogTemperatureCorrelationV1,
    NativeConstantPlusExponentialTermsCorrelationV1,
    NativePiecewiseQuadraticTemperatureCorrelationV1,
    NativeSaltFreeWaterMoleFractionCubicPermittivityCorrelationV1
>;

struct NativeScientificRecordV1 {
    std::string record_id;
    std::size_t component_index;
    std::string component;
    std::string field;
    std::string units;
    std::string source_kind;
    std::string source_locator;
    NativeDependencySignatureV1 dependency_signature;
    NativeTemperatureDomainV1 temperature_domain;
    NativeCorrelationDefinitionV1 correlation;
};

struct NativeScientificInteractionRecordV1 {
    std::string record_id;
    std::string family;
    std::size_t component_i;
    std::size_t component_j;
    std::string units;
    std::string source_kind;
    std::string source_locator;
    NativeDependencySignatureV1 dependency_signature;
    NativeTemperatureDomainV1 temperature_domain;
    NativeCorrelationDefinitionV1 correlation;
};

struct StructuralZeroEvidence {
    std::string record_id;
    std::string family;
    std::size_t component_i;
    std::size_t component_j;
    std::string reason;
    std::string scientific_source_id;
};

struct NativeFormulationV1 {
    bool electrostatics_enabled{false};
    bool relative_permittivity_enabled{false};
    int relative_permittivity_rule{0};
    bool debye_huckel_enabled{false};
    int ion_diameter_mode{0};
    bool bjerrum_pairing{false};
    bool born_enabled{false};
    int born_diameter_mode{0};
    bool born_solvation_shell_model{false};
    bool born_dielectric_saturation{false};
    int born_bulk_mode{0};
    bool solvated_ion_diameter_enabled{false};
    bool ion_dispersion_enabled{false};
};

struct EvaluatedRecordEvidence {
    std::string record_id;
    std::string scientific_source_id;
    std::vector<std::string> dependency_signature;
    std::vector<double> evaluated_value;
    std::vector<std::string> derivative_variable_order;
    int carried_derivative_order{0};
    bool definition_backed_ad{false};
    std::vector<double> first_derivatives;
    std::vector<double> second_derivatives_row_major;
    std::string native_field;
    std::string native_consumer;
};

struct NativeStateDependentDefinitionV1 {
    std::string record_id;
    NativeDependencySignatureV1 dependency_signature;
    NativeCorrelationDefinitionV1 correlation;
};

struct NativeStateDependentDefinitionGraphV1 {
    std::vector<NativeStateDependentDefinitionV1> records;
};

struct MixedRelativePermittivityInputs {
    std::vector<double> coefficient_a;
    std::vector<double> coefficient_b;
    std::vector<double> coefficient_c;
    std::vector<int> mask;
    int water_component_index{-1};
};

struct NativeFieldReference {
    std::string field;
    std::string consumer;
};

struct ResolvedNativeInput {
    std::string contract_id{"provider_resolved_input_definition_v1"};
    std::string schema{"epcsaft.resolved-model-input"};
    int schema_version{1};
    std::string definition_fingerprint_sha256;
    std::vector<std::string> component_order;
    NativeFormulationV1 formulation;
    std::vector<NativeScientificRecordV1> records;
    std::vector<NativeScientificInteractionRecordV1> interactions;
    std::vector<StructuralZeroEvidence> structural_zeros;
};

// The inherited add_args storage is the snapshot's one native parameter store.
// It permits the additive checkpoint to execute existing kernels by const base
// reference without constructing a compatibility payload or a second field copy.
struct NativeEvaluatedInputSnapshot final : add_args {
    std::string contract_id{"provider_resolved_input_handle_v1"};
    std::string schema{"epcsaft.resolved-model-input"};
    int schema_version{1};
    std::string definition_fingerprint_sha256;
    std::string snapshot_fingerprint_sha256;
    std::vector<std::string> component_order;
    double temperature_K{0.0};
    std::string composition_basis{"mole_fraction"};
    std::vector<double> canonical_composition;
    std::vector<EvaluatedRecordEvidence> evaluated_records;
    NativeStateDependentDefinitionGraphV1 state_dependent_definitions;
    std::map<std::string, std::vector<std::string>> affected_record_ids;
    bool trial_phase_composition_invariant{false};
    std::vector<std::string> active_residual_families;
    std::vector<int> ionic_component_indices;
    std::string association_topology_fingerprint_sha256;
    std::vector<StructuralZeroEvidence> structural_zeros;
    std::vector<std::string> scientific_source_classifications;
    MixedRelativePermittivityInputs mixed_relative_permittivity;
    NativeFormulationV1 formulation;
    std::map<std::string, NativeFieldReference> native_mapping;
};

class ProviderResolvedInputHandleV1 final {
public:
    explicit ProviderResolvedInputHandleV1(
        std::shared_ptr<const NativeEvaluatedInputSnapshot> snapshot
    );

    const NativeEvaluatedInputSnapshot& snapshot() const;
    std::shared_ptr<const NativeEvaluatedInputSnapshot> shared_snapshot() const;

private:
    std::shared_ptr<const NativeEvaluatedInputSnapshot> snapshot_;
};

ResolvedNativeInput make_resolved_native_input_v1(
    std::string definition_fingerprint_sha256,
    std::vector<std::string> component_order,
    NativeFormulationV1 formulation,
    std::vector<NativeScientificRecordV1> records,
    std::vector<NativeScientificInteractionRecordV1> interactions,
    std::vector<StructuralZeroEvidence> structural_zeros
);

std::shared_ptr<ProviderResolvedInputHandleV1> evaluate_resolved_native_input_v1(
    const ResolvedNativeInput& input,
    double temperature_K,
    const std::vector<double>& canonical_composition
);

std::map<std::string, std::string> resolved_input_field_accounting_v1();
