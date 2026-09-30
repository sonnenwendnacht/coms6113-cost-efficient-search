# Multiobjective recommendation for complete retry rows

A row search has three distinct quantities:

```text
profiling_spend: money paid while selecting a row
heldout_quality: correctness of the frozen row on audit questions
deployment_cost: cold-run path charge of that row on deployment questions
```

Confusing them changes the research question. A selector that saves profiling
money is not necessarily finding a cheap deployment row, and a cheap deployment
row is not automatically the most accurate row.

## Registered recommendation targets

Choose one target before the search:

- **Best accuracy:** maximize held-out correctness among the registered rows at
  each profiling budget. Search cost is a reported resource, not subtracted from
  accuracy.
- **Cost-constrained accuracy:** maximize correctness subject to a declared
  deployment-cost cap `D`. During search, maintain separate confidence bounds on
  quality and cold deployment cost; a row is definitely infeasible only when its
  lower cost bound exceeds `D`.
- **Scalar utility:** maximize `quality - lambda * deployment_cost` for a
  pre-registered `lambda`. Do not tune `lambda` on the audit set.
- **Pareto set:** return all rows not confidently dominated in the quality/cost
  plane, with a direct confirmation block for each reported frontier member.

The Table-7-style primary result should use best accuracy at fixed profiling
spend, then report deployment cost as a separate column. A second registered
frontier analysis can study cost-constrained selection.

## Paired vector evidence

For two complete rows on the same question, store the vector residual

```text
(DeltaY, DeltaK) = (Y_a - Y_b, K_a - K_b).
```

Common questions can reduce uncertainty in both quality and cost differences,
but the two confidence regions are separate. A quality winner can be more
expensive; a low-cost row can have lower quality. Do not collapse the vector to a
single score unless the scalar utility was frozen before observing outcomes.

To certify that row `a` dominates row `b`, require simultaneous bounds such as
`LCB(Y_a-Y_b) > 0` and `UCB(K_a-K_b) <= 0`. If either component remains
uncertain, keep both rows active or collect a direct complete-row block. The
search ledger still charges every reached call and never treats an omitted retry
as zero cost.

## Algorithm 2 reporting rule

Every selector/parameter pair should output:

```text
profiling_budget_requested
profiling_spend_realized
profiling_overshoot_or_unused_reservation
selected_row
heldout_accuracy
heldout_deployment_cost
verifier_pass_rate
constraint_status
```

The audit split is opened only after the row and the recommendation target are
frozen. This makes any claimed similarity benefit interpretable: it reduced the
profiling dollars needed to find a row meeting the pre-registered quality or
frontier target, rather than quietly changing the row objective.
