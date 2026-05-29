---
issue: 157
title: "Replace user-facing derivative and Born option schema"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/157"
state: "open"
milestone: "M2 - Python API"
project: "ePC-SAFT Roadmap"
package: "core"
capability: "derivatives"
backend: "CppAD"
readiness: "ready"
release_target: "core-0.x"
last_synced: "2026-05-29"
---

# Replace user-facing derivative and Born option schema

Replace the public Python-facing derivative and Born option schema so user
configuration matches the current EOS/backend model and avoids stale option
names.

Next useful agent action: update API schema, docs, and tests together so option
names, derivative backend behavior, and Born model selection stay aligned.
