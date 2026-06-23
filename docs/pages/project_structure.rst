Project Structure
=================

This repository is organized as a Python package with separate source-owned
analysis workflows. ADR 0005 defines the long-term package-extension split:
``epcsaft`` remains the core provider package, while equilibrium and regression
move to extension packages after provider/native boundaries are proven.

Package Surfaces
----------------

``packages/epcsaft/src/epcsaft/``
    Public provider package code, pure-Python helpers, and native-extension wrappers for the ``epcsaft`` distribution. The repository root is now the workspace/controller, not the provider distribution root.

``packages/epcsaft-equilibrium/`` and ``packages/epcsaft-regression/``
    Extension distributions that own their Python APIs, native modules, and package-local tests.

``tests/``
    Repository/workflow, docs/registry, integration, and cross-package governance contracts. Provider tests live under ``packages/epcsaft/tests``; extension tests live under their package-local ``tests`` trees. Default tests should stay fast and should not reproduce full scientific studies, benchmark scripts, regenerate plot galleries, or run long fitting/equilibrium sweeps.

``scripts/``
    Repository tooling only: native builds, doctor checks, validation orchestration, packaging, docs, reference-data curation, LaTeX sync, and issue triage. Analysis-specific coordinators may live under ``analyses/<category>/<short_id>/scripts/``, while figure-local generation and rendering scripts belong under ``analyses/<category>/<short_id>/figures/<figure_id>/scripts/``.

``data/reference/``
    Reusable checkout data: parameter datasets, benchmark records, literature tables, and curation sources that may be shared by several analyses or package tests.

``docs/``
    Package documentation and archival paper material. Archival PDFs and paper notes remain under ``docs/papers/``.

Analysis Workflows
------------------

Scientific reproductions, validation plots, fits, and paper figure workflows live under analysis roots such as ``analyses/paper_validation/<short_id>/`` or ``analyses/data_validation/<short_id>/``.

Use this layout for new analyses:

.. code-block:: text

   analyses/<category>/<short_id>/
     README.md
     analysis.yaml
     references.bib
     config/
     scripts/
     figures/
       <figure_id>/
         source/
         scripts/
         results/
     tables/
       table_###/
         source/
         scripts/
         results/
     parameters/
       mixed/
       pure/
       user_options.json
     shared/
       source/
       results/
     notebooks/
     tests/

Only create optional folders when they are useful. Keep each analysis self-contained: local scripts should read local analysis inputs or ``data/reference/`` and write outputs under the same analysis folder.

Data Ownership
--------------

Use ``data/reference/`` for stable reusable inputs:

- equilibrium benchmark fixtures under ``data/reference/equilibrium_benchmarks/``
- reusable literature data such as ``MIAC``, ``osmotic``, ``pure_component``, and regression tables

Use ``data/reference/`` for stable reusable inputs shared by multiple analyses. Organize reference data by scientific data type and component or mixture system, not by paper-validation context, author, year, or figure id. Use ``analyses/<category>/<short_id>/figures/<figure_id>/source/`` for hand-curated or figure-owned source assets. Use ``analyses/<category>/<short_id>/figures/<figure_id>/results/`` for generated model tables and the exact plotted data retained with that figure.

For full paper-validation analyses, ePC-SAFT parameter datasets and parameter CSV bundles used to execute the analysis must be analysis-owned input snapshots directly under ``analyses/paper_validation/<short_id>/parameters/``.
The ``parameters/`` folder should contain ``mixed/``, ``pure/``, and ``user_options.json`` directly; do not add a nested dataset-name folder such as ``parameters/2005_Cameretti/``.
Root ``data/reference/epcsaft_parameters/`` is retained only as a pointer README for the retired shared dataset tree.
Direct in-code parameter dictionaries are acceptable for focused tests, tiny synthetic fixtures, and smoke checks, but full validation analyses should use the analysis-local dataset snapshot.

Paper-validation source papers are copied under ``docs/md/`` and ``docs/pdf/``. Figure folders must be named ``figure_NN`` and contain only ``source/``, ``scripts/``, and ``results/``. Source paper figures live under ``figures/figure_NN/source/`` as ``figure_NN.png`` files, reusable source data lives under the appropriate ``data/reference/<data_type>/<component_or_system>/`` taxonomy home and is copied into figure-local ``source/`` folders by the figure scripts, extracted source tables live under ``tables/table_###/source/`` as Markdown snippets plus CSV conversions, paper-wide source manifests live under ``shared/source/``, and analysis-wide generated artifacts live under ``shared/results/``.

Output Policy
-------------

Generated figure outputs use figure-owned ``results/`` folders:

- ``figures/<figure_id>/results/runs/`` for ignored run-specific payloads, logs, sweeps, and exploratory output
- ``figures/<figure_id>/results/`` for curated generated tables, exact plotted data snapshots, rendered SVG/PNG/PDF figures, and CSV fit statistics that are intentionally retained

Each figure-owned output folder keeps the figure, exact plotted data snapshot, and provenance together:

.. code-block:: text

   figures/response_curve/results/
     model_curve.csv
     plotted_data.csv
     fit_statistics.csv
     figure_01.svg
     figure_01.png
     figure_01.pdf

Use one meaningful figure folder per figure or figure family. This layout is designed so external tools such as ``mplgallery`` can discover analysis-owned Matplotlib SVG plots through the project root ``.mplgallery/manifest.yaml`` without package-owned plotting servers or per-figure registration files.

Do not add new gallery index, server, or manifest workflows to this package. External visualization tools should discover analysis-owned assets directly.

Paper-validation figure folders do not keep per-figure JSON files. If a paper-level machine summary is needed, keep it under ``shared/results/``. Use ``analyses/paper_validation/AGENTS.md`` and ``analyses/paper_validation/scripts/check_figure_contract.py`` as the local gate for migrated figure folders.
