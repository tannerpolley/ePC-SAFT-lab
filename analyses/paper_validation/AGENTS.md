# Paper-Validation Figure Rules

Paper-validation analyses keep source-paper snapshots, parameter snapshots, and
figure workflows local to each paper folder.

These rules apply inside `analyses/paper_validation/**/figures/figure_NN/`.

## Required Shape

Figure folders such as `figures/figure_NN/source/` must contain only:

- `source/`
- `scripts/`
- `results/`

Use local names inside the figure folder. Do not prefix files with the paper or
analysis id such as `gross_2002`; the parent path already carries that context.

Paper-wide parameter snapshots live directly under `parameters/`, including
`parameters/mixed/`, `parameters/pure/`, and `parameters/user_options.json`.
Do not add nested dataset-name folders under `parameters/`.

## Source Files

Use `source/` for figure-local working copies only. Durable scientific source
data belongs under the data taxonomy in `data/reference/`, organized by data
type and component or mixture system, not by paper, author, year, or figure id.
Figure-local scripts must copy or assemble the needed reference inputs into
`source/` before generating results.

- `figure_NN.png` for the retained source figure image.
- `source_points.csv` for source or literature points used by the primary plot.
- `source_notes.csv` for axis calibration, provenance, uncertainty, and notes.
- Descriptive source-only CSV files are allowed when the figure needs additional
  literature tables, for example `pure_association_aad.csv`.

Reference CSVs should include a method/provenance label such as
`source_method=published_figure_trace`, `source_method=published_figure_marker`,
or `source_method=source_table` when the source path matters.

Do not create `data/reference/paper_validation/`. Paper-validation context stays
in figure manifests, source notes, and row-level provenance fields.

Do not keep JSON files in figure folders. If machine-readable campaign summaries
are needed, keep them at the paper level under `shared/results/`.

## Scripts

Use:

- `scripts/generate_data.py`
- `scripts/render_figure.py`

`generate_data.py` owns model/data generation. `render_figure.py` renders from
retained data and must be cheap enough to run repeatedly.

Do not keep `__pycache__`, placeholder files, scratch scripts, or one-off helper
scripts in figure folders.

## Results

Use `results/` for generated package outputs and retained plot artifacts:

- `model_curve.csv`
- `plotted_data.csv`
- `fit_statistics.csv`
- `figure_NN.svg`
- `figure_NN.png`
- `figure_NN.pdf`

Additional diagnostics must be CSV unless there is a specific paper-level
reason to keep a different format.

All retained `png`, `svg`, and `pdf` image files inside a migrated figure folder
must use the figure id as the filename stem, for example `figure_01.png`.

## Plot Evidence

For fit or replication evidence, do not use bar plots when a source-vs-model
curve, parity plot, residual plot, or direct overlay can show the fit. Bar plots
are only acceptable for genuinely categorical source data, not as the primary
evidence that a model reproduces a figure.

## Gate

Run the local structure gate on any migrated figure:

```powershell
.venv\Scripts\python.exe analyses\paper_validation\scripts\check_figure_contract.py analyses\paper_validation\2002_gross\figures\figure_01
```

Use `--all` only after the active paper-validation figure backlog has been
migrated to this contract.
