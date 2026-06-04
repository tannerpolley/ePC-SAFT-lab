# Saturation Property Validation Lane

The target validation is a Chapman-Figures-16/17-style associating-fluid
property comparison: experimental vapor-pressure and saturated-liquid-density
points against curves from exact implicit association and the explicit Picard
closure.

Current fixed-state property plots are a diagnostic lane, not saturation
validation. They use experimental saturated liquid density or vapor pressure as
inputs to provider state probes and a toy PC-SAFT exact-vs-Picard
pressure-density coupling. They report pressure/density inverse mismatch and
liquid density-root status, root-bracket policy, pressure-evaluation count,
and retained \(Z\) contribution terms. They do not solve phase coexistence.

The `quick_phase_equilibrium` lane is a separate toy equilibrium diagnostic.
It solves pure-component density pairs for pressure equality and equality of a
reduced chemical-potential expression, \(\ln\rho+a^{res}+Z\), using the same
toy PC-SAFT pressure path. It is useful for exact-vs-Picard solver behavior,
but it remains analysis-only evidence until parameter provenance, vapor/liquid
branch selection, and provider coexistence contracts are explicitly validated.

The automated public source currently keeps only associating compounds with
paired vapor-pressure and saturated-liquid-density rows from the NIST fluid
table endpoint: methanol and water. Acetic acid from Chapman Fig. 16 should be
added only through a separately labeled digitized-figure source or another
paired public saturation table; NIST's acetic-acid Chemistry WebBook page has
phase-change correlations, but the fluid saturation table endpoint returns no
paired density/pressure rows for this lane.

## Model Gates

Do not render Picard model curves as \(P_{\mathrm{sat}}(T)\) or
\(\rho_L(T)\) saturation predictions until these pieces exist in the analysis
lane:

1. A unit-consistent PC-SAFT association strength
   \(\Delta_{AB}(T, \rho, x)\) using the same parameter basis as the provider:
   segment diameter, contact radial distribution, association energy, and
   association volume.
2. A shared residual Helmholtz evaluator
   \(a^{res}=a^{hc}+a^{disp}+a^{assoc}\) where exact implicit and Picard differ
   only in the association site-fraction closure. The current toy diagnostic
   path has this for pure associating fixed-state probes.
3. Pressure from the same residual Helmholtz path:
   \(Z=1+\rho\,\partial a^{res}/\partial \rho\), with units traced back to
   molar density and temperature.
4. Liquid and vapor density-root solves with recorded convergence status. The
   current toy diagnostic path has only the fixed-state liquid-density root
   check.
5. Pure-component coexistence equations, at minimum
   \(P^L=P^V\) and \(\mu^L=\mu^V\), or the equivalent fugacity equality.
6. Retained output rows for every experimental point with model name, solver
   status, residuals, elapsed time, and a reason when a model curve point is
   not produced.

## Required Plots

When those gates are met, use paper-like plots:

- \(\log_{10}(P/\mathrm{kPa})\) vs. \(1000/T\): experimental points,
  exact implicit curve, Picard curve, and retained residual rows.
- \(T\) vs. \(\rho_L\) in \(\mathrm{mol}\,\mathrm{cm}^{-3}\): experimental
  points, exact implicit curve, Picard curve, and retained residual rows.
- Use dotted colored model curves and black data points. Plot Picard only when
  the retained CSV has finite Picard pressure/density outputs for that row.

The plot labels must say `Exact implicit` and `Picard`; internal names such as
`damped_picard_7_05` belong only in retained CSV metadata.
