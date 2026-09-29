# Two structured-search alternatives without workflow-prefix reuse

Prepared 2026-09-29. This is a literature synthesis and design proposal. No
new experiment, replay, or model/API call was run for this note.

## Scope and objective

A row is a complete assignment of models to all solver, verifier, and retry
slots. A paid evaluation of row \(c\) on question \(q\) executes the complete
workflow and returns

\[
 (Y(c,q), C(c,q)),
\]

where \(Y\) is the final answer-key-blind verifier outcome and \(C\) is the
realized input-token charge for every call that was reached. The selector never
sees the answer key. A later held-out audit estimates
\[
 \mu(c)=E_q[Y(c,q)] \quad\text{and}\quad \kappa(c)=E_q[C(c,q)].
\]

The primary search question is how to maximize \(\mu(c)\) after a fixed profiling
budget \(B_s\). A deployment-cost cap or scalar utility such as
\(\mu(c)-\lambda\kappa(c)\) must be registered separately. Search cost,
independent audit cost, and cold deployment cost are different quantities.

The designs below use similarity only to decide which complete row to measure
next. They never fill an unmeasured row from a neighbor, reuse a workflow
prefix, or treat an unreached retry as a failure. A model prediction is a
proposal or an uncertainty score; the final recommendation must have direct
observations and a fresh audit.

## What the literature already covers

Several ingredients are established and should be treated as baselines or
constraints:

