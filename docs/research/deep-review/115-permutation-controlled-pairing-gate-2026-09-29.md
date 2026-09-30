# 115: Permutation-controlled pairing gate (2026-09-29)

The EGCR gate should test whether a candidate edge benefits from pairing on the
same question, rather than merely observe that one pilot block happened to be
easy. A simple, reproducible diagnostic is available once both complete rows
have been paid on the pilot questions.

## Statistic

For edge `e=(a,b)` and pilot block `P`, compute

\[
v_{\mathrm{pair}} = \operatorname{Var}_{q\in P}(Y_{bq}-Y_{aq}),
\qquad
v_{\mathrm{ind}} = \operatorname{Var}_{q\in P}(Y_{aq})+
                    \operatorname{Var}_{q\in P}(Y_{bq}).
\]

The observed pairing gain is

\[
g_e = 1 - v_{\mathrm{pair}} / \max(v_{\mathrm{ind}},\epsilon).
\]

This is a variance diagnostic, not a quality estimate. It says that the same
question makes the *difference* easier to estimate; it does not say that either
row is accurate or that one row is better.

## Null control

Within the pilot block, repeatedly permute the question labels of row `b` while
leaving row `a` fixed and recompute `g_e`. The resulting null distribution asks
how often the observed gain would appear if the two rows did not share
question-aligned variation. Use a predeclared lower quantile of the gain (or a
one-sided permutation p-value) and a multiplicity correction across all tested
edges. A row pair passes only if:

1. the cross-fitted lower confidence bound for `g_e` exceeds the registered
   minimum gain;
2. the reserved complete-cell cost of paired racing is lower than the direct
   comparison alternative; and
3. the result remains positive under the permutation control.

The question labels and all pilot outcomes are frozen before this decision.
The racing fold cannot update the edge list or threshold. For finite MathQA,
the permutation is a diagnostic over the registered pilot bank, not a claim
about arbitrary future questions.

## Failure cases

- If the rows have different marginal means but no shared difficulty pattern,
  `g_e` can be near zero; the gate should fall back to direct racing.
- If both rows are nearly constant, `v_ind` is near zero and the ratio is
  unstable; reject the edge unless a predeclared absolute-width test passes.
- If retry reach changes which questions produce a final outcome, the pilot
  must use the complete execution ledger. Treating an unexecuted suffix as a
  zero reward creates spurious pairing gain.
- If the pilot questions are selected by observed cost or correctness, the
  finite-bank target changes. Use a fixed outcome-independent permutation.

This gives EGCR an interpretable gate and a negative control without workflow
prefix reuse. It is still a proposed protocol: implementation and equal-dollar
evaluation are pending, and the permutation test itself does not establish a
new theoretical bandit class.
