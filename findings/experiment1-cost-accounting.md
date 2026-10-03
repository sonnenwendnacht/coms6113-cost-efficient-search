# Experiment 1 finding: realized cost follows the calls that occur

## Rule

For one complete configuration/question cell, the proxy charge is the sum of
the input-token charge for every solver and verifier request that actually
runs:

```text
cell cost = sum(model coefficient × input tokens for reached calls)
```

The verifier controls whether the next retry is reached. Knowing a model's
coefficient does not make the total workflow cost known in advance.

## Example

If a workflow reaches only the first two attempts, charge:

```text
original solver
+ verifier after attempt 1
+ retry-1 solver
+ verifier after attempt 2
```

Do not charge the third solver or verifier, because they were never called.
If the verifier accepts the first attempt, charge only the original solver and
the first verifier. A solver or verifier request that runs and fails is still
charged because the request occurred.

## What Experiment 1 records

The tracked [cost matrix](../results/experiment1-nine-model-cost-usd.csv) has
one named configuration per row and 200 search plus 200 audit columns. Each
cell is the completed workflow's realized proxy charge. The underlying trace
also records the individual calls, input tokens, model coefficients, reached
attempts, and verifier decisions.

Experiment 1 deliberately charges only input tokens. Output tokens, cache
discounts, and latency are excluded. The coefficients are local proxy values,
not provider invoices. The fixed verifier is Qwen2.5-1.5B and is charged on
each verifier call that is reached.

## How search cost is reported

For a selector, search cost is the sum of realized cell costs for the cells it
profiles. A row-fraction or cell-fraction setting is only an allocation rule;
the reported comparison uses the resulting realized proxy dollars. Equal
fractions do not necessarily mean equal dollars. The selected row's cold
deployment cost is reported separately from profiling cost.

This accounting is the rule that Experiment 2 must preserve. Any cost-aware
screening method must track quality, retry reach, and realized charge
separately, and must never treat an uncalled retry as a failed or free call.

See the [detailed Experiment 2 algorithm specification](../experiment2-algorithm.pdf)
and the [cost export script](../scripts/export_experiment1_cost_csv.py).
