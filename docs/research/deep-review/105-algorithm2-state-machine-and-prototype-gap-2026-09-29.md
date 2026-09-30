# Algorithm 2 state machine and current prototype gap

The existing `run_cacr` and `run_sccr` modules are useful replay heuristics, but
they are not yet the gated Algorithm 2 described in notes 101–104. They use an
empirical radius, allow a realized-cost overshoot, and accept a complete reward
and cost matrix as a replay fixture. None of those facts is wrong for debugging;
they are insufficient for a deployment or confidence claim.

## Required state machine

**Registered.** Freeze row IDs and slot coordinates, search and audit question
IDs, question permutations, quality signal, cost definition, budget mode,
confidence allocation, gate thresholds, and tie-breaking. The oracle interface
must expose only requested complete cells and return their realized ledger.

**Calibration.** Use a disjoint search fold to estimate residual variance,
row/anchor cost, and any covariance gate. If the hub or graph was selected from
this fold, do not use the same cells as execution-fold evidence without a
simultaneous selection bound.

**Mode frozen.** Choose exactly one of hub-anchored, Cost-SySR, or direct
cost-aware racing. Record the gate inputs and the reason for every fallback.
The audit fold cannot affect this choice.

**Executing.** Each action is a complete `(row, question)` cell. A synchronized
block must be admitted before any cell in it starts. The ledger stores stream ID,
question, row, reservation, realized charge, quality signal, and whether the
cell was an exact previously paid cell. Question streams are fixed permutations;
no cost- or outcome-based question substitution is allowed.

**Eliminating.** Apply simultaneous row/pair confidence bounds. Elimination is
allowed only when the selected reward contract (offline `final_correct` or
verifier proxy) supports it. If the next action cannot fit a safe reservation,
stop rather than treating a mean forecast as a hard cap.

**Confirming.** Evaluate the proposed row on a fresh registered block with direct
complete-row cells. Include this spend in the search ledger. If confirmation
fails or is inconclusive, return an unresolved recommendation rather than
silently using the calibration winner.

**Frozen/audited.** Freeze the row and only then open the held-out evaluation
questions. Report search spend, confirmation spend, audit accuracy, cold
deployment cost, overshoot or unused reservation, and the mode/gate decision.

## Invariants

1. No solver output, verifier state, retry prefix, or unpulled cost is reused.
2. A missing later retry is not imputed as failure or as a cheap fidelity.
3. Every quality observation has a complete-row charge and a registered question.
4. Search cost, deployment cost, and quality are separate quantities.
5. Every adaptive confidence stream has a preallocated or anytime-valid error
   share; fixed-`n` intervals are never repeatedly peeked at.
6. The audit split is never used for allocation, mode selection, or stopping.
7. The recommendation is directly observed and confirmed, even if a surrogate
   predicted it well.

## Prototype-to-algorithm changes

Before calling the implementation Algorithm 2, replace the current heuristic
radius with a declared finite-population/anytime rule, add a cell-oracle ledger,
separate calibration and execution folds, implement the safe reservation mode,
and expose the verifier-only versus offline-gold reward contract. Keep the
current replay as an ablation and debugging fixture. Its results must be labeled
heuristic, and its access to a full matrix must not be presented as an online
API experiment.

This state machine is compatible with the established SySRs, resource-aware BAI,
and control-variate baselines. The possible new result remains conditional on
showing that the gated complete-row protocol improves held-out selection per
realized dollar while satisfying these invariants.
