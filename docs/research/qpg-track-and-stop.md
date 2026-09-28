# Question-Paired Graph Track-and-Stop (QPG-TS)

This is the strongest Algorithm 2 direction found so far. It is a proposed
research design, not an implemented result or a novelty claim.

## Setting

There are `K` complete retry rows and `N` registered benchmark questions. A
cell evaluation gives final correctness `Y(a,q)` and the realized input-token
cost `C(a,q)`. The selector sees neither the held-out questions nor their
answers. It must recommend one complete row after a limited search spend.

Rows are vertices of a Hamming graph: an edge changes one ordered model slot.
The graph proposes comparisons; it does not reveal a neighbor's reward when a
row is pulled. This distinction matters because graph-feedback bandits often
grant free observations of similar arms, while this experiment pays for every
row/question cell.

## Measurements

Maintain two kinds of streams.

**Direct stream.** A row is run on a question chosen from its fixed,
pre-shuffled question stream. The direct mean estimates that row's accuracy.

**Paired edge stream.** Two neighboring complete rows are run on the same
question. Store the residual

```text
D_ab(q) = Y(a,q) - Y(b,q).
```

For a uniformly sampled question stream,

```text
mu_a - mu_b = E[D_ab(q)].
```

The residual can have much lower variance than either absolute score when
question difficulty affects both rows similarly. Pairing is a statistical
comparison only; it does not reuse a workflow prefix and does not turn one
paid call into two observations.

## Graph-constrained estimate

For a provisional set of direct row means `d_a` and edge residual means
`r_ab`, fit a row-mean vector by solving

```text
min_mu  sum_a w_a (mu_a - d_a)^2
      + sum_(a,b) lambda_ab ((mu_a - mu_b) - r_ab)^2.
```

Weights are based on the number and variance of observations, with a floor on
direct evidence. An edge with large disagreement is downweighted rather than
treated as a reliable similarity relation. This is a surrogate for allocating
experiments, not a free license to report an unmeasured row as known.

Residuals telescope around every graph cycle for every reward matrix when the
same question is used: the sum is zero by algebra, even for a completely
non-smooth matrix. A nonzero cycle sum therefore detects sampling mismatch,
implementation error, or nonstationarity; it is not evidence that the Hamming
graph is a good similarity model. Test graph usefulness by comparing
neighbor-versus-random residual variance or by predicting held-out search
cells with a permuted-graph control.

Graph estimates are exploratory side information. A direct probe of a
survivor does not certify an unobserved row by itself; the final recommendation
must be a directly measured row with a valid interval, or every finalist must
be evaluated on an independent confirmation block. For the exhaustive
fraction, ignore the surrogate and use exact direct means.

### Question schedules keep pairing honest

An edge gets a random permutation of the full search questions when it is
created, before its outcomes are observed. Its sample is always a prefix of
that permutation; known endpoint cells may be inserted, but earlier questions
are not skipped. A synchronized-block alternative must run every active row on
every earlier block; a newly admitted row catches up on those blocks before it
is compared. Choosing a fresh block only from questions left after an
outcome-dependent admission can bias the residual mean. The log should record
planned and realized token cost, including any overshoot at the stopping
boundary.

## Allocation rule

At each round:

1. Build simultaneous confidence intervals for direct rows and registered edge
   residuals. The first implementation can use a conservative time-uniform
   bounded-data radius; later work can use finite-population empirical
   Bernstein bounds.
2. Identify the current leader and the most dangerous challenger: the row
   whose upper interval most overlaps the leader's lower interval.
3. Propose a graph edge on a leader/challenger path. Choose the edge/question
   pair by expected reduction in that overlap divided by predicted *new*
   input-token cost. Cost estimates use only previously observed calls.
4. With a cooling probability, choose a global random row or a random graph
   edge instead. This is the simulated-annealing exploration floor; it keeps a
   wrong local neighborhood from trapping the search.
5. Eliminate a row only when its upper bound is below the leader's lower bound.
   If the budget ends first, recommend the direct-measured row with the best
   lower bound and report the uncertainty interval.

The method is a patchwork of graph BAI, top-two/track-and-stop sampling,
paired common-question comparisons, and cost-aware experimental design. The
research contribution would be the combination specialized to retry-row
profiling with early-termination costs, plus evidence that the allocation
reduces search spending without hurting held-out row selection. The pieces
themselves are established; the paper must say this plainly.

## A conservative confidence rule