- **BOCS** fits a sparse polynomial model over binary/combinatorial variables
  and chooses a structure with a Bayesian acquisition function. Its purpose is
  to exploit low-order interactions in expensive combinatorial optimization
  ([Baptista and Poloczek, ICML 2018](https://proceedings.mlr.press/v80/baptista18a.html)).
- **COMBO** puts a Gaussian process on the graph Cartesian product of
  categorical variables, using an ARD diffusion kernel and a sparsity-inducing
  prior to learn which variables matter
  ([Oh et al., NeurIPS 2019](https://proceedings.neurips.cc/paper/2019/hash/2cb6b10338a7fc4117a80da24b582060-Abstract.html)).
- **Casmopolitan** combines a global categorical surrogate with local
  trust-region optimization and probabilistic reparameterization
  ([Wan et al., ICML 2021](https://arxiv.org/abs/2102.07188)).
- **Hyperband/BOHB** use a nested resource budget and successive halving;
  BOHB replaces random configuration proposals with a model-based sampler
  ([Hyperband](https://arxiv.org/abs/1603.06560),
  [BOHB](https://arxiv.org/abs/1807.01774)). **TuRBO** runs local Bayesian
  models to avoid a single globally homogeneous surrogate
  ([Eriksson et al., NeurIPS 2019](https://proceedings.neurips.cc/paper/2019/hash/6c990b7aca7bc7058f5e98ea909e924b-Abstract.html)).
- Cost-aware Bayesian optimization has a direct warning for this project:
  Xie et al. show that expected improvement per unit cost can be arbitrarily
  worse than an optimal policy and develop a Pandora's-Box Gittins index
  ([NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/file/d14c355d5e88cff437a6303d2d716252-Abstract-Conference.html)).
  A cost-divided acquisition is therefore a baseline or engineering heuristic,
  not a theoretical contribution by itself.
- ParamILS/FocusedILS already use one-change local moves and racing, and SySRs
  already use matched-question model comparisons. CACR/SCCR in this repository
  already use paired rows, realized costs, and a safety gate.
- Robust pure-exploration work shows why a structural model needs an explicit
  misspecification treatment. In particular, MISLID adapts to a bounded
  deviation from a linear model, and the linear advantage can disappear as
  misspecification grows
  ([Réda, Tirinzoni, and Degenne, NeurIPS 2021](https://proceedings.neurips.cc/paper/2021/hash/d5fcc35c94879a4afad61cacca56192c-Abstract.html);
  [Alieva, Cutkosky, and Das, ICML 2021](https://proceedings.mlr.press/v139/alieva21a.html)).

Consequently, “use a Hamming graph,” “fit a categorical Bayesian optimizer,”
“run simulated annealing,” or “use paired questions” is not a novelty claim.
The narrow possible gap is a complete retry-row setting in which the outcome and
the cost of one evaluation are jointly observed, cost depends on which
attempts are reached, and a structural model can be rejected safely when it is
wrong. That gap must be tested against ordinary categorical BO, SySRs, CACR,
SCCR, a cost-aware hybrid-feedback method, and direct unstructured allocation.

## Design A: Robust Structured Bayesian Pure Exploration (RS-BPE)

### Structural assumption

Represent row \(c=(c_1,\ldots,c_d)\) with one-hot slot features, optional
one-hot pair interactions, and a learned similarity kernel over model choices.
Use a robust mean model
\[
 \mu(c)=x(c)^\top\theta+r(c),\qquad |r(c)|\le \rho.
\]
The parameter \(\rho\) is a registered misspecification allowance, not a
quantity tuned on the audit set. A hierarchical prior can shrink related model
choices together, but a row with no direct observations still has only a
prediction, not a measured score. Fit a separate cost model for \(C(c,q)\);
because retries make cost outcome-dependent, it should predict a distribution
or an upper quantile from reached-call features rather than one fixed row
price.

This assumption is useful if changing one slot has a roughly additive effect,
model choices form clusters, or only a few slot interactions matter. It is
dangerous if one model changes prompts or stopping behavior for all later slots.
The robust residual term and a global unstructured fallback are therefore
required.

### Acquisition objective

At time \(t\), maintain a direct empirical mean and interval for every measured
row, plus a robust surrogate interval for every candidate:
\[
 L_t(c)=x(c)^\top\hat\theta-\operatorname{rad}_t(c)-\rho_t,\qquad
 U_t(c)=x(c)^\top\hat\theta+\operatorname{rad}_t(c)+\rho_t.
\]
rad contains observation noise and parameter uncertainty. The practical
misspecification estimate \(\rho_t\) is the upper registered residual quantile
on held-out search observations; it is never selected after looking at audit
outcomes. If residual checks fail, increase \(\rho_t\), disable structural
elimination, and revert to direct row intervals.

Let \(b_t(c)\) be a conservative estimate of the incremental cost of one new
complete-row question. A useful fixed-budget acquisition is
\[
 a_t(c)=
 \frac{\text{expected reduction in the upper bound on simple regret after
       measuring }c}
      {b_t(c)}.
\]
A simpler implementable proxy is
\[
 a_t(c)=
 \frac{[U_t(c)-\max_{c'\ {\rm directly\ measured}}L_t(c')]_+
       +\eta\,{\rm design\_gain}_t(c)}
      {b_t(c)},
\]
where design_gain is the expected reduction in the surrogate parameter
ellipsoid (a D-optimal or A-optimal criterion). The score is an allocation
heuristic; conservative intervals, not the acquisition score, govern
elimination.

### Procedure

1. Spend a preregistered scout budget on diverse complete rows (random rows
   plus one row per slot/model where feasible). Use a fixed question block and
   record every reached call and its cost.
2. Fit the structured mean and cost models using search questions only.
3. Form robust intervals for all candidate rows. Keep a directly measured
   incumbent and never report a purely predicted row.
4. Compute a_t(c) for unmeasured rows. Include a fixed global-random
   probability and a fixed amount of direct design exploration, so a wrong
   structure cannot permanently trap the search.
5. Evaluate the selected complete row on a fresh block. A block can be paired
   with the incumbent on the same questions for variance reduction, but both
   full workflows are run; there is no prefix reuse.
6. Update the models, residual test, cost quantiles, and direct intervals.
   Eliminate c only when its robust upper bound is below the incumbent's lower
   bound by the registered practical margin. If the fit fails its residual gate,
   inflate rho_t or use an unstructured confidence interval.
7. Reserve a final direct confirmation block for the recommended row and then
   freeze the recommendation before the held-out audit.

### Pseudocode

~~~
RS-BPE(rows, search_questions, budget B):
    S <- diverse scout rows; direct_evaluate(S, fixed scout block)
    while realized_cost < B:
        fit robust slot/interactions model on all search observations
        fit a separate upper-quantile cost model
        compute direct confidence intervals and robust surrogate intervals
        if residual test fails:
            use unstructured direct intervals for elimination
        candidates <- unmeasured rows plus measured rows needing confirmation
        c <- argmax acquisition(c) / conservative_incremental_cost(c)
              with global-random probability epsilon_t
        direct_evaluate(c, next fixed question block)
        update observations and actual cost
        prune only rows whose robust UCB < incumbent LCB - margin
    c_star <- best directly observed surviving row
    direct_evaluate(c_star, fresh confirmation block)
    return c_star, direct evidence, search ledger, residual diagnostics
~~~

### Why this is different from CACR/SCCR

CACR/SCCR use a local edge and a paired difference as the central object.
RS-BPE treats paired outcomes as an optional variance reduction, while its main
benefit comes from a low-dimensional surrogate that can prioritize unvisited
complete rows. The model is allowed to propose a two-slot change or a row far
from the incumbent when the posterior says it is informative. Its safety
mechanism is residual inflation/model disablement, rather than an edge-specific
variance gate.

This is still not automatically new. It is a retry-aware adaptation of
COMBO/BOCS/Casmopolitan plus robust pure exploration. A credible empirical
distinction would require: (i) a separate cost model for realized cascades,
(ii) direct-vs-structured allocation at equal realized cost, and (iii) a
misspecification stress test showing that RS-BPE falls back instead of making
confident wrong eliminations.

### Benefits and failure modes

If low-order structure holds, estimating O(dM+d^2M^2) coefficients can avoid
testing all M^d rows. The gain is largest when the budget is small, the number
of slots is large, and the true mean is smooth in learned model similarity. If
effects are highly non-additive, rho must become large and the method should
approach unstructured search; this is the intended behavior, not a failure to
hide.

The cost model can be misspecified in the opposite direction: a high-quality
row may have more successful retries and therefore lower or higher realized
cost depending on the checker. Report cold deployment cost separately and do
not optimize search cost as though it were deployment cost.

## Design B: Metric-Annealed Trust-Region Elimination (MATRE)

### Structural assumption

MATRE does not impose a globally additive model. It learns a slot-specific
distance from observed complete rows. For slot j and two model choices u,v,
estimate a disagreement or substitution distance from paired question outcomes
on rows differing at that slot:
\[
 d_j(u,v)
 = {\rm shrink}\!\left(
   E_q[\,|Y(c_{j\leftarrow u},q)-Y(c_{j\leftarrow v},q)|\,]
   \right).
\]
Use hierarchical shrinkage and retain a wide interval until enough pairs are
observed. The row distance is
\(D(c,c')=\sum_j w_j d_j(c_j,c'_j)\), with weights learned from the same
search records. This learns that two models can be similar even if their names
or Hamming distance suggest otherwise.

The distance must be estimated across several contexts for slot j, not from a
single pair of rows. Otherwise an interaction with the other slots is silently
called a model similarity. Use leave-one-context-out search validation and
allow a separate distance for solver, verifier, and retry positions; a model
can be interchangeable in one position and very different in another.

The extra assumption is local smoothness: within a trust region, the mean
difference is approximately bounded by \(L D(c,c')+\xi\), where \(\xi\) is a
registered violation allowance. Unlike a global GP, this assumption is only
used to choose proposals and elimination candidates inside the region. Every
promoted row receives direct complete-row observations.

### Procedure

1. Initialize with diverse rows and a global scout fraction. Build conservative
   d_j estimates from same-question pairs.
2. Set an initial trust-region radius in the learned metric around the best
   directly observed incumbent.
3. Generate one-slot and multi-slot candidates inside that region. Their
   proposal probability is weighted by low metric distance and high uncertainty,
   not just by Hamming adjacency.
4. Use cost-aware successive elimination within the region. Select the next
   complete row by estimated probability of improving the incumbent divided by
   its upper cost quantile. Pairing on the same question is allowed, but both
   workflows are evaluated.
5. A simulated-annealing temperature controls proposal movement: accept a
   candidate that appears worse with probability
   exp((mu_new-mu_current)/T_t). This is not treated as evidence that the
   candidate is better; it prevents a local trust region from becoming a
   permanent local optimum.
6. Expand the region after repeated uncertainty or residual violations,
   contract it after a registered number of confidently inferior proposals,
   and restart globally with probability epsilon_t.
7. Disable metric-based elimination when a placebo or permuted-slot test shows
   no lower residual variance than random pairs. Keep direct intervals and
   random search active.
8. Confirm the final directly observed row on a fresh block and then audit.

### Pseudocode

~~~
MATRE(rows, search_questions, budget B):
    S <- diverse global scout rows; direct_evaluate(S)
    incumbent <- best direct row
    temperature <- T0; radius <- R0
    while realized_cost < B:
        learn conservative slot distances d_j and row metric D
        learn direct means, paired residuals, and cost upper quantiles
        if metric placebo test fails:
            candidate_pool <- global rows
        else:
            candidate_pool <- rows within radius of incumbent
        with probability epsilon_t:
            c <- global random row
        otherwise:
            c <- argmax_{pool} [
                    probability of improving incumbent
                    + annealing exploration bonus
                  ] / cost_upper_quantile(c)
        direct_evaluate(c, a fixed fresh block)
        update incumbent and confidence intervals
        eliminate only with direct or registered smoothness bounds
        if local progress stalls or violations rise:
            radius <- expand; temperature <- reheat
        else if region is confidently poor:
            radius <- contract; temperature <- cool
    confirm incumbent directly; return incumbent and diagnostics
~~~

A practical implementation should keep a direct interval for every row that has
been evaluated. A local smoothness bound can prioritize and tentatively screen
a neighbor, but a row with no direct observations must not be returned solely
because its predicted mean is high.

### Difference from RS-BPE and current methods

RS-BPE shares statistical strength globally through a fitted feature model.
MATRE shares strength only through a learned local metric and uses an annealed
trust-region path. It can capture clusters and nonlinear substitution effects
that a small additive model misses, but it gives weaker global guarantees. It
also explicitly tests whether its learned metric beats a permuted-slot placebo.

The local move, annealing, trust region, paired question, and racing ingredients
all have close precedents in ParamILS, Casmopolitan, SySRs, common-random-number
ranking, and CACR. The only defensible project-specific angle is the
interaction with full retry cascades and realized per-question cost, plus a
precommitted safety fallback. If the metric does not predict same-question
residuals beyond Hamming distance, MATRE should collapse to its global direct
search control.

In particular, Casmopolitan already learns categorical kernel sensitivity,
searches within Hamming trust regions, and uses restarts. MATRE should therefore
be treated as a diagnostic/control adaptation rather than a likely standalone
paper contribution. The learned outcome-distance diagnostic and a reliable
retry-cost fallback would have to add measurable value beyond that baseline.

## Required comparisons and ablations

Neither design should replace CACR/SCCR before the following comparison is
registered:

1. Random complete-row search with the same realized-cost cap.
2. Uniform synchronized evaluation and SySRs-style paired elimination.
3. AgentOpt's available selector and a cost-aware independent-arm baseline.
4. Categorical BO baselines: BOCS/COMBO or Casmopolitan adapted to direct
   complete-row observations.
5. Hyperband and BOHB, but only with a preregistered question-count fidelity:
   low-fidelity blocks must be fixed independently of outcomes, and promotion
   must be charged by every question and reached call. A small question subset
   is not automatically a valid fidelity because difficulty and retry reach
   rates can differ across questions.
6. CACR and SCCR, including their fixed restart floors.
7. A hybrid absolute/pairwise feedback baseline and, if feasible, a
   generative-proxy control.
8. For RS-BPE: additive-only, interaction-enabled, and structure-disabled
   variants; known versus underestimated or overestimated rho.
9. For MATRE: true metric, learned metric, Hamming metric, and permuted-slot
   placebo; annealing off/on; global-restart floor off/on.
10. Equalize by realized search cost, count all reached solver/verifier calls,
   freeze audit questions until recommendations are fixed, and report final
   cold deployment cost separately.

Report recommendation accuracy, simple regret on exhaustive small spaces,
held-out audit accuracy, search cost, number of complete-row evaluations,
reached-call cost, calibration/model-fitting overhead, and confidence intervals.
A win only at one synthetic smoothness level is not evidence. The iid and
permuted controls should show no systematic similarity gain.

## Decision rule for the group

Start with RS-BPE only if the completed traces show that a registered
low-order or metric model predicts held-out search outcomes and costs better
than an unstructured baseline. Start with MATRE only if the slot-distance
diagnostic predicts paired residual variance beyond Hamming distance. If these
diagnostics fail, retain the negative result and use CACR/SCCR as comparisons,
not as a claimed contribution.

The strongest publishable statement may be conditional:

> Under a measured, bounded structural assumption on complete retry-row
> outcomes, a robust structural allocation rule reaches a target selection
> quality with fewer realized search dollars, while its fallback matches direct
> search when the assumption is wrong.

That statement requires evidence that the assumption is measured before the
audit, that wrong models trigger the fallback, and that the same benefit is not
already explained by SySRs, categorical BO, or AgentOpt.
