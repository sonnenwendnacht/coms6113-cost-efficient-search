# Algorithm 2 candidate: cost-weighted pairwise local racing

Status: design and audit note, 2026-09-28. This is not a publication claim or
an empirical result.

## Problem

Each complete retry workflow is one configuration. A configuration is a tuple
of model choices for all ordered solver and retry slots. A search evaluation
chooses one configuration and one benchmark question, runs the full workflow,
records the final answer-key-blind verifier result, and charges the actual
input-token cost of every solver and verifier call that was reached.

The selector must recommend one complete tuple. It may use similarity between
tuples to decide what to test next, but it may not treat a nearby tuple as an
exact cache hit or reuse a workflow prefix.

## Proposed procedure

Call the method **Cost-Weighted Pairwise Local Racing (CW-PLR)**. It combines
categorical local search, simulated-annealing restarts, and a paired
sequential comparison:

1. Choose a random complete row as the incumbent and evaluate a small direct
   block of search questions.
2. Propose a one-slot Hamming neighbor. With a cooling probability, propose a
   uniformly random complete row instead, so an incorrect local neighborhood
   cannot trap the search forever.
3. When a race starts, draw a fresh random permutation of the *entire* search
   question set before seeing any outcome from that race. Evaluate incumbent
   and challenger on prefixes of the same permutation. A previously observed
   row/question cell may be reused as an exact value; no prefix, model output,
   or verifier state is reused.
4. Let `D(q) = Y_challenger(q) - Y_incumbent(q)`. After each paired block,
   update a time-uniform confidence interval for `E[D]`. Stop a losing race
   when its upper bound is below a practical margin; promote the challenger
   when its lower bound is above that margin.
5. Select the next block size using expected interval-overlap reduction divided
   by predicted *new* realized input-token cost. The prediction uses only
   prior calls. The selector records actual cost and any final block overshoot.
6. Reserve a fixed fraction of pulls for direct rows or global random proposals.
   Before reporting a winner, evaluate the finalist on a fresh confirmation
   block and report its direct accuracy and interval.

The primary objective is held-out accuracy. Search cost is the profiling
expense reported beside it; it is not silently subtracted from accuracy. A
separate Pareto or scalarized objective can be added only as a preregistered
variant.

## Why the graph is only a proposal mechanism

A path of residuals is not a free estimator. If all edges use the same
questions, the residuals telescope question by question to the direct
endpoint difference while intermediate rows add paid calls. If edges use
separate question samples, path variance is the sum of edge variances after
allocation; at equal per-cell cost, a direct paired endpoint comparison is at
least as efficient absent a cheap proxy or an amortization benefit across many
targets. The Hamming graph is therefore used to propose likely useful local
comparisons, not to claim that a path reveals an unmeasured row.

This separates two hypotheses:

- **Search-locality hypothesis:** one-slot changes are more likely than random
  changes to produce a promising challenger.
- **Measurement-similarity hypothesis:** one-slot changes have lower
  same-question residual variance than random row pairs.

Both must be measured. A permuted graph, random-pair racing, and global-restart
rate ablations are required. If locality helps but residual variance does not,
CW-PLR can still be useful as a proposal heuristic; if neither helps, remove
the graph.

## Statistical and implementation guardrails

- Race question permutations are fixed at race creation and are independent of
  the prior outcomes. A race uses a prefix; it does not skip difficult-looking
  questions or select only cells that remain unseen.
- If a globally synchronized block is used instead, a newly admitted row must
  catch up on all earlier blocks before it is compared. Selecting only the
  questions left after outcome-dependent admission is biased.
- Paired intervals must use a time-uniform or preregistered finite-population
  bound. A fixed-sample interval is not valid after repeatedly checking it.
- The direct confirmation row must itself be evaluated on held-out-from-search
  questions. A small confirmation block is evidence, not an exhaustive proof.
- Cost estimation never reads an unpulled cell. A missing later retry is not a
  failed response; the full workflow's observed final score is the outcome.
- The search split and audit split are disjoint. The audit split never tunes
  temperature, confidence, margins, block sizes, or graph weights.

## Prior-art boundary