The prototype currently uses a heuristic uncertainty score. A publishable
version needs an anytime rule that remains valid while the selector chooses
the next stream adaptively. One simple finite-population guardrail is to fix
each stream's question permutation before collecting any outcomes and use a
union allocation over all registered rows, edges, and sample counts. If
`S = |V| + |E|` streams are registered, `S` must appear in the error
allocation; spending the entire error probability only over edges leaves the
direct row intervals uncovered. For a bounded residual `D_e` in `[-1, 1]`,
with `m` observations from a stream of `N` questions, a Serfling-style radius
can be written as

```text
r_e(m) = sqrt(2 * (1 - (m-1)/N) * log(2/alpha_m) / m),
alpha_m = 6 * delta / (S * pi^2 * m^2).
```

For a direct binary row stream, use the corresponding `[0, 1]` radius. A
path estimate from anchor `a` to row `x` then has the safe, conservative
interval radius `r_a + sum_e r_e` along the path. A weighted graph fit may
tighten the point estimate, but elimination should use the path-union bound
unless its simultaneous coverage is proved. Eliminate a row only when its
upper bound is below the leader's lower bound. This is a design target, not a
theorem about the current implementation; the finite-population correction
must be checked against the cited concentration theorem before it is used in
a paper.

## Conditions for a meaningful claim

- Questions for each direct and edge stream are sampled uniformly from the
  search split, or the estimator uses known sampling weights.
- A question may be selected because of previous outcomes, but not because of
  its unrevealed outcome. Every edge keeps its own fixed random question order.
- A missing later retry is not recorded as a failure. Its actual final score
  is the score produced by the deployment checker and evaluator.
- Costs include every reached solver and verifier call. Pairing must charge
  both complete rows' new calls, including failed attempts.
- The graph model is auxiliary. A wrong graph is tested by permuting row
  labels, changing the position of the edited slot, and using deliberately
  non-smooth synthetic landscapes.
- Held-out questions are used only after a row is selected. The audit set
  cannot tune graph weights, stopping thresholds, or temperatures.

## Required comparisons and ablations

Compare QPG-TS with random, uniform cells, Matrix-UCB, independent top-two,
cost-aware independent-arm racing, the current similarity-annealed baseline,
and the anchor graph-residual prototype. Ablate paired versus unpaired
measurements, graph versus permuted graph, fixed versus learned edge weights,
count versus realized-cost acquisition, cooling versus fixed exploration, and
direct-only versus graph-assisted recommendation. On small spaces, enumerate
all rows and report exact simple regret.

## Prior-art boundary

