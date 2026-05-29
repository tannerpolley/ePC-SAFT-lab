---
issue: 145
title: "[Blocked] Associating neutral LLE after HELD/TPD and associating VLE proofs"
url: "https://github.com/ePC-SAFT/ePC-SAFT/issues/145"
state: "open"
milestone: "M4 - Equilibrium"
project: "ePC-SAFT Roadmap"
package: "equilibrium"
capability: "lle"
backend: "Ipopt"
readiness: "blocked"
release_target: "equilibrium-0.x"
last_synced: "2026-05-29"
---

# [Blocked] Associating neutral LLE after HELD/TPD and associating VLE proofs

Associating neutral LLE is blocked behind HELD-style neutral phase discovery,
TPD certification, and associating VLE/EOS proof work. Do not implement from
older associating-LLE branch assumptions.

Next useful agent action: work #148 and the required associating EOS/VLE gates
first; keep this issue blocked until those proofs exist.
