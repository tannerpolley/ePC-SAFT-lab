#pragma once

namespace pybind11 {
class module_;
}

void register_equilibrium_bindings(pybind11::module_& m);
