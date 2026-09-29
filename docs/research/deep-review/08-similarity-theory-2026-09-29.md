# Similarity without prefix reuse: a validity-first design note

Prepared during the research-only window ending 2026-09-29 11:00 ET. This is
an analysis and design record. It is not an experiment, a theorem about the
current code, or a novelty claim.

## The question we can actually answer

Let `C` be the finite set of complete retry configurations. A row `c` fixes
the model in every solver, verifier, and retry slot. For a search question
`q`, one paid execution of the complete row returns

```text
Y(c,q) in {0,1}       final answer-key-blind verifier outcome
K(c,q) >= 0           all input-token charges for reached calls
```

The answer key is used only on the held-out audit set. The search sees `Y` as
the deployment verifier would see it and records `K`; it does not see whether
an unreached retry would have succeeded. The target quality is the mean of
`Y(c,q)` over the deployment question distribution (or the finite benchmark
population, if that is the declared target). Similarity between rows means
that `Y(c,q)` and `Y(c',q)` tend to agree for the *same* question. It does not
mean that a response, retry prefix, or missing cell can be copied from one row
to another.

For two rows, the useful observation is the paired difference

```text
D(c,c',q) = Y(c',q) - Y(c,q).
```

Its mean is exactly the quality difference. If the rows agree on difficult and
easy questions, `D` has less variation than two separately sampled row means,
so a comparison can stop sooner. This is the only universally safe benefit of
row similarity without prefix reuse: it can reduce the uncertainty of a
*comparison between two rows that were actually run*. It cannot estimate an
unvisited row, and a path of neighboring residuals does not create free
information. Using independent questions on different edges gives a sum of
edge variances; using the same questions telescopes to the direct endpoint
difference while paying for the intermediate rows.

## Fatal assumptions in the current CACR/SCCR prototypes

The prototypes are useful engineering ablations, but their current stopping
rules are not valid fixed-confidence inference.

1. **The variance gate is a heuristic.** SCCR compares a sample variance of
   paired differences with two sample variances and adds
   `variance_margin/sqrt(m)`. That is not a lower confidence bound for a
   finite-population variance reduction. The edge is also chosen after earlier
   outcomes. The gate may be used to choose an allocation, but it cannot be
   described as proving that the edge is safe.
2. **Repeated peeking is uncorrected.** `_radius` is checked after many
   adaptive blocks. A fixed-sample radius does not retain its nominal error
   probability after optional stopping. A time-uniform confidence sequence or
   a preregistered final sample size is required.
3. **Observed row cells are not automatically a random row sample.** A row may
   enter the matrix through several adaptively chosen pair races. Combining
   those cells into `row_estimate` is only justified if the inclusion rule is
   independent of that row's outcomes, or if the estimator accounts for the
   sampling design. Exact reuse is valid accounting, but it is not a fresh
   independent observation.
4. **A cached pair stream can be conditionally selected.** CACR gives each
   pair a permutation, but a pair can be opened after one or both rows were
   already observed on some of those questions through another race. If those
   cells are treated as a new random pair sample, the pair's history has been
   selected using outcomes. Either use a global precommitted block schedule and
   make late rows catch up on every earlier block, or reserve disjoint
   cross-fitted blocks for each inferential comparison. Reusing an exact cell
   remains correct for spending, but it is not automatically valid for a new
   confidence interval.
5. **A dollar cap can select on the outcome.** In a retry workflow, `K` is
   observed after early termination and can correlate with `Y`. If a random
   question stream is truncated whenever its accumulated cost reaches a cap,
   the included questions are no longer a simple uniform sample. Cost-based
   stopping therefore needs a valid anytime bound, or blocks must be admitted
   using a known worst-case charge and completed in full.
6. **The cost forecast has no certificate.** The empirical mean plus a normal
   standard-error term is a scheduling heuristic for heavy-tailed or bounded
   cascade costs. It is not a high-probability upper bound. It must not be used
   to claim that a row satisfies a deployment cost constraint without a
   separate cost interval.
