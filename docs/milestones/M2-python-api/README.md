# M2 - Python API

Public Python package surface, user-facing workflow ergonomics, result schemas,
diagnostics, examples, import stability, and package-level user experience.

## Project Field Defaults

- Package: `core` unless the API is extension-owned
- Capability: `derivatives` only for derivative-facing user APIs
- Backend: set only when the public API exposes or configures backend behavior
- Release target: usually `core-0.x`

## Current Open Issues

| Issue | Capability | Backend | Readiness | Summary |
| --- | --- | --- | --- | --- |
| [#156](issues/0156-add-folder-loadable-model-options-and-one-call-mixture-loading.md) | blank | blank | `ready` | Add folder-loadable model options and one-call mixture loading. |
| [#157](issues/0157-replace-user-facing-derivative-and-born-option-schema.md) | `derivatives` | `CppAD` | `ready` | Replace the user-facing derivative and Born option schema. |
