# Algorithm 2 candidate: graph-residual cost-aware racing

Status: implementation candidate and research hypothesis, 2026-09-27. This
note does not claim a theorem, a publication-level result, or superiority on
MathQA.

## The central idea

Represent each complete retry workflow as a vertex. Connect two vertices when
one model choice differs in exactly one ordered slot. A similarity edge does
not make the rows interchangeable and does not reuse a prefix. It only says
that we should try to measure the two rows on the same questions, because the
difference may be easier to estimate than two separate accuracies.

For rows `a` and `b`, and a uniformly sampled question `q`, record

```text
D_ab(q) = Y_a(q) - Y_b(q),   where Y is the final 0/1 score.
```

The row means obey the identity

```text
mu_a = mu_b + E[D_ab(q)].
```

If the same question is used for both rows, question difficulty cancels in
the difference whenever the rows agree. An anchor row can therefore be
measured on a wider question sample, while candidate rows spend calls on the
anchor's already measured questions. This is the useful case: the residual
has low variance even though the two absolute accuracies may vary greatly
with question difficulty.

## Allocation rule in the prototype

1. Choose an anchor row and a random question order before observing outcomes.
2. Spend an initial part of the cell budget on the anchor.
3. Construct the one-slot Hamming graph over complete rows.
4. For an edge, prefer questions already measured for either endpoint. Pull
   the missing endpoint, then store the paired residual. Each edge has its own
   pre-shuffled question order; the order is never changed after seeing a
   score.
5. Estimate a candidate through a path of measured edge residuals from the
   anchor. The prototype chooses the next edge by residual uncertainty per
   observed pair cost, with a small random reserve for leaving a bad local
   region.
6. If the whole matrix is paid for, discard all residual estimates and choose
   the exact direct row mean. This preserves the exhaustive reference.

The implementation is `graph_residual_racing` in
`src/retry_search/selection_sweep.py`. Its reported search cost is the sum of
the actual pulled cell costs. An unpulled cell's cost is never read by the
selector.

## What is valid without an extra smoothness assumption

For a fixed edge whose questions are a uniform random sample, the residual
mean estimates `mu_a - mu_b` without assuming that a one-slot change has a
small effect. If the rows are measured on the same question, the finite
population variance is governed by the residuals rather than by the two
absolute scores. This is a variance-reduction opportunity, not a guarantee.

Adaptive stopping requires a time-uniform or fixed-design confidence rule;
an ordinary fixed-sample interval is not automatically valid after repeatedly
looking at the results. The next version should use simultaneous
finite-population bounds for every registered edge and sample count. The
current prototype uses a heuristic uncertainty score for allocation and must
not be described as fixed-confidence best-arm identification.

## Why this is not automatically novel

Paired residuals are closely related to common-random-number comparisons and
to covariance-adaptive best-arm identification. Covariance-adaptive BAI
explicitly uses same-round observations and the variance of arm differences;
its formal assumptions and guarantees must be compared before making a
novelty claim. Graph kernels, structured BAI, transductive experimental
design, and resource-constrained BAI also cover important pieces of this
idea. The possible gap is narrower: in this project the graph vertices are
complete retry rows, each cell can terminate early, and the measurement price
is a realized input-token ledger. The anchor is itself costly and its mean is
not known for free, unlike a cheap external proxy. Those differences need an
explicit model and controlled experiments; they do not establish novelty by
themselves.

Primary comparisons to audit:

- [Covariance-adaptive best arm identification](https://proceedings.neurips.cc/paper_files/paper/2023/file/e82ef7865f29b40640f486bbbe7959a7-Paper-Conference.pdf), which uses pairwise residual variance under simultaneous arm queries;
- [COMBO](https://proceedings.neurips.cc/paper/2019/hash/2cb6b10338a7fc4117a80da24b582060-Abstract.html) and [GRUB](https://proceedings.neurips.cc/paper_files/paper/2022/hash/0d561979f0f4bc6127cfcfe9c46ee205-Abstract-Conference.html), which use graph structure for categorical/combinatorial search or best-arm identification;
- [Best Arm Identification with Resource Constraints](https://proceedings.mlr.press/v238/li24c.html), for random cost/resource accounting;
- the mentor's cost-aware language-model evaluation method and SySRs, for the same-question matrix and unequal pull-cost setting.

## Required evaluation

The held-out 200-question audit set remains untouched during selection. At
each budget, report accuracy of the finally recommended complete row, actual
search cost, number of paid cells, and the cold deployment cost of the
recommendation. Compare:

- independent random, uniform-cell, matrix-UCB, Bayesian optimization, and
  the original similarity-annealed prototype;
- graph-residual racing with and without shared-question pairing;
- true Hamming edges versus a permuted graph;
- one anchor versus several fixed random anchors;
- residual variance divided by pair cost versus reward-only acquisition;
- direct-only recommendation versus path-based recommendation;
- full-matrix reference on small spaces.

The synthetic check currently favors the original kernel prototype on the
handcrafted smooth landscape (`0.862` versus `0.662` mean latent reward over
20 seeds at a 10% cell fraction). That is a useful negative result: the
paired method is not ready to replace the baseline, and its failure mode must
be understood before running the expensive nine-model trace.
