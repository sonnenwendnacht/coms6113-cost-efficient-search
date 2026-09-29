# Hub-anchored Algorithm 2 protocol (2026-09-29)

This is a research design, not an experiment, theorem, or novelty claim. It
uses complete retry rows only; no workflow prefix or continuation is purchased.

## Objective

Given 729 complete rows and a registered search set of `N=200` questions, return
one row whose finite-search accuracy is high under a declared search-spend
limit. Let `Q(c,q)` be the offline final correctness and `K(c,q)` the realized
input-token charge. For benchmark profiling, `Q` is revealed after the paid
cell completes; held-out questions remain withheld until the recommendation
is frozen. A deployment-adaptive variant must replace `Q` with a permitted
runtime signal and is a separate, calibrated problem.

## Protocol

1. **Register the design.** Fix the question permutations, calibration and
   confirmation folds, row identifiers, confidence level, tolerance, charge
   reservation rule, and tie-breaking. Never choose questions after seeing a
   candidate's outcome.
2. **Choose a hub without the target outcomes.** Start with a cost-only or
   independently calibrated cheap row `h`. If a pilot chooses `h`, fit and
   choose it on one question fold and evaluate its screening role on a separate
   fold. Keep a second hub or direct-comparison fallback predeclared.
3. **Buy hub cells.** Evaluate `h` on the registered screening permutation and
   retain its complete cells and realized charges. If the hub covers the whole
   finite search set, its finite-set mean is known exactly; otherwise keep an
   interval for the hub mean.
4. **Screen candidates against the hub.** For a candidate `c`, evaluate its
   complete row on hub questions and form `D_c(q)=Q(c,q)-Q(h,q)`. Choose the
   next candidate/block by estimated confidence-width reduction per reserved
   charge, with a fallback schedule that eventually opens every candidate that
   remains plausible. Use finite-population paired confidence sequences for
   elimination, not a posterior point prediction.
5. **Eliminate conservatively.** Remove `c` only when its simultaneous upper
   bound is below the incumbent lower bound by the registered tolerance, or
   when a declared cost constraint is definitely violated. A weak or negative
   hub covariance must turn off transfer and revert toward direct independent
   row sampling.
6. **Confirm finalists.** On a fresh registered question block, compare the
   remaining leader and challengers directly or with a second hub. Preserve
   overlap covariance; do not treat shared hub differences as independent. Give
   the selected row a fresh direct confirmation before freezing the
   recommendation and then evaluate it on the hidden audit set.

Every action must satisfy the hard-cap admission check

```text
spent + reserved + maximum_new_action_charge <= budget.
```

If a maximum charge is unavailable, declare a soft cap and report overshoot.

## Why a hub may help

If `m` challengers would otherwise each be paired with a leader on `n`
questions, reusing one hub block saves roughly `n*(m*K_leader-K_hub)` in
reached-row charges. The statistical benefit is separate: the variance of
`Q(c,q)-Q(h,q)` can be much smaller than the variance of `Q(c,q)` when question
difficulty is shared. A hub never reveals a candidate's unexecuted answer and
does not make candidate calls free.

## Required baselines and falsification

Compare at equal realized search spend against uniform/random row allocation,
independent cost-aware BAI, ordinary synchronized paired racing that pays both
rows, PBGI/Gittins-style allocation, the mentor's GittinsEval setup where
applicable, and a two-hub control. Include a deterministic-cost control and the
actual path-dependent retry ledger. Measure selected-row audit quality, search
spend, cost overshoot, number of complete cells, and confirmation failures.

The idea is falsified as a useful contribution if the hub's residual variance
does not reduce enough to repay its cells, if a second hub/direct racing matches
it at equal spend, if anchor choice is unstable across folds, or if valid
intervals remain too wide to eliminate rows. A positive result would support a
narrow empirical claim about amortized complete-row comparisons under the
retry-cost protocol. It would not establish novelty for control variates,
common random numbers, correlated BAI, or cost-aware acquisition in general.
