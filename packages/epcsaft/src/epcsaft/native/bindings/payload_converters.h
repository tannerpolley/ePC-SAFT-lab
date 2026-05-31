#pragma once

#include <pybind11/pybind11.h>

#include <map>
#include <string>
#include <vector>

#include "eos/core_internal.h"
#include "eos/contributions/contribution_internal.h"

namespace epcsaft::native::bindings {

namespace py = pybind11;

py::dict cppad_smoke_to_dict(const epcsaft::native::cppad_support::CppADDerivativeResult& result);
py::dict association_solve_result_to_dict(const AssociationSolveResult& result);
py::dict phase_state_sensitivity_to_dict(const PhaseStateCompositionSensitivityResult& result);
py::dict born_parameter_derivative_to_dict(const BornDerivativeResult& result);
py::dict neutral_binary_kij_property_derivatives_to_dict(
    const NeutralBinaryKijPhaseDerivatives& forward,
    const NeutralBinaryKijPhaseDerivatives& reverse
);
py::dict association_component_parameter_derivatives_to_dict(
    const NeutralBinaryKijPhaseDerivatives& e_assoc,
    const NeutralBinaryKijPhaseDerivatives& vol_a
);
py::dict neutral_binary_pair_property_derivatives_to_dict(
    const NeutralBinaryKijPhaseDerivatives& kij_forward,
    const NeutralBinaryKijPhaseDerivatives& kij_reverse,
    const NeutralBinaryKijPhaseDerivatives* lij_forward,
    const NeutralBinaryKijPhaseDerivatives* lij_reverse,
    const NeutralBinaryKijPhaseDerivatives* khb_forward,
    const NeutralBinaryKijPhaseDerivatives* khb_reverse
);
py::dict native_diagnostics_to_dict(
    const std::map<std::string, double>& doubles,
    const std::map<std::string, int>& ints,
    const std::map<std::string, bool>& bools,
    const std::map<std::string, std::string>& strings,
    const std::map<std::string, std::vector<double>>& vectors
);
py::dict native_density_diagnostics_to_dict(const DensitySolveDiagnostics& diagnostics);
py::dict native_density_failure_payload(const DensitySolveDiagnostics& diagnostics);

}  // namespace epcsaft::native::bindings
