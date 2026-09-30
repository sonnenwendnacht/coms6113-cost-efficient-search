# Realized-dollar curves for selector comparison

A fair Table-7-style comparison needs a common axis: cumulative profiling
spend, not a fraction of cells. The following protocol makes that axis
reproducible without giving selectors access to unobserved cells.

## Event ledger

Each selector run writes an ordered event stream:

```text
step, row_id, question_id, quality_signal, realized_charge,
stream_id, reservation, reused_exact_cell
```

`realized_charge` is the sum of all reached solver and verifier input-token
charges for that complete cell. An exact previously paid cell costs zero new
profiling dollars, but the original charge remains in the ledger. Prefixes,
outputs, verifier state, and unpulled costs are never reused.

## Checkpoint reconstruction

Choose dollar checkpoints `B_1 < ... < B_J` before reading held-out results.
For each seed and each checkpoint `B_j`, replay the selector's event order and
retain the latest state whose **completed** cumulative ledger is at most `B_j`.
The recommendation at `B_j` is the row returned by that state. If the next cell
or synchronized block crosses `B_j`, its completed information is not credited
at `B_j`; record the overshoot separately and use the previous state. This rule
prevents a large last block from receiving an unfair accuracy benefit.

A safe-reservation selector can guarantee that no block crosses a checkpoint.
A realized-spend selector may overshoot and must expose the amount. If it has no
recommendation before a very small checkpoint, report `unresolved` rather than
silently using a later row.

## Aggregation and plotting

For each `(algorithm, parameter, B_j)`, report mean held-out accuracy across
seeds, mean realized profiling spend, overshoot rate, and a seed-level confidence
interval. Plot the empirical step curve against actual dollars. Do not linearly
interpolate accuracy between checkpoints or tune the curve on the audit split.
A normalized horizontal axis `B_j / exhaustive_search_cost` may be shown after
all runs for readability, but the denominator is a reporting constant, not an
input available to the selector.

The exhaustive row is a reference recommendation, not free search evidence. Its
full cost and accuracy are reported separately. Calibration, confirmation, and
hub cells count toward the method's profiling spend unless the same cost is
explicitly charged to every baseline.

## Parameter pairs

Each `(algorithm, parameter)` is a separate pre-registered run family. If a
parameter is a budget, evaluate the family at the dollar checkpoints. If a
parameter controls exploration or confidence, freeze it before the audit. The
best parameter may be selected for a development analysis, but the final held-
out table must either report every pair or use a separate development split for
selection.

This protocol is compatible with cell-oracle replay and online API collection.
It fixes the earlier mismatch where standard selectors used cell fractions while
structured selectors used a full-matrix cost fraction, and it keeps search cost
separate from cold deployment cost.
