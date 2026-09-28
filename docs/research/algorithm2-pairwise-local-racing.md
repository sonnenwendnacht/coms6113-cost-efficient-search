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
identification. CW-PLR is therefore an experimental combination for this
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

## First synthetic check

I implemented a small prototype in `src/retry_search/pairwise_local_racing.py`
and a separate held-out benchmark in
`scripts/benchmark_pairwise_local_racing.py`. With 27 rows, 50 search
questions, 200 independent audit questions, 50 seeds, and the same 135-cell
budget for both methods, the smooth synthetic landscape produced:

| Selector | Mean audit accuracy | Optimal-row rate | Mean search cost |
| --- | ---: | ---: | ---: |
| Random cells | 0.449 at 5% budget; 0.614 at 10%; 0.799 at 20% | 0.00; 0.08; 0.48 | 98.4; 198.4; 396.7 |
| CW-PLR | 0.576 at 5% budget; 0.608 at 10%; 0.704 at 20% | 0.06; 0.06; 0.14 | 96.1; 191.7; 387.0 |

These numbers are synthetic only. They suggest a useful low-budget search
curve but a worse medium-budget curve than random cells. That is exactly the
kind of boundary we need to measure: local similarity may help find a good
region early, while broad coverage wins once the budget is large enough. The
prototype uses a practical empirical radius rather than a proven confidence
sequence, so this table is a debugging result, not evidence of superiority.

As a second check, a realized-cost cap gave the same pattern on 50 seeds:
at caps `100/200/400`, CW-PLR reached `0.588/0.618/0.723` audit accuracy,
while random cells reached `0.454/0.626/0.801`. The realized costs were within
one endpoint call of the cap for both selectors. This is still one invented
landscape; it does not justify choosing CW-PLR for MathQA.

The companion diagnostic `scripts/diagnose_row_similarity.py` measured the
same synthetic search matrix before running a selector. Its residual variance
by Hamming distance was `0.182`, `0.279`, and `0.363` for distances one, two,
and three. This confirms that the generator contains the locality assumption
CW-PLR needs. It is a sanity check of the generator, not evidence that the
MathQA rows have the same property. The real experiment must publish this
neighbor-versus-random residual diagnostic from the search split before
interpreting any gain.

## Recommended successor: cost-aware correlated racing (CACR)

The next implementation should make the allocation rule explicit rather than
presenting CW-PLR's heuristic as the final algorithm. We call the narrower
candidate **Cost-Aware Correlated Racing (CACR)**:

1. Keep a direct estimate for every row that has been pulled and a paired
   difference stream for every incumbent--challenger race. A paired sample is
   `D(q) = Y_challenger(q) - Y_incumbent(q)` from the same question; it is not
   an estimate of an unpulled cell.
2. Use one-slot Hamming neighbors only to propose challengers, with a fixed
   random-restart floor. Do not add residuals along a path and do not infer a
   row that has never received a direct confirmation block.
3. For each open race, estimate both the uncertainty of its paired difference
   and the expected *new* full-workflow cost of the two endpoints. Choose the
   next block size by predicted reduction in the paired confidence radius per
   conservative cost estimate. The cost estimate is based on reached calls
   observed so far, with an uncertainty margin; it never reads a missing cell.
4. Stop a race when the challenger is clearly behind, promote it when it is
   clearly ahead by the preregistered margin, and retain a global scout/restart
   budget. Independently confirm the final row on fresh questions.

This is a testable combination of known ideas: common-random-number paired
ranking and selection, correlated-arm best-arm identification, heterogeneous
resource accounting, and categorical local proposals. The possible gap is the
joint objective: the observation is a complete retry cascade whose realized
cost depends on early termination, and the same paired question supplies both
the score difference and the cost evidence. That gap is a hypothesis, not a
novelty claim. The first paper result should be a comparison against a
cost-weighted synchronized-elimination baseline, random search, and a local
racing control with the cost term removed.

Relevant prior art that constrains the claim includes Bayesian ranking and
selection with common random numbers
([Görder and Kolonko](https://arxiv.org/abs/1410.6782)), correlated-arm
best-arm identification ([C-LUCB](https://arxiv.org/abs/2109.04941)), and
cost-aware best-arm identification ([CABAI](https://arxiv.org/abs/2402.16710)).
The newer [Hybrid Feedback](https://arxiv.org/abs/2605.05745) paper also
allocates between absolute and pairwise feedback with heterogeneous costs and
gives a cost-aware Track-and-Stop rule. Therefore CACR's paired-versus-direct
allocation is not, by itself, a novelty claim. A defensible distinction would
have to come from the full retry cascade: one evaluation can terminate early,
its realized cost is outcome-dependent, and the observation is not a cheap
dueling query under a shared GLM. That distinction still needs a formal model
and an experiment against the hybrid-feedback baseline.

The prototype accepts explicit row_slots when configuration IDs are not in
canonical base-side order. This is required for real experiments: a string ID
or shuffled matrix row must never silently change the neighborhood.

The benchmark now also has an `--landscape iid` negative control that removes
row locality. At 135 cells and 50 seeds, its independent 200-question audit
gave mean accuracies `0.597` (random), `0.597` (CW-PLR), and `0.596` (CACR);
at a matched cost cap of 170, the values were `0.596`, `0.598`, and `0.596`.
The small differences are noise-level in this control and do not support a
similarity benefit. This control must stay in later reports.

## CACR prototype check

The prototype was added in `src/retry_search/cost_aware_correlated_racing.py`.
On the same invented 27-row landscape, using 50 seeds and 200 independent
audit questions, a realized-cost cap gave the following audit accuracies:

| Search cap | Random cells | CW-PLR | CACR |
| ---: | ---: | ---: | ---: |
| 100 | 0.454 | 0.588 | 0.745 |
| 200 | 0.626 | 0.618 | 0.796 |
| 400 | 0.801 | 0.723 | 0.861 |

The mean realized spends were respectively about `100.7/101.3/101.6`,
`200.8/200.9/201.5`, and `400.7/400.8/399.0` for random/CW-PLR/CACR. CACR
also selected higher-cost rows in this generator, so its better accuracy is
not a claim about a cost--accuracy deployment trade-off. The generator makes
high-quality rows more expensive by construction. These results are a
debugging signal that the acquisition rule is implementable, not evidence of
superiority. The next check must use retry traces or a synthetic model with
independent controls for quality and reached-call cost.

With the canonical Hamming slots permuted before CACR proposals (50 seeds,
cap 200), the audit accuracy was `0.764` versus `0.796` for canonical CACR,
`0.626` for random cells, and `0.618` for CW-PLR. The gap is only a control
diagnostic: random restarts and direct row evidence still let the permuted
version find good rows, so it does not isolate a pure graph effect.

## Publication gate

Before treating CACR as Algorithm 2 for a paper, run a matched-dollar study
against random search, uniform synchronized evaluation, SySRs-style paired
elimination, AgentOpt's available selector, a cost-aware resource-constrained
BAI baseline, and a direct/pairwise hybrid-feedback baseline. Use the same
question split, full-row retry semantics, stopping checker, cache permissions,
and final fresh audit. Retain CACR only if its benefit survives the iid and
permuted-graph controls and exceeds uncertainty from search seeds and audit
questions. Otherwise the honest result is that ordinary paired allocation or
AgentOpt already captures the gain.
