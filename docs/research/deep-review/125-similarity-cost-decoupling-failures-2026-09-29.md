# 125: When similarity does not save profiling cost (2026-09-29)

Low paired reward variance is useful evidence for a comparison, but it is not
by itself evidence that the comparison is cheaper or that it estimates the
right target. Three small counterexamples should be registered before testing.

## 1. Identical rewards, unequal paths

Suppose rows `a` and `b` have `Y_{aq}=Y_{bq}` for every question, so the paired
residual variance is zero. Let `a` cost one unit per cell and `b` cost ten units
because its verifier reaches more retries. A paired block has perfect ranking
precision but still pays eleven units per question. If a direct incumbent is
already well estimated, the edge has no cost advantage. A gate based only on
residual variance would choose it incorrectly.

## 2. Cheap easy questions and expensive hard questions

Let half the questions be cheap and have zero row difference, while the other
half are expensive and have a nonzero difference. The full-bank mean can be
determined only by including both groups. A block chosen after observing cheap
cells can look extremely similar and stop early, even though the hard group
would change the winner. Fixed outcome-independent permutations or valid
inverse-probability weighting are required; a heuristic radius on the cheap
prefix is not enough.

## 3. Reward similarity but cost disagreement

Two rows can have the same final correctness pattern but different retry reach
on exactly the questions where the verifier is uncertain. Then the reward
comparison is easy while the charge forecast is wrong. A cost-aware gate needs
its own cost interval or deterministic reservation; reward residuals cannot
stand in for cost uncertainty.

## Gate consequence

For edge `e`, require two separate quantities:

```text
quality_gain_e = reduction in a valid paired confidence width
cost_gain_e    = direct-race reserved cost - paired-race reserved cost
```

Trust the edge only when the lower confidence bound for `quality_gain_e` is
positive **and** the lower bound for `cost_gain_e` is positive. If costs are
only observed after a cell completes, the second quantity is a realized-spend
diagnostic unless a hard per-cell upper bound was reserved. The gate should
also reject edges with an unstable cost distribution, even when reward
residuals are small.

This is a falsification criterion for Algorithm 2: if the hybrid wins only on
low-variance reward instances where `cost_gain_e <= 0`, its claimed cost
efficiency is unsupported.
