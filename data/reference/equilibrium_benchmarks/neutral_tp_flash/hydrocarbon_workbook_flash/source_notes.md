# Hydrocarbon Workbook Derived TP Flash

This folder records a source-backed neutral PC-SAFT TP flash fixture derived
from `workbooks/PC-SAFT Calculations - Hydrocarbon Basis.xlsm`.

Status: executable Stage 10 fixture for the current ePC-SAFT runtime when a
complete Stage 9 evidence payload is supplied.

Source facts:

- Sheet `PC-SAFT VLE` gives `T = 233.15 K`, `P = 1.2763694735856401 MPa`,
  liquid composition `[0.1, 0.3, 0.6]`, and vapor composition
  `[0.72466289283432894, 0.20293191372324873, 0.0724051934424223]`.
- Sheet `PC-SAFT Liquid` gives pure PC-SAFT parameters in cells `B16:D18`.
- Sheet `PC-SAFT Liquid` gives the symmetric binary interaction matrix in
  cells `G15:I17`.

The TP flash feed is constructed as an equal-mole blend of the source liquid and
vapor compositions. At the same source `T` and `P`, the expected vapor and
liquid phase fractions are therefore both `0.5`.

This is not Pereira 2012 proof evidence. Pereira System III remains HELD
literature context because the local source audit shows SAFT-VR parameters, not
an executable PC-SAFT/ePC-SAFT fixture for this package.