One-change categorical local search and same-instance racing are already used
by [ParamILS](https://www.cs.ubc.ca/labs/algorithms/Projects/ParamILS/papers/09-JAIR-ParamILS.pdf)
and [FocusedILS/SMAC](https://www.cs.ubc.ca/labs/algorithms/Projects/SMAC/papers/11-LION5-SMAC.pdf).
Synchronized paired model evaluation is already central to
[SySRs](https://arxiv.org/html/2606.07726). Cost-aware best-arm methods such as
[BAIwRC](https://proceedings.mlr.press/v238/li24c.html) cover resource-limited
identification. The LLM-specific [CAPO](https://arxiv.org/html/2504.16005v2)
also combines population racing, paired tests on common blocks, and a token
length penalty. CW-PLR is therefore an experimental combination for this
retry-row setting, with a possible gap only in how it charges and allocates
realized early-terminating cascade costs. Pairing, Hamming neighbors, racing,
and simulated annealing are not individually new contributions.

## Required experiment

On small matrices, enumerate the exhaustive best row. On each search budget,
compare random search, UCB1, BO, Hyperband/BOHB, a SySRs-style synchronized
elimination baseline, ParamILS-style local racing, CW-PLR, and a permuted-graph
CW-PLR control. Equalize by realized search cost, not by the same fraction
parameter. Report held-out accuracy, simple regret, paid cells, solver/verifier
input tokens, final recommendation's cold deployment cost, and time to reach
each regret or accuracy level. Use multiple seeds and keep every negative
result.

The current graph-residual prototype does not satisfy this protocol: its
synthetic report has no independent audit matrix, its selector fractions do
not imply equal realized spend, and its path estimate is usually replaced by
the direct observed-row estimate. It remains useful only as a recorded
ablation.

## Recommended successor: cost-aware correlated racing (CACR)

The safer successor to the graph-residual idea is **Cost-Aware Correlated
Racing (CACR)**. Similarity is used only to propose one-slot Hamming
neighbors; every recommended row is directly evaluated. For each
incumbent--challenger pair, CACR keeps same-question score differences and
chooses the next block by predicted confidence-radius reduction per
conservative estimate of the two rows' *new full-workflow cost*. It has a
fixed random-restart floor, stops clearly losing races, and confirms the
final row on fresh questions. It never adds residuals along a path and never
reads a missing retry cell.

This combines established common-random-number ranking and selection
([Görder and Kolonko](https://arxiv.org/abs/1410.6782)), correlated-arm
best-arm identification ([C-LUCB](https://arxiv.org/abs/2109.04941)), and
resource-cost accounting ([BAIwRC](https://proceedings.mlr.press/v238/li24c.html)).
The newer [Hybrid Feedback](https://arxiv.org/abs/2605.05745) paper also
allocates between absolute and pairwise feedback with heterogeneous costs, so
CACR's paired-versus-direct allocation is not itself a novelty claim. The
possible gap is narrower: a complete retry cascade has outcome-dependent
realized cost, and the same question supplies both the paired score and cost
evidence. That is a hypothesis to test, not a novelty claim. The prototype
and synthetic results are currently on the Algorithm 2 branch in PR #4.

[Best-Arm Identification with Generative Proxy](https://arxiv.org/abs/2607.06879)
is another close boundary: it uses a correlated cheap proxy and controls
residual variance. A proxy version of CACR would need to compare against that
framework rather than claim control-variate allocation as new.

The branch also includes an independent-row (`iid`) negative control. With
135 cells and 50 seeds, CACR was effectively tied with random search on that
control, so the smooth-landscape gain must not be presented as universal.

The go/no-go test is a matched-dollar comparison against uniform paired
elimination, SySRs, AgentOpt, resource-constrained BAI, and hybrid-feedback
allocation. If CACR does not beat those baselines beyond search and audit
uncertainty, it should remain a negative or descriptive result rather than the
paper's claimed new algorithm.

In the prototype's smooth control at cap 200, randomly permuting row slots
reduced CACR audit accuracy from 0.796 to 0.764 (50 seeds), while random cells
reached 0.626. This is only a partial graph ablation because the restart floor
and direct evidence remain active.

A possible refinement is a safe-cost gate: estimate variance reduction for each
neighbor on a preregistered calibration block, use local racing only when a
conservative lower bound says the reduction is positive, and otherwise fall
back to a random/direct proposal. This is a future hypothesis, not an
implemented or theorem-backed method.
