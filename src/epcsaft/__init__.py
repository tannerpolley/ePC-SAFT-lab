"""Public package interface for the native ePC-SAFT runtime."""

from __future__ import annotations

import os

_DLL_DIRECTORY_HANDLES: list[object] = []


def _add_runtime_dll_directories() -> None:
    if os.name != "nt" or not hasattr(os, "add_dll_directory"):
        return
    raw_dirs = os.environ.get("EPCSAFT_RUNTIME_DLL_DIRS", "")
    for raw_dir in raw_dirs.split(os.pathsep):
        dll_dir = raw_dir.strip()
        if not dll_dir:
            continue
        _DLL_DIRECTORY_HANDLES.append(os.add_dll_directory(dll_dir))


_add_runtime_dll_directories()

from epcsaft._types import InputError, SolutionError
from epcsaft.frontend import Mixture, State
from epcsaft.model.options import BornModelOptions, MissingModelParameterError, ModelOptions
from epcsaft.model.parameters import ParameterSet
from epcsaft.model.templates import create_input_template
from epcsaft.runtime import __version__, capabilities, provider_native_sdk, runtime_build_info

__all__ = [
    "InputError",
    "BornModelOptions",
    "MissingModelParameterError",
    "Mixture",
    "ModelOptions",
    "ParameterSet",
    "SolutionError",
    "State",
    "__version__",
    "capabilities",
    "create_input_template",
    "provider_native_sdk",
    "runtime_build_info",
]
