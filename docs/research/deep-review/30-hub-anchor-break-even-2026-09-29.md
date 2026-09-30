# Hub-anchor break-even analysis (2026-09-29)

Research-only derivation. No experiments, traces, replays, or model calls were
used.

## What the hub actually saves

Suppose a leader row `l` is compared with `m` challengers on a fresh block of
`n` questions. If every comparison uses a fresh same-question block, the
leader's cells are paid once per challenger, so the rough charge is

```text
n * sum_i (K_l + K_{c_i}).
```

If a hub `h` is evaluated once on that block and its cells are reused for every
challenger, the rough charge is

```text
n * (K_h + sum_i K_{c_i}).
```

The gross saving is therefore approximately `n * (m K_l - K_h)`. A cheap hub
can be worthwhile when several challengers need to be screened, even though
every challenger still requires its own complete workflow execution. If the
hub is more expensive than the repeated leader, or only one challenger is
tested, there is no saving before statistical effects are considered.

This calculation assumes that the comparison block is registered in advance
and that the hub cells are retained. It is an API-call/accounting saving; it is
not workflow-prefix reuse and it does not make an unexecuted candidate cell
known.

## Finite-population estimator when the hub is complete

Let the registered search set contain `N` questions and suppose the hub has
been evaluated on all of them, so its finite-set mean `mu_h` is known exactly.
If candidate `c` is evaluated on a uniformly sampled subset `S_c` of size
`m_c`, then

```text
mu_hat_c = mu_h + (1/m_c) sum_{q in S_c} [Q(c,q) - Q(h,q)]
```

is unbiased for the candidate's finite-set mean. Its design-based variance is
approximately

```text
(1 - m_c/N) * S^2_{D_c} / m_c,
```

where `S^2_{D_c}` is the finite-population variance of the paired difference.
Positive question-level covariance can make `S^2_{D_c}` much smaller than the
candidate's marginal variance. This is the precise reason a cheap complete row
can be a useful control variate.

If the hub is observed only on the candidate subset, the hub mean is not known
and the difference estimates only `mu_c - mu_h`; add a direct hub estimate or
use a confidence sequence for the contrast and a separate interval for the hub.
Do not treat the same hub cells as independent evidence for every candidate's
absolute mean. For a future-task target, `mu_h` is also a sample estimate of a
population mean and needs its own task-distribution uncertainty.

## Statistical tradeoff

For a candidate `c`, use

```text
D_c(q) = Q(c,q) - Q(h,q).
```

The hub can reduce the variance of a candidate-vs-hub comparison when the two
rows succeed and fail on the same questions. Differences for two candidates
share the same hub outcome, so their estimates are dependent. A simultaneous
confidence allocation over all registered candidate streams is safe; treating
the candidate differences as independent is not.

An anchor is useful for screening, but its identity can distort the apparent
ordering. A row that is close to the hub may be easy to distinguish while two
rows that differ from the hub in the same direction remain hard to compare.
The method therefore needs a fresh direct confirmation block for the selected
row and at least one of:

* a second hub chosen before seeing the screening outcomes;
* a direct leader–challenger comparison on a new question permutation; or
* a transitive confidence certificate whose total error is allocated across
  both hub comparisons and the final recommendation.

The hub should be chosen from a registered cheap pilot or a cost-only prior.
Choosing it after inspecting the same screening outcomes is a selection bias.

## Relation to existing methods

This is a specialization of common random numbers and control variates to
complete retry rows with conditional charges. It should be compared with
ordinary synchronized pair racing, which pays both rows on every comparison,
and with a two-hub design. A positive result would support a narrow systems
claim: a paid cheap complete row can be reused as a common-question anchor for
many row-level comparisons under the retry cost ledger. It would not establish
novelty for paired evaluation, control variates, or cost-aware pure exploration
in general.
