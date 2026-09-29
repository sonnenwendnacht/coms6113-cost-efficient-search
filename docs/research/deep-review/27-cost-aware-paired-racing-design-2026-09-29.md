# Cost-aware paired racing design (2026-09-29)

This is a candidate design assembled from the audited methods. It is not an
experiment, theorem, or novelty claim, and no model calls were made.

## Candidate method: CAPR

**Cost-aware Paired Racing (CAPR)** treats each complete `(row, question)` run as
the paid unit. It precommits a random question permutation for every direct-row
stream and for every paired leader–challenger stream. A paired stream evaluates
two complete rows on the same question and records the difference in final quality.

The method keeps time-uniform finite-population confidence sequences for direct row
means and paired differences. A small registered calibration stage estimates
charges and the variance of each pair; these estimates only guide allocation.
At each step it selects the complete row or pair that promises the largest
reduction in the current leader/challenger uncertainty per reserved charge. A row
is eliminated only when a simultaneous confidence sequence proves it is worse by
the registered tolerance. The final recommendation receives a fresh direct
confirmation block. Every action passes the admission check

`spent + reserved + maximum_new_action_charge <= budget`.

## Why this is a useful research target

The confidence argument can be made transparent by combining finite-population
sampling-without-replacement confidence sequences with a union budget over all
registered streams and prefixes. The paired variance can be much smaller when
question difficulty affects two rows similarly, while a cost-aware score avoids
spending those paired evaluations on cheap but already-separated rows. If the
same-question covariance is weak or negative, the method should fall back toward
independent row streams.

This is not a new building block by itself. Covariance-adaptive BAI, CRN ranking,
and cost-aware acquisition each predate it. A defensible contribution would have
to show that this particular complete-retry-row protocol handles heterogeneous
realized path charges and answer-key-blind checker control better than those
baselines at equal search cost, or prove a new instance-dependent complexity
bound. Until then CAPR is a transparent baseline/design target rather than a
claimed novel algorithm.

