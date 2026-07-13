#include "bindings/resolved_input_bindings.h"

#include <pybind11/stl.h>

#include "bindings/resolved_input_binding_internal.h"
#include "eos/core_internal.h"
#include "model/provider_parameter_access.h"
#include "model/resolved_input.h"

namespace py = pybind11;

namespace {

py::list evaluated_records_payload(const NativeEvaluatedInputSnapshot& snapshot) {
    py::list output;
    for (const EvaluatedRecordEvidence& evidence : snapshot.evaluated_records) {
        output.append(resolved_input_binding_internal::evaluated_record_evidence_to_dict(evidence));
    }
    return output;
}

py::list structural_zeros_payload(const NativeEvaluatedInputSnapshot& snapshot) {
    py::list output;
    for (const StructuralZeroEvidence& evidence : snapshot.structural_zeros) {
        output.append(resolved_input_binding_internal::structural_zero_evidence_to_dict(evidence));
    }
    return output;
}

py::dict native_mapping_payload(const NativeEvaluatedInputSnapshot& snapshot) {
    py::dict output;
    for (const auto& [record_id, reference] : snapshot.native_mapping) {
        py::dict item;
        item["field"] = reference.field;
        item["consumer"] = reference.consumer;
        output[py::str(record_id)] = std::move(item);
    }
    return output;
}

}  // namespace

void register_resolved_input_bindings(py::module_& module) {
    resolved_input_binding_internal::register_resolved_input_record_bindings(module);

    py::class_<ResolvedNativeInput>(module, "ResolvedNativeInput")
        .def(py::init(&make_resolved_native_input_v1))
        .def_readonly("contract_id", &ResolvedNativeInput::contract_id)
        .def_readonly("schema", &ResolvedNativeInput::schema)
        .def_readonly("schema_version", &ResolvedNativeInput::schema_version)
        .def_readonly("definition_fingerprint_sha256", &ResolvedNativeInput::definition_fingerprint_sha256)
        .def_readonly("component_order", &ResolvedNativeInput::component_order);

    py::class_<ProviderResolvedInputHandleV1, std::shared_ptr<ProviderResolvedInputHandleV1>>(
        module, "ProviderResolvedInputHandleV1"
    )
        .def_property_readonly("contract_id", [](const ProviderResolvedInputHandleV1& handle) {
            return handle.snapshot().contract_id;
        })
        .def_property_readonly("schema", [](const ProviderResolvedInputHandleV1& handle) {
            return handle.snapshot().schema;
        })
        .def_property_readonly("schema_version", [](const ProviderResolvedInputHandleV1& handle) {
            return handle.snapshot().schema_version;
        })
        .def_property_readonly("definition_fingerprint_sha256", [](const ProviderResolvedInputHandleV1& handle) {
            return handle.snapshot().definition_fingerprint_sha256;
        })
        .def_property_readonly("snapshot_fingerprint_sha256", [](const ProviderResolvedInputHandleV1& handle) {
            return handle.snapshot().snapshot_fingerprint_sha256;
        })
        .def_property_readonly("component_order", [](const ProviderResolvedInputHandleV1& handle) {
            return handle.snapshot().component_order;
        })
        .def_property_readonly("temperature_K", [](const ProviderResolvedInputHandleV1& handle) {
            return handle.snapshot().temperature_K;
        })
        .def_property_readonly("composition_basis", [](const ProviderResolvedInputHandleV1& handle) {
            return handle.snapshot().composition_basis;
        })
        .def_property_readonly("canonical_composition", [](const ProviderResolvedInputHandleV1& handle) {
            return handle.snapshot().canonical_composition;
        })
        .def_property_readonly("evaluated_records", [](const ProviderResolvedInputHandleV1& handle) {
            return evaluated_records_payload(handle.snapshot());
        })
        .def_property_readonly("structural_zeros", [](const ProviderResolvedInputHandleV1& handle) {
            return structural_zeros_payload(handle.snapshot());
        })
        .def_property_readonly("affected_record_ids", [](const ProviderResolvedInputHandleV1& handle) {
            return handle.snapshot().affected_record_ids;
        })
        .def_property_readonly("trial_phase_composition_invariant", [](const ProviderResolvedInputHandleV1& handle) {
            return handle.snapshot().trial_phase_composition_invariant;
        })
        .def_property_readonly("active_residual_families", [](const ProviderResolvedInputHandleV1& handle) {
            return handle.snapshot().active_residual_families;
        })
        .def_property_readonly("ionic_component_indices", [](const ProviderResolvedInputHandleV1& handle) {
            return handle.snapshot().ionic_component_indices;
        })
        .def_property_readonly("association_topology_fingerprint_sha256", [](const ProviderResolvedInputHandleV1& handle) {
            return handle.snapshot().association_topology_fingerprint_sha256;
        })
        .def_property_readonly("scientific_source_classifications", [](const ProviderResolvedInputHandleV1& handle) {
            return handle.snapshot().scientific_source_classifications;
        })
        .def_property_readonly("native_mapping", [](const ProviderResolvedInputHandleV1& handle) {
            return native_mapping_payload(handle.snapshot());
        })
        .def_property_readonly("segment_count", [](const ProviderResolvedInputHandleV1& handle) {
            return handle.snapshot().m;
        })
        .def_property_readonly("sigma_angstrom", [](const ProviderResolvedInputHandleV1& handle) {
            return handle.snapshot().s;
        })
        .def_property_readonly("epsilon_k_K", [](const ProviderResolvedInputHandleV1& handle) {
            return handle.snapshot().e;
        })
        .def_property_readonly("molecular_weight_kg_per_mol", [](const ProviderResolvedInputHandleV1& handle) {
            return handle.snapshot().mw;
        })
        .def_property_readonly("charge_number", [](const ProviderResolvedInputHandleV1& handle) {
            return handle.snapshot().z;
        })
        .def_property_readonly("association_energy_K", [](const ProviderResolvedInputHandleV1& handle) {
            return handle.snapshot().e_assoc;
        })
        .def_property_readonly("association_volume", [](const ProviderResolvedInputHandleV1& handle) {
            return handle.snapshot().vol_a;
        })
        .def_property_readonly("k_ij_row_major", [](const ProviderResolvedInputHandleV1& handle) {
            return handle.snapshot().k_ij;
        })
        .def_property_readonly("l_ij_row_major", [](const ProviderResolvedInputHandleV1& handle) {
            return handle.snapshot().l_ij;
        })
        .def_property_readonly("k_hb_ij_row_major", [](const ProviderResolvedInputHandleV1& handle) {
            return handle.snapshot().k_hb;
        })
        .def_property_readonly("pure_relative_permittivity", [](const ProviderResolvedInputHandleV1& handle) {
            return handle.snapshot().dielc;
        })
        .def_property_readonly("born_diameter_angstrom", [](const ProviderResolvedInputHandleV1& handle) {
            return handle.snapshot().d_born;
        })
        .def_property_readonly("solvation_factor", [](const ProviderResolvedInputHandleV1& handle) {
            return handle.snapshot().f_solv;
        });

    module.def("_native_evaluate_resolved_input_v1", &evaluate_resolved_native_input_v1);
    module.def("_native_resolved_input_field_accounting", &resolved_input_field_accounting_v1);
}
