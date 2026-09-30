# 134: CG-RTE algorithm specification (2026-09-29)

This note turns the current hypothesis into a concrete protocol. The temporary
name is **Costed Graph-Residual Transductive Elimination (CG-RTE)**. It is an
adaptation target, not a claim that the combination is novel or correct.

## Inputs and target

* A finite row set (V), where each row is a complete solver/verifier/retry
  configuration.
* A pre-registered graph (G=(V,E)), initially the one-coordinate Hamming
  graph over row slots. Graph edges are hypotheses, not free observations.
* A pre-shuffled search-question permutation split into fixed blocks. The audit
  questions are never used by the selector.
* A complete-cell executor returning terminal reward (Y_{v,q}in[0,1]), the
  full retry-call ledger, and realized charge (C_{v,q}).
* A profiling objective: identify an epsilon-best row for the finite-bank mean
  (mu_v=N^{-1}sum_q Y_{v,q}) under a declared soft realized-dollar target
  or a hard cap with deterministic cell reservations.

## State maintained

For every directly sampled row, keep its mean estimate, a simultaneous radius,
the exact question IDs, and the realized ledger total. For every opened edge
(e=(u,v)), keep paired residuals

\[
D_{e,q}=Y_{v,q}-Y_{u,q},
\]

the disjoint calibration and elimination blocks, a conservative residual
interval, and the edge's realized endpoint charge. A path estimate is allowed
only when all of its node/edge intervals are still valid and its edge gates
have passed. Exact cached cells may be reused only with matching row,
question, model snapshot, prompt version, stopping rule, and reward contract;
this is cell reuse, never workflow-prefix reuse.

## Protocol

1. Reserve a small direct calibration block for every initially active row,
   using the fixed question schedule. Do not eliminate during this block.
2. Choose an anchor among rows with valid direct estimates using a declared
   rule, such as lowest certified incremental charge with deterministic ties.
   If no anchor is sufficiently precise, continue direct racing.
3. Open only one-coordinate edges whose endpoints have a common fresh block or
   an exact cached cell match. Fit the paired residual on the calibration
   block, then test its stability on a disjoint block. An edge that fails the
   gate is marked unavailable until a fresh calibration design is registered.
4. For each candidate (v), form direct and graph-supported intervals. A path
   (P) from the anchor gives a conservative interval with radius equal to the
   anchor radius plus the sum of the gated edge radii; a covariance-aware
   radius may replace the sum only when its joint coverage is established.
   Limit path length and use the minimum-width valid path.
5. At each block boundary, compute the expected reduction in the largest
   incumbent/challenger interval overlap per *new* realized-charge estimate.
   Prefer the edge or direct row block with the largest score, subject to a
   fixed direct-exploration reserve. A hard-cap run reserves deterministic
   upper charges for every endpoint before launching the block. A soft run
   records actual charges and overshoot.
6. Eliminate a row only when its valid upper interval is below the incumbent's
   valid lower interval by the configured epsilon. Graph intervals may drive
   this decision, but the row remains marked indirectly supported until a
   direct complete observation is available.
7. Stop when one row remains, the epsilon intervals overlap only within the
   requested tolerance, or the declared budget cannot fund another complete
   block. If the last block is partial, ignore its extra cells for ranking and
   report a provisional common-prefix result or no recommendation.
8. Before returning a deployment recommendation, run the surviving row on a
   fresh direct search block when one remains. Report this confirmation and
   keep the held-out audit evaluation entirely separate.

## What the score must not do

The score must not divide by a cost estimate learned from only cheap questions,
open an edge because its observed rewards look favorable, or treat a skipped
retry as a zero reward. A verifier PASS is a deployment-visible proxy; the
answer-key correctness label remains audit-only. Every terminal failure or
timeout is a complete cell with an explicit quality status and all charges
incurred.

## Correctness target and limits

The first theorem target is conditional: on the event that all direct and
cross-fitted edge intervals have simultaneous coverage, every graph-based
elimination is safe and the final directly confirmed row is epsilon-best over
the registered finite bank. A hard-dollar theorem additionally needs a
deterministic upper charge for every possible retry cascade and atomic block
reservations. A realized-spend run can claim only an observed cumulative
charge and its overshoot.

The method should be rejected as an Algorithm 2 candidate if direct paired
elimination matches it at equal realized dollars, if edge gates rarely pass,
if anchor calls are not amortized across multiple candidates, or if graph
propagation increases false elimination. Required comparisons are direct
paired racing, CAET-style cost-aware pairwise allocation, PROBE-style
residual calibration, ungated graph prediction, and a shuffled-edge control.

No implementation or experiment is claimed by this note.
