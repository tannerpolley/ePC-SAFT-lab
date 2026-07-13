from copy import deepcopy

import numpy as np

from .. import _core
from .._types import InputError


def _as_rule_number(value, aliases, default):
    if value is None:
        return int(default)
    if isinstance(value, (int, np.integer)):
        return int(value)
    token = str(value).strip().lower()
    if token in aliases:
        return int(aliases[token])
    if token.isdigit() or (token.startswith("-") and token[1:].isdigit()):
        return int(token)
    return int(default)


def _state_rel_perm_rule_and_mode(params):
    z = np.asarray(params.get("z", []), dtype=float).flatten()
    default_rule = 1 if z.size else 0
    elec_model = params.get("elec_model") if isinstance(params.get("elec_model"), dict) else {}
    rel_perm = elec_model.get("rel_perm", {}) if isinstance(elec_model.get("rel_perm", {}), dict) else {}
    rule_alias = {
        "constant": 0,
        "rule0": 0,
        "linear": 1,
        "linear-molefraction": 1,
        "linear-mixing-mole": 1,
        "rule1": 1,
        "linear-massfraction": 2,
        "linear-mixing-weight": 2,
        "rule2": 2,
        "combined": 3,
        "rule3": 3,
        "empirical": 4,
        "rule4": 4,
        "rule5": 5,
        "rule6": 6,
        "aqueous-organic": 8,
        "aqueous_organic": 8,
        "mixed-aqueous-organic": 8,
        "mixed_aqueous_organic": 8,
        "rule8": 8,
        "salt-free-massfraction": 9,
        "salt_free_massfraction": 9,
        "salt-free-solvent-massfraction": 9,
        "salt_free_solvent_weight": 9,
        "rule9": 9,
    }
    diff_alias = {
        "auto": 3,
        "automatic": 3,
        "implicit": 3,
        "analytic_implicit": 3,
        "cppad_implicit": 3,
        "cppad_implicit_association": 3,
        "analytic": 0,
        "analytical": 0,
        "cppad": 2,
    }
    rule = _as_rule_number(rel_perm.get("rule"), rule_alias, default_rule)
    mode = _as_rule_number(rel_perm.get("differential_mode"), diff_alias, 3)
    return rule, mode


def _relative_permittivity_backend(params):
    rule, mode = _state_rel_perm_rule_and_mode(params)
    if mode == 2 or (mode == 3 and rule == 8):
        return "cppad"
    return "analytic"


def _canonical_runtime_parameter_payload(params, species=None):
    from ..model.parameters import ParameterSet, ParameterSource

    if isinstance(params, ParameterSet):
        source = ParameterSource(params, species=species)
        if species is None:
            species = list(params.components)
        params = source.to_parameter_set()._to_stage4_legacy_runtime_dict()
    return params, species


def check_input(x, vars):
    if abs(np.sum(x) - 1) > 1e-7:
        raise InputError(f"The mole fractions do not sum to 1. x = {x}")
    if "temperature" in vars:
        if vars["temperature"] <= 0:
            raise InputError(
                "The {} must be a positive number. {} = {}".format("temperature", "temperature", vars["temperature"])
            )
    if "density" in vars:
        if vars["density"] <= 0:
            raise InputError("The {} must be a positive number. {} = {}".format("density", "density", vars["density"]))
    if "pressure" in vars:
        if vars["pressure"] <= 0:
            raise InputError(
                "The {} must be a positive number. {} = {}".format("pressure", "pressure", vars["pressure"])
            )
    if "Q" in vars:
        if (vars["Q"] < 0) or (vars["Q"] > 1):
            raise InputError("{} must be <= 1 and >= 0. {} = {}".format("Q", "Q", vars["Q"]))


