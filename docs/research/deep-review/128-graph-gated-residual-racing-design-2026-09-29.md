# 128: Graph-gated residual racing design (2026-09-29)

The useful similarity signal is a relation between *complete rows*, not a
claim that a row's answer on one question reveals another row's answer. A
configuration graph can be built from one-coordinate mutations of the
solver/verifier/retry tuple. An edge is only a candidate for sharing
information; it is not permission to copy a reward or eliminate a row.

## Proposed Algorithm 2 shape

Call the method **graph-gated cost-aware residual racing (GCRR)** for now. For
row (i), question (q), record the terminal reward (Y_{i,q}) and the full
realized dollar charge (C_{i,q}) for the complete retry cascade. The target
for a finite registered question bank is

\[
\mu_i = N^{-1}\sum_q Y_{i,q}.
\]

For an edge ((i,j)), execute both rows on the same question block and form
the paired residual (D_{ij,q}=Y_{i,q}-Y_{j,q}). A direct row estimate and an
edge residual estimate are fitted on one question split. On a disjoint split,
check whether the residual is stable enough to use. Only a passing edge may
provide a prediction interval for an incompletely sampled row. A multi-edge
prediction uses the shortest path under the sum of edge uncertainty widths,
with a maximum path length; if no path passes the gate, the row must be sampled
directly.

At each round, keep an incumbent lower bound and challenger upper bounds. Buy a
common question block for the active rows or a gated edge pair according to
the largest expected reduction in the incumbent/challenger overlap per
estimated dollar. The selection rule is allowed to use similarity for
allocation and elimination, but the final recommendation is a directly
observed row (or a row with a clearly labeled provisional common-prefix
estimate). If a gate fails, discard its propagated interval and fall back to
ordinary complete-row racing.

## What is and is not new

Graph smoothness in best-arm identification is established prior art; see
[Best Arm Identification in Spectral Bandits](https://arxiv.org/abs/2005.09841)
and [Structured Best Arm Identification with Fixed
Confidence](https://proceedings.mlr.press/v76/huang17a.html). Graph-feedback
bandits also use known similarity relations, but a pulled arm reveals
neighbors' feedback in that model; our rows do not receive free neighbor
answers. Pairwise synchronized measurements are prior art in SySRs and
covariance-adaptive BAI. Cost-aware resource-rationed elimination is prior art
in [Li and Cheung's BAI with Resource
Constraints](https://proceedings.mlr.press/v238/li24c.html).

The defensible research question is therefore narrower: whether cross-fitted,
gated *paired residuals* can reduce complete retry-row purchases when (a)
configuration edges predict finite-bank reward differences, (b) every cell
has an endogenous, heterogeneous retry charge, and (c) similarity is used
only when its held-out edge test passes. The combination may still be an
engineering synthesis rather than a new theory; the novelty claim must wait
for a prior-art search and an ablation showing each gate matters.

## Conditions needed for a theorem

An initial theorem target should be conditional and modest:

* questions are a fixed finite bank sampled by a predeclared random
  permutation, and the recommendation target is the bank mean;
* rewards are bounded, and the cross-fitted edge residual interval has a
  simultaneous coverage statement over all registered edges and rounds;
* any propagated path has a valid union bound for its summed edge errors;
* the selected row has a complete direct observation or is labeled
  provisional; and
* a hard-dollar claim uses deterministic per-cell upper bounds and atomic
  reservations, while a realized-spend claim reports overshoot separately.

Under these conditions the proof can aim only at an epsilon-best observed row
or at safe elimination of a row whose upper bound is below the incumbent's
lower bound. It should not claim that the deployed best row is globally
optimal, that verifier passes equal gold correctness, or that similarity saves
money on every workload.

## Falsifiers and required ablations

The method should lose its advantage when one-coordinate changes interact
strongly, when edge residuals vary by question difficulty, when retry reach
changes the cost without changing reward, or when a cheap easy-question block
misleads the gate about expensive hard questions. Required controls are direct
paired elimination, ungated graph prediction, a gate trained and tested on
the same questions, and the cost-blind version. Report false eliminations,
held-out regret, total realized search dollars, overshoot, and deployment
cost separately.

No implementation or experiment is claimed by this note; it is a candidate
design and a list of conditions that can disprove it.
