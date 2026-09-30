# 119: Budget-basis audit (2026-09-29)

## Why the old fraction column is unsafe

The legacy selector sweep does not give every algorithm the same meaning of
`fraction`:

- random search and Bayesian row search evaluate a fraction of complete rows;
- uniform, matrix UCB, annealed similarity, and graph residual racing consume a
  fraction of cells;
- arm elimination and hill climbing use a confidence/restart parameter and do
  not have a direct profiling budget;
- the structured replay uses a fraction of the exhaustive **realized dollar
  cost**.

Their measured `search_cost` values are useful, but a table that labels all
these parameter values “budget” can compare methods at different resources.
This is a reporting error even if each individual selector is implemented
correctly.

## Source-level repair

The sweep now records `budget_basis` for every standard selector, and the
structured replay records `realized_cost_fraction`. This metadata does not
make the methods equal-dollar; it makes the mismatch visible and prevents the
report from implying a false common budget.

## Required comparison protocol

For the main Algorithm 2 result, construct one event ledger for each
algorithm/seed and freeze recommendations at common cumulative-dollar
checkpoints. At a checkpoint, do not credit a cell whose completion crosses
the checkpoint; report its full realized overshoot separately. For selectors
without a native budget parameter, use the ledger checkpoint as the resource
limit and retain their original parameter as a separate algorithm setting.

The table should therefore contain at least:

```text
selector, algorithm_parameter, budget_basis, target_dollars,
actual_search_dollars, overshoot, heldout_accuracy, cold_deployment_cost
```

Until this ledger exists, cell-fraction curves and realized-dollar curves must
be shown separately. The metadata patch is a guardrail, not evidence of an
algorithmic improvement.
