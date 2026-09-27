# Algorithm 2: adaptive similarity-annealed UCB

## Research question

The retry row is an ordered tuple of model choices, for example
`(small, strong, strong)`. Two rows are similar when they differ in only one
or two model slots. This is configuration similarity, not execution-prefix
reuse: every observed reward remains tied to the exact row and question that
was evaluated.

The proposed selector is `similarity_annealed_ucb`. It is a practical
combination of ideas from structured bandits, categorical Bayesian
optimization, and simulated annealing. It is an algorithm candidate, not yet
a theorem or a claim of a new general-purpose optimizer.

## Method

1. Build a Hamming graph over complete retry rows. An edge joins two rows that
   differ in one of the three model-choice slots.
2. When a cell `(row, question)` is pulled, store its reward and realized
   input-token cost. For an unpulled row on that same question, estimate the
   reward with an exponential Hamming kernel over already observed rows.
3. Learn a separate trust weight for each retry slot. If rows that differ in
   slot 1 disagree repeatedly on the same questions, distance in slot 1 is
   increased. This prevents the method from treating every model change as
   equally safe to share.
4. Use an optimistic score, `mean + beta * uncertainty`, with a small penalty
   for rows whose observed cost estimate is high. The cost estimate is formed
   only from already pulled cells; the policy never peeks at an unpulled cost.
5. Select candidate cells using a temperature that decreases with the search
   budget. Early pulls sample graph neighborhoods broadly; later pulls focus on
   high-scoring candidates. This is the simulated-annealing part of the
   method.
6. At the end, recommend the row with the highest similarity-smoothed mean,
   even if that row was not directly pulled. The held-out evaluator then runs
   that exact row normally.

The implementation uses the same cell-fraction settings as the other
selectors, so each `(algorithm, fraction, seed)` is a separate report entry.
It returns the recommendation basis so we can distinguish a directly observed
winner from a posterior recommendation.

## Why this may help here

Independent-arm UCB spends evidence separately on all `9^3 = 729` rows. The
new selector can use a strong observation for `(A, B, C)` to prioritize nearby
rows such as `(A, B, D)` on the same question, while the learned slot weights
can stop that transfer when a slot is empirically decisive. The method does
not assume that changing the first attempt is equivalent to changing a retry,
and it never treats a suffix as a standalone workflow.

The key risk is the smoothness assumption. If nearby rows have unrelated
performance, smoothing can be worse than random search. That failure is part
of the experiment, not something to hide.

## Required ablations

The paper should report at least:

- adaptive slot weights versus fixed unit Hamming weights;
- true row graph versus a randomly permuted graph;
- kernel transfer versus independent-arm UCB;
- annealing enabled versus greedy UCB;
- cost penalty enabled versus reward-only acquisition;
- direct-only recommendation versus posterior recommendation.

For each setting, report held-out accuracy, realized search cost, search cell
count, cost savings against exhaustive search, and the fraction of selected
rows that were not directly evaluated. Use the 200-question search split only
for selection and the separate 200-question evaluation split only afterward.

## Prior art and positioning

SMAC established model-based algorithm configuration for categorical
parameters and instance sets. COMBO models categorical/ordinal combinatorial
spaces with a graph kernel. GRUB and related graph-bandit work use similarity
graphs for pure best-arm identification. BOHB combines Bayesian modeling with
bandit-style resource allocation. Our setting differs in that each row is a
retry-aware workflow, each question produces a separate cell with early
termination, and the profiling ledger charges the realized input-token cost
of every reached call. The proposed contribution is the question-conditioned,
trust-adaptive graph transfer plus annealed cost-aware cell allocation for
this retry-aware matrix; it should be presented as an empirical algorithmic
contribution until a formal guarantee is developed.

## Current implementation

The selector is in `src/retry_search/selection_sweep.py` under
`similarity_annealed_ucb`. Its tests use a synthetic smooth Hamming landscape
and verify that it can recommend a row from side information without
duplicating cells. The full nine-model trace currently running was started
before this selector was added; it will be replayed with Algorithm 2 after the
trace completes, without rerunning model calls.
