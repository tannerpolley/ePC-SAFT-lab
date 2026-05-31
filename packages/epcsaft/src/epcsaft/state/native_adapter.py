from copy import deepcopy

import numpy as np

from .. import _core
from .._types import ActivityCoefficientResult, InputError, SolutionError, phase_to_int, vector_to_array
from .eos_views import (
    CONTRIBUTION_NAMES as _CONTRIBUTION_NAMES,
    GAS_CONSTANT as _GAS_CONSTANT,
    STATE_METHOD_ALIAS_LOOKUP as _STATE_METHOD_ALIAS_LOOKUP,
    STATE_METHOD_ALIAS_MAP,
    StateDiagnosticsView,
    backend_from_contribution_details as _backend_from_contribution_details,
    composition_derivative_residual_helmholtz_result as _composition_derivative_residual_helmholtz_result_payload,
    derivative_result_payload as _derivative_result_payload,
    fugacity_coefficient_term_result as _fugacity_coefficient_term_result_payload,
    public_contribution_terms as _public_contribution_terms,
    scalar_terms_dict as _scalar_terms_dict,
    state_diagnostics_payload,
    unsupported_derivative as _unsupported_derivative,
    vector_terms_dict as _vector_terms_dict,
)
from .native_payload import (
    _canonical_runtime_parameter_payload,
    _relative_permittivity_backend,
    _resolve_solvent_override,
    _state_rel_perm_rule_and_mode,
    check_association,
    check_input,
    create_assoc_matrix,
    create_struct,
    ensure_numpy_input,
    np_to_vector_double,
    np_to_vector_int,
)

_NATIVE_CALL_ERRORS = (
    InputError,
    SolutionError,
    ValueError,
    RuntimeError,
    ArithmeticError,
    getattr(_core, "NativeValueError", ValueError),
    getattr(_core, "NativeSolutionError", SolutionError),
)
_DERIVATIVE_VALUE_ERRORS = (
    InputError,
    SolutionError,
    KeyError,
    ValueError,
    RuntimeError,
    ArithmeticError,
)

def _state_construction_error_message(T, x, phase, ncomp, mode_name, variable_name, variable_value, exc):
    return (
        f"{mode_name}-based state solve failed for "
        f"T={float(T)}, {variable_name}={float(variable_value)}, phase={phase}, ncomp={ncomp}, x={x.tolist()}: {exc}"
    )




class ePCSAFTMixture:
    """Native-backed ePC-SAFT parameter model and state factory."""

    def __init__(self, params=None, species=None):
        """Create a mixture from a resolved parameter payload."""
        self._native = None
        self._params = None
        self._species = None
        if params is not None:
            self._init_from_params(params, species)

    @classmethod
    def from_params(cls, params, species=None):
        """Construct a mixture from an already-resolved parameter dict."""
        params, species = _canonical_runtime_parameter_payload(params, species)
        return cls(params=params, species=species)

    @classmethod
    def from_dataset(cls, dataset_name, species, x, T, user_options=None):
        """Construct a mixture by resolving packaged dataset parameters."""
        from ..model.parameters import ParameterSource

        params = ParameterSource(dataset_name, species=species).to_parameter_set(x=x, T=T, user_options=user_options)
        return cls.from_params(params)

    def _init_from_params(self, params, species=None):
        """Initialize the native mixture from a normalized parameter payload."""
        params, species = _canonical_runtime_parameter_payload(params, species)
        params = check_association(params)
        cppargs = create_struct(params)
        self._native = _core.NativeMixture(cppargs)
        self._params = params
        if species is None:
            ncomp = int(np.asarray(params["m"], dtype=float).size)
            self._species = [str(i) for i in range(ncomp)]
        else:
            self._species = [str(s) for s in species]

    @property
    def species(self):
        """Return the species labels in the mixture order."""
        return list(self._species)

    @property
    def parameters(self):
        """Return a deep copy of the resolved parameter payload."""
        return deepcopy(self._params)

    @property
    def ncomp(self):
        """Return the number of components in the mixture."""
        return int(self._native.ncomp())

    def clear_runtime_caches(self):
        """Clear internal runtime caches used for repeated state/reference evaluations."""
        self._native.clear_runtime_caches()

    def reset_runtime_cache_stats(self):
        """Reset runtime cache hit/rejection counters without clearing cached values."""
        self._native.reset_runtime_cache_stats()

    def runtime_cache_stats(self):
        """Return native runtime cache counters for profiling and validation."""
        return {
            "reference_state_cache_hits": int(self._native.reference_state_cache_hits()),
            "reference_state_cache_misses": int(self._native.reference_state_cache_misses()),
            "density_warm_start_hits": int(self._native.density_warm_start_hits()),
            "density_warm_start_rejections": int(self._native.density_warm_start_rejections()),
        }

    def state(self, T, x, P=None, rho=None, phase="liq", rho_guess=None):
        """Create an immutable thermodynamic state for the mixture.

        States built from pressure resolve and cache density during construction.
        ``rho_guess`` may seed that pressure-density solve but does not replace pressure closure.
        """
        if (P is None) == (rho is None):
            raise InputError("Provide exactly one of P or rho when constructing a state.")
        return ePCSAFTState(self, T, x, P=P, rho=rho, phase=phase, rho_guess=rho_guess)

    def check_density(self, T, x, P, rho, *, phase="liq", rtol=1.0e-6, atol=1.0e-3):
        """Return pressure-consistency diagnostics for an externally supplied density."""
        if float(P) <= 0.0:
            raise InputError("P must be positive when checking density consistency.")
        if not np.isfinite(float(rtol)) or float(rtol) < 0.0:
            raise InputError("rtol must be finite and non-negative.")
        if not np.isfinite(float(atol)) or float(atol) < 0.0:
            raise InputError("atol must be finite and non-negative.")
        state = self.state(T=T, x=x, rho=rho, phase=phase)
        pressure_target = float(P)
        pressure_from_density = float(state.pressure())
        pressure_residual = pressure_from_density - pressure_target
        scale = max(abs(pressure_target), float(atol))
        relative_pressure_residual = abs(pressure_residual) / scale
        within_tolerance = bool(abs(pressure_residual) <= float(atol) + float(rtol) * abs(pressure_target))
        return {
            "density": float(rho),
            "pressure_target": pressure_target,
            "pressure_from_density": pressure_from_density,
            "pressure_residual": float(pressure_residual),
            "relative_pressure_residual": float(relative_pressure_residual),
            "within_tolerance": within_tolerance,
            "state": state,
        }

    def __repr__(self):
        """Return a short debugging representation of the mixture."""
        return f"ePCSAFTMixture(ncomp={self.ncomp}, species={self._species})"


