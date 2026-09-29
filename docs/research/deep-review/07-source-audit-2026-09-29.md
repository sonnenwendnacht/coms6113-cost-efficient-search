# Source audit: correlated rewards, costs, and retry cascades

Prepared 2026-09-29. This is a source-verification record, not a novelty
claim and not an experiment report. I checked the primary arXiv HTML versions
where available and the PMLR paper/PDF for Li and Cheung. No local experiment
traces were opened for this audit.

## The observation we need to model

For a complete ordered retry configuration `c` and a task `q`, our intended
deployment observation is a pair

```text
Y(c, q) = final correctness after the fixed retry/checker policy
C(c, q) = sum of the reached-call input-token charges
```

The coefficient multiplying input tokens can be known before a call. The
realized total `C` need not be known before the workflow runs: a verifier may
accept an answer early, a failed attempt may trigger a later retry, and the
next prompt can contain earlier output. Thus `C` can be statistically
dependent on `Y` and on intermediate outcomes. For two configurations tested
on the same task, the outcomes can also be correlated because task difficulty
is shared. If a profiling action can execute a shared prefix or a reached
continuation, the action exposes only a partial set of the complete rows and
its price depends on the path actually reached.

This is more specific than saying that an arm has a “cost.” A paper may cover
one of the following without covering all of them:

1. a random cost paired with one arm reward;
2. multiple arm rewards observed for the same stochastic unit;
3. a direct pairwise/dueling observation;
4. a partial, stateful retry execution whose number of calls is random.

The papers below cover the first three ingredients in different combinations.
The fourth and their joint interaction remain an open modeling question, not
an established gap.

## Primary-source findings

### Hybrid Feedback (Zeng et al.)

