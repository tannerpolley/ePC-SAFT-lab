#include <pybind11/pybind11.h>

#include "bindings/equilibrium_bindings.h"

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
    register_equilibrium_bindings(m);
}
