#pragma once

#include <pybind11/pybind11.h>

#include "model/resolved_input.h"

namespace resolved_input_binding_internal {

void register_resolved_input_record_bindings(pybind11::module_& module);
pybind11::dict evaluated_record_evidence_to_dict(const EvaluatedRecordEvidence& evidence);
pybind11::dict structural_zero_evidence_to_dict(const StructuralZeroEvidence& evidence);
pybind11::dict provider_handle_identity(
    const std::shared_ptr<ProviderResolvedInputHandleV1>& handle
);

}  // namespace resolved_input_binding_internal