7. **The iid null is too weak as a safety test.** If all rows are iid, a local
   method should have no advantage, but this does not test the failure mode of
   a false similarity gate. A gate can pass on a benign calibration stratum
   and fail on the remaining questions, or neighboring rows can be
   anti-correlated. Such alternatives are not represented by an iid control.
8. **Locality is not a guarantee.** One model-slot changes can have nonlinear
   interactions with the other slots, especially when a verifier or retry
   policy changes which later calls are reached. A Hamming neighbor may be the
   wrong direction, and a globally best row can be separated by several
   locally poor rows. A restart floor is an exploration heuristic, not a
   best-arm guarantee.

These points do not make CACR/SCCR useless. They define the exact claim they
can support today: a cost-aware allocation heuristic whose recommendation must
be evaluated on a fresh audit split. They cannot yet support a delta-correct
best-row claim.

## A validity-first algorithm

The principled baseline to implement and compare is **Conservative Paired
Racing with Successive Elimination (CPR-SE)**. The name describes a direct
construction from ranking-and-selection and best-arm identification; it is
not proposed as a new primitive.

### Fixed design and data splits

Before any model call, declare the search question set, confidence level
`delta`, indifference margin `epsilon`, and a finite edge family `E` (for
example all one-slot neighbors plus a set of global restart edges). Draw one
global random permutation of the search questions and split it into fixed
blocks before observing outcomes. At epoch `t`, every row used in an
inference block is evaluated on that same block. A row admitted late catches
up on every earlier block before it is compared; exact cells can be reused for
that catch-up. This global schedule makes each row's question inclusion
independent of its own outcomes. A pair-specific schedule is allowed only if
its block is disjoint from all prior data used to choose that pair.

A block is never shortened because its early questions look bad. Optional
stopping happens only between complete blocks. This is more conservative than
the current pair-specific cursor, but it makes the inferential target explicit
and lets the implementation distinguish exact accounting reuse from fresh
statistical evidence.

For a fixed-confidence certificate, use a small, equal-size direct pilot for
every row. This pilot is expensive, but it makes the selection design explicit:
every row has a genuine random sample and a cost observation. A budgeted
variant may screen only a subset of rows and let local similarity propose the
rest; it must then be labeled a fixed-budget recommendation procedure, not a
whole-space confidence certificate. That distinction prevents a plausible
local search curve from being reported as a guarantee over all `|C|` rows.

### Comparison and gate

For a proposed edge `(c,c')`, run both complete rows on the same fixed
question block. A *trusted* edge is one whose preregistered pilot block has a
conservative empirical indication that `D` is less variable than separate row
means. The gate only chooses the estimator and block priority; it never widens
or narrows the validity guarantee. If the gate fails, keep direct row
intervals and treat the pair as an ordinary two-arm comparison. There is no
need to trust a similarity assumption for correctness.

For every edge, maintain a time-uniform confidence sequence for the finite
population mean of `D`. For an untrusted edge, maintain separate confidence
sequences for the two row means. Allocate the edge error as
`delta/(|E|)` (with a further explicit time-uniform allocation if the chosen
confidence-sequence construction requires one). Waudby-Smith and Ramdas give
Hoeffding- and empirical-Bernstein-type confidence sequences for sampling
without replacement; those are the appropriate starting point for a finite
benchmark population. The confidence sequence, rather than the empirical gate,
controls elimination.

The score ranges are known: `Y` lies in `[0,1]` and `D` in `[-1,1]`. Thus a
conservative Hoeffding-without-replacement sequence is always available even
when the paired variance is large; an empirical-Bernstein sequence can be used
only with the source paper's valid variance process. The same construction
applies to `K` after declaring a finite maximum input-token charge. If that
maximum cannot be defended, cost remains a measured deployment statistic rather
than a certified constraint. This separation keeps an optimistic cost model
from entering the quality guarantee.

### Elimination and cost scheduling