def check_association(params):
    params = deepcopy(params)
    if ("e_assoc" in params) and ("vol_a" not in params):
        raise InputError("e_assoc was given, but not vol_a.")
    elif ("vol_a" in params) and ("e_assoc" not in params):
        raise InputError("vol_a was given, but not e_assoc.")

    if ("e_assoc" in params) and ("assoc_scheme" not in params):
        params["assoc_scheme"] = []
        for a in params["vol_a"]:
            if a != 0:
                params["assoc_scheme"].append("2b")
            else:
                params["assoc_scheme"].append(None)

    if "e_assoc" in params:
        params = create_assoc_matrix(params)

    return params


def create_assoc_matrix(params):
    charge = (
        []
    )  # whether the association site has a partial positive charge (i.e. hydrogen), negative charge, or elements of both (e.g. for acids modelled as type 1)

    scheme_charges = {
        "1": [0],
        "2a": [0, 0],
        "2b": [-1, 1],
        "3a": [0, 0, 0],
        "3b": [-1, -1, 1],
        "4a": [0, 0, 0, 0],
        "4b": [1, 1, 1, -1],
        "4c": [-1, -1, 1, 1],
    }

    assoc_num = []
    for comp in params["assoc_scheme"]:
        if comp is None:
            assoc_num.append(0)
        elif type(comp) is list:
            num = 0
            for site in comp:
                if site.lower() not in scheme_charges:
                    raise InputError(f"{site} is not a valid association type.")
                charge.extend(scheme_charges[site.lower()])
                num += len(scheme_charges[site.lower()])
            assoc_num.append(num)
        else:
            if comp.lower() not in scheme_charges:
                raise InputError(f"{comp} is not a valid association type.")
            charge.extend(scheme_charges[comp.lower()])
            assoc_num.append(len(scheme_charges[comp.lower()]))
    params["assoc_num"] = np.asarray(assoc_num)

    params["assoc_matrix"] = np.zeros(len(charge) * len(charge))
    ctr = 0
    for c1 in charge:
        for c2 in charge:
            if c1 == 0 or c2 == 0:
                params["assoc_matrix"][ctr] = 1
            elif c1 == 1 and c2 == -1:
                params["assoc_matrix"][ctr] = 1
            elif c1 == -1 and c2 == 1:
                params["assoc_matrix"][ctr] = 1
            else:
                params["assoc_matrix"][ctr] = 0
            ctr += 1

    return params


def ensure_numpy_input(x, params):
    if np.isscalar(x):
        x = np.asarray([x], dtype=float)
    if np.isscalar(params["m"]):
        params["m"] = np.asarray([params["m"]], dtype=float)
    if np.isscalar(params["s"]):
        params["s"] = np.asarray([params["s"]], dtype=float)
    if np.isscalar(params["e"]):
        params["e"] = np.asarray([params["e"]], dtype=float)
    return x, params

def _resolve_solvent_override(mixture, species, solvent):
    z = np.asarray(mixture._params.get("z", []), dtype=float).flatten()
    if z.size == 0:
        if solvent is not None:
            raise InputError("solvent override requires ionic parameters with params['z'].")
        return False, -1
    neutral_idx = np.where(np.abs(z) <= 1e-12)[0]
    if neutral_idx.size == 0:
        if solvent is not None:
            raise InputError("solvent override requires at least one neutral solvent species.")
        return False, -1
    if solvent is None:
        return False, -1
    if isinstance(solvent, (int, np.integer)):
        idx = int(solvent)
    else:
        token = str(solvent)
        if token not in species:
            raise InputError(f"Unknown solvent label '{token}'. Available species={list(species)}")
        idx = species.index(token)
    if idx < 0 or idx >= z.size:
        raise InputError(f"solvent index out of bounds: {idx} (ncomp={int(z.size)})")
    if abs(float(z[idx])) > 1e-12:
        raise InputError("solvent override must reference a neutral species (z=0).")
    return True, idx


def np_to_vector_double(np_array):
    """Take a numpy array and return a C++ vector."""
    return np.asarray(np_array, dtype=float).ravel().tolist()


def np_to_vector_int(np_array):
    """Take a numpy array and return a C++ vector."""
    return np.asarray(np_array, dtype=int).ravel().tolist()


