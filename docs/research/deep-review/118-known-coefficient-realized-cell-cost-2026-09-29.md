# 118: Known model coefficient versus realized retry-cell cost (2026-09-29)

## Code-level audit

The experiment metadata records a known coefficient for each model and charges

```text
sum(coefficient(model) * input_tokens(call))
```

with output tokens excluded and cache discounts disabled. That does **not** make
the full `(row, question)` price known before the workflow runs:

- the verifier prompt contains the generated candidate response;
- a retry prompt contains the previous response and verifier feedback;
- whether a retry is reached depends on the verifier result;
- generated length therefore affects the input-token count of later calls even
  though generated tokens themselves are not charged.

The runner computes `cost_usd` only after collecting the complete call ledger.
The source of truth is `scripts/run_experiment1_nine_model.py`, where
`run_workflow` appends every solver/verifier call and `primary_cost` multiplies
the measured input tokens by the model coefficient.

## Correct budget language

The experiment should say:

> Model coefficients are known before deployment; complete retry-cell costs are
> realized after the workflow path is observed.

It should not say that the complete row/question charge is known in advance
unless a separate tokenizer-based upper bound is proved and reserved. A mean
cost estimated from earlier questions is a forecast, not a hard cap.

This distinction matters for all selectors:

1. A realized-dollar replay may stop after the next complete cell crosses the
   target. Record the actual overshoot.
2. A safe hard-cap implementation must reserve an upper bound for every solver
   and verifier call that the retry policy could reach, including prompt-length
   limits and failure paths.
3. The coefficient can still be used for cost-aware ordering, but the ordering
   must not inspect an unpulled cell's realized token count.

The local 729-row run therefore supports an equal-realized-spend comparison,
not a claim that every method obeyed a strict dollar cap. This is consistent
with the CABAI audit in note 117 and the reservation protocol in note 98.
