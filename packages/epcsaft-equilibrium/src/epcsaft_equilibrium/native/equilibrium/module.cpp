#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "bindings/equilibrium_bindings.h"
#include "model/resolved_input.h"

namespace py = pybind11;

#ifndef EPCSAFT_EQUILIBRIUM_NATIVE_SOURCE_IDENTITY
#error "EPCSAFT_EQUILIBRIUM_NATIVE_SOURCE_IDENTITY must be provided by the package build"
#endif

#ifndef EPCSAFT_EQUILIBRIUM_NATIVE_SOURCE_FILE_COUNT
#error "EPCSAFT_EQUILIBRIUM_NATIVE_SOURCE_FILE_COUNT must be provided by the package build"
#endif

#ifndef EPCSAFT_EQUILIBRIUM_NATIVE_SOURCE_IDENTITY_ALGORITHM
#error "EPCSAFT_EQUILIBRIUM_NATIVE_SOURCE_IDENTITY_ALGORITHM must be provided by the package build"
#endif

#ifndef EPCSAFT_EQUILIBRIUM_NATIVE_SOURCE_IDENTITY_SCOPE
#error "EPCSAFT_EQUILIBRIUM_NATIVE_SOURCE_IDENTITY_SCOPE must be provided by the package build"
#endif

#ifndef EPCSAFT_EQUILIBRIUM_NATIVE_SOURCE_IDENTITY_LIMIT
#error "EPCSAFT_EQUILIBRIUM_NATIVE_SOURCE_IDENTITY_LIMIT must be provided by the package build"
#endif

PYBIND11_MODULE(_native_core, m) {
    py::module_::import("epcsaft._core");
    m.doc() = "package-owned native backend for epcsaft-equilibrium";
    m.def("_native_equilibrium_build_identity", []() {
        py::dict identity;
        identity["algorithm"] = EPCSAFT_EQUILIBRIUM_NATIVE_SOURCE_IDENTITY_ALGORITHM;
        identity["source_identity"] = EPCSAFT_EQUILIBRIUM_NATIVE_SOURCE_IDENTITY;
        identity["source_scope"] = EPCSAFT_EQUILIBRIUM_NATIVE_SOURCE_IDENTITY_SCOPE;
        identity["source_file_count"] = EPCSAFT_EQUILIBRIUM_NATIVE_SOURCE_FILE_COUNT;
        identity["scope_limit"] = EPCSAFT_EQUILIBRIUM_NATIVE_SOURCE_IDENTITY_LIMIT;
        return identity;
    });
    m.def("_native_provider_resolved_input_handle_probe", [](
        const std::shared_ptr<ProviderResolvedInputHandleV1>& handle
    ) {
        if (!handle) throw ValueError("provider resolved-input handle is required");
        const NativeEvaluatedInputSnapshot& snapshot = handle->snapshot();
        py::dict identity;
        identity["contract_id"] = snapshot.contract_id;
        identity["schema"] = snapshot.schema;
        identity["schema_version"] = snapshot.schema_version;
        identity["definition_fingerprint_sha256"] = snapshot.definition_fingerprint_sha256;
        identity["snapshot_fingerprint_sha256"] = snapshot.snapshot_fingerprint_sha256;
        identity["component_order"] = snapshot.component_order;
        identity["temperature_K"] = snapshot.temperature_K;
        identity["composition_basis"] = snapshot.composition_basis;
        identity["canonical_composition"] = snapshot.canonical_composition;
        return identity;
    });
    register_equilibrium_bindings(m);
}
