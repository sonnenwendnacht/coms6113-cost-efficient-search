# Candidate theory problem: correlated resource-constrained BAI for complete rows

Prepared 2026-09-29 during the research-only window. This is a theorem
sketch and not a claim that the problem is unpublished.

## A clean reduction

Let `C` be the finite set of complete retry rows and let `q` be a random
benchmark question. One execution of row `c` returns

```text
Y_c(q) in [0,1]       final deployment-valid result
K_c(q) in [0,K_max]   realized charge for reached calls
```

The vector `(Y_c(q), K_c(q))_{c in C}` may have arbitrary dependence across
rows and between outcome and cost. The finite `K_max` is enforced by a
registered context/output limit; if it is unavailable, dollar constraints
cannot receive a finite-sample certificate and must be reported descriptively.

A direct action observes one row on a fresh question. A paired action observes
two complete rows on the same fresh question and pays both realized charges.
No action exposes a retry prefix or an unreached continuation. The goal is
fixed-confidence identification of an epsilon-best row under a profiling
resource budget, or, in the fixed-budget form used by our tables, minimizing
simple regret at a matched realized charge.

This reduction isolates the likely gap more precisely than “similar rows”:
we need best-row identification with (i) shared-question covariance, (ii)
random resource consumption that may be outcome-dependent, and (iii) a choice
between single-row and paired complete-row observations.

## Quantities that should drive the allocation

For an edge `e=(c,c')`, define the paired difference variance and expected
charge

```text
v_e = Var_q[Y_c'(q) - Y_c(q)]
k_e = E_q[K_c'(q) + K_c(q)].
```

For a direct row, use `v_c = Var_q[Y_c(q)]` and `k_c = E_q[K_c(q)]`. The
same-question action is useful only when its uncertainty per charge is better
than the corresponding direct comparison. Hamming distance is not a substitute
for estimating `v_e`, and a nominal model price is not a substitute for `k_e`.

A possible instance-dependent complexity term for a fixed-confidence theorem
would use the cheapest valid information route for every serious competitor,
for example

```text
H(e) = k_e * v_e / Delta_e^2
```

for paired edge `e`, compared with the direct route's analogous sum. This is
only a dimensional guide: a full result must handle unknown variances, edge
selection, and the fact that a row can participate in many comparisons.

## A validity-first algorithmic template

1. Before observing outcomes, choose a global question permutation, block
   sizes, an edge family, and an error allocation over rows and edges.
2. Maintain a confidence sequence for every direct row mean and every paired
   difference stream. Use bounded finite-population sequences when the target
   is the fixed benchmark population; use an iid sequence only when questions
   are sampled with replacement from the declared distribution.
3. Use a structural row model, a learned neighbor metric, or a Gittins/BO
   score only to rank the next actions. Its prediction cannot eliminate a row
   or certify an unobserved cell.
4. Select a complete direct or paired block by a conservative predicted
   uncertainty reduction per worst-case charge, while reserving a global
   restart fraction.
5. Eliminate a row only when a valid interval for its difference from a
   currently competitive row is below `-epsilon`. If paired evidence is not
   trusted, use the union of direct intervals.
6. For a deployment-cost constraint, maintain a separate confidence sequence
   for `E[K_c]` and reject a row only when its upper cost bound violates the
   cap. Do not infer feasibility from a plug-in mean plus a normal standard
   error after dollar-based optional stopping.
7. Return a directly observed row and use a fresh confirmation block before
   the held-out audit.

The algorithmic novelty, if any, would be in a proof that the paired/direct
choice preserves a delta guarantee while its complexity depends on both the
cross-row covariance and the realized resource process. The structural model
is an efficiency heuristic and should be removable without invalidating the
proof.

## Why the obvious proofs fail

- A fixed-sample variance estimate checked after every adaptive block is not
  a confidence bound under optional stopping. Use an anytime sequence or stop
  only at preregistered block boundaries.
- Selecting a pair after seeing one row's outcomes can make its subsequent
  cells conditionally selected. Use a global schedule, catch-up blocks, or
  disjoint cross-fitted blocks.
- Truncating a question stream when a dollar cap is reached can overrepresent
  cheap failures if success triggers a long retry. Admit complete blocks under
  a known worst-case envelope, or make the primary budget a cell/block cap.
- A graph path does not estimate an unobserved endpoint. Same-question
  residuals telescope algebraically but every intermediate row still costs a
  complete execution; independently sampled residuals do not telescope in
  variance.

## Prior-art boundary

Resource-constrained BAI already permits random resources correlated with
reward at an indivisible arm level ([Li and Cheung, AISTATS 2024]
(https://proceedings.mlr.press/v238/li24c.html)). Covariance-adaptive BAI
already uses same-time multi-arm observations ([Saad, Blanchard, and
Verzelen](https://arxiv.org/abs/2306.02630)). Cost-aware pairwise pure
exploration already studies arm-dependent pair costs
([Wu et al., ICML 2025](https://proceedings.mlr.press/v258/wu25c.html)), and
Hybrid Feedback already allocates between absolute and pairwise feedback under
known action costs ([Zeng et al.](https://arxiv.org/abs/2605.05745)). Price of
Knowledge further develops cost-adjusted information measures for correlated
actions with heterogeneous observation costs ([Schur, Lago, and Fiez, UAI
2026](https://proceedings.mlr.press/v337/schur26a.html)). The candidate gap is
therefore even narrower: a joint complete-retry-row reduction with
same-question paired outcomes and a realized reward/charge process, not any
one of these ingredients.

The theorem target should therefore be stated conditionally and modestly:
under bounded complete-row charges and a declared question-sampling design,
prove a cost bound or epsilon-good selection guarantee for an adaptive mix of
direct and same-question paired row blocks. If the proof is too broad, the
empirical paper can still evaluate whether the complexity proxy predicts
when pairing saves money, while reporting the method as a cost-aware
allocation heuristic.

## Evidence needed before a novelty claim

The planned study must compare the candidate with direct resource-aware BAI,
GittinsEval, AgentOpt selectors, SySRs-style synchronized pairing,
CACR/SCCR, and unstructured random allocation. It must include smooth,
iid, anti-correlated, stratum-reversal, and nonlinear retry controls. The
primary claim should be a matched-profiling-charge reduction in the
probability of selecting an epsilon-good complete row. A source search and
formal proof review must precede the words “new algorithm” or “first.”
