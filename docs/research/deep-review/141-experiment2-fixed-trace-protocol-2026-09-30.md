# 141: Experiment 2 fixed-trace protocol (2026-09-30)

The completed nine-model trace is a deterministic response matrix for an
offline allocation audit. It contains 729 complete ordered rows, 200 search
questions, and a disjoint 200-question audit set. A replay may reveal a search
cell only when the selector pays its recorded complete-cell charge. The audit
matrix stays hidden until the selector freezes one row.

## What the trace can and cannot test

The trace is strong enough to compare allocation rules under a fixed realized
cost ledger. It is not a fresh provider evaluation, and it cannot estimate
model sampling variability because every cell was generated once with
deterministic decoding. The primary target is therefore held-out accuracy of a
row selected from this finite question bank, not a population guarantee.

The verifier never saw the answer key during generation. For replay, keep two
separate selector contracts:

1. **Labeled offline profiling:** `final_correct` on revealed search cells is
   allowed as a supervised research label. It is useful for testing whether an
   allocator can recover a good row, but it is not a deployment-faithful
   verifier signal.
2. **Deployment-faithful profiling:** `verifier_pass` is the selector reward.
   The audit answer key is used only after selection to measure final
   correctness. A verifier-to-gold mismatch is part of the result.

The trace diagnostic found a severe retry confound: 284,553 of 291,600 cells
ended after one attempt, only 6,012 reached a second attempt and 1,035 reached
the third, while the verifier accepted 291,398 cells. Search reward vectors
are therefore mostly controlled by the first solver choice; retry-slot
similarity in this trace is evidence about an almost-never-reached suffix, not
evidence that a retry-aware method works.

## Prespecified E2 comparison

Run every `(algorithm, parameter, seed)` as its own report row. Use the fixed
seeds already registered in the nine-model configuration and a common
realized-dollar grid. Record the exact charge of every revealed cell, any
overshoot, the number of unique cells, the frozen recommendation, held-out
accuracy, and cold deployment cost. Do not pick a parameter after looking at
the audit set.

The minimum comparison is random rows, random cells, uniform cells, Matrix
UCB-E, Bayesian categorical UCB, arm elimination, hill climbing, synchronized
Cost-SySR, CW-PLR, CAET-style pair allocation, and CG-RTE. The graph method
must have a fixed sparse edge set and a calibration block declared before the
replay; an edge is not a free observation and both complete endpoints must be
charged unless exact eligible cells are already in the cache.

Required negative controls are a shuffled row-coordinate graph, independently
permuted question columns that preserve row marginals, unit cell costs, and
costs permuted across questions. These controls separate a real matched-row
signal from first-slot dominance, question ordering, and cost heterogeneity.

Primary summaries are cost-to-held-out-accuracy curves, paired audit
differences across seeds, selected-row frequency, simple regret against the
full search reference, cold deployment cost, and false elimination or
no-recommendation rates. Search charge, audit charge, and deployment charge
must be separate. Confidence-interval width alone is not a saving.

## Decision rule for Algorithm 2

CG-RTE remains only a candidate. Keep it if it lowers unique paid cells or
realized profiling dollars at matched held-out accuracy and error protection
against direct paired racing and unrestricted target-difference allocation.
If the Hamming graph fails its shuffled-graph control, or if a verifier-proxy
run cannot preserve the gold ranking, report the negative result and use
Cost-SySR or direct cost-aware racing as the paper's method. If the retry
reach rate remains near zero, redesign the workflow/checker before claiming a
retry contribution.

No model/API calls are made by this protocol; it is a replay design for the
completed trace.
