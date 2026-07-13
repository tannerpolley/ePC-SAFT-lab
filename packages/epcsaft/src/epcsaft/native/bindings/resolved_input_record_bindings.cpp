#include "bindings/resolved_input_binding_internal.h"

#include <pybind11/stl.h>

#include <utility>

namespace py = pybind11;

namespace resolved_input_binding_internal {

void register_resolved_input_record_bindings(py::module_& module) {
    py::class_<NativeDependencySignatureV1>(module, "_NativeDependencySignatureV1")
        .def(py::init([](
            std::vector<std::string> variables,
            std::vector<std::string> composition_components
        ) {
            return NativeDependencySignatureV1{
                std::move(variables), std::move(composition_components),
            };
        }))
        .def_readonly("variables", &NativeDependencySignatureV1::variables)
        .def_readonly("composition_components", &NativeDependencySignatureV1::composition_components);

    py::class_<NativeTemperatureDomainV1>(module, "_NativeTemperatureDomainV1")
        .def(py::init([](
            double minimum_K,
            double maximum_K,
            std::string evidence_kind,
            std::string evidence_source
        ) {
            return NativeTemperatureDomainV1{
                minimum_K, maximum_K, std::move(evidence_kind), std::move(evidence_source),
            };
        }))
        .def_readonly("minimum_K", &NativeTemperatureDomainV1::minimum_K)
        .def_readonly("maximum_K", &NativeTemperatureDomainV1::maximum_K)
        .def_readonly("evidence_kind", &NativeTemperatureDomainV1::evidence_kind)
        .def_readonly("evidence_source", &NativeTemperatureDomainV1::evidence_source);

    py::class_<NativeConstantCorrelationV1>(module, "_NativeConstantCorrelationV1")
        .def(py::init([](double value) { return NativeConstantCorrelationV1{value}; }))
        .def_readonly("value", &NativeConstantCorrelationV1::value);
    py::class_<NativeReferenceTemperatureLinearCorrelationV1>(
        module, "_NativeReferenceTemperatureLinearCorrelationV1"
    ).def(py::init([](double reference_temperature_K, double reference_value, double slope_per_K) {
        return NativeReferenceTemperatureLinearCorrelationV1{
            reference_temperature_K, reference_value, slope_per_K,
        };
    }));
    py::class_<NativeLogTemperatureCorrelationV1>(module, "_NativeLogTemperatureCorrelationV1")
        .def(py::init([](double coefficient, double intercept, double reference_temperature_K) {
            return NativeLogTemperatureCorrelationV1{
                coefficient, intercept, reference_temperature_K,
            };
        }));
    py::class_<NativeExponentialTermV1>(module, "_NativeExponentialTermV1")
        .def(py::init([](double coefficient, double temperature_coefficient_per_K) {
            return NativeExponentialTermV1{coefficient, temperature_coefficient_per_K};
        }));
    py::class_<NativeConstantPlusExponentialTermsCorrelationV1>(
        module, "_NativeConstantPlusExponentialTermsCorrelationV1"
    ).def(py::init([](double constant, std::vector<NativeExponentialTermV1> terms) {
        return NativeConstantPlusExponentialTermsCorrelationV1{constant, std::move(terms)};
    }));
    py::class_<NativeQuadraticCoefficientsV1>(module, "_NativeQuadraticCoefficientsV1")
        .def(py::init([](double quadratic, double linear, double constant) {
            return NativeQuadraticCoefficientsV1{quadratic, linear, constant};
        }));
    py::class_<NativePiecewiseQuadraticTemperatureCorrelationV1>(
        module, "_NativePiecewiseQuadraticTemperatureCorrelationV1"
    ).def(py::init([](
        double transition_temperature_K,
        NativeQuadraticCoefficientsV1 lower,
        NativeQuadraticCoefficientsV1 upper
    ) {
        return NativePiecewiseQuadraticTemperatureCorrelationV1{
            transition_temperature_K, lower, upper,
        };
    }));
    py::class_<NativeSaltFreeWaterMoleFractionCubicPermittivityCorrelationV1>(
        module, "_NativeSaltFreeWaterMoleFractionCubicPermittivityCorrelationV1"
    ).def(py::init([](
        std::string water_component,
        std::string organic_component,
        double coefficient_a,
        double coefficient_b,
        double coefficient_c
    ) {
        return NativeSaltFreeWaterMoleFractionCubicPermittivityCorrelationV1{
            std::move(water_component),
            std::move(organic_component),
            coefficient_a,
            coefficient_b,
            coefficient_c,
        };
    }));

    py::class_<NativeScientificRecordV1>(module, "_NativeScientificRecordV1")
        .def(py::init([](
            std::string record_id,
            std::size_t component_index,
            std::string component,
            std::string field,
            std::string units,
            std::string source_kind,
            std::string source_locator,
            NativeDependencySignatureV1 dependency_signature,
            NativeTemperatureDomainV1 temperature_domain,
            NativeCorrelationDefinitionV1 correlation
        ) {
            return NativeScientificRecordV1{
                std::move(record_id), component_index, std::move(component), std::move(field),
                std::move(units), std::move(source_kind), std::move(source_locator),
                std::move(dependency_signature), std::move(temperature_domain), std::move(correlation),
            };
        }));
    py::class_<NativeScientificInteractionRecordV1>(module, "_NativeScientificInteractionRecordV1")
        .def(py::init([](
            std::string record_id,
            std::string family,
            std::size_t component_i,
            std::size_t component_j,
            std::string units,
            std::string source_kind,
            std::string source_locator,
            NativeDependencySignatureV1 dependency_signature,
            NativeTemperatureDomainV1 temperature_domain,
            NativeCorrelationDefinitionV1 correlation
        ) {
            return NativeScientificInteractionRecordV1{
                std::move(record_id), std::move(family), component_i, component_j,
                std::move(units), std::move(source_kind), std::move(source_locator),
                std::move(dependency_signature), std::move(temperature_domain), std::move(correlation),
            };
        }));
    py::class_<StructuralZeroEvidence>(module, "_NativeStructuralZeroEvidenceV1")
        .def(py::init([](
            std::string record_id,
            std::string family,
            std::size_t component_i,
            std::size_t component_j,
            std::string reason,
            std::string scientific_source_id
        ) {
            return StructuralZeroEvidence{
                std::move(record_id), std::move(family), component_i, component_j,
                std::move(reason), std::move(scientific_source_id),
            };
        }));
    py::class_<NativeFormulationV1>(module, "_NativeFormulationV1")
        .def(py::init([](
            bool electrostatics_enabled,
            bool relative_permittivity_enabled,
            int relative_permittivity_rule,
            bool debye_huckel_enabled,
            int ion_diameter_mode,
            bool bjerrum_pairing,
            bool born_enabled,
            int born_diameter_mode,
            bool born_solvation_shell_model,
            bool born_dielectric_saturation,
            int born_bulk_mode,
            bool solvated_ion_diameter_enabled,
            bool ion_dispersion_enabled
        ) {
            return NativeFormulationV1{
                electrostatics_enabled,
                relative_permittivity_enabled,
                relative_permittivity_rule,
                debye_huckel_enabled,
                ion_diameter_mode,
                bjerrum_pairing,
                born_enabled,
                born_diameter_mode,
                born_solvation_shell_model,
                born_dielectric_saturation,
                born_bulk_mode,
                solvated_ion_diameter_enabled,
                ion_dispersion_enabled,
            };
        }));
}

py::dict evaluated_record_evidence_to_dict(const EvaluatedRecordEvidence& evidence) {
    py::dict output;
    output["record_id"] = evidence.record_id;
    output["scientific_source_id"] = evidence.scientific_source_id;
    output["dependency_signature"] = evidence.dependency_signature;
    output["evaluated_value"] = evidence.evaluated_value;
    output["derivative_variable_order"] = evidence.derivative_variable_order;
    output["carried_derivative_order"] = evidence.carried_derivative_order;
    output["definition_backed_ad"] = evidence.definition_backed_ad;
    output["first_derivatives"] = evidence.first_derivatives;
    output["second_derivatives_row_major"] = evidence.second_derivatives_row_major;
    output["native_field"] = evidence.native_field;
    output["native_consumer"] = evidence.native_consumer;
    return output;
}

py::dict structural_zero_evidence_to_dict(const StructuralZeroEvidence& evidence) {
    py::dict output;
    output["record_id"] = evidence.record_id;
    output["family"] = evidence.family;
    output["component_i"] = evidence.component_i;
    output["component_j"] = evidence.component_j;
    output["reason"] = evidence.reason;
    output["scientific_source_id"] = evidence.scientific_source_id;
    return output;
}

py::dict provider_handle_identity(const std::shared_ptr<ProviderResolvedInputHandleV1>& handle) {
    if (!handle) throw ValueError("provider resolved-input handle is required");
    const NativeEvaluatedInputSnapshot& snapshot = handle->snapshot();
    py::dict output;
    output["contract_id"] = snapshot.contract_id;
    output["schema"] = snapshot.schema;
    output["schema_version"] = snapshot.schema_version;
    output["definition_fingerprint_sha256"] = snapshot.definition_fingerprint_sha256;
    output["snapshot_fingerprint_sha256"] = snapshot.snapshot_fingerprint_sha256;
    output["component_order"] = snapshot.component_order;
    output["temperature_K"] = snapshot.temperature_K;
    output["composition_basis"] = snapshot.composition_basis;
    output["canonical_composition"] = snapshot.canonical_composition;
    return output;
}

}  // namespace resolved_input_binding_internal
