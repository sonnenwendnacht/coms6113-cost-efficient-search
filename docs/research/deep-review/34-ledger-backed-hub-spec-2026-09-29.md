# Ledger-backed hub protocol specification (2026-09-29)

This note turns the hub idea into an implementable research protocol. It is a
specification and audit target, not an experiment or a new theorem.

## Objects and information boundary

Let `C` be the registered set of complete retry rows and `S` the registered
search questions. A single paid cell action is `pull(c,q)`, which executes the
whole row on one question. It returns only:

```text
(quality_signal, realized_input_token_charge, execution metadata)
```

The quality signal used for live decisions must be deployable (for example,
the answer-key-blind verifier's accepted/retry signal or a declared judge).
`final_correct` remains an audit label and cannot enter a live stopping rule.
The action must not expose an unexecuted retry suffix or a different row's
output.

The oracle owns the complete trace fixture. The algorithm sees no public
reward/cost matrix; it can request a cell only through the oracle. Every
request receives a unique ledger record with method, seed, stream ID, row,
question, reservation, realized charge, reuse flag, and timestamp/order.

## Registered design

Before selection, write a manifest containing:

- immutable row IDs and the explicit slot map;
- the search question IDs and a hash of each seed's permutation;
- hub ID and how it was selected (cost-only, or an independent calibration
  fold);
- candidate block streams, a confirmation stream, and their disjointness;
- `epsilon`, error allocation, tie-breaking, global-exploration reserve, and
  hard or soft budget semantics;
- tokenizer/model/checker versions and a conservative maximum charge for one
  complete cell.

The question order is fixed before any outcome. A stream can be opened
adaptively, but its next question is the next item in its already registered
permutation. If a stream is selected after observing outcomes, its interval
must be valid under that adaptive filtration or the stream must be
cross-fitted and disjoint from the data used to select it.

## Minimal algorithm

1. **Initialize the hub.** Pull the hub on a predeclared screening block. Keep
   the hub's quality cells and charges in the method ledger. If hub choice was
   learned, use a calibration fold and do not reuse its target-fold outcomes
   for choosing the hub.
2. **Open candidates.** Give every candidate a small registered block on the
   same questions as the hub. Form paired differences
   `D_c(q) = Q(c,q) - Q(h,q)`. Compute a finite-population or anytime-valid
   interval for the mean difference. The hub's own mean interval is retained;
   it is not treated as known unless the full finite search population was
   paid.
3. **Allocate by information per reserved dollar.** For each live candidate
   and possible next block, estimate only its expected interval-width
   reduction and divide by the block's conservative charge bound. This score
   chooses the next action; it cannot eliminate a row or certify an answer.
   Include a fixed global reserve that periodically opens an untested row.
4. **Eliminate.** Remove a candidate only when its simultaneous upper bound is
   below the incumbent lower bound by `epsilon`, or its cost-feasibility upper
   bound is definitely over the declared deployment limit. A failed similarity
   or covariance gate disables transfer for that candidate and falls back to
   direct row evidence.
5. **Confirm.** Require a fresh direct block for the proposed row, or a
   predeclared second hub, before freezing the recommendation. The confirmation
   charge is part of the search budget and is reported separately. Then, and
   only then, evaluate the frozen row on the held-out audit questions.

At every action, a hard-cap oracle admits only if

```text
spent + reservations_for_in_flight + maximum_new_action_charge <= B.
```

If the maximum charge cannot be bounded from the pinned local tokenizer and
prompt limits, mark the run soft-cap, stop at the measured threshold, and
report overshoot rather than claiming a hard guarantee.

## Required output fields

The method report should include:

```text
selected_row
selected_row_directly_observed
search_spend_usd
confirmation_spend_usd
reserved_usd_peak
overshoot_usd
paid_complete_cells
reused_hub_cells
hub_id
question_manifest_hash
candidate_stream_ids
audit_accuracy
audit_mean_cold_cost
```

For each candidate, retain its paired sample count, estimated difference,
interval, covariance/variance gate result, and elimination reason. This makes
it possible to distinguish a real saving from an unobserved surrogate row or
from a method that simply spent beyond its nominal cap.

## What this does and does not claim

The design is a complete-row common-question comparison with explicit
resource accounting. Common-random-number ranking and selection, correlated
best-arm methods, and resource-constrained BAI are established foundations;
the protocol does not claim those ingredients as novel. The possible
application contribution is an empirical or conditional theoretical result
about when one already-paid complete retry row amortizes paired evidence over
many other complete rows under path-dependent charges.

