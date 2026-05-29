Publishing To PyPI
==================

GitHub releases and PyPI uploads are separate steps. A GitHub release can carry
wheel and sdist assets before the PyPI pending publisher exists. PyPI uploads
run manually through GitHub Actions and PyPI Trusted Publishing after that
publisher is configured.

PyPI trusted publisher setup
----------------------------

Configure a PyPI trusted publisher for the current organization-owned
repository:

- PyPI project name: ``epcsaft``
- Owner: ``ePC-SAFT``
- Repository name: ``ePC-SAFT``
- Workflow filename: ``publish-pypi.yml``
- Environment name: ``pypi``

The package-extension split will later require separate PyPI projects and
trusted publishers for ``epcsaft-equilibrium`` and ``epcsaft-regression``.

For a new PyPI project, create this as a pending publisher in PyPI before the
first GitHub Actions publish run. PyPI can still return 404 for
``https://pypi.org/pypi/epcsaft/json`` until that first upload succeeds, so the
workflow allows the 404 first-publish case and relies on the trusted-publisher
exchange to fail loudly if the pending publisher is missing or mismatched.

If the PyPI project already exists, the workflow checks the version in
``pyproject.toml`` and stops before building artifacts when that version has
already been published. PyPI files are immutable, so duplicate-version retries
must use a new version.

Publish a release
-----------------

1. Update ``pyproject.toml`` and ``uv.lock`` to the new version.
2. Update ``CHANGELOG.md`` and add ``docs/releases/vX.Y.Z.md``.
3. Commit and push ``main``.
4. Run ``uv run python scripts/dev/build_dist.py``. The default release
   baseline disables local Ipopt so the wheel does not require Ipopt runtime
   DLLs.
5. Create and push tag ``vX.Y.Z``.
6. Create the GitHub release for ``vX.Y.Z`` with the files from ``dist/``.

Creating a GitHub release does not upload to PyPI. Attach the built wheel and
sdist to the GitHub release so users can install from GitHub while PyPI is not
published.

Publish to PyPI
---------------

After the PyPI pending publisher exists, run the publish workflow manually from
GitHub Actions:

.. code-block:: powershell

   gh workflow run publish-pypi.yml --repo ePC-SAFT/ePC-SAFT -f ref=vX.Y.Z

The workflow builds the sdist and Windows CPython 3.13 wheel from the requested
tag, then publishes the distributions to PyPI through
``pypa/gh-action-pypi-publish`` using OIDC. Use manual dispatch only for a tag
that already points at the intended release commit.

Failure modes
-------------

- ``trusted publishing exchange failure`` usually means the PyPI publisher
  configuration does not exactly match the repository, workflow filename, or
  environment name above.
- ``invalid-publisher`` on the first upload means PyPI has no matching pending
  publisher for the OIDC claims. Create the pending publisher with the values
  above, then rerun the workflow.
- Duplicate-file errors mean that version was already published to PyPI. Bump
  the package version and publish a new release; PyPI files are immutable.
- Wheel build failures should be fixed in the package or build workflow before
  retrying publish.
