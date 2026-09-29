# Similarity-gated exploration of complete retry rows

Research checkpoint: 2026-09-29. This note was prepared without launching an
experiment or reading the active response matrix. It is a design proposal and
prior-art boundary, not a novelty or performance claim.

## The legal use of similarity

Let a complete configuration be a row

```text
c = (solver-attempt-1, solver-attempt-2, ..., verifier choices)
```

and let a question be `q`. A paid evaluation returns

```text
Y(c,q) : the final workflow result, scored after the run
C(c,q) : the realized input-token charge of reached calls
```

The search policy may use `Y` only through a deployment-valid checker. It may
not read the answer key, an unreached retry, or a response from another row.
Two rows evaluated on the same question give a paired difference

```text
D(c,c',q) = Y(c',q) - Y(c,q).
```

Similarity can reduce the uncertainty of this difference. It cannot reveal
`Y(c',q)` when only `Y(c,q)` was observed, and residuals along a path do not
create a free estimate of an unmeasured endpoint. The final recommendation
must therefore have direct observations; a neighboring row is a proposal or a
paired comparison partner, never an exact cache hit.

For a fixed pair, the basic identity is

```text
Var[D] = Var[Y(c')] + Var[Y(c)] - 2 Cov(Y(c'), Y(c)).
```

With equal numbers of shared questions, pairing is useful only when the
covariance is positive enough to make `Var[D]` smaller than the variance of a
difference based on separate questions. Hamming distance is a hypothesis
about this covariance, not evidence of it. A cost correlation is a separate
hypothesis; the pilot's weak cost signal means we should use observed cost as
an acquisition denominator, not assume that nearby rows have similar costs.

## A stronger candidate than ungated local racing

The working design is **Similarity-Gated Robust Row Racing (SG-RR)**. It is a
fixed-budget pure-exploration method for complete rows. The name is temporary;
the method should not be presented as new until the baseline and source audit
are complete.

### 1. Keep two kinds of evidence

For every row, maintain a direct estimate of its question-level mean. For a
pair, maintain a same-question difference stream. Never replace a row's direct
estimate with a path estimate. A paired stream can decide whether one directly
observed row beats another; it cannot fill an unobserved row.

### 2. Represent the row structure, but allow it to be wrong

Represent each categorical slot with one-hot indicators. Begin with an
additive model and a small, preregistered set of slot-interaction terms:

```text
mu(c) = phi(c)^T theta + r(c),       |r(c)| <= gamma.
```

