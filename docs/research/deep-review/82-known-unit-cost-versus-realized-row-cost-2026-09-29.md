# Known unit cost versus realized retry-row cost

The cost coefficient can be known before a call while the complete workflow
charge remains unknown. For row `c` and question `q`, write

```text
K(c,q) = sum_j R_j(c,q) * coefficient(model_j) * input_tokens_j(q),
```

where `R_j` is the event that attempt `j` is reached. The coefficient and the
input length may be known at launch, but `R_j` depends on earlier verifier
events. Thus a row's realized cost is a random, outcome-linked quantity even
when every per-attempt price is public and there is no output-token or cache
charge.

## Consequences for Algorithm 2

- A profiling budget must be charged by realized complete-cell cost. Do not
  treat equal numbers of questions as equal dollars.
- Before a cell is pulled, cost estimates can guide acquisition only through a
  declared reach model or a conservative upper bound. The selector must not
  peek at an unpulled realized cost.
- For a deployment-cost constraint, estimate a row's mean cost with its own
  confidence interval. Expected cost below the cap is not a guaranteed cap;
  certification needs an upper cost bound or a predeclared risk allowance.
- If a scalar utility is used, `U=Y-lambda*K` must retain the observed
  correlation between quality and path cost. Separately ranking accuracy and
  cost and then multiplying marginal estimates can change the winner.

This reconciles the project's known coefficient assumption with path-aware
profiling: unit prices are fixed inputs, while retry reach determines the
realized row-level charge that the search ledger and confidence procedure must
record.
