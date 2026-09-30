# Measuring row similarity before using it

A row's Hamming distance is metadata. It is not evidence that two complete retry
rows behave similarly on questions. The measurable quantity for paired search is
the variance of their final-outcome residual

```text
D_ab(q) = Y(a,q) - Y(b,q).
```

A low residual variance means that common-question evaluation can distinguish the
pair efficiently. It does not mean either row's unobserved cells can be filled in.

## Edge-validation protocol

1. Register all row IDs, explicit slot coordinates, candidate Hamming edges, a
   random-edge control, and independent question permutations before observing
   outcomes. The edge registry is part of the multiplicity correction.
2. Run a small complete-row pilot on synchronized search questions. For every
   observed pair, estimate residual variance and the realized cost of missing
   endpoint cells. Keep a separate cost estimate for each endpoint; a row mean is
   not a hard charge bound.
3. Rank candidate comparisons by a conservative estimate of uncertainty reduction
   per **new** complete-row dollar. A useful heuristic is residual width divided
   by predicted new charge; a principled allocation should derive this from the
   chosen confidence-radius reduction. If cost and residual variance are
   uncertain, use upper cost and lower information estimates and fail closed.
4. Use a fresh, pre-shuffled question block for selected comparisons, or use a
   cross-fitting split. Do not select an edge and then certify it only on the
   same pilot residuals without accounting for adaptive selection.
5. Require direct complete-row confirmation of the recommended row. A path of
   edge differences is never a free observation of an unpulled row.

For an anytime confidence contract with `S` registered row/pair streams, a
possible error allocation is

```text
alpha_(s,n) = 6 delta / (S pi^2 n^2),
```

combined with a valid bounded without-replacement or martingale confidence
sequence. This is a bookkeeping template, not a proof for the current
prototype. Fixed phase sizes can instead use a preregistered union bound.

## Why cost-aware question choice is dangerous

Suppose hard questions cause both more retries and more failures. Selecting the
next question because its predicted charge is low over-samples easy questions;
selecting it because it is uncertain may over-sample hard questions. The raw
mean then targets a cost-weighted or selection-weighted question distribution,
not the uniform MathQA search-bank mean. Valid options are:

- keep a uniform outcome-independent question permutation and let cost affect
  only the number of completed blocks;
- use known inclusion probabilities and an inverse-probability estimator; or
- explicitly redefine the estimand as cost-weighted and report that choice.

A confidence sequence can make optional stopping safer, but it does not repair a
changed sampling distribution. This distinction applies to both graph edges and
factorized models.

## Recommended similarity diagnostic

Before claiming a structural gain, report residual variance and covariance by
Hamming distance and against a permuted-slot control, using the same question
blocks and equal realized dollar accounting. A useful result would show that
one-slot edges have lower residual variance **and** that the edge-aware selector
reaches better held-out row identification at equal spend. If only the first
pattern appears, it is a measurement observation. If only local proposals help,
call the benefit search locality rather than variance reduction. If neither
survives permutation, remove similarity from Algorithm 2.

This protocol keeps the strongest defensible use of similarity—better allocation
of paid complete-row comparisons—while avoiding workflow-prefix reuse,
answer-key leakage, and unregistered selective comparisons.