The feature map is used to allocate measurements and to propose promising
complete rows. It is not allowed to suppress direct evidence on its own. The
residual radius `gamma` is estimated from held-out-from-fitting calibration
questions or set to the unstructured fallback when there is not enough data.
This is the same safety idea as robust pure exploration in misspecified linear
bandits, adapted to rows whose features describe model choices rather than
continuous actions. Alieva, Cutkosky, and Das explicitly model
`y = <theta,x> + gamma`, use optimal experimental design, and retain a
graceful fallback when the structure is not useful; see their
[ICML 2021 paper](https://proceedings.mlr.press/v139/alieva21a.html) and the
formal problem statement in the [PDF](https://proceedings.mlr.press/v139/alieva21a/alieva21a.pdf).

The important restriction here is that the model is a proposal and uncertainty
tool. A high predicted row that has no direct observations is only a candidate
for measurement, not the answer.

### 3. Calibrate an edge before trusting it

For a proposed pair `(c,c')`, reserve a question block whose identity is
chosen before observing outcomes. Estimate the paired-difference variance and
the two marginal variances on that block. Permit paired racing only when a
conservative lower bound on

```text
Var[Y(c)] + Var[Y(c')] - Var[D(c,c')]
```

is positive. If the lower bound is non-positive, use direct row uncertainty or
choose a global candidate. Keep a nonzero random-restart floor. This gate is
not a fixed-confidence certificate unless it is replaced by a valid
time-uniform construction; an adaptively chosen edge and repeatedly checked
sample variance are otherwise vulnerable to selection bias.

The safe default is a batch schedule: calibrate at fixed block sizes
`m, 2m, 4m, ...`, decide only at those checkpoints, and reserve a separate
confirmation block. A stronger implementation could use an always-valid
confidence sequence or an e-value, but that must be derived for the actual
paired finite-population sampling scheme rather than imported by name.

### 4. Choose the next measurement by regret reduction per dollar

At each batch, score two legal actions:

* **Direct row action:** evaluate one candidate row on a new question block.
* **Paired action:** evaluate two directly observed rows on the same new
  questions, only for a gate-approved pair.

For each action, estimate the reduction in the current upper bound on simple
regret, divide by an upper estimate of *new* realized charge, and choose the
largest score. The cost estimate must be based only on reached calls already
observed for those rows. It must not assume a missing retry was a failure.
Because a pair's second cascade can overshoot a dollar cap before its cost is
known, the implementation must either use a hard per-call token ceiling or
declare the budget a soft cap and report the realized overshoot.

The pair action is useful for resolving a close contest; the direct action is
needed to discover a row that the current neighborhood model missed. This
separates *where to look* from *how to compare two rows*.

### 5. Recommend only after direct confirmation

Use the robust surrogate and paired intervals to select a short finalist set.
Spend a preregistered fresh block directly on every finalist, then recommend
the row with the highest direct estimate. The audit questions remain untouched
until this choice is frozen. Report profiling cost, audit accuracy, and cold
deployment cost separately.

## Why this is not automatically a new algorithm

Every component has close precedent:

* COMBO models categorical configurations with a graph-Cartesian-product
  diffusion kernel, learns variable-wise smoothness, and optimizes an
  acquisition function over complete structures. See the
  [COMBO paper](https://arxiv.org/abs/1902.00448), especially its graph and
  ARD-kernel construction.
* BOCS uses a Bayesian linear/quadratic surrogate for combinatorial structures;
  the PSR follow-up improves its acquisition optimization. See the
  [PSR paper](https://arxiv.org/abs/2008.08177).
* Robust pure exploration already combines structure-aware experimental design
  with an unstructured fallback under bounded misspecification
  ([Alieva et al.](https://proceedings.mlr.press/v139/alieva21a.html)).
* Covariance-adaptive BAI, common-random-number ranking and selection, SySRs,
  Hybrid Feedback BAI, and Generative Proxy BAI already establish that
  correlated observations, paired feedback, or a cheap proxy can reduce
  evaluation effort.
* Cost-aware pairwise pure exploration explicitly studies pairwise targets with
  arm-dependent costs ([Wu et al., AISTATS 2025](https://proceedings.mlr.press/v258/wu25c.html)).
* Costly-reward bandits establish that paying to observe a reward changes the
  exploration problem ([Tucker et al., UAI 2023](https://proceedings.mlr.press/v216/tucker23a.html)).

Therefore the following claims are not sufficient:

```text
we use Hamming neighbors
we compare rows on the same questions
we combine UCB with simulated annealing
we use a graph or a Bayesian surrogate
we divide an uncertainty score by estimated API cost
```

A defensible contribution would need to show that **complete-row evaluations
with retry-dependent, outcome-dependent realized cost** require an allocation
rule not captured by these baselines, and then demonstrate that the rule
survives iid, permuted-slot, adversarial-locality, and matched-cost controls.
That is a research hypothesis, not an established gap.

## A counterexample the algorithm must survive

Suppose every one-slot neighbor has a high same-question correlation but a
rare question reverses the ordering: the incumbent wins almost every easy
question, while a distant row wins the rare hard question and is globally
best. A local race can be statistically precise and still recommend the wrong
region if it has no random restart or direct coverage. Conversely, suppose
neighbor outcomes are anti-correlated because changing an early solver changes
all downstream prompts. Pairing then increases the variance of the difference;
an ungated method spends more to learn less. These examples show why a
similarity gate and global exploration are part of the method's validity, not
optional tuning.

## Recommended research position

Treat SG-RR as a candidate implementation only after the nine-model trace is
complete. In the paper, compare it against:

1. uniform direct allocation;
2. random search with the same realized-dollar cap;
3. AgentOpt's selectors, including its cost-aware parameter settings;
4. a synchronized same-question elimination baseline (SySRs-style);
5. robust linear pure exploration with the row feature map;
6. Hybrid Feedback-style direct-versus-paired allocation; and
7. CACR/SCCR as the ungated/gated local-racing ablations.

If SG-RR does not beat these methods with uncertainty intervals on held-out
questions, the publishable result can instead be a careful negative finding:
Hamming similarity predicts paired score correlation in some retry workflows,
but does not reliably reduce the cost of selecting the best complete row.

