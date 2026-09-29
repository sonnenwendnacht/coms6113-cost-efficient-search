# Hub amortization and baseline accounting (2026-09-29)

This note is a research-only accounting check. No experiment, replay, or model
call was launched.

## A hub is not automatically a saving

Suppose `m` candidates each need a same-question comparison on `n` questions.
Let `k_h` be the hub's mean complete-row charge and `k_c` a candidate charge.
A protocol that measures the hub once and every candidate once costs roughly

```text
n * k_h + n * sum_c k_c.
```

Comparing every candidate to a freshly rerun leader costs roughly

```text
n * sum_c (k_leader(c) + k_c).
```

The apparent saving `n * (m*k_leader - k_h)` exists only if the baseline is
forbidden from reusing its leader. A fair incumbent-racing baseline can cache
the leader's already-paid cells, reducing its charge to the same order as the
hub protocol. The hub method then needs a statistical advantage (lower
same-question difference variance, wider coverage, or fewer confirmation
blocks) to win. Report both baselines:

1. **fresh-comparator baseline:** intentionally no row reuse, useful as a
   diagnostic of pure amortization;
2. **cached-incumbent baseline:** reuses paid cells under the same ledger and
   is the primary fair comparison.

If the hub is chosen as the cheapest row, its cost is not free. If it is
chosen after a pilot, include the pilot and calibration charges in the hub
ledger and use a separate fold for evaluating its screening benefit.

## A conservative break-even test

Let `r_h` be the expected number of candidate blocks that can reuse the hub,
`v_pair` the variance of a hub-candidate difference, and `v_ind` the variance
of a comparator difference without the shared question. Let `n_ind` and
`n_pair` be the required samples at the registered confidence/tolerance. A
hub is useful only if its total charge, including calibration and confirmation,
satisfies

```text
calibration_h + n_pair * (k_h + sum_c k_c / r_h)
  <  n_ind * cached_baseline_charge
```

This is a planning inequality, not a theorem: `n_pair` must come from the
actual registered confidence procedure, and the cost terms must be measured
under the same retry/checker semantics. If the candidate-hub covariance is
weak, `n_pair` approaches the independent requirement and the hub can lose
even when its row is cheap.

## Required baseline controls

The comparison matrix should include:

- independent direct allocation with a cached incumbent;
- synchronized pairing with a cached incumbent;
- one fixed cost-only hub;
- a pilot-selected hub with cross-fitting;
- a two-hub control, to test whether one anchor is brittle;
- fresh-comparator pairing only as an upper-bound diagnostic.

All methods receive the same registered question blocks, hard/soft cap rule,
and direct final confirmation. Every reused cell is logged once per method
ledger. A method cannot claim a saving merely because it was replayed after
another method and inherited an in-memory answer.

## Consequence for the claim

The strongest defensible claim is conditional: a registered hub can reduce
the *total cost of reliable row selection* when its shared-question covariance
reduces the number of candidate blocks enough to repay its own charge and
when it beats a cached-incumbent baseline. The weak claim “one cheap row can
be reused for many candidates” is an accounting identity and is not novel by
itself.

