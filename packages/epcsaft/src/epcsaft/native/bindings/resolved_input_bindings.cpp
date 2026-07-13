#include "bindings/resolved_input_bindings.h"

#include <pybind11/stl.h>

#include "bindings/resolved_input_binding_internal.h"
#include "eos/core_internal.h"
#include "model/provider_parameter_access.h"
#include "model/resolved_input.h"

#include <cmath>
#include <cstdint>

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

bool vector_equal(const std::vector<double>& left, const std::vector<double>& right) {
    return left == right;
}

py::dict derivative_pair(
    const epcsaft::native::cppad_support::CppADDerivativeResult& legacy,
    const epcsaft::native::cppad_support::CppADDerivativeResult& snapshot
) {
    py::dict output;
    output["legacy_value"] = legacy.value;
    output["snapshot_value"] = snapshot.value;
    output["legacy_jacobian"] = legacy.jacobian_row_major;
    output["snapshot_jacobian"] = snapshot.jacobian_row_major;
    output["outputs_equal"] = legacy.outputs == snapshot.outputs;
    output["variables_equal"] = legacy.variables == snapshot.variables;
    output["shape_equal"] = legacy.rows == snapshot.rows && legacy.cols == snapshot.cols;
    return output;
}

py::dict parameter_derivative_pair(
    const NeutralBinaryKijPhaseDerivatives& legacy,
    const NeutralBinaryKijPhaseDerivatives& snapshot
) {
    py::dict output;
    output["legacy_scalars"] = std::vector<double>{
        legacy.ares,
        legacy.dares_dk_fixed_rho,
        legacy.pressure,
        legacy.rho,
        legacy.z,
        legacy.dpdrho,
        legacy.dpdk,
        legacy.drhodk,
    };
    output["snapshot_scalars"] = std::vector<double>{
        snapshot.ares,
        snapshot.dares_dk_fixed_rho,
        snapshot.pressure,
        snapshot.rho,
        snapshot.z,
        snapshot.dpdrho,
        snapshot.dpdk,
        snapshot.drhodk,
    };
    output["legacy_mu_res"] = legacy.mu_res;
    output["snapshot_mu_res"] = snapshot.mu_res;
    output["legacy_lnphi"] = legacy.lnphi;
    output["snapshot_lnphi"] = snapshot.lnphi;
    output["legacy_dlnphi_total"] = legacy.dlnphi_dk_total;
    output["snapshot_dlnphi_total"] = snapshot.dlnphi_dk_total;
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
    module.def("_native_provider_parameter_access_parity", [](
        const add_args& legacy,
        const std::shared_ptr<ProviderResolvedInputHandleV1>& handle
    ) {
        if (!handle) throw ValueError("provider resolved-input handle is required");
        const LegacyAddArgsParameterAccessV1 legacy_access(legacy);
        const SnapshotParameterAccessV1 snapshot_access(handle->snapshot());
        const bool equal = vector_equal(legacy_access.m, snapshot_access.m)
            && vector_equal(legacy_access.s, snapshot_access.s)
            && vector_equal(legacy_access.e, snapshot_access.e)
            && vector_equal(legacy_access.mw, snapshot_access.mw)
            && vector_equal(legacy_access.z, snapshot_access.z)
            && vector_equal(legacy_access.e_assoc, snapshot_access.e_assoc)
            && vector_equal(legacy_access.vol_a, snapshot_access.vol_a)
            && vector_equal(legacy_access.k_ij, snapshot_access.k_ij)
            && vector_equal(legacy_access.l_ij, snapshot_access.l_ij)
            && vector_equal(legacy_access.k_hb, snapshot_access.k_hb)
            && vector_equal(legacy_access.dielc, snapshot_access.dielc)
            && vector_equal(legacy_access.d_born, snapshot_access.d_born)
            && vector_equal(legacy_access.f_solv, snapshot_access.f_solv);
        const std::size_t pair_index = legacy_access.s.size() > 1 ? 1 : 0;
        const int right = legacy_access.s.size() > 1 ? 1 : 0;
        const double legacy_sigma = 0.5 * (legacy_access.s[0] + legacy_access.s[right])
            * (1.0 - legacy_access.l_ij[pair_index]);
        const double snapshot_sigma = 0.5 * (snapshot_access.s[0] + snapshot_access.s[right])
            * (1.0 - snapshot_access.l_ij[pair_index]);
        const double legacy_epsilon = std::sqrt(legacy_access.e[0] * legacy_access.e[right])
            * (1.0 - legacy_access.k_ij[pair_index]);
        const double snapshot_epsilon = std::sqrt(snapshot_access.e[0] * snapshot_access.e[right])
            * (1.0 - snapshot_access.k_ij[pair_index]);
        py::dict output;
        output["all_equal"] = equal;
        output["legacy_storage_address"] = reinterpret_cast<std::uintptr_t>(legacy_access.m.data());
        output["snapshot_storage_address"] = reinterpret_cast<std::uintptr_t>(snapshot_access.m.data());
        output["pair_sigma"] = py::make_tuple(legacy_sigma, snapshot_sigma);
        output["pair_epsilon"] = py::make_tuple(legacy_epsilon, snapshot_epsilon);
        return output;
    });
    module.def("_native_provider_parameter_kernel_parity", [](
        const add_args& legacy,
        const std::shared_ptr<ProviderResolvedInputHandleV1>& handle,
        double density
    ) {
        if (!handle) throw ValueError("provider resolved-input handle is required");
        if (!(density > 0.0) || !std::isfinite(density)) {
            throw ValueError("parameter-kernel parity requires a positive finite density");
        }
        const NativeEvaluatedInputSnapshot& snapshot = handle->snapshot();
        const LegacyAddArgsParameterAccessV1 legacy_access(legacy);
        const SnapshotParameterAccessV1 snapshot_access(snapshot);
        const double temperature = snapshot.temperature_K;
        const std::vector<double>& composition = snapshot.canonical_composition;

        const ScalarContributionTerms legacy_ares = residual_helmholtz_result_cpp(
            temperature, density, composition, legacy_access
        );
        const ScalarContributionTerms snapshot_ares = residual_helmholtz_result_cpp(
            temperature, density, composition, snapshot_access
        );
        const CompressibilityFactorResult legacy_z = compressibility_factor_result_cpp(
            temperature, density, composition, legacy_access
        );
        const CompressibilityFactorResult snapshot_z = compressibility_factor_result_cpp(
            temperature, density, composition, snapshot_access
        );
        const FugacityContributionResult legacy_fugacity = fugacity_coefficient_result_cpp(
            temperature, density, composition, legacy_access
        );
        const FugacityContributionResult snapshot_fugacity = fugacity_coefficient_result_cpp(
            temperature, density, composition, snapshot_access
        );
        const CompositionContributionResult legacy_composition =
            composition_derivative_residual_helmholtz_result_cpp(
                temperature, density, composition, legacy_access
            );
        const CompositionContributionResult snapshot_composition =
            composition_derivative_residual_helmholtz_result_cpp(
                temperature, density, composition, snapshot_access
            );
        const ScalarContributionTerms legacy_temperature =
            temperature_derivative_residual_helmholtz_result_cpp(
                temperature, density, composition, legacy_access
            );
        const ScalarContributionTerms snapshot_temperature =
            temperature_derivative_residual_helmholtz_result_cpp(
                temperature, density, composition, snapshot_access
            );
        const double legacy_pressure = p_cpp(temperature, density, composition, legacy_access);
        const double snapshot_pressure = p_cpp(temperature, density, composition, snapshot_access);
        const auto legacy_cppad = cppad_eos_contribution_derivatives_cpp(
            temperature, density, composition, legacy_access
        );
        const auto snapshot_cppad = cppad_eos_contribution_derivatives_cpp(
            temperature, density, composition, snapshot_access
        );
        const auto legacy_pressure_derivative = cppad_pressure_density_derivative_cpp(
            temperature, density, composition, legacy_access
        );
        const auto snapshot_pressure_derivative = cppad_pressure_density_derivative_cpp(
            temperature, density, composition, snapshot_access
        );

        py::dict output;
        output["ares"] = py::make_tuple(legacy_ares.total, snapshot_ares.total);
        output["compressibility"] = py::make_tuple(legacy_z.terms.total, snapshot_z.terms.total);
        output["pressure"] = py::make_tuple(legacy_pressure, snapshot_pressure);
        output["density_residual"] = py::make_tuple(
            density_root_residual_cpp(
                density, temperature, legacy_pressure, composition, legacy_access
            ),
            density_root_residual_cpp(
                density, temperature, snapshot_pressure, composition, snapshot_access
            )
        );
        output["ln_fugacity"] = py::make_tuple(
            legacy_fugacity.lnfugcoef.total, snapshot_fugacity.lnfugcoef.total
        );
        output["composition_dadx"] = py::make_tuple(
            legacy_composition.dadx.total, snapshot_composition.dadx.total
        );
        output["temperature_derivative"] = py::make_tuple(
            legacy_temperature.total, snapshot_temperature.total
        );
        output["cppad_contributions"] = derivative_pair(legacy_cppad, snapshot_cppad);
        output["cppad_pressure_density"] = derivative_pair(
            legacy_pressure_derivative, snapshot_pressure_derivative
        );
        if (composition.size() == 1) {
            output["pure_parameter_derivatives"] = derivative_pair(
                cppad_pure_neutral_parameter_derivatives_cpp(temperature, density, legacy_access),
                cppad_pure_neutral_parameter_derivatives_cpp(temperature, density, snapshot_access)
            );
        }
        if (composition.size() == 2) {
            output["binary_k_ij_derivatives"] = parameter_derivative_pair(
                neutral_binary_pair_parameter_phase_derivatives_cpp(
                    temperature, density, composition, legacy_access, 1, "k_ij"
                ),
                neutral_binary_pair_parameter_phase_derivatives_cpp(
                    temperature, density, composition, snapshot_access, 1, "k_ij"
                )
            );
            output["component_sigma_derivatives"] = parameter_derivative_pair(
                generic_component_parameter_phase_derivatives_cpp(
                    temperature, density, composition, legacy_access, 1, 0
                ),
                generic_component_parameter_phase_derivatives_cpp(
                    temperature, density, composition, snapshot_access, 1, 0
                )
            );
            output["component_epsilon_derivatives"] = parameter_derivative_pair(
                generic_component_parameter_phase_derivatives_cpp(
                    temperature, density, composition, legacy_access, 2, 0
                ),
                generic_component_parameter_phase_derivatives_cpp(
                    temperature, density, composition, snapshot_access, 2, 0
                )
            );
        }
        return output;
    });
}
