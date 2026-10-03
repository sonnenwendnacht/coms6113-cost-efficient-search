# Gated complete-row racing: choosing the Algorithm 2 mode

The research has three plausible complete-row modes:

- **Cost-SySR:** synchronized blocks for every active row; safe statistical
  baseline, but potentially expensive when there are 729 rows.
- **Hub-anchored racing:** one fully measured row supplies common-question
  residuals for many candidates; it can amortize the hub but introduces shared
  uncertainty and hub-selection risk.
- **Direct cost-aware racing:** pair only the current leader and challenger and
  pay both complete rows; it remains the fallback when measured covariance is
  weak or the hub does not amortize.

The recommendation is a **gated portfolio**, not an unconditional claim that
one of these is always best.

## Cross-fitted gate

1. Register the complete rows, explicit slot coordinates, fixed question
   permutations, two search folds, confidence allocation, and cost protocol.
2. On a calibration fold, measure a small complete-row block for a cost-only or
   independently chosen hub and a random set of candidate rows. Estimate paired
   residual variance, covariance, and realized new charge. Do not choose the hub
   from the same outcomes used to certify its screening performance.
3. For each candidate class, compute conservative lower/upper estimates of the
   direct and paired variance-per-dollar. Open the hub mode only when its upper
   paired cost--variance expression is below the lower direct expression and the
   hub's amortized charge is repaid by the number of candidates it will screen.
   Otherwise use Cost-SySR if the synchronized block fits the budget, or direct
   cost-aware racing.
4. Freeze the mode and run it on the execution fold with complete cells only.
   Use fixed question streams, simultaneous confidence sequences, global random
   scouts, safe reservations when a hard cap is claimed, and direct confirmation
   of the final row.
5. Evaluate the frozen recommendation once on the untouched audit fold. Report
   which mode was selected, its calibration and execution spend, and all mode
   failures; do not tune the gate on audit accuracy.

The mode decision is a measurement-allocation choice. It does not infer a
candidate's unpulled correctness from a hub or a Hamming neighbor.

## Why the gate is necessary

For a pair difference `D` and a complete-row anchor `Z`, a control-variate
residual `R=D-beta(Z-E[Z])` is useful only if its confidence-adjusted cost is
lower than direct paired racing. The anchor's mean and coefficient are uncertain
and shared across candidates; their estimation cost does not divide by the
number of races. If the hub is chosen adaptively, the calibration/execution
split or a simultaneous selection bound is required. If covariance is near zero,
the hub is a costly extra row. If costs are highly heterogeneous, synchronized
blocks can waste budget on an expensive active row even when residual variance is
small.

These are observable failure modes, so the gate can fail closed. A failed gate
is a result about the workload, not a reason to silently switch estimands or
relax the budget.

## Publication claim boundary

This portfolio combines established common-random-number ranking, control
variates, synchronized successive rejection, and cost-aware BAI. The conditional
application result would be that the gate chooses a lower-cost complete-row
measurement mode for some retry workloads while preserving held-out row
selection quality. A new theorem would need to analyze the actual cross-fitted
mode selection, random verifier-gated charges, and adaptive confidence rule.
Without that proof, report Algorithm 2 as an empirically gated protocol and keep
the established methods as explicit baselines.