Primary source: [arXiv:2605.05745v1](https://arxiv.org/abs/2605.05745), with
[full HTML](https://arxiv.org/html/2605.05745v1). The paper is dated 7 May
2026. It studies fixed-confidence best-arm identification in a generalized
linear bandit. Each arm has a known feature vector and a shared unknown
parameter. In one round the learner chooses either:

- an **absolute** query of one arm and receives a reward from one GLM; or
- a **dueling** query of an arm pair and receives a binary relative outcome
  from another GLM applied to the feature difference.

The two observations share the latent parameter, but they are different
feedback channels. The paper's Problem Formulation states the arm and pair
observation models explicitly (HTML Sections 2 and 4). Its cost-aware
extension assigns each action a known positive cost `c_a`, accumulates the
deterministic sum of those costs, and minimizes total cost until a
fixed-confidence stopping rule fires (HTML Section 4.2, especially the cost
model and equations (6)–(7)). The cost-aware design normalizes information per
unit cost and has a high-probability total-cost bound.

**What it establishes for us.** Choosing between an individual and a paired
information source by information per dollar is already a formal BAI idea.
An algorithm that merely adds “direct versus paired” acquisition or divides a
paired uncertainty score by its predicted cost is therefore not a new
primitive.

**What it does not establish for our setting.** A dueling query is one direct
binary observation generated from a latent feature difference. It is not two
complete retry cascades run on a MathQA task, and the paper does not model a
random number of downstream calls, path-dependent prompts, or a cost/reward
joint distribution for a cascade. Its known `c_a` is also different from our
known price *rate* plus unknown realized token count. The GLM feature and
shared-parameter assumptions cannot be silently applied to a Hamming-neighbor
configuration graph.

### Generative Proxy (Ma et al.)

Primary source: [arXiv:2607.06879v1](https://arxiv.org/abs/2607.06879), with
[full HTML](https://arxiv.org/html/2607.06879v1). The paper is dated 8 July
2026. Each pull of arm `i` returns a paired costly reward `X_{i,l}` and proxy
score `Y_{i,l}` for the same sampled unit. The paper assumes these pairs are
i.i.d. within an arm and independent across arms, with an arm-specific
correlation. The proxy's marginal mean is estimated offline and treated as
known. The control variate reduces the residual variance by the correlation;
the paper's PROBE algorithm learns a valid upper certificate on residual
variance rather than plugging an anti-conservative sample estimate into a
confidence bound (HTML Sections 2.2–4).

**What it establishes for us.** Learning whether a correlated side signal is
useful and paying an explicit calibration cost is already a rigorous best-arm
technique. A gate based only on a plug-in correlation or paired variance is not
enough for a correctness claim. If our neighboring row is treated as a proxy,
PROBE is a required comparison or conceptual baseline.

**What it does not establish for our setting.** Their proxy is cheap and
available with every costly reward pull; proxy-only scores can be generated
offline, and the proxy mean is known. A neighboring retry row is normally
another full cascade, not a free score. Its cost may be comparable to the
target row and its reached retries can differ. The paper also assumes one
paired reward/proxy observation per arm pull and does not provide a
path-dependent cascade-cost model. Recasting a full neighboring row as a
“proxy” without charging its calls would be invalid.

### Cost Aware Best Arm Identification (Kanarios, Zhang, and Ying; CABAI)

Primary source: [arXiv:2402.16710v2](https://arxiv.org/abs/2402.16710), with
[full HTML](https://arxiv.org/html/2402.16710v2). The arXiv page identifies v2
as 1 July 2024. CABAI gives every arm a reward distribution and a cost
distribution. A pull returns a reward-cost pair, and the goal is to identify
the highest expected-reward arm while minimizing expected cumulative testing
cost. The important detail is its explicit product assumption: the pair is
sampled from `nu_mu_a × nu_c_a`, so reward and cost are independently
generated for the selected arm (HTML Section 2, equations around the problem
formulation). It assumes positive bounded costs and a natural exponential
family for reward. CTAS is an asymptotically cost-optimal Track-and-Stop rule;
Chernoff Overlap is a lower-computation alternative.

**What it establishes for us.** Heterogeneous testing cost changes the
allocation and stopping rule; using an ordinary equal-cost BAI method and
reporting only the number of pulls can be suboptimal. Separating profiling
cost from the quality of the configuration used after selection is directly
relevant to our evaluation table.

**What it does not establish for our setting.** CABAI's cost and reward are
independent conditional on an arm. It therefore does **not** cover a retry
cascade in which a wrong verifier decision both changes `Y` and triggers a
costly extra call. It also observes one selected arm per round and has no
same-question cross-arm covariance or reusable prefix. If we cite CABAI, the
correct statement is that it is a cost-aware arm-level baseline whose
independence and one-arm-per-pull assumptions our workflow violates.

### Covariance Adaptive BAI (Saad, Blanchard, and Verzelen)

Primary source: [arXiv:2306.02630v2](https://arxiv.org/abs/2306.02630), with
[full HTML](https://arxiv.org/html/2306.02630v2). The arXiv page identifies
the revised version as 20 December 2023 and gives the NeurIPS 2023 reference.
The paper models a joint vector of `K` arm rewards. At each round the learner
chooses a subset of arms and receives all selected rewards for the same time
point. The vectors are i.i.d. over rounds; rewards are bounded or multivariate
Gaussian, and there is a unique best mean arm. The learner estimates unknown
cross-arm covariance and uses it in fixed-confidence best-arm identification.
Its complexity can depend on the variance of a paired difference rather than
the sum of independent variances (HTML Sections 1–2 and the Gaussian
discussion).

**What it establishes for us.** Same-task paired outcomes and covariance
adaptive allocation are established statistical ideas. A one-slot model change
can be tested on the same questions to reduce variance, but the benefit must
be estimated and justified; a graph label alone is not a covariance model.

**What it does not establish for our setting.** The paper counts query cost as
the number of revealed arm entries and contains no monetary or random
resource-cost process. It does not model retries, early termination, verifier
states, or a cost correlated with the reward vector. Its subset query reveals
selected arm rewards simultaneously; it is not a shared-prefix execution in
which some calls are skipped and later calls depend on earlier outputs.
Applying its covariance gains requires checking whether complete row outcomes
are i.i.d. across tasks and whether every paired row outcome is actually
observed at the same task. A future extension combining this covariance model
with a path-dependent resource process would need a new theorem or a clearly
defined reduction.

### Best Arm Identification with Resource Constraints (Li and Cheung)

Primary sources: [PMLR article](https://proceedings.mlr.press/v238/li24c.html)
and the [30-page PDF](https://proceedings.mlr.press/v238/li24c/li24c.pdf),
PMLR volume 238, AISTATS 2024. The paper defines BAI with one or more resource
types. Pulling arm `k` yields a reward `R_k` and consumes random resources
`D_{1,k},...,D_{L,k}`. Crucially, its model allows `R_k` and the resource
consumptions to be **arbitrarily correlated** (PDF Section 2, model and
equations on pages 2–3). It treats deterministic consumption as a special
case, and analyzes stochastic consumption under a hard total-resource budget.
SH-RR uses successive halving with resource rationing and bounds the failure
probability of identifying the best mean-reward arm. The PMLR abstract also
explicitly records different rates for deterministic and stochastic resource
consumption.

**What it establishes for us.** Outcome-dependent cost by itself is not a
new gap. If a complete retry configuration is collapsed into one indivisible
arm pull, then `(R,D)=(Y,C)` is already within this paper's broad
arm-level model after scaling costs to bounded resources. A claim such as
“we are the first to allow cost correlated with success” would be false.
The paper is also the closest fixed-budget reference for an experiment that
must not exceed a profiling resource cap.

**What it does not establish for our setting.** Its arm pull is indivisible:
the learner chooses one arm and receives that arm's outcome/resource tuple.
There is no cross-arm same-question covariance, no simultaneous subset query,
and no reusable execution prefix. The theory assumes bounded resource
consumption (`D` in `[0,1]`); raw token dollars must be normalized or bounded
before invoking it. It optimizes fixed-budget identification failure
probability, whereas our proposed table freezes a recommendation and measures
quality on a separate held-out task set. If profiling can purchase a partial
retry continuation that informs several complete rows, the arm-pull reduction
loses the central execution-sharing feature.

## Does “outcome-dependent cost” remain a possible contribution?

Not by itself. The source audit gives the following boundary:

| Component | Closest verified source | Covered? |
| --- | --- | --- |
| Random arm cost correlated with that arm's reward | Li and Cheung, BAIwRC | Yes, at an indivisible arm-pull level |
| Independent heterogeneous reward/cost and cost-minimal fixed-confidence BAI | CABAI | Yes, but its independence assumption is weaker/different |
| Same-task cross-arm covariance and paired differences | Covariance Adaptive BAI | Yes, without monetary/path costs |
| Absolute versus pairwise information with heterogeneous known action costs | Hybrid Feedback | Yes, under a shared GLM and fixed action costs |
| Cheap correlated proxy with an online variance certificate | Generative Proxy | Yes, when the proxy is cheap/available and has the stated paired model |
| A retry cascade with skipped calls, stateful continuations, and realized cost depending on the path | None of these papers by itself | Not established by this audit |
| The combination of path-dependent cascade cost, cross-row same-task covariance, and optional shared-prefix/continuation queries | No verified direct match here | Open question; not a novelty claim |

The safe research statement is therefore: **we will test whether these known
ideas retain their guarantees or practical savings when a single observation
is a complete retry cascade with endogenous cost and when a profiling action
may expose shared execution state.** We must compare against Li/CABAI-style
cost-aware baselines, covariance-aware paired allocation, and the Generative
Proxy control-variate idea before claiming an algorithmic contribution.

## Consequences for our model and experiment

1. Keep the known coefficient and realized charge separate. The coefficient
   is a price rate; `C(c,q)` is the realized total. Report both the search
   budget and the cold deployment charge.
2. Do not label one full row's observed cost as a fixed arm cost unless the
   row's retry path is deterministic. If the selector sees intermediate
   reached/failure information, record the path and charge every call.
3. If we use same-question pair comparisons, report the actual paired cells
   and their two realized costs. Do not call the pair a cheap dueling query.
4. If a neighboring row is used as a proxy, charge it as a real cascade and
   distinguish this from Generative Proxy's cheap proxy setting. Any variance
   gate should be treated as a heuristic unless a valid time-uniform
   certificate is supplied.
5. Preserve an iid/no-covariance control and an adversarial non-smooth control.
   A gain that disappears when row labels are permuted is evidence about the
   structural assumption, not proof of a new theorem.
6. State the objective precisely. A fixed profiling budget and held-out
   recommendation quality is closer to fixed-budget BAI; expected cost until
   fixed-confidence identification is closer to CABAI/Track-and-Stop. They
   are different experiments.

## Source availability and limits of this audit

The five cited primary sources were accessible on 2026-09-29 through the
linked arXiv HTML pages or the PMLR article/PDF. This audit verified the model
definitions and the claims above from those primary texts. It did not audit
code repositories, reproduce theorem constants, inspect unpublished
supplements, or perform a complete search for papers that combine all three
ingredients. “No direct match in this audit” must not be rewritten as “no
prior work exists.”
