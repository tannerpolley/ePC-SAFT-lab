#include <pybind11/pybind11.h>

#include "bindings/equilibrium_bindings.h"

namespace py = pybind11;

PYBIND11_MODULE(_native_core, m) {
    py::module_::import("epcsaft._core");
    m.doc() = "package-owned native backend for epcsaft-equilibrium";
    register_equilibrium_bindings(m);
}
