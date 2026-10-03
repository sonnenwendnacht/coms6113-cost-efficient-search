# 114: Cross-fitted edge gate and the current SCCR gap (2026-09-29)

## Source audit

The current `run_sccr` prototype calibrates an incumbent/challenger pair with
`calibration_block` questions, stores those paired differences in
`pair_values`, and then lets the same history drive `paired_decision` during
the next race. The gate therefore decides that an edge is safe and evaluates
the edge on overlapping observations.

This is a reasonable debugging ablation, but it is not the cross-fitted gate
specified by EGCR. It can select a favorable edge because its calibration
sample happened to have low residual variance, then report that same sample as
evidence that the edge was useful. The additive `variance_margin / sqrt(m)` is
also a heuristic buffer, not a simultaneous confidence bound.

## Required correction for a publishable version

Register one global question permutation before any rows are pulled and split
it into disjoint roles, for example:

```text
Q_pilot      -> estimate residual variance and charge quantiles
Q_race       -> choose and compare challengers
Q_confirm    -> final selected-row confirmation
Q_audit      -> untouched held-out gold evaluation
```

The edge set and all gate thresholds must be frozen from `Q_pilot` (or from a
separate development bank). A racing block may use only `Q_race`. If a pair
has no pilot evidence, it receives the direct-racing fallback; it cannot be
declared safe after looking at its racing outcomes. The confirmation and audit
questions must not be used to update the edge gate.

For edge `e`, the pilot statistic is the paired residual variance

\[
\hat v_e^{(p)} = \operatorname{Var}\{Y_{bq}-Y_{aq}:q\in Q_p\}.
\]

The gate should compare an upper confidence bound for `v_e` against the
registered direct-comparison variance/cost baseline, including a multiplicity
allowance across all candidate edges. If that bound does not clear the
variance and amortization threshold, the edge is ordinary proposal order or is
rejected. The racing stream then has a clean conditional interpretation.

## Consequence for current results

Until this split is implemented, SCCR results can be reported only as a
heuristic ablation showing behavior of an overlapping calibration/race rule.
They cannot support a claim that the gate protects against false similarity or
that its savings generalize to new questions. The direct CACR/CW-PLR baselines
also use empirical radii, so they remain heuristic selectors rather than
confidence-certified EGCR implementations.

This correction does not require workflow-prefix reuse. It only changes which
complete row/question cells are allowed to decide the similarity gate and
which disjoint complete cells are allowed to evaluate the selected row.