def _native_metadata_string(params, key, default):
    value = params.get(key, default)
    if value in (None, ""):
        return str(default)
    return str(value)


def _native_metadata_string_list(params, key):
    value = params.get(key, ())
    if value in (None, ""):
        return []
    if isinstance(value, str):
        return [value]
    return [str(item) for item in value]


def create_struct(params):
    """Convert ePC-SAFT parameters to a C++ struct."""

    cppargs = _core.NativeArgs()

    for removed_key in ("dipm", "dip_num"):
        if removed_key in params:
            raise ValueError(
                f'Removed polar parameter "{removed_key}" is not supported by the active ePC-SAFT package.'
            )

    cppargs.mixed_rel_perm_water_index = -1
    cppargs.m = np_to_vector_double(params["m"])
    ncomp = len(np.asarray(params["m"]).flatten())
    cppargs.s = np_to_vector_double(params["s"])
    cppargs.e = np_to_vector_double(params["e"])
    if "k_ij" in params:
        cppargs.k_ij = np_to_vector_double(params["k_ij"])
    if ("e_assoc" in params) and np.any(params["e_assoc"]):
        cppargs.e_assoc = np_to_vector_double(params["e_assoc"])
    if ("vol_a" in params) and np.any(params["vol_a"]):
        cppargs.vol_a = np_to_vector_double(params["vol_a"])
    z_arr = None
    if "z" in params:
        z_arr = np.asarray(params["z"], dtype=float).flatten()
        if z_arr.size not in (0, ncomp):
            raise ValueError(f'params["z"] must have length {ncomp} (or be empty), got {z_arr.size}.')
        if z_arr.size == ncomp:
            cppargs.z = np_to_vector_double(z_arr)
    if "dielc" in params:
        dielc_arr = np.asarray(params["dielc"], dtype=float).flatten()
        if dielc_arr.size != ncomp:
            raise ValueError(f'params["dielc"] must have length {ncomp}, got {dielc_arr.size}.')
        cppargs.dielc = np_to_vector_double(dielc_arr)
    if "MW" in params:
        mw_arr = np.asarray(params["MW"], dtype=float).flatten()
        if mw_arr.size != ncomp:
            raise ValueError(f'params["MW"] must have length {ncomp}, got {mw_arr.size}.')
        cppargs.mw = np_to_vector_double(mw_arr)
    if "mixed_rel_perm_a" in params:
        mixed_a_arr = np.asarray(params["mixed_rel_perm_a"], dtype=float).flatten()
        if mixed_a_arr.size != ncomp:
            raise ValueError(f'params["mixed_rel_perm_a"] must have length {ncomp}, got {mixed_a_arr.size}.')
        cppargs.mixed_rel_perm_a = np_to_vector_double(mixed_a_arr)
    if "mixed_rel_perm_b" in params:
        mixed_b_arr = np.asarray(params["mixed_rel_perm_b"], dtype=float).flatten()
        if mixed_b_arr.size != ncomp:
            raise ValueError(f'params["mixed_rel_perm_b"] must have length {ncomp}, got {mixed_b_arr.size}.')
        cppargs.mixed_rel_perm_b = np_to_vector_double(mixed_b_arr)
    if "mixed_rel_perm_c" in params:
        mixed_c_arr = np.asarray(params["mixed_rel_perm_c"], dtype=float).flatten()
        if mixed_c_arr.size != ncomp:
            raise ValueError(f'params["mixed_rel_perm_c"] must have length {ncomp}, got {mixed_c_arr.size}.')
        cppargs.mixed_rel_perm_c = np_to_vector_double(mixed_c_arr)
    if "mixed_rel_perm_mask" in params:
        mixed_mask_arr = np.asarray(params["mixed_rel_perm_mask"], dtype=int).flatten()
        if mixed_mask_arr.size != ncomp:
            raise ValueError(f'params["mixed_rel_perm_mask"] must have length {ncomp}, got {mixed_mask_arr.size}.')
        cppargs.mixed_rel_perm_mask = np_to_vector_int(mixed_mask_arr)
    if "mixed_rel_perm_water_index" in params:
        cppargs.mixed_rel_perm_water_index = int(params["mixed_rel_perm_water_index"])
    if len(cppargs.z) > 0 and len(cppargs.dielc) == 0:
        raise ValueError('Electrolyte parameters require params["dielc"] as a per-species array.')
    d_born_arr = None
    if "d_born" in params:
        d_born_arr = np.asarray(params["d_born"], dtype=float).flatten()
        if d_born_arr.size != ncomp:
            raise ValueError(f'params["d_born"] must have length {ncomp}, got {d_born_arr.size}.')
        cppargs.d_born = np_to_vector_double(d_born_arr)
    if "f_solv" in params:
        cppargs.f_solv = np_to_vector_double(np.asarray(params["f_solv"], dtype=float))

    unsupported_flat_elec_keys = {
        "dielc_rule",
        "dielc_diff_mode",
        "born_model",
        "born_radius_model",
        "born_diff_mode",
        "born_eps_mode",
        "DH_model",
        "bjeruum_treatment",
        "d_ion_mode",
        "include_born_model",
        "d_Born_mode",
        "born_solvation_shell_model",
        "born_dielectric_saturation",
        "born_bulk_mode",
        "mu_DH_diff_mode",
        "mu_DH_comp_dep_rel_perm",
        "mu_DH_include_sum_term",
        "mu_born_diff_mode",
        "mu_born_comp_dep_rel_perm",
        "mu_born_include_sum_term",
        "mu_born_comp_dep_delta_d",
    }
    if any((k in params) for k in unsupported_flat_elec_keys):
        raise ValueError(
            'Flat electrostatic params are no longer supported; provide nested params["elec_model"] schema.'
        )

    elec_model = params.get("elec_model", None)
    if elec_model is None:
        if len(cppargs.z) > 0:
            # Apply the canonical electrolyte defaults when ionic parameters are present.
            elec_model = {
                "rel_perm": {"rule": 1, "differential_mode": "auto"},
                "hc_model": {"dadx_differential_mode": "auto"},
                "disp_model": {"dadx_differential_mode": "auto"},
                "assoc_model": {"dadx_differential_mode": "auto"},
                "DH_model": {
                    "d_ion_mode": 1,
                    "bjeruum_treatment": False,
                    "mu_DH_model": {
                        "differential_mode": "auto",
                        "comp_dep_rel_perm": True,
                        "include_sum_term": True,
                    },
                },
                "include_born_model": True,
                "born_model": {
                    "d_Born_mode": 0,
                    "solvation_shell_model": True,
                    "dielectric_saturation": True,
                    "bulk_mode": "mix",
                    "mu_born_model": {
                        "differential_mode": "auto",
                        "comp_dep_rel_perm": True,
                        "include_sum_term": True,
                        "comp_dep_delta_d": True,
                    },
                },
            }
        else:
            elec_model = {}
    if not isinstance(elec_model, dict):
        raise ValueError('params["elec_model"] must be a dict when provided.')

    def _reject_unknown_keys(mapping, allowed, label):
        unknown = sorted(set(mapping) - set(allowed))
        if unknown:
            raise ValueError(f"{label} contains unsupported key(s): {unknown}.")

    _reject_unknown_keys(
        elec_model,
        {"rel_perm", "hc_model", "disp_model", "assoc_model", "DH_model", "include_born_model", "born_model"},
        'params["elec_model"]',
    )

    def _as_bool(v):
        if isinstance(v, bool):
            return v
        if isinstance(v, (int, np.integer)):
            return bool(v)
        if isinstance(v, str):
            s = v.strip().lower()
            if s in {"1", "true", "yes", "y", "on"}:
                return True
            if s in {"0", "false", "no", "n", "off"}:
                return False
        raise ValueError(f"Could not coerce value to bool: {v}")

    def _as_int_alias(v, aliases):
        if isinstance(v, (int, np.integer)):
            return int(v)
        if isinstance(v, str):
            s = v.strip().lower()
            if s in aliases:
                return int(aliases[s])
            if s.isdigit() or (s.startswith("-") and s[1:].isdigit()):
                return int(s)
        raise ValueError(f"Unknown option value: {v}")

    rule_alias = {
        "constant": 0,
        "rule0": 0,
        "linear": 1,
        "linear-molefraction": 1,
        "linear-mixing-mole": 1,
        "rule1": 1,
        "linear-massfraction": 2,
        "linear-mixing-weight": 2,
        "rule2": 2,
        "combined": 3,
        "rule3": 3,
        "empirical": 4,
        "rule4": 4,
        "rule5": 5,
        "rule6": 6,
        "aqueous-organic": 8,
        "aqueous_organic": 8,
        "mixed-aqueous-organic": 8,
        "mixed_aqueous_organic": 8,
        "rule8": 8,
        "salt-free-massfraction": 9,
        "salt_free_massfraction": 9,
        "salt-free-solvent-massfraction": 9,
        "salt_free_solvent_massfraction": 9,
        "salt-free-solvent-weight": 9,
        "salt_free_solvent_weight": 9,
        "rule9": 9,
    }
    diff_alias = {
        "auto": 3,
        "automatic": 3,
        "analytic": 0,
        "analytical": 0,
        "cppad": 2,
    }
    d_ion_alias = {"t_indep": 0, "t_dep_1": 1, "t_dep_2": 2}
    d_born_alias = {"t_indep": 0, "t_dep_1": 1, "t_dep_2": 2, "fitted_param": 3}
    bulk_alias = {"mix": 0, "bulk": 0, "solvent": 1}

    rel_perm = elec_model.get("rel_perm", {})
    if not isinstance(rel_perm, dict):
        raise ValueError('params["elec_model"]["rel_perm"] must be a dict.')
    _reject_unknown_keys(rel_perm, {"rule", "differential_mode"}, 'params["elec_model"]["rel_perm"]')
    hc_model_dict = elec_model.get("hc_model", {})
    if not isinstance(hc_model_dict, dict):
        raise ValueError('params["elec_model"]["hc_model"] must be a dict.')
    _reject_unknown_keys(hc_model_dict, {"dadx_differential_mode"}, 'params["elec_model"]["hc_model"]')
    disp_model_dict = elec_model.get("disp_model", {})
    if not isinstance(disp_model_dict, dict):
        raise ValueError('params["elec_model"]["disp_model"] must be a dict.')
    _reject_unknown_keys(disp_model_dict, {"dadx_differential_mode"}, 'params["elec_model"]["disp_model"]')
    assoc_model_dict = elec_model.get("assoc_model", {})
    if not isinstance(assoc_model_dict, dict):
        raise ValueError('params["elec_model"]["assoc_model"] must be a dict.')
    _reject_unknown_keys(assoc_model_dict, {"dadx_differential_mode"}, 'params["elec_model"]["assoc_model"]')
    dh_model_dict = elec_model.get("DH_model", {})
    if not isinstance(dh_model_dict, dict):
        raise ValueError('params["elec_model"]["DH_model"] must be a dict.')
    _reject_unknown_keys(
        dh_model_dict, {"d_ion_mode", "bjeruum_treatment", "mu_DH_model"}, 'params["elec_model"]["DH_model"]'
    )
    born_model_dict = elec_model.get("born_model", {})
    if not isinstance(born_model_dict, dict):
        raise ValueError('params["elec_model"]["born_model"] must be a dict.')
    _reject_unknown_keys(
        born_model_dict,
        {"d_Born_mode", "solvation_shell_model", "dielectric_saturation", "bulk_mode", "mu_born_model"},
        'params["elec_model"]["born_model"]',
    )
    mu_dh = dh_model_dict.get("mu_DH_model", {})
    if not isinstance(mu_dh, dict):
        raise ValueError('params["elec_model"]["DH_model"]["mu_DH_model"] must be a dict.')
    _reject_unknown_keys(
        mu_dh,
        {"differential_mode", "comp_dep_rel_perm", "include_sum_term"},
        'params["elec_model"]["DH_model"]["mu_DH_model"]',
    )
    mu_born = born_model_dict.get("mu_born_model", {})
    if not isinstance(mu_born, dict):
        raise ValueError('params["elec_model"]["born_model"]["mu_born_model"] must be a dict.')
    _reject_unknown_keys(
        mu_born,
        {"differential_mode", "comp_dep_rel_perm", "include_sum_term", "comp_dep_delta_d"},
        'params["elec_model"]["born_model"]["mu_born_model"]',
    )

    cppargs.dielc_rule = _as_int_alias(rel_perm.get("rule", 1), rule_alias)
    cppargs.dielc_diff_mode = _as_int_alias(rel_perm.get("differential_mode", "auto"), diff_alias)
    if cppargs.dielc_diff_mode not in (0, 2, 3):
        raise ValueError("Unknown rel_perm differential_mode. Supported values are analytic/cppad/auto (0/2/3).")
    cppargs.hc_dadx_diff_mode = _as_int_alias(hc_model_dict.get("dadx_differential_mode", "auto"), diff_alias)
    if cppargs.hc_dadx_diff_mode not in (0, 2, 3):
        raise ValueError("Unknown hc_model dadx_differential_mode. Supported values are analytic/cppad/auto (0/2/3).")
    cppargs.disp_dadx_diff_mode = _as_int_alias(disp_model_dict.get("dadx_differential_mode", "auto"), diff_alias)
    if cppargs.disp_dadx_diff_mode not in (0, 2, 3):
        raise ValueError("Unknown disp_model dadx_differential_mode. Supported values are analytic/cppad/auto (0/2/3).")
    cppargs.assoc_dadx_diff_mode = _as_int_alias(assoc_model_dict.get("dadx_differential_mode", "auto"), diff_alias)
    if cppargs.assoc_dadx_diff_mode not in (0, 2, 3):
        raise ValueError(
            "Unknown assoc_model dadx_differential_mode. Supported values are analytic/cppad/auto (0/2/3)."
        )
    if cppargs.dielc_rule < 0 or cppargs.dielc_rule > 9:
        raise ValueError("Unknown rel_perm rule. Supported values are 0..9.")

    cppargs.d_ion_mode = _as_int_alias(dh_model_dict.get("d_ion_mode", 1), d_ion_alias)
    if cppargs.d_ion_mode not in (0, 1, 2):
        raise ValueError("Unknown d_ion_mode. Supported values are 0,1,2.")
    bjeruum = _as_bool(dh_model_dict.get("bjeruum_treatment", False))
    cppargs.mu_DH_diff_mode = _as_int_alias(mu_dh.get("differential_mode", "auto"), diff_alias)
    if cppargs.mu_DH_diff_mode not in (0, 2, 3):
        raise ValueError("Unknown mu_DH differential_mode. Supported values are analytic/cppad/auto (0/2/3).")
    cppargs.mu_DH_comp_dep_rel_perm = int(_as_bool(mu_dh.get("comp_dep_rel_perm", True)))
    cppargs.mu_DH_include_sum_term = int(_as_bool(mu_dh.get("include_sum_term", True)))

    cppargs.include_born_model = int(_as_bool(elec_model.get("include_born_model", True)))
    cppargs.d_born_mode = _as_int_alias(born_model_dict.get("d_Born_mode", 0), d_born_alias)
    if cppargs.d_born_mode not in (0, 1, 2, 3):
        raise ValueError("Unknown d_Born_mode. Supported values are 0,1,2,3.")
    cppargs.born_solvation_shell_model = int(_as_bool(born_model_dict.get("solvation_shell_model", True)))
    cppargs.born_dielectric_saturation = int(_as_bool(born_model_dict.get("dielectric_saturation", True)))
    cppargs.born_bulk_mode = _as_int_alias(born_model_dict.get("bulk_mode", "mix"), bulk_alias)
    cppargs.mu_born_diff_mode = _as_int_alias(mu_born.get("differential_mode", "auto"), diff_alias)
    if cppargs.mu_born_diff_mode not in (0, 2, 3):
        raise ValueError("Unknown mu_born differential_mode. Supported values are analytic/cppad/auto (0/2/3).")
    cppargs.mu_born_comp_dep_rel_perm = int(_as_bool(mu_born.get("comp_dep_rel_perm", True)))
    cppargs.mu_born_include_sum_term = int(_as_bool(mu_born.get("include_sum_term", True)))
    cppargs.mu_born_comp_dep_delta_d = int(_as_bool(mu_born.get("comp_dep_delta_d", True)))

    if cppargs.include_born_model == 0:
        cppargs.born_model = 0
        cppargs.born_radius_model = 1
        cppargs.born_diff_mode = 0
        cppargs.born_eps_mode = cppargs.born_bulk_mode
    else:
        cppargs.born_model = 2

        # Project the canonical Born radius mode into the current native runtime encoding.
        if cppargs.d_born_mode == 0:
            cppargs.born_radius_model = 1
        elif cppargs.d_born_mode == 1:
            cppargs.born_radius_model = 2
        elif cppargs.d_born_mode == 2:
            cppargs.born_radius_model = 3
        else:
            cppargs.born_radius_model = 5

        cppargs.born_eps_mode = cppargs.born_bulk_mode

        if cppargs.mu_born_diff_mode == 1:
            cppargs.born_diff_mode = 1
        elif cppargs.mu_born_diff_mode == 2:
            cppargs.born_diff_mode = 4
        elif cppargs.mu_born_diff_mode == 3:
            cppargs.born_diff_mode = 5
        elif cppargs.mu_born_comp_dep_rel_perm == 0:
            cppargs.born_diff_mode = 3
        elif cppargs.mu_born_include_sum_term == 0:
            cppargs.born_diff_mode = 2
        else:
            cppargs.born_diff_mode = 0

    if cppargs.born_model > 0 and cppargs.born_radius_model in (4, 5):
        if z_arr is None:
            raise ValueError("fitted d_Born_mode requires params['z'] as a per-species array.")
        if d_born_arr is None:
            raise ValueError("fitted d_Born_mode requires params['d_born'] as a per-species array.")
        ion_mask = np.abs(z_arr) > 1e-12
        if np.any(d_born_arr[ion_mask] <= 0.0):
            raise ValueError("fitted d_Born_mode requires positive ionic params['d_born'] values.")

    cppargs.DH_model = 2 if bjeruum else 1
    if cppargs.DH_model == 2:
        raise ValueError("Bjerrum treatment is reserved; DH_model=2 has no active public route.")
    if cppargs.DH_model < 0 or cppargs.DH_model > 2:
        raise ValueError("Unknown DH_model. Supported values are 0, 1, and reserved 2.")
    if "assoc_num" in params:
        cppargs.assoc_num = np_to_vector_int(params["assoc_num"])
    if "assoc_matrix" in params:
        cppargs.assoc_matrix = np_to_vector_int(params["assoc_matrix"])
    if "k_hb" in params:
        cppargs.k_hb = np_to_vector_double(params["k_hb"])
    if "l_ij" in params:
        cppargs.l_ij = np_to_vector_double(params["l_ij"])
    cppargs.parameter_source_label = _native_metadata_string(params, "_parameter_source_label", "runtime_payload")
    cppargs.parameter_provenance_status = _native_metadata_string(
        params,
        "_parameter_provenance_status",
        "runtime_payload_without_source_provenance",
    )
    cppargs.binary_interaction_provenance_status = _native_metadata_string(
        params,
        "_binary_interaction_provenance_status",
        "runtime_payload_binary_matrix",
    )
    cppargs.parameter_provenance_fields = _native_metadata_string_list(params, "_parameter_provenance_fields")

    return cppargs