Maintain an active set of rows. Eliminate `c'` only when a valid interval for
`mu(c')-mu(c)` is wholly below `-epsilon` for a currently competitive row `c`.
If no paired edge is trusted, use the union of the two absolute intervals.
Never eliminate a row because an unreached retry is interpreted as failure.
Choose the next edge/block by predicted uncertainty reduction per conservative
cost envelope, while reserving a fixed fraction for global rows. This affects
spending only; all intervals remain valid under adaptive edge choice because
the edge family and error allocation were fixed before observing outcomes.

For a dollar budget, admit a complete block only when its known worst-case
charge fits the remaining reserve. If no finite worst-case envelope is
available, use a cell budget as the primary guarantee and report realized
dollars afterward. Do not silently turn outcome-dependent stopping into a
uniform question sample.

If deployment cost is a constraint rather than a report, maintain a second
confidence sequence for `mu_K(c)`. Eliminate rows whose *upper* cost bound is
above the cap, and select the highest-quality surviving row. A scalar utility
`Y - lambda K` is also possible, but `lambda` and its units must be fixed
before search. Quality and cold deployment cost should still be reported
separately.

### Recommendation and audit

At the search budget, return only a directly evaluated row. A fresh
confirmation block is required before the held-out audit. The audit questions
are never used to tune the gate, edge list, block schedule, confidence level,
or cost model. Report search spend, number of paid cells, confidence intervals,
selected-row cold cost, and audit quality separately.

This procedure uses similarity where it is defensible: same-question pairing
can shrink a comparison interval, and local edges can prioritize likely
competitors. It does not use similarity to hallucinate a row or to certify an
unseen retry path.

## A concrete counterexample to an ungated-similarity claim

Take two rows `A` and `B` and 100 fixed questions. On the four questions used
for calibration, set `A=B=(0,1,0,1)`. Their paired-difference variance is zero,
while each marginal variance is positive, so any small-sample ratio gate that
declares a large variance reduction accepts the edge. On the remaining 96
questions, set `A=1` and `B=0`. The true means differ by approximately `0.46`
in favor of `A`, despite the calibration showing perfect similarity. If a
race stops or allocates aggressively after the calibration block, it can
recommend `B` or spend too little to discover the reversal. The event has
positive probability under a uniform random calibration permutation, and its
probability is larger when questions have latent strata. The iid control does
not expose this construction because the rows are deliberately dependent and
the dependence changes by stratum.

A separate cost counterexample is a row whose successes always trigger a long
retry and whose failures terminate cheaply. Stopping a random question stream
when accumulated dollars hit a cap then preferentially includes cheap
failures. The observed mean is biased even though the question order was
initially random. Full fixed blocks, or an anytime confidence sequence that
explicitly handles the stopping rule, are necessary.

## What would count as evidence

The next study should compare CPR-SE, direct uniform successive elimination,
SySRs-style synchronized pairing, CACR, SCCR, and the AgentOpt baselines on
the same trace engine and splits. It should include smooth, iid, permuted,
stratified-reversal, and anti-correlated synthetic controls before the full
MathQA run. The claim should be limited to an observed reduction in paid
search cost at a matched probability of selecting an epsilon-good row. If the
similarity gate does not survive the reversal and anti-correlation controls,
the contribution is a useful negative result: row similarity is a proposal
heuristic, not a reliable estimator for complete retry configurations.

## Primary references

- Waudby-Smith and Ramdas, “Confidence sequences for sampling without
  replacement,” NeurIPS 2020:
  <https://proceedings.neurips.cc/paper_files/paper/2020/file/e96c7de8f6390b1e6c71556e4e0a4959-Paper.pdf>
- Nelson, Swann, Goldsman, and Song, “Simple procedures for selecting the best
  simulated system when the number of alternatives is large,” Operations
  Research 2001: <https://doi.org/10.1287/opre.49.6.950.10019>
- Zeng et al., “Best Arm Identification in Generalized Linear Bandits via
  Hybrid Feedback,” 2026: <https://arxiv.org/abs/2605.05745>
- “Best-Arm Identification with Generative Proxy,” 2026:
  <https://arxiv.org/abs/2607.06879>
- “Correlated Best-Arm Identification,” C-LUCB:
  <https://arxiv.org/abs/2109.04941>
