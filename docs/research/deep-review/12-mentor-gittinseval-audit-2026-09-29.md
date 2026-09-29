# Audit of the mentor's GittinsEval paper

Prepared 2026-09-29 from the primary arXiv HTML version
([arXiv:2609.25645v1](https://arxiv.org/html/2609.25645)). This is a source
note, not an experiment report.

## What GittinsEval actually assumes

The paper treats each candidate configuration as one arm and each benchmark
example as a fresh observation of that arm. A batch pull evaluates one arm on
a batch of examples and returns a scalar batch mean. Its setup uses an arm's
per-example cost, so the cost of a batch is the known price rate times the
batch size. The working model is a Gaussian prior over the arm mean and a
fixed observation-noise variance; rows/arms evolve as independent Markov
chains. The paper explicitly says that its Gittins optimality statement is
Bayesian and model-dependent, not a distribution-free finite-sample guarantee
for a realized response matrix.

There are two related objectives:

- Under a fixed external budget, return an anytime recommendation, which may
  be only partially evaluated.
- Under adaptive stopping, require completed arms and maximize expected terminal
  quality minus accumulated evaluation cost.

GittinsEval precomputes cost- and horizon-dependent stopping roots, selects the
unfinished arm with the highest index, and adds an LCB-style anytime
recommendation. The paper reports that the configuration-level BO baseline
usually evaluates a selected configuration over the whole benchmark, whereas
GittinsEval allocates partial batches across arms. Those are the relevant
allocation ideas to reproduce as baselines, not claims to import unchanged.

## What transfers to our project

1. **The row/column view is correct.** A complete retry configuration is an
   arm and a benchmark question is an item. A profiling policy can choose
   which row to evaluate on which new question batch.
2. **A fixed-budget table and an adaptive-stopping table are different.** Our
   main comparison should fix actual profiling charge and report recommendation
   quality at that charge. If we also report stopping, the completion rule and
   utility units must be stated separately.
3. **GittinsEval is a required baseline.** It is particularly relevant because
   it already uses known heterogeneous evaluation costs and an anytime
   recommendation. A fair implementation should use the same question blocks,
   same cost accounting, and same direct row observations for every selector.
4. **The LCB recommendation is a useful diagnostic.** It gives a simple
   conservative-looking recommendation rule, but its Bayesian surrogate must
   not be presented as a frequentist confidence certificate for our rows.

## What does not transfer without a new reduction

Our observation from a complete row is `(Y(c,q), K(c,q))`, where `Y` is the
answer-key-blind deployment outcome and `K` is the sum of input-token charges
for calls that were actually reached. A failed early attempt can trigger a
later call; an early verifier acceptance can skip it. Therefore `K` is random,
can depend on intermediate outcomes, and can be correlated with `Y`. The
known model price is only a coefficient in that realized charge.

Two rows evaluated on the same question are also statistically coupled by task
difficulty. GittinsEval's independent arm-chain model does not provide a
same-question covariance model, a paired-difference estimator, or a way to
purchase one stateful retry continuation and treat it as observations for
several complete rows. Its per-example arm cost is not the same object as a
path-dependent cascade charge.

This means “we added retries and cost to Gittins” is not enough for a
contribution. We must either:

- define a conservative reduction in which one complete cascade is an
  indivisible arm pull and compare against GittinsEval/CABAI/resource-aware
  BAI under that model; or
- explicitly model same-question paired rows and path-dependent costs, then
  prove or honestly label the structural allocation heuristic and retain a
  direct fallback.

## Practical baseline specification

When experiments resume, implement a row-level Gittins baseline with the
paper's assumptions visible in the configuration:

- fixed, outcome-independent question blocks;
- direct complete-row observations only;
- per-row batch charge equal to the **realized** sum of reached-call charges,
  while keeping the nominal model coefficient in a separate field;
- the paper's Gaussian index using a preregistered batch-noise approximation;
- its anytime LCB recommendation and required-completion stopping variant;
- no paired observations or structural row prediction.

Then add a paired/structured selector as a separate method. Any difference
between them can be attributed to same-question structure and robust fallback
rather than to an unreported change in cost accounting.

## Source-backed limits to state in the paper

The primary source says GittinsEval's exact policy is optimal only under its
Gaussian Markov-chain surrogate, positive predetermined batch costs, and
required-completion policy class. Its fixed-benchmark extension treats the
full-row empirical mean as the target but still relies on the surrogate for
allocation. It does not establish a guarantee for answer-key-blind verifier
outcomes, retry reach probabilities, endogenous token cost, or cross-row
paired covariance. These are the precise reasons it is a strong baseline and
not the complete solution to our retry-row setting.
