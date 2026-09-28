# CACR audit: new literature boundary and controls

Prepared 2026-09-28. This is a research record, not a novelty or performance
claim.

## What the additional reading changes

The closest new prior art is **Best Arm Identification in Generalized Linear
Bandits via Hybrid Feedback** ([Zeng et al., 2026](https://arxiv.org/abs/2605.05745)).
It allows an algorithm to choose either an absolute arm observation or a
pairwise observation, gives them different acquisition costs, and uses a
cost-normalized Track-and-Stop rule. This rules out claiming that “choose
paired versus direct evaluations by information per dollar” is new on its own.
Our setting differs only if the distinction is made explicit and measured: a
pairwise comparison here runs two complete retry cascades on the same question;
each cascade can terminate early, so its realized cost is jointly distributed
with its score and is not a cheap dueling query from a shared generalized
linear model.

Other boundaries are equally important:

- Common-random-number ranking and selection already uses correlated
  alternatives and covariance-aware allocation.
- Correlated-arm best-arm identification already gives sample savings when a
  conditional correlation model is available.
- Spectral best-arm identification already studies graph-smooth arm means.
- Resource-constrained and cost-aware best-arm identification already handle
  arm-dependent or random sampling costs.

The remaining candidate contribution is therefore narrow: an empirical or
eventual theoretical treatment of **full-row, outcome-dependent retry costs
under same-question correlated comparisons**, with a safe fallback when the
Hamming similarity assumption fails. We should not describe this as a new
bandit primitive until a formal reduction shows why the existing models do not
cover the chosen workflow semantics.

## CACR prototype

The prototype in `src/retry_search/cost_aware_correlated_racing.py` does the
following:

1. Scouts a few complete rows.
2. Proposes one-slot neighbors plus a random-restart floor.
3. Creates one random question permutation per pair before seeing outcomes and
   consumes only its prefix on later blocks.
4. Stores same-question score differences and predicts endpoint cost only from
   observed reached calls.
5. Chooses the next block using an empirical uncertainty-reduction-per-cost
   score, with no graph-path estimator.
6. Returns a directly observed incumbent; final fresh confirmation remains a
   separate operation.

The radius is deliberately heuristic. It is not a fixed-confidence guarantee.
The implementation accepts explicit row slot tuples so a shuffled or
noncanonical configuration ID cannot silently change the neighborhood.

## Synthetic checks

The benchmark uses 27 rows, 50 search questions, 200 independent audit
questions, and 50 seeds. Search methods receive a realized-cost cap; the
smooth generator makes high-quality rows more expensive, so accuracy and cold
deployment cost must be read separately.

| Cap | Random audit accuracy | CW-PLR | CACR |
| ---: | ---: | ---: | ---: |
| 100 | 0.454 | 0.588 | 0.745 |
| 200 | 0.626 | 0.618 | 0.796 |
| 400 | 0.801 | 0.723 | 0.861 |

An iid negative control removes row locality. At 135 cells the audit means
were 0.597, 0.597, and 0.596 for random/CW-PLR/CACR; at a matched cost cap of
170 they were 0.596, 0.598, and 0.596. These are debugging results from an
invented generator, not evidence of a MathQA improvement. The iid control and
a permuted-neighborhood control are required in the real study.

## Existing pilot trace

The completed local pilot `results/runs/exp1-local-20260924` contains 27 rows
and 30 questions per row (20 search and 10 audit). Running
`scripts/diagnose_trace_locality.py` gave:

| Hamming distance | Pairs | Mean squared score difference | Mean correlation |
| ---: | ---: | ---: | ---: |
| 1 | 81 | 0.116 | 0.775 |
| 2 | 162 | 0.220 | 0.581 |
| 3 | 108 | 0.317 | 0.404 |

This is the first descriptive signal from actual workflow traces that one-slot
rows may be more correlated on the same question. It is not a confirmatory
result: the pilot is small, the rows use only three local models, and its
question split is too small to support a powered comparison. The diagnostic
must be rerun on the completed 400-question experiment and kept separate from
any tuning data.

## Required next test

Implement or reproduce a cost-aware absolute/pairwise hybrid baseline, then
compare it with uniform paired elimination, SySRs, AgentOpt's selector, and
CACR on the same trace engine. Use search questions only for allocation and a
fresh audit split for the recommendation. Report search cost, audit quality,
and cold deployment cost separately. If CACR does not beat the close
baselines beyond seed and audit uncertainty, keep the negative result and
reframe the project around measurement of when retry-row similarity helps.
