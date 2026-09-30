# 129: CAET prior art and the context/cost gap (2026-09-29)

The prior-art boundary is narrower than the earlier notes suggested. Wu, Shi,
Zhou, and Shen's 2025 [Cost-Aware Optimal Pairwise Pure
Exploration](https://arxiv.org/abs/2503.07877) defines a general pairwise pure
exploration task with arm-specific costs and proposes CAET, an asymptotically
cost-aware track-and-stop method. Best-arm identification is one of its
special cases. We therefore must not claim that a cost-aware pairwise BAI
algorithm is new.

The paper's observation model still leaves a concrete gap for this project. It
assigns each arm a reward distribution and a cost distribution and samples the
two for an arm pull; its baseline formulation is arm-level, with an expected
cost (c_i). It does not model a finite question bank whose same question is
run under multiple complete configurations, nor a retry cascade whose realized
charge depends on the generated response and verifier path. It also does not
provide a cross-fitted test for whether an edge's paired residual remains
stable across question difficulty.

That gap does not make GCRR or CG-RTE automatically novel. It gives a precise
extension to test: **context-indexed pairwise pure exploration with
execution-dependent cell costs**. A defensible Algorithm 2 should:

* use a pre-registered row graph and outcome-independent question permutations;
* collect paired residuals only from complete row/question cells;
* maintain simultaneous intervals for an anchor row and edge residuals;
* use a graph path only to allocate or eliminate, never to treat an unpulled
  row as directly measured; and
* confirm the final recommended row on fresh complete cells.

If the graph edge is not cheaper to measure, has no lower residual variance,
and is not reused across enough target rows, an edge path can cost as much as
or more than directly measuring its endpoints. This is a structural
failure-case: graph similarity by itself is not a savings argument. The
experiment must compare against CAET-style cost-aware pairwise allocation,
direct synchronized elimination, and ungated graph prediction at equal
realized dollars.

The remaining novelty claim should therefore be phrased as a possible
contextual extension and systems evaluation, not as the first cost-aware
pairwise or graph BAI method. A theorem would need the finite-bank target,
simultaneous confidence over adaptive edge/path choices, a common question
design, and either deterministic cost reservations or an explicitly softer
realized-spend objective.
