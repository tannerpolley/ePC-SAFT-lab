# Extraction Gate Evidence

Local phases 0-3 are complete as of the T999 judge receipt in `state.yaml`.

The pre-extraction gate is satisfied locally by these proof lanes:

- provider: wheel build with Ceres OFF and Ipopt OFF;
- equilibrium: wheel build with Ipopt ON and Ceres OFF;
- regression: wheel build with Ceres ON and Ipopt OFF;
- integration: normal fast native build with Ceres, CppAD, and Ipopt enabled.

Remaining transfer work is external organization/repository follow-up, not a
local blocker for this goal.