Graph-smooth best-arm methods such as [GRUB](https://proceedings.neurips.cc/paper_files/paper/2022/hash/0d561979f0f4bc6127cfcfe9c46ee205-Abstract-Conference.html),
categorical graph Bayesian optimization such as
[COMBO](https://proceedings.neurips.cc/paper/2019/hash/2cb6b10338a7fc4117a80da24b582060-Abstract.html),
and correlated-arm methods such as
[covariance-adaptive BAI](https://proceedings.neurips.cc/paper_files/paper/2023/file/e82ef7865f29b40640f486bbbe7959a7-Paper-Conference.pdf)
already cover important parts of this design. [Top-two best-arm methods](https://proceedings.neurips.cc/paper_files/paper/2022/hash/ab5f5f22e3e09f4424592ffb06840ab0-Abstract-Conference.html)
cover the leader/challenger allocation idea. [CABAI](https://rlj.cs.umass.edu/2024/papers/Paper193.html)
and [budgeted multi-step BO](https://proceedings.neurips.cc/paper_files/paper/2021/hash/a8ecbabae151abacba7dbde04f761c37-Abstract.html)
cover heterogeneous evaluation costs. QPG-TS should therefore be presented
as a retry-row, question-conditioned adaptation unless its estimator and cost
allocation yield a result those methods cannot express.

Classical algorithm configuration also already combines one-change neighbors
with racing. [ParamILS](https://www.cs.ubc.ca/labs/algorithms/Projects/ParamILS/papers/09-JAIR-ParamILS.pdf)
uses categorical local moves and restarts, while [FocusedILS/SMAC](https://www.cs.ubc.ca/labs/algorithms/Projects/SMAC/papers/11-LION5-SMAC.pdf)
intensifies promising configurations on the same instance/seed cases and
stops losing candidates early. Our method cannot claim local search, matching,
or early stopping as new. The plausible gap is narrower: use a principled
paired confidence rule and realized retry-call cost when deciding how much
additional profiling a complete row receives.

Most critically, [SySRs](https://arxiv.org/html/2606.07726) already
synchronizes model evaluations on the same benchmark questions and uses
paired differences with a provable similarity-dependent bound. A plain
same-question residual method is therefore not our novelty. SySRs must be an
explicit baseline. The proposed gap is narrower: extend synchronized
successive rejection from single models to complete retry rows, charge each
comparison by its realized cascade cost, and handle row-specific graph edges
and interaction effects. This gap remains a hypothesis until formalized and
measured.

The closest matrix-shaped prior is [Active Ranking of Experts Based on their
Performances in Many Tasks](https://proceedings.mlr.press/v202/saad23b/saad23b.html),
which sequentially samples an expert/task matrix to identify a strong expert.
Its guarantees use a global monotonic ranking assumption: one expert beats
another on every task. Our complete retry rows can cross in quality from one
question to the next, so that assumption must be tested rather than silently
imported. An adapted active-ranking baseline belongs in the experiment. The
row graph and early-termination token cost are possible extensions, not the
matrix search alone.

## Simpler model-based alternative: Adaptive Factorial Graph Racing

If graph paths remain unstable, use the fact that a row has three categorical
slots directly. In a development phase, choose a balanced covering set of
rows and run them on the same random question blocks. Fit a regularized
factorial model with a question intercept:

```text
Y(m1,m2,m3,q) = eta_q
              + beta[1,m1] + beta[2,m2] + beta[3,m3]
              + selected two-slot interactions + noise.
```

The shared `eta_q` absorbs question difficulty. A one-slot residual is then a
direct estimate of a factor effect, while interaction terms allow a retry
slot to matter differently when paired with a particular earlier model. Use
Thompson or top-two sampling over fitted row means, selecting a direct cell or
matched edge by expected top-two uncertainty reduction per observed cost. Keep
random scouts and direct probes, and use only direct confirmation for the
final recommendation. Call this **Adaptive Factorial Graph Racing (AFGR)** if
it is implemented.

AFGR has a clear failure test: compare a main-effects-only model, a model with
two-slot interactions, and a permuted-question-intercept control. It is easier
to explain to a reviewer as hyperparameter search over three categorical
factors. Its ingredients are still established factorial modeling,
categorical BO, and top-two exploration; the possible contribution remains
their cost-aware use for complete retry rows with question-conditioned
early-stop costs.

## Simpler successor: Cost-Weighted Pairwise Local Racing

The graph-path estimator should not be the default. For two rows `u` and `v`,
the shared-question residual `Y_v(q)-Y_u(q)` is already the direct paired
comparison. A path through intermediate rows only adds paid calls: if all
edges use the same questions, residuals telescope sample by sample; if they
use separate questions, path variance is bounded by the sum of edge variances
and cannot beat a direct endpoint pair at equal cell cost without an extra
assumption such as a cheap proxy row or amortization across many targets.

The practical candidate is **Cost-Weighted Pairwise Local Racing (CW-PLR)**:

1. Start from a random complete row and measure a small direct block.
2. Propose a one-slot Hamming neighbor, with a cooling probability for a
   global random restart.
3. Before seeing that race's outcomes, draw a fresh random permutation of the
   full search questions. Evaluate the incumbent and challenger on paired
   prefixes, reusing only exact row/question cells.
4. Use a time-uniform paired confidence interval. Stop a losing challenger as
   soon as its upper advantage is below zero (or a practical margin), and
   promote it only when its lower advantage is positive.
5. Divide the next block's information gain by predicted *new* realized token
   cost. Keep a small direct/random reserve and directly confirm the final
   incumbent on fresh questions.

CW-PLR is a research baseline and candidate extension of classical racing,
not an established new algorithm. Its testable claim is about the cost-to-
regret curve under retry-specific realized costs, compared with ParamILS-style
local racing, SySRs-style synchronized elimination, and independent UCB/BO.

## Lower-risk implementation: Cost-Aware Similarity Hyperband

If QPG-TS is too ambitious for the first paper, a cleaner engineering
candidate is **Cost-Aware Similarity Hyperband (CASH)**. Draw a broad first
rung of complete rows, evaluate every active row on the same small question
block, and eliminate the lower part using paired confidence intervals. Promote
survivors to larger synchronized blocks. Replace Hyperband's equal-cell rung
sizes with a target for *incremental realized token cost*, since one row can
reach more retry calls than another. Hamming neighbors can receive a small
residual-based optimistic bonus when deciding whom to admit, but every
promoted row gets direct measurements and the final winner is directly
confirmed.

CASH is easier to compare fairly with BOHB, Hyperband, SySRs, and random
search. Its likely contribution is practical: a retry-row-aware cost schedule
with synchronized questions and a transparent cost-to-quality curve. It is
also less likely to overclaim a new estimator. If the paired confidence rule
does not beat a SySRs adaptation, that negative result still tells us that
the row graph adds no value under the tested workloads.
