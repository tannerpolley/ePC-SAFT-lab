# Digitization Benchmark

This analysis stores generated receipts from the user-level consensus figure
digitization skill. It checks plot digitization tools against synthetic figures
with known source data and the Gross 2002 hard-case seed-refinement manifest.

Run:

```powershell
.\.venv\Scripts\python.exe C:\Users\Tanner\.agents\skills\consensus-figure-digitizer\scripts\benchmark_digitizer_toolchain.py --repo-root .
```

The skill utility writes source data and rendered benchmark plots under
`figures/*/input`, extracted CSVs and QA overlays under `figures/*/output`, and
cross-method metrics under `results`.

The benchmark intentionally uses known pixel-to-data transforms so extraction
error is scored against source CSV data, not visual estimates.

## Covered extraction paths

- Direct CSV source tables.
- Machine-readable PDF tables through `pdfplumber`.
- PDF text receipts through `pypdf`.
- PDF vector-path detection through PyMuPDF.
- PDF rendering through Poppler `pdftoppm`.
- Local XY point extraction from a PNG plot.
- Local XY curve extraction from a black-and-white PNG plot.
- scikit-image skeletonization plus SciPy smoothing for continuous curves.
- `plotdigitizer` extraction from a black-and-white, single-trajectory PNG plot.
- OCR-assisted tick-label reading through Tesseract.
- ImageMagick preprocessing before OpenCV extraction.
- Gross 2002 hard-case seed refinement with retained review rows.
- Manual-review lanes for WebPlotDigitizer and Engauge when needed.

The retained summary is `results/digitization_toolchain_summary.csv`. A route is
accepted when it stays within the encoded error thresholds and writes retained
CSV plus QA overlay, reconstructed plot, or extraction metadata.

`plotdigitizer` is deliberately limited to the black-and-white single-curve case
because that is the tool's documented operating mode. The local OpenCV-based and
PDF-based lanes cover the rest of the automated workflow.
