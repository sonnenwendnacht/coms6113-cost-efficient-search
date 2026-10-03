# Constrained-BAI audit: cost dependence is already covered

Prepared 2026-09-29 from the official NeurIPS 2025 abstract for [Constrained
Best Arm Identification](https://proceedings.nips.cc/paper_files/paper/2025/hash/917373186cceb7efe90742ea8a51ca78-Abstract-Conference.html).
No experiments or local traces were used.

## Verified overlap

Lardy, Katsimerou, and Koolen define each arm as a joint distribution of a
quality reward and a cost, allow the two to be dependent, and seek the highest
mean reward among arms whose mean cost is below a threshold. They give lower
bounds for fixed-covariance Gaussian, unknown-covariance Gaussian, and
nonparametric rectangular-support models, and give sampling/stopping rules
matching those complexities for the corresponding models.

A complete retry row collapsed to one indivisible pull produces exactly a
joint observation `(Y(c,q), K(c,q))`. Therefore these ingredients are already
covered at the arm level:

- realized cost can be random;
- cost can be correlated with correctness;
- a deployment cost cap can be expressed as a mean-cost feasibility
  constraint;
- the selector can use a fixed-confidence sampling/stopping rule.

The project's central claim must not be “we are the first to handle cost that
is correlated with success” or “we are the first to optimize accuracy under a
cost cap.” Those statements would ignore this prior work and Li--Cheung's
resource-constrained BAI model.

## Remaining distinction

The constrained-BAI model chooses one arm per round and observes that arm's
reward/cost pair. It does not provide same-question observations of two rows,
paired differences whose variance depends on shared task difficulty, or a
stateful retry execution whose later calls depend on previous generated
outputs. It also does not give a free observation of an unpulled neighbor.

A legitimate extension would have to make the observation action itself
richer: on one question, the evaluator may run two complete rows and pay both
realized charges. The potential gain is then a reduction in the variance of a
**comparison**, not a reduction in the cost of a row pull. Any proof should
reduce to constrained BAI when paired actions are disabled and to covariance
adaptive BAI when costs are ignored.

## Consequences for our paper

1. Treat constrained BAI as a mandatory baseline if deployment cost is a
   constraint. Its cost/reward dependence is not optional background.
2. Keep the main fixed-budget experiment separate from constrained selection.
   “Quality at profiling dollars” and “best quality subject to a cold-cost
   cap” are different targets.
3. If we present a paired/direct extension, compare its sample complexity or
   matched-dollar selection quality against a direct constrained-BAI rule.
4. State that the remaining gap is conditional: complete retry-row
   observations with same-question cross-row covariance and path-dependent
   charge, under a valid block/optional-stopping design. A source search and a
   theorem review are still required before claiming priority.
