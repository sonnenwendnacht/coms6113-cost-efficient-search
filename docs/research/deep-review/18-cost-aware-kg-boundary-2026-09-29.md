# Cost-aware knowledge-gradient boundary

Research note prepared 2026-09-29. This is a source audit, not an
experiment or a novelty claim. No traces, held-out answers, model calls, or
selector replays were used.

## Finding

Cost-aware acquisition is established. A paper cannot claim novelty merely
because it divides expected improvement or knowledge gain by a known model
price. The closest primary source is Xie et al., *Cost-aware Bayesian
Optimization via the Pandora's Box Gittins Index* (NeurIPS 2024). In the
independent finite Pandora's Box setting, their Gittins index is Bayesian
optimal under an expected budget after scaling the cost by a multiplier
`lambda`; the paper states this as a theorem. Their extension to correlated
Bayesian optimization plugs the current posterior into the same acquisition
equation and uses `lambda` as a budget-matching parameter. Their paper also
describes an anytime dynamic-decay variant.

Primary source: [Xie et al. on arXiv](https://arxiv.org/abs/2406.20062),
especially the statements corresponding to the independent Pandora's Box
setting, the budget theorem, and the posterior PBGI construction.

This directly overlaps with any proposal of the form

```text
choose c = argmax_c KG(c) / predicted_cost(c)
```

or “use a Gittins/KG score and tune a cost multiplier.” Such a score is still
useful as a baseline or a component, but it is not by itself Algorithm 2's
contribution.

The boundary is broader than PBGI. Cost-weighted multiobjective KG already
defines a KG-per-cost acquisition and studies its consistency; cost-constrained
Bayesian optimization already studies strict budgets and multi-step rollout
approximations. Sequential-sampling work also studies adaptive stopping with
different sample costs. These are reasons to treat a cost ratio, a tuned
multiplier, and a stopping rule as established building blocks rather than a
new central idea.

Related primary sources are [Buckingham et al., cost-weighted
multiobjective KG](https://arxiv.org/abs/2302.01310), [Astudillo et al.,
multi-step budgeted BO](https://papers.nips.cc/paper_files/paper/2021/hash/a8ecbabae151abac7dbde04f761c37-Abstract.html), and [Chick and
Frazier, sequential sampling with economics of selection
procedures](https://pubsonline.informs.org/doi/10.1287/mnsc.1110.1425).

Similarity through a feature hierarchy is also established. Mes, Powell, and
Frazier's *Hierarchical Knowledge Gradient* (JMLR 2011) represents alternatives
with categorical/numeric attributes and uses aggregate estimates so one
measurement can improve beliefs about many alternatives. It explicitly relates
the construction to correlated KG and proves consistency under its model. A
one-hot or hierarchical feature prior by itself is therefore not novel. The
remaining distinction for SC-KG would have to be the observation and cost
contract: a measured unit is a complete retry row on a question, pair actions
can share question difficulty, and the charge is a realized path cost.

Primary source: [Mes, Powell, and Frazier, Hierarchical Knowledge
Gradient](https://jmlr.csail.mit.edu/papers/v12/mes11a.html).

Recent LLM-evaluation work makes the same caution concrete. SySRs uses
synchronized query blocks and successive elimination for correlated model
outcomes, so matched-question elimination is a required baseline rather than a
new contribution. PULSE uses low-rank predictions for missing model-by-example
cells together with residual correction and martingale confidence bounds;
prediction alone is not treated as a valid observation. Generative Proxy BAI
similarly pairs a cheap correlated proxy with a costly reward and calibrates a
control-variate residual before claiming fixed-confidence savings.

Primary sources: [SySRs](https://arxiv.org/html/2606.07726),
[PULSE](https://arxiv.org/html/2605.10405), and [Generative Proxy
BAI](https://arxiv.org/html/2607.06879). These works reinforce the proposed
separation: use similarity to prioritize or reduce residual variance only when
its relation is calibrated; use direct evidence or a valid residual-correction
bound for certification.

## What changes in our setting

The row search has a different observation contract from the classical
independent Pandora problem:

* A paid action is one complete `(row, question)` execution. It includes the
  fixed checker and whatever retries the checker reaches. We do not buy a
  workflow prefix or a partial continuation in Algorithm 2.
* The offline final-quality signal `Q` is scored with the answer key only
  after the run. The checker signal that controls retries is answer-key blind.
  A deployed system therefore cannot use an answer-key correctness bit while
  searching; a live method must name its observable quality signal separately.
* Two complete rows run on the same question can have correlated measurement
  noise because question difficulty is shared. This is a sampling covariance,
  distinct from posterior covariance over unknown row means.
* A row's charge is a realized path cost. Its tariff coefficient may be known,
  but token counts and the number of reached retries are revealed by the
  execution. A fixed per-row price is therefore a proxy, not the realized
  charge used for an honest search ledger.

These differences motivate using correlated KG as a *Bayesian allocation
heuristic* while keeping a separate confidence or interval mechanism for
elimination and recommendation. They do not imply that SC-KG is theoretically
optimal.

## Existing stopping and budget results we must not duplicate

Xie et al. use PBGI to connect an acquisition rule with cost-aware stopping.
Xie et al., *Cost-aware Stopping for Bayesian Optimization* (2025), makes
the boundary especially clear: the PBGI/LogEIPC stopping rule halts when no
unevaluated point has positive one-step expected gain relative to its cost,
and proves a cost-adjusted simple-regret guarantee for that pairing. The same
paper explains that in the independent discrete setting a cost multiplier can
be selected to meet an expected budget, while in the general correlated
setting Bayesian optimality and budget matching do not automatically carry
over.

Primary source: [Cost-aware Stopping for Bayesian Optimization](https://arxiv.org/abs/2507.12453), especially the discussion of the stopping rule,
the “no worse than immediate stopping” result, and the independent-versus-
correlated budget distinction.

The 2026 *Price of Knowledge* paper goes further for costly observations in
correlated-action Gaussian-process bandits: it defines cost-adjusted
information-gain complexities and gives C3-GP and GP-C-LUCB regret bounds.
That work is a warning against claiming that a heuristic cost ratio is a
general correlated-cost theorem. It also provides a strong related-work
baseline if the project later wants regret rather than final best-row
identification.

Primary source: [Schur, Lago, and Fiez, *The Price of Knowledge*](https://proceedings.mlr.press/v337/schur26a.html).

## A narrower defensible Algorithm 2 statement

The current SC-KG design should be described as follows:

> A structured, correlated-Gaussian allocation heuristic for complete retry
> rows. It models row means with categorical main effects, pairwise slot
> interactions, and an explicit unstructured residual; it models same-question
> pairing separately; it scores single-row and paired actions by posterior
> decision value; and it charges every realized cell cost. It uses confidence
> intervals or finite-population bounds—not the posterior alone—to eliminate
> rows and certify the final recommendation.

The phrase “structured” refers to a finite configuration prior, not to shared
workflow execution. The phrase “correlated” must state whether it means
posterior row-mean covariance, same-question measurement covariance, or both.
The method should never call a posterior prediction for an unvisited row a
measured result.

The most credible novelty hypothesis is therefore conditional and empirical:

> In complete-row retry search with heterogeneous realized costs and
> same-question paired noise, does separating structural transfer from paired
> covariance reduce the *search bill needed to select a good row* versus
> independent-arm cost-aware methods, PBGI/Gittins-style allocation, and a
> synchronized paired baseline, while maintaining a pre-registered error or
> regret tolerance?

This wording makes the burden explicit. If PBGI or a generic correlated KG
baseline matches SC-KG, the contribution is a careful benchmark and a negative
result, not a new algorithm. If the gain comes only from a better prior or
from using answer-key quality during search, the claim must be narrowed or
rejected.

## Design consequence

Do not tune a cost multiplier on held-out audit questions. Register any
multiplier schedule using only search information, or report it as a method
parameter and include sensitivity. Distinguish these three choices:

1. **Expected-cost objective:** a Lagrange multiplier can be reasonable, but
   report expected versus realized spend.
2. **Hard dollar cap:** reserve the maximum possible charge before each action;
   otherwise call it a soft cap and report overshoot.
3. **Fixed search budget:** use the budget only to compare allocation quality;
   do not claim that an acquisition ratio enforces a cap.

For a hard cap, the admission check is conceptually

```text
spent + reserved + maximum_new_action_charge <= cap.
```

The maximum charge must include all retries that the declared deployment
protocol can reach. If that bound is too conservative, the paper should use a
soft cap with an explicit overshoot statistic rather than silently spend past
the limit.

## What remains open

The literature does not answer the project-specific question of how much
same-question pairing helps when the retry checker changes which calls are
reached and the quality target is the completed workflow's final correctness.
It also does not validate the proposed 217-feature row prior for the chosen
models. Those are empirical hypotheses. They require a fixed search split,
hidden audit split, leakage-safe priors, and direct comparisons at equal
realized search cost.

For a rigorous fallback certificate, the closest correlated-BAI result is
Saad, Blanchard, and Verzelen's covariance-adaptive best-arm identification:
same-round arm vectors permit confidence tests based on pairwise difference
variance under adaptive allocation and stopping. In our setting, a same-round
vector means the same randomly sampled question evaluated by the paired rows.
Fixed benchmark questions need a finite-population or martingale argument;
they should not be called i.i.d. merely because they are listed in a dataset.
The paper is therefore a useful certificate baseline, not a theorem for our
retry traces. See [Covariance Adaptive Best Arm Identification](https://arxiv.org/abs/2306.02630).
