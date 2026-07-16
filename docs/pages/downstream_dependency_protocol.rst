Downstream Dependency Protocol
==============================

Use this protocol when another project fails because of a suspected upstream
``epcsaft`` package bug, missing public API contract, packaging problem,
documentation ambiguity, or numerical behavior change.

Evidence intake
---------------

When a downstream project exposes a possible package defect, capture the
downstream repo or path, task goal, failing command, error or bad result,
minimal reproducer, imported package path, expected and actual behavior, the
downstream validation command, and any temporary workaround. Submit that
evidence through the current clean repository's own contribution channel. The
preserved lab does not route or mutate live issues.

Upstream workflow
-----------------

For complete reports, reproduce the failure before editing. Classify the issue
as API misuse, missing public contract, native equation issue, packaging/build
issue, numerical/solver issue, or documentation ambiguity. Add a focused
regression test when feasible, fix the package rather than patching downstream
code, and validate with the smallest relevant ladder:

.. code-block:: bash

   uv run python run_pytest.py <focused-test-targets> -q
   uv run python scripts/dev/validate_project.py quick

Run ``uv run python scripts/dev/build_epcsaft.py`` and ``uv run python
scripts/dev/doctor.py`` when native code or package import state is involved. Use
``uv run python scripts/dev/validate_project.py confidence`` only for broad or
native-risk changes.

Before handing the result back, record the root cause, files or APIs changed,
focused tests run, install or rebuild command, downstream validation command,
and any remaining risk. The downstream project must confirm that its original
command now passes; solver termination alone is not sufficient confirmation.
