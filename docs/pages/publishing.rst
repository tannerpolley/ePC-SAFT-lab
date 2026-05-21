Publishing To PyPI
==================

Package releases are published by GitHub Actions through PyPI Trusted
Publishing. This avoids storing a long-lived PyPI API token in GitHub secrets.

PyPI trusted publisher setup
----------------------------

For the first PyPI publish, configure a PyPI trusted publisher for this project:

- PyPI project name: ``epcsaft``
- Owner: ``tannerpolley``
- Repository name: ``ePC-SAFT``
- Workflow filename: ``publish-pypi.yml``
- Environment name: ``pypi``

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
4. Create and push tag ``vX.Y.Z``.
5. Create the GitHub release for ``vX.Y.Z``.

The ``publish-to-pypi`` workflow runs when a GitHub release is published. It
builds the sdist and Windows CPython 3.13 wheel, then publishes the
distributions to PyPI through ``pypa/gh-action-pypi-publish`` using OIDC.
Historical ``v0.1.x`` release receipts are explicitly skipped by the publish
workflow.

Manual publish
--------------

The workflow can also be run manually from GitHub Actions:

.. code-block:: powershell

   gh workflow run publish-pypi.yml --repo tannerpolley/ePC-SAFT -f ref=vX.Y.Z

Use manual dispatch only for a tag that already points at the intended release
commit.

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