class ePCSAFTState:
    """Immutable thermodynamic state bound to one mixture."""

    def __init__(self, mixture, T, x, P=None, rho=None, phase="liq", rho_guess=None):
        """Create a state with exactly one intensive variable fixed.

        Pressure-based states solve the internal T, P, x -> rho closure eagerly.
        """
        if not isinstance(mixture, ePCSAFTMixture):
            raise InputError("mixture must be a ePCSAFTMixture instance.")
        mix = mixture
        x, _params = ensure_numpy_input(x, mix._params)
        x = np.asarray(x, dtype=float).flatten()
        ncomp = int(mix.ncomp)
        if x.size != ncomp:
            raise InputError(f"State composition length ({int(x.size)}) must match mixture component count ({ncomp}).")
        # ensure_numpy_input may normalize a scalar mixture parameter path, but the
        # state should retain the original mixture data unchanged.
        phase_num = phase_to_int(phase)
        has_p = P is not None
        has_rho = rho is not None
        if has_p == has_rho:
            raise InputError("Provide exactly one of P or rho when constructing a state.")
        has_rho_guess = rho_guess is not None
        if has_rho_guess and not has_p:
            raise InputError("rho_guess is only supported for pressure-based states constructed with P.")
        if has_rho_guess and (not np.isfinite(float(rho_guess)) or float(rho_guess) <= 0.0):
            raise InputError("rho_guess must be finite and positive.")
        if has_p:
            check_input(x, {"temperature": T, "pressure": P})
        else:
            check_input(x, {"temperature": T, "density": rho})
        cpp_x = np_to_vector_double(x)
        try:
            self._native = _core.NativeState(
                mix._native,
                float(T),
                cpp_x,
                phase_num,
                has_p,
                float(P) if P is not None else 0.0,
                has_rho,
                float(rho) if rho is not None else 0.0,
                has_rho_guess,
                float(rho_guess) if rho_guess is not None else 0.0,
            )
        except _NATIVE_CALL_ERRORS as exc:
            variable_name = "P" if has_p else "rho"
            mode_name = "pressure" if has_p else "density"
            variable_value = P if has_p else rho
            message = _state_construction_error_message(
                T, x, phase, ncomp, mode_name, variable_name, variable_value, exc
            )
            diagnostics = None
            if has_p and hasattr(mix._native, "last_density_diagnostics"):
                diagnostics = dict(mix._native.last_density_diagnostics())
                for context in diagnostics.get("density_failure_contexts", []):
                    context["phase_label"] = "state"
                    context["phase_kind"] = "vap" if phase_num == 1 else "liq"
                if diagnostics.get("density_scan_summary"):
                    diagnostics["density_scan_summary"]["phase_label"] = "state"
                    diagnostics["density_scan_summary"]["phase_kind"] = "vap" if phase_num == 1 else "liq"
            raise SolutionError(message, diagnostics) from exc
        self._mixture = mixture
        self._x = np.asarray(x, dtype=float)
        self._T = float(T)
        self._P = None if P is None else float(P)
        self._rho = None if rho is None else float(rho)
        self._phase = phase_num

    @property
    def mixture(self):
        """Return the parent mixture."""
        return self._mixture

    @property
    def T(self):
        """Return the state temperature in kelvin."""
        return self._T

    @property
    def x(self):
        """Return the state composition as a NumPy array."""
        return np.asarray(self._x, dtype=float)

    @property
    def phase(self):
        """Return the native liquid/vapor phase flag."""
        return self._phase

    def method_aliases(self):
        """Return the canonical full-name -> abbreviation map for state methods."""
        return dict(STATE_METHOD_ALIAS_MAP)

    def pressure(self):
        """Return the pressure of the bound state."""
        return float(self._native.pressure())

    def density(self, units="molar"):
        """Return the state density in the requested units."""
        token = str(units or "molar").strip().lower()
        if token in {"molar", "mol", "molar_density", "mol/m^3", "mol/m3"}:
            return float(self._native.density())
        if token in {"mass", "mass_density", "kg/m^3", "kg/m3"}:
            return self.mass_density()
        raise InputError("density units must be 'molar'/'mol/m^3' or 'mass'/'kg/m^3'.")

    def molar_density(self):
        """Return the molar density of the bound state in mol/m^3."""
        return float(self._native.density())

    def mass_density(self):
        """Return the mass density of the bound state in kg/m^3."""
        mix = self._mixture
        mw = np.asarray(mix._params.get("MW", []), dtype=float).flatten()
        if mw.size == 0:
            raise InputError("Mass density requires component molecular weights in kg/mol.")
        if mw.size != self._x.size:
            raise InputError("Mass density requires one molecular-weight value per component.")
        return float(self.molar_density() * float(np.dot(np.asarray(self._x, dtype=float), mw)))

    def _native_args_copy(self):
        return create_struct(self._mixture._params)

    def _neutral_binary_kij_property_derivatives(self):
        if int(self._x.size) != 2:
            return None
        try:
            raw = _core._native_cppad_neutral_binary_pair_properties(
                self._T,
                self.molar_density(),
                np_to_vector_double(self._x),
                self._native_args_copy(),
            )
        except _NATIVE_CALL_ERRORS:
            return None
        return raw if bool(raw.get("supported", raw.get("cppad_used", False))) else None

    def _neutral_binary_pair_parameter_order(self, raw):
        species = tuple(self._mixture.species)
        order = []
        for name in tuple(raw.get("parameter_names", ("k_ij",))):
            order.append(f"{name}:{species[0]}:{species[1]}")
        return tuple(order)

    @staticmethod
    def _neutral_binary_pair_jacobian(raw, quantity, nrows):
        columns = []
        for name in tuple(raw.get("parameter_names", ("k_ij",))):
            columns.append(np.asarray(raw[f"{name}_{quantity}_derivative"], dtype=float).reshape((nrows, 1)))
        return np.concatenate(columns, axis=1) if columns else np.empty((nrows, 0), dtype=float)

    @staticmethod
    def _association_sensitivity_payload(raw):
        if "association_sensitivity_backend" not in raw:
            return {}
        return {
            "association_sensitivity_backend": str(raw["association_sensitivity_backend"]),
            "association_sensitivity_helper": str(raw["association_sensitivity_helper"]),
            "association_site_count": int(raw["association_site_count"]),
            "association_site_sensitivity": np.asarray(raw["association_site_sensitivity_row_major"], dtype=float),
        }

    def _pure_neutral_parameter_derivatives(self):
        if int(self._x.size) != 1:
            return None
        try:
            raw = _core._native_cppad_pure_neutral_parameters(
                self._T,
                self.molar_density(),
                self._native_args_copy(),
            )
        except _NATIVE_CALL_ERRORS:
            return None
        return raw if bool(raw.get("supported", raw.get("cppad_used", False))) else None

    def _pure_neutral_parameter_order(self):
        species = str(self._mixture.species[0])
        return (f"m:{species}", f"sigma:{species}", f"epsilon:{species}")

    def _associating_component_parameter_derivatives(self):
        if int(self._x.size) != 1:
            return None
        assoc_num = np.asarray(self._mixture._params.get("assoc_num", []), dtype=int).flatten()
        if assoc_num.size != 1 or int(assoc_num[0]) <= 0:
            return None
        try:
            raw = _core._native_cppad_association_component_parameters(
                self._T,
                self.molar_density(),
                np_to_vector_double(self._x),
                self._native_args_copy(),
                0,
            )
        except _NATIVE_CALL_ERRORS:
            return None
        return raw if bool(raw["supported"]) else None

    def _associating_component_parameter_order(self, raw):
        species = str(self._mixture.species[0])
        return tuple(f"{name}:{species}" for name in tuple(raw["parameter_names"]))

    @staticmethod
    def _associating_component_parameter_jacobian(raw, quantity, nrows):
        columns = []
        for name in tuple(raw["parameter_names"]):
            columns.append(np.asarray(raw[f"{name}_{quantity}_derivative"], dtype=float).reshape((nrows, 1)))
        return np.concatenate(columns, axis=1) if columns else np.empty((nrows, 0), dtype=float)

    def pressure_density_derivative_result(self):
        """Return the pressure derivative with respect to density in result-contract form."""
        ncomp = int(self._x.size)
        try:
            raw = _core._native_cppad_pressure_density(
                self._T,
                self.molar_density(),
                np_to_vector_double(self._x),
                self._native_args_copy(),
            )
        except _NATIVE_CALL_ERRORS as exc:
            _unsupported_derivative(f"pressure-density derivative backend failed: {exc}")
        if not bool(raw.get("cppad_compiled", False)):
            _unsupported_derivative("CppAD derivative backend did not report required compiled support.")
        return _derivative_result_payload(
            supported=bool(raw.get("supported", raw.get("cppad_used", False))),
            backend=str(raw.get("derivative_backend", "cppad")),
            message=str(raw.get("message", "CppAD pressure-density derivative available")),
            value=[self.pressure()],
            jacobian=np.asarray(raw.get("jacobian_row_major", []), dtype=float),
            shape=[1, 1],
            output_order=("pressure",),
            variable_order=("density",),
            component_order=tuple(self._mixture.species[:ncomp]),
        )

    def pressure_composition_derivative_result(self):
        """Return pressure composition derivatives when production support exists."""
        _unsupported_derivative("pressure composition derivatives require EOS pressure sensitivity routing.")

    def pressure_parameter_derivative_result(self):
        """Return pressure parameter-derivative support status."""
        raw = self._pure_neutral_parameter_derivatives()
        if raw is not None:
            jacobian = np.asarray(raw["jacobian_row_major"], dtype=float).reshape((3, 3))
            return _derivative_result_payload(
                supported=True,
                backend=str(raw.get("derivative_backend", "cppad")),
                message=str(raw.get("message", "CppAD pure-neutral m/sigma/epsilon pressure derivatives available")),
                value=[float(np.asarray(raw["value"], dtype=float)[0])],
                jacobian=jacobian[0:1, :],
                shape=[1, 3],
                output_order=("pressure",),
                parameter_order=self._pure_neutral_parameter_order(),
                source_equation_ids=("pressure_from_z", "ares_hc", "ares_disp"),
            )
        raw = self._associating_component_parameter_derivatives()
        if raw is not None:
            parameter_order = self._associating_component_parameter_order(raw)
            return _derivative_result_payload(
                supported=True,
                backend=str(raw["backend"]),
                message=str(raw["message"]),
                value=[float(raw["e_assoc_pressure"])],
                jacobian=self._associating_component_parameter_jacobian(raw, "pressure", 1),
                shape=[1, len(parameter_order)],
                output_order=("pressure",),
                parameter_order=parameter_order,
                component_order=tuple(self._mixture.species),
                association_sensitivity_backend=str(raw["association_sensitivity_backend"]),
                association_sensitivity_helper=str(raw["association_sensitivity_helper"]),
                association_site_count=int(raw["association_site_count"]),
                association_site_sensitivity=np.asarray(raw["association_site_sensitivity_row_major"], dtype=float),
                source_equation_ids=("pressure_from_z", "ares_assoc", "association_mass_action_implicit"),
            )
        raw = self._neutral_binary_kij_property_derivatives()
        if raw is not None:
            parameter_order = self._neutral_binary_pair_parameter_order(raw)
            association_payload = self._association_sensitivity_payload(raw)
            return _derivative_result_payload(
                supported=True,
                backend=str(raw.get("backend", "cppad")),
                message=str(raw.get("message", "CppAD neutral binary pair-parameter pressure derivative available")),
                value=[float(raw.get("k_ij_pressure", self.pressure()))],
                jacobian=self._neutral_binary_pair_jacobian(raw, "pressure", 1),
                shape=[1, len(parameter_order)],
                output_order=("pressure",),
                parameter_order=parameter_order,
                component_order=tuple(self._mixture.species),
                **association_payload,
                source_equation_ids=("pressure_from_z", "ares_disp"),
            )
        _unsupported_derivative("pressure parameter derivatives require an analytic or CppAD route for this state.")

    def density_pressure_derivative_result(self):
        """Return density pressure derivatives when production support exists."""
        _unsupported_derivative(
            "density-root implicit pressure derivatives require an analytic or CppAD implicit route."
        )

    def ares_composition_derivative_result(self):
        """Return residual-Helmholtz composition derivatives in the public result shape."""
        result = self._composition_derivative_residual_helmholtz_result()
        backend, message = _backend_from_contribution_details(
            result["derivative_backend"],
            available=bool(result["derivative_available"]),
        )
        return _derivative_result_payload(
            supported=backend != "unsupported",
            backend=backend,
            message=message,
            value=[self.residual_helmholtz()],
            jacobian=np.asarray(result["total"], dtype=float).reshape((1, int(self._x.size))),
            shape=[1, int(self._x.size)],
            output_order=("ares_residual",),
            variable_order=tuple(self._mixture.species),
            backend_details=dict(result["derivative_backend"]),
            source_equation_ids=("ares_total",),
        )

    def chemical_potential_composition_derivative_result(self):
        """Return chemical-potential composition derivatives when production support exists."""
        _unsupported_derivative("chemical-potential composition Jacobians require second composition derivatives.")

    def chemical_potential_parameter_derivative_result(self):
        """Return residual-chemical-potential parameter derivatives where production support exists."""
        ncomp = int(self._x.size)
        value = self.residual_chemical_potential()
        raw = self._pure_neutral_parameter_derivatives()
        if raw is not None:
            jacobian = np.asarray(raw["jacobian_row_major"], dtype=float).reshape((3, 3))
            return _derivative_result_payload(
                supported=True,
                backend=str(raw.get("derivative_backend", "cppad")),
                message=str(
                    raw.get(
                        "message",
                        "CppAD pure-neutral m/sigma/epsilon residual-chemical-potential derivatives available",
                    )
                ),
                value=[float(np.asarray(raw["value"], dtype=float)[1])],
                jacobian=jacobian[1:2, :],
                shape=[1, 3],
                component_order=tuple(self._mixture.species),
                parameter_order=self._pure_neutral_parameter_order(),
                value_basis="residual_chemical_potential",
                source_equation_ids=("mu_res", "ares_hc", "ares_disp"),
            )
        raw = self._associating_component_parameter_derivatives()
        if raw is not None:
            species = tuple(self._mixture.species)
            parameter_order = self._associating_component_parameter_order(raw)
            return _derivative_result_payload(
                supported=True,
                backend=str(raw["backend"]),
                message=str(raw["message"]),
                value=np.asarray(raw["e_assoc_residual_chemical_potential"], dtype=float),
                jacobian=self._associating_component_parameter_jacobian(raw, "residual_chemical_potential", ncomp),
                shape=[ncomp, len(parameter_order)],
                component_order=species,
                parameter_order=parameter_order,
                value_basis="residual_chemical_potential",
                association_sensitivity_backend=str(raw["association_sensitivity_backend"]),
                association_sensitivity_helper=str(raw["association_sensitivity_helper"]),
                association_site_count=int(raw["association_site_count"]),
                association_site_sensitivity=np.asarray(raw["association_site_sensitivity_row_major"], dtype=float),
                source_equation_ids=("mu_res", "ares_assoc", "association_mass_action_implicit"),
            )
        raw = self._neutral_binary_kij_property_derivatives()
        if raw is not None:
            species = tuple(self._mixture.species)
            parameter_order = self._neutral_binary_pair_parameter_order(raw)
            association_payload = self._association_sensitivity_payload(raw)
            return _derivative_result_payload(
                supported=True,
                backend=str(raw.get("backend", "cppad")),
                message=str(
                    raw.get(
                        "message",
                        "CppAD neutral binary pair-parameter residual-chemical-potential derivative available",
                    )
                ),
                value=np.asarray(raw.get("k_ij_residual_chemical_potential", value), dtype=float),
                jacobian=self._neutral_binary_pair_jacobian(raw, "residual_chemical_potential", ncomp),
                shape=[ncomp, len(parameter_order)],
                component_order=species,
                parameter_order=parameter_order,
                value_basis="residual_chemical_potential",
                **association_payload,
                source_equation_ids=("mu_res", "ares_disp"),
            )
        _unsupported_derivative(
            "chemical-potential parameter derivatives require an analytic or CppAD route for this state."
        )

    def ln_fugacity_composition_derivative_result(self):
        """Return ln-fugacity composition derivatives for pressure-based native states."""
        ncomp = int(self._x.size)
        if self._P is None:
            _unsupported_derivative(
                "ln-fugacity composition Jacobians require second composition derivatives through a pressure-based phase state."
            )
        try:
            raw = _core._native_phase_state_ln_fugacity_composition_sensitivity(
                self._T,
                self._P,
                np_to_vector_double(self._x),
                self._phase,
                self._native_args_copy(),
            )
        except _NATIVE_CALL_ERRORS as exc:
            _unsupported_derivative(f"phase-state ln-fugacity composition sensitivity backend failed: {exc}")
        if not bool(raw.get("supported", False)):
            _unsupported_derivative(
                str(
                    raw.get(
                        "message",
                        "phase-state ln-fugacity composition sensitivities require a CppAD implicit route.",
                    )
                )
            )
        shape = [int(raw["shape"][0]), int(raw["shape"][1])]
        if shape != [ncomp, ncomp]:
            _unsupported_derivative("invalid phase-state sensitivity payload.")
        return _derivative_result_payload(
            supported=True,
            backend=str(raw.get("backend", "cppad_implicit")),
            message=str(raw.get("message", "CppAD phase-state ln-fugacity composition sensitivities available.")),
            value=np.asarray(raw.get("ln_fugacity", self.fugacity_coefficient(natural_log=True)), dtype=float),
            jacobian=np.asarray(raw.get("jacobian_row_major", []), dtype=float),
            shape=shape,
            component_order=tuple(self._mixture.species),
            variable_order=tuple(self._mixture.species),
            value_basis="natural_log_fugacity_coefficient_at_fixed_pressure",
            density=float(raw.get("density", self.molar_density())),
            density_backend=str(raw.get("density_backend", "implicit_density_root")),
            density_composition_derivative=np.asarray(raw.get("density_composition_derivative", []), dtype=float),
            pressure_density_derivative=float(raw.get("pressure_density_derivative", 0.0)),
            pressure_composition_fixed_density_derivative=np.asarray(
                raw.get("pressure_composition_fixed_density_derivative", []),
                dtype=float,
            ),
            ln_fugacity_density_derivative=np.asarray(raw.get("ln_fugacity_density_derivative", []), dtype=float),
            fixed_density_jacobian=np.asarray(raw.get("fixed_density_jacobian_row_major", []), dtype=float).reshape(
                (ncomp, ncomp)
            ),
            association_sensitivity_backend=str(raw.get("association_sensitivity_backend", "")),
            association_sensitivity_helper=str(raw.get("association_sensitivity_helper", "")),
            association_site_count=int(raw.get("association_site_count", 0)),
            association_site_sensitivity=np.asarray(
                raw.get("association_site_sensitivity_row_major", []),
                dtype=float,
            ),
            association_site_second_sensitivity=np.asarray(
                raw.get("association_site_second_sensitivity_tensor_row_major", []),
                dtype=float,
            ),
            source_equation_ids=("lnphi_total", "pressure_from_z", "density_root_implicit"),
        )

    def ln_fugacity_parameter_derivative_result(self):
        """Return ln-fugacity parameter derivatives where production support exists."""
        ncomp = int(self._x.size)
        value = self.fugacity_coefficient(natural_log=True)
        raw = self._pure_neutral_parameter_derivatives()
        if raw is not None:
            jacobian = np.asarray(raw["jacobian_row_major"], dtype=float).reshape((3, 3))
            return _derivative_result_payload(
                supported=True,
                backend=str(raw.get("derivative_backend", "cppad")),
                message=str(raw.get("message", "CppAD pure-neutral m/sigma/epsilon ln-fugacity derivatives available")),
                value=[float(np.asarray(raw["value"], dtype=float)[2])],
                jacobian=jacobian[2:3, :],
                shape=[1, 3],
                component_order=tuple(self._mixture.species),
                parameter_order=self._pure_neutral_parameter_order(),
                value_basis="natural_log_fugacity_coefficient",
                source_equation_ids=("lnphi_total", "ares_hc", "ares_disp"),
            )
        raw = self._associating_component_parameter_derivatives()
        if raw is not None:
            species = tuple(self._mixture.species)
            parameter_order = self._associating_component_parameter_order(raw)
            return _derivative_result_payload(
                supported=True,
                backend=str(raw["backend"]),
                message=str(raw["message"]),
                value=np.asarray(raw["e_assoc_ln_fugacity"], dtype=float),
                jacobian=self._associating_component_parameter_jacobian(raw, "ln_fugacity", ncomp),
                shape=[ncomp, len(parameter_order)],
                component_order=species,
                parameter_order=parameter_order,
                value_basis="natural_log_fugacity_coefficient",
                association_sensitivity_backend=str(raw["association_sensitivity_backend"]),
                association_sensitivity_helper=str(raw["association_sensitivity_helper"]),
                association_site_count=int(raw["association_site_count"]),
                association_site_sensitivity=np.asarray(raw["association_site_sensitivity_row_major"], dtype=float),
                source_equation_ids=("lnphi_total", "ares_assoc", "association_mass_action_implicit"),
            )
        raw = self._neutral_binary_kij_property_derivatives()
        if raw is not None:
            species = tuple(self._mixture.species)
            parameter_order = self._neutral_binary_pair_parameter_order(raw)
            association_payload = self._association_sensitivity_payload(raw)
            return _derivative_result_payload(
                supported=True,
                backend=str(raw.get("backend", "cppad")),
                message=str(raw.get("message", "CppAD neutral binary pair-parameter ln-fugacity derivative available")),
                value=np.asarray(raw.get("k_ij_ln_fugacity", value), dtype=float),
                jacobian=self._neutral_binary_pair_jacobian(raw, "ln_fugacity", ncomp),
                shape=[ncomp, len(parameter_order)],
                component_order=species,
                parameter_order=parameter_order,
                value_basis="natural_log_fugacity_coefficient",
                **association_payload,
                source_equation_ids=("lnphi_total", "ares_disp"),
            )
        born = self.born_parameter_derivatives()
        if not bool(born.get("supported", False)):
            _unsupported_derivative(
                str(born.get("message", "ln-fugacity parameter derivatives require a CppAD route."))
            )
        jacobian = np.concatenate(
            [
                np.asarray(born["lnfug_d_d_born"], dtype=float),
                np.asarray(born["lnfug_d_f_solv"], dtype=float),
            ],
            axis=1,
        )
        parameter_order = tuple(f"d_born:{name}" for name in self._mixture.species) + tuple(
            f"f_solv:{name}" for name in self._mixture.species
        )
        return _derivative_result_payload(
            supported=True,
            backend=str(born.get("backend", "cppad")),
            message=str(born.get("message", "CppAD liquid-electrolyte Born parameter derivatives available")),
            value=value,
            jacobian=jacobian,
            shape=[ncomp, 2 * ncomp],
            component_order=tuple(self._mixture.species),
            parameter_order=parameter_order,
            phase_scope="liquid_electrolyte_only",
        )

    def activity_composition_derivative_result(self, species=None):
        """Return activity-coefficient composition derivatives when production support exists."""
        _ = self._mixture.species if species is None else [str(s) for s in species]
        _unsupported_derivative("activity-coefficient composition Jacobians require an analytic or CppAD route.")

    def activity_parameter_derivative_result(self, species=None):
        """Return activity-coefficient parameter derivatives where production support exists."""
        species = self._mixture.species if species is None else [str(s) for s in species]
        ncomp = int(self._x.size)
        born = self.born_parameter_derivatives()
        try:
            gamma = self.activity_coefficient(species=species)
            value = np.log(np.asarray([gamma[label] for label in species], dtype=float))
        except _DERIVATIVE_VALUE_ERRORS:
            value = np.asarray([], dtype=float)
        if not bool(born.get("supported", False)):
            _unsupported_derivative(
                str(born.get("message", "activity parameter derivatives require a CppAD route."))
            )
        jacobian = np.concatenate(
            [
                np.asarray(born["lngamma_d_d_born"], dtype=float),
                np.asarray(born["lngamma_d_f_solv"], dtype=float),
            ],
            axis=1,
        )
        parameter_order = tuple(f"d_born:{name}" for name in self._mixture.species) + tuple(
            f"f_solv:{name}" for name in self._mixture.species
        )
        return _derivative_result_payload(
            supported=True,
            backend=str(born.get("backend", "cppad")),
            message=str(born.get("message", "CppAD liquid-electrolyte Born activity derivatives available")),
            value=value,
            jacobian=jacobian,
            shape=[ncomp, 2 * ncomp],
            component_order=tuple(species),
            parameter_order=parameter_order,
            value_basis="natural_log_activity_coefficient",
            phase_scope="liquid_electrolyte_only",
        )

    def relative_permittivity_composition_derivative_result(self):
        """Return relative-permittivity composition derivatives in result-contract form."""
        try:
            epsilon, deps_dx = self.relative_permittivity()
        except _DERIVATIVE_VALUE_ERRORS as exc:
            _unsupported_derivative(f"relative-permittivity derivative backend failed: {exc}")
        return _derivative_result_payload(
            supported=True,
            backend=_relative_permittivity_backend(self._mixture._params),
            message="relative-permittivity composition derivative available",
            value=[float(epsilon)],
            jacobian=np.asarray(deps_dx, dtype=float).reshape((1, int(self._x.size))),
            shape=[1, int(self._x.size)],
            output_order=("relative_permittivity",),
            variable_order=tuple(self._mixture.species),
            source_equation_ids=("relative_permittivity",),
        )

    def relative_permittivity_parameter_derivative_result(self):
        """Return relative-permittivity parameter derivatives for supported dielectric rules."""
        params = self._mixture._params
        try:
            epsilon, _ = self.relative_permittivity()
        except _DERIVATIVE_VALUE_ERRORS as exc:
            _unsupported_derivative(f"relative-permittivity derivative backend failed: {exc}")
        rule, _mode = _state_rel_perm_rule_and_mode(params)
        dielc = np.asarray(params.get("dielc", []), dtype=float).flatten()
        if rule != 1 or dielc.size != self._x.size:
            _unsupported_derivative(
                "relative-permittivity parameter derivatives are implemented for linear mole-fraction mixing only."
            )
        return _derivative_result_payload(
            supported=True,
            backend="analytic",
            message="analytic linear-mixing relative-permittivity parameter derivatives available",
            value=[float(epsilon)],
            jacobian=np.asarray(self._x, dtype=float).reshape((1, int(self._x.size))),
            shape=[1, int(self._x.size)],
            output_order=("relative_permittivity",),
            parameter_order=tuple(f"relative_permittivity:{name}" for name in self._mixture.species),
            source_equation_ids=("relative_permittivity",),
        )

    def derivative_coverage_matrix(self):
        """Return structured implemented derivative backend coverage for EOS property workflows."""
        ncomp = int(self._x.size)
        rows = []

        def classify(*, supported, out_of_scope, override=None):
            if override:
                return str(override)
            if out_of_scope:
                return "out_of_scope"
            if supported:
                return "production_supported"
            raise SolutionError("Derivative coverage rows must be supported or explicitly out of scope.")

        def add(quantity, derivative, result, *, out_of_scope=False, source_equation_ids=()):
            supported = bool(result.get("supported", False))
            row_out_of_scope = bool(out_of_scope)
            if not supported and not row_out_of_scope:
                return
            rows.append(
                {
                    "quantity": quantity,
                    "derivative": derivative,
                    "backend": "out_of_scope" if row_out_of_scope else str(result.get("backend", "unspecified")),
                    "supported": supported,
                    "classification": classify(
                        supported=supported,
                        out_of_scope=row_out_of_scope,
                        override=result.get("classification"),
                    ),
                    "source_equation_ids": list(source_equation_ids),
                    "parameter_family": str(result.get("parameter_family", "")),
                }
            )

        def add_result_factory(quantity, derivative, factory, *, source_equation_ids=()):
            try:
                result = factory()
            except _NATIVE_CALL_ERRORS:
                return
            add(quantity, derivative, result, source_equation_ids=source_equation_ids)

        composition = self._composition_derivative_residual_helmholtz_result()
        details = dict(composition["derivative_backend"])
        assoc_active = bool(np.asarray(self._mixture._params.get("assoc_num", []), dtype=int).size)
        for key, quantity, eqid in (
            ("hc", "hard_chain", "ares_hc"),
            ("disp", "dispersion", "ares_disp"),
            ("assoc", "association", "ares_assoc"),
            ("ion", "debye_huckel / ion", "ares_dh"),
            ("born", "born_direct", "ares_born"),
        ):
            backend = details.get(key, "unsupported")
            if key == "assoc" and assoc_active and backend == "analytic":
                backend = "analytic_implicit"
            inactive_term = key in {"assoc", "ion", "born"} and np.allclose(composition["terms"][key], 0.0)
            add(
                quantity,
                "composition",
                {"supported": backend != "unsupported", "backend": backend, "message": ""},
                out_of_scope=inactive_term,
                source_equation_ids=(eqid,),
            )

        add_result_factory(
            "born_parameter",
            "d_born/f_solv",
            self.born_parameter_derivatives,
            source_equation_ids=("ares_born",),
        )
        add_result_factory(
            "relative_permittivity", "composition", self.relative_permittivity_composition_derivative_result
        )
        add_result_factory("relative_permittivity", "parameter", self.relative_permittivity_parameter_derivative_result)
        add_result_factory(
            "pressure",
            "density",
            self.pressure_density_derivative_result,
            source_equation_ids=("pressure_from_z",),
        )
        add_result_factory(
            "pressure",
            "parameter",
            self.pressure_parameter_derivative_result,
            source_equation_ids=("pressure_from_z",),
        )
        add_result_factory(
            "fugacity",
            "composition",
            self.ln_fugacity_composition_derivative_result,
            source_equation_ids=("lnphi_total",),
        )
        add_result_factory(
            "fugacity",
            "parameter",
            self.ln_fugacity_parameter_derivative_result,
            source_equation_ids=("lnphi_total",),
        )
        add_result_factory(
            "activity",
            "composition",
            self.activity_composition_derivative_result,
            source_equation_ids=("lngamma_sym",),
        )
        add_result_factory(
            "activity",
            "parameter",
            self.activity_parameter_derivative_result,
            source_equation_ids=("lngamma_sym",),
        )
        add_result_factory(
            "chemical_potential",
            "composition",
            self.chemical_potential_composition_derivative_result,
            source_equation_ids=("mu_res",),
        )
        add_result_factory(
            "chemical_potential",
            "parameter",
            self.chemical_potential_parameter_derivative_result,
            source_equation_ids=("mu_res",),
        )
        add_result_factory(
            "density_root",
            "pressure",
            self.density_pressure_derivative_result,
            source_equation_ids=("density_root",),
        )
        if ncomp == 0:
            raise SolutionError("Derivative coverage matrix requires at least one component.")
        return rows

    def _temperature_derivative_residual_helmholtz_term_result(self):
        result = self._native.temperature_derivative_residual_helmholtz_result()
        return _scalar_terms_dict(result)

    def _composition_derivative_residual_helmholtz_result(self):
        return _composition_derivative_residual_helmholtz_result_payload(self)

    def _fugacity_coefficient_term_result(self):
        return _fugacity_coefficient_term_result_payload(self)

    def compressibility_factor(self, return_contribution_terms=False):
        """Return the compressibility factor."""
        if not return_contribution_terms:
            return float(self._native.compressibility_factor())
        result = self._native.compressibility_factor_result()
        payload_dict = _scalar_terms_dict(result.terms)
        terms = {name: float(payload_dict[name]) for name in _CONTRIBUTION_NAMES}
        terms["ideal"] = 1.0
        return {
            "total": float(payload_dict["total"]),
            "terms": terms,
        }

    def pressure_contributions(self):
        """Return pressure contributions derived from native compressibility-factor terms."""
        z_payload = self.compressibility_factor(return_contribution_terms=True)
        pressure_scale = float(self.molar_density() * _GAS_CONSTANT * self._T)
        return {
            "total": float(self.pressure()),
            "terms": {
                name: float(value) * pressure_scale
                for name, value in _public_contribution_terms(z_payload["terms"]).items()
            },
            "term_basis": "pressure_from_compressibility_factor",
            "compressibility_factor": z_payload,
        }

    def residual_helmholtz(self, return_contribution_terms=False):
        """Return the residual Helmholtz energy."""
        if not return_contribution_terms:
            return float(self._native.residual_helmholtz())
        result = self._native.residual_helmholtz_result()
        payload_dict = _scalar_terms_dict(result)
        terms = {name: float(payload_dict[name]) for name in _CONTRIBUTION_NAMES}
        return {
            "total": float(payload_dict["total"]),
            "terms": terms,
        }

    def helmholtz_contributions(self):
        """Return the native residual Helmholtz contribution map."""
        payload = self.residual_helmholtz(return_contribution_terms=True)
        return {
            **payload,
            "terms": _public_contribution_terms(payload["terms"]),
            "term_basis": "dimensionless_residual_helmholtz",
            "ideal": {"available": False, "reason": "ideal Helmholtz decomposition is not exposed by the native API"},
        }

    def residual_helmholtz_contributions(self):
        """Return the native residual Helmholtz contribution map."""
        payload = self.residual_helmholtz(return_contribution_terms=True)
        return {
            **payload,
            "terms": _public_contribution_terms(payload["terms"]),
            "term_basis": "dimensionless_residual_helmholtz",
        }

    def temperature_derivative_residual_helmholtz(self, return_contribution_terms=False):
        """Return the temperature derivative of the residual Helmholtz energy."""
        if not return_contribution_terms:
            return float(self._native.temperature_derivative_residual_helmholtz())
        result = self._temperature_derivative_residual_helmholtz_term_result()
        terms = {name: float(result[name]) for name in _CONTRIBUTION_NAMES}
        return {
            "total": float(result["total"]),
            "terms": terms,
        }

    def composition_derivative_residual_helmholtz(self):
        """Return the composition-derivative contribution breakdown."""
        return self._composition_derivative_residual_helmholtz_result()

    def residual_enthalpy(self):
        """Return the residual enthalpy."""
        return float(self._native.residual_enthalpy())

    def residual_entropy(self):
        """Return the residual entropy."""
        return float(self._native.residual_entropy())

    def residual_gibbs(self):
        """Return the residual Gibbs energy."""
        return float(self._native.residual_gibbs())

    def residual_chemical_potential(self, return_contribution_terms=False):
        """Return the residual chemical potentials."""
        if not return_contribution_terms:
            return vector_to_array(self._native.residual_chemical_potential())
        result = self._native.residual_chemical_potential_result()
        payload_dict = _vector_terms_dict(result.mu, int(self._x.size), "mu")
        terms = {name: np.asarray(payload_dict[name], dtype=float) for name in _CONTRIBUTION_NAMES}
        return {
            "total": np.asarray(payload_dict["total"], dtype=float),
            "terms": terms,
        }

    def chemical_potential_contributions(self):
        """Return the native residual chemical-potential contribution map."""
        payload = self.residual_chemical_potential(return_contribution_terms=True)
        return {
            **payload,
            "terms": _public_contribution_terms(payload["terms"]),
            "term_basis": "residual_chemical_potential",
        }

    def _activity_coefficient_bundle(self, species=None, solvent=None, include_aux=False):
        """Build the full activity-coefficient payload for internal reuse."""
        species = self._mixture.species if species is None else [str(s) for s in species]
        if len(species) != self._x.size:
            raise InputError(f"species length ({len(species)}) must match composition length ({self._x.size}).")
        has_solvent_override, solvent_index = _resolve_solvent_override(self._mixture, species, solvent)
        include_aux_c = bool(include_aux)
        has_solvent_override_c = bool(has_solvent_override)
        solvent_index_c = int(solvent_index)
        out = self._native.activity_coefficient_native(include_aux_c, has_solvent_override_c, solvent_index_c)
        pair_cat = np.asarray(out.pair_cation_indices, dtype=int)
        pair_an = np.asarray(out.pair_anion_indices, dtype=int)
        pair_labels = tuple(species[int(ic)] + species[int(ia)] for ic, ia in zip(pair_cat.tolist(), pair_an.tolist()))
        ion_idx = np.sort(
            np.unique(
                np.concatenate([np.asarray(out.cation_indices, dtype=int), np.asarray(out.anion_indices, dtype=int)])
            )
        )
        ion_labels = tuple(species[int(i)] for i in ion_idx.tolist())
        return ActivityCoefficientResult(
            species=tuple(species),
            component_activity_coefficients=np.asarray(out.component_activity_coefficients, dtype=float),
            solvation_free_energy_values=np.asarray(out.solvation_free_energy, dtype=float),
            mean_ionic_activity_coefficients_mole_fraction_values=np.asarray(
                out.mean_ionic_activity_coefficients_mole_fraction, dtype=float
            ),
            mean_ionic_activity_coefficients_molality_values=np.asarray(
                out.mean_ionic_activity_coefficients_molality, dtype=float
            ),
            pair_labels=pair_labels,
            ion_labels=ion_labels,
            ion_indices=ion_idx,
            cation_indices=np.asarray(out.cation_indices, dtype=int),
            anion_indices=np.asarray(out.anion_indices, dtype=int),
            solvent_indices=np.asarray(out.solvent_indices, dtype=int),
            pair_cation_indices=pair_cat,
            pair_anion_indices=pair_an,
            pair_nu_cation=np.asarray(out.pair_nu_cation, dtype=int),
            pair_nu_anion=np.asarray(out.pair_nu_anion, dtype=int),
            pair_molality=np.asarray(out.pair_molality, dtype=float),
            pair_conversion_factor=np.asarray(out.pair_conversion_factor, dtype=float),
            solvent_index=int(out.solvent_index),
            osmotic_coefficient=float(out.osmotic_coefficient),
        )

    def activity_coefficient(self, species=None, solvent=None, mean_ionic_form=False, basis="mole"):
        """Return activity coefficients in the requested form."""
        species = self._mixture.species if species is None else [str(s) for s in species]
        if len(species) != self._x.size:
            raise InputError(f"species length ({len(species)}) must match composition length ({self._x.size}).")
        has_solvent_override, solvent_index = _resolve_solvent_override(self._mixture, species, solvent)
        include_aux_c = False
        has_solvent_override_c = bool(has_solvent_override)
        solvent_index_c = int(solvent_index)
        out = self._native.activity_coefficient_native(include_aux_c, has_solvent_override_c, solvent_index_c)
        if mean_ionic_form:
            token = str(basis).strip().lower()
            if token in {"mole", "mole_fraction", "molefraction", "x"}:
                values = np.asarray(out.mean_ionic_activity_coefficients_mole_fraction, dtype=float)
            elif token in {"molality", "m"}:
                values = np.asarray(out.mean_ionic_activity_coefficients_molality, dtype=float)
            else:
                raise InputError("basis must be one of: 'mole', 'mole_fraction', 'x', 'molality', 'm'.")
            pair_cat = np.asarray(out.pair_cation_indices, dtype=int)
            pair_an = np.asarray(out.pair_anion_indices, dtype=int)
            return {
                species[int(ic)] + species[int(ia)]: float(value)
                for ic, ia, value in zip(pair_cat.tolist(), pair_an.tolist(), values.tolist())
            }
        values = np.asarray(out.component_activity_coefficients, dtype=float)
        return {label: float(value) for label, value in zip(species, values.tolist())}

    def activity_coefficient_contributions(self, *args, **kwargs):
        """Reject unsupported additive activity-coefficient decomposition explicitly."""
        raise InputError(
            "Activity coefficients are available through activity_coefficient(), but additive "
            "hard_chain/dispersion/association/ionic/born activity-coefficient contributions are not exposed by "
            "the native activity API."
        )

    def fugacity_coefficient(self, natural_log=True, return_contribution_terms=False):
        """Return fugacity coefficients, defaulting to natural-log form."""
        ln_total = vector_to_array(self._native.ln_fugacity_coefficient())
        if not return_contribution_terms:
            if natural_log:
                return ln_total
            return np.exp(ln_total)
        result = self._fugacity_coefficient_term_result()
        ln_term_total = np.asarray(result["lnfugcoef_total"], dtype=float)
        terms = {name: np.asarray(result["lnfugcoef_" + name], dtype=float) for name in _CONTRIBUTION_NAMES}
        out = {
            "total": ln_total if natural_log else np.exp(ln_total),
            "terms": terms,
            "term_basis": "natural_log",
            "terms_total_natural_log": ln_term_total,
        }
        return out

    def ln_fugacity_coefficient_contributions(self):
        """Return native natural-log fugacity-coefficient contribution terms."""
        payload = self.fugacity_coefficient(natural_log=True, return_contribution_terms=True)
        return {
            **payload,
            "terms": _public_contribution_terms(payload["terms"]),
        }

    def born_parameter_derivatives(self):
        """Return CppAD-backed liquid-electrolyte Born parameter derivatives."""
        if self._phase != 0:
            raise InputError("unsupported: Born parameter derivatives are liquid-electrolyte only.")
        try:
            payload = dict(self._native.born_parameter_derivatives())
        except _NATIVE_CALL_ERRORS as exc:
            _unsupported_derivative(str(exc))
        ncomp = int(payload.get("ncomp", self._x.size))
        for key in (
            "a_born_d_d_born",
            "a_born_d_f_solv",
            "mu_res_d_d_born_row_major",
            "mu_res_d_f_solv_row_major",
            "lnfug_d_d_born_row_major",
            "lnfug_d_f_solv_row_major",
            "lngamma_d_d_born_row_major",
            "lngamma_d_f_solv_row_major",
        ):
            payload[key] = np.asarray(payload[key], dtype=float)
        for key in (
            "mu_res_d_d_born",
            "mu_res_d_f_solv",
            "lnfug_d_d_born",
            "lnfug_d_f_solv",
            "lngamma_d_d_born",
            "lngamma_d_f_solv",
        ):
            row_major_key = key + "_row_major"
            payload[key] = np.asarray(payload[row_major_key], dtype=float).reshape((ncomp, ncomp))
        payload["parameter_order"] = tuple(self._mixture.species)
        payload["component_order"] = tuple(self._mixture.species)
        payload["phase_scope"] = "liquid_electrolyte_only"
        payload["parameters"] = ("d_born", "f_solv")
        payload["vapor_support"] = False
        return payload

    def relative_permittivity(self):
        """Return the dielectric model evaluation for the current state."""
        flat = vector_to_array(self._native.relative_permittivity())
        return flat[0], flat[1:]

    def osmotic_coefficient(self):
        """Return the osmotic coefficient."""
        return np.asarray([self._native.osmotic_coefficient()], dtype=float)

    def state_diagnostics(self, species=None):
        """Return a diagnostic dictionary of the main state properties."""
        return state_diagnostics_payload(self, species=species)

    def state_diagnostics_view(self, species=None):
        """Return a typed view over the stable state diagnostics payload."""
        return StateDiagnosticsView(self.state_diagnostics(species=species))

    def solvation_free_energy(self, species=None):
        """Return ion solvation free-energy values keyed by species."""
        return self._activity_coefficient_bundle(species=species, include_aux=True).solvation_free_energy()

    def __getattr__(self, name):
        """Resolve supported short scientific aliases for state methods."""
        target = _STATE_METHOD_ALIAS_LOOKUP.get(str(name))
        if target is not None:
            return getattr(self, target)
        raise AttributeError(f"{type(self).__name__} has no attribute '{name}'")

    def __repr__(self):
        """Return a short debugging representation of the state."""
        return f"ePCSAFTState(T={self._T}, phase={self._phase}, x={self._x})"
