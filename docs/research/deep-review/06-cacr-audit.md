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

The recent [Generative Proxy BAI](https://arxiv.org/abs/2607.06879) paper is a
close control-variate precedent. Treating an already measured neighboring row
as a proxy may be useful, but it must be compared with that framework and must
account for the proxy's own full-cascade cost.

A safer successor worth testing is a gated version, tentatively SCCR
(safe-cost correlated racing): use a neighbor's paired allocation only after a
calibration block gives a conservative positive lower bound on variance
reduction; otherwise use a random/direct proposal. This may protect against
the iid and permuted-graph cases, but it is not implemented or theoretically
validated yet.

## Precise target problem

Let `Q` be a question drawn from the deployment distribution and let `c` be a
complete ordered model assignment for every solver/retry slot. One full
evaluation returns two linked observations:

```text
Y(c, Q) = final workflow outcome, scored later by the answer key
C(c, Q) = realized input-token charge for every reached solver/verifier call
```

The search policy may choose the next complete row and question adaptively,
but it must pay newly executed calls and may not read answer keys. It must
recommend one complete row after a profiling budget `B`; deployment quality is
`E[Y(c,Q)]`, while `E[C(c,Q)]` is reported separately or constrained by a
pre-registered deployment cap. Similarity is an unknown property of the
question-level outcomes, such as the covariance of `Y(c,Q)` and `Y(c',Q)` for
one-slot neighbors. A neighboring row is not an exact cache hit, and an
unreached retry is not a failed outcome.

This definition makes the possible contribution testable. Existing methods
cover ordinary arm costs, paired/common-random-number scores, graph-smooth
means, and cheap proxies. The remaining question is whether the endogenous
cost of a complete retry cascade changes the best allocation once those
baselines receive the same trace engine and cache permissions.

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

In the smooth generator at cap 200, randomly permuting the row slots before
CACR proposals reduced audit accuracy from `0.796` to `0.764` (50 seeds), but
it remained above random (`0.626`). Because the selector has a restart floor
and direct row evidence, this is only a partial graph ablation; the real study
must also report the restart rate and the same control with restarts disabled.

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
