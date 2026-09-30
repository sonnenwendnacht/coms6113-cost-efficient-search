# 140: Correlated-arm and costly-observation boundary (2026-09-30)

Two recent lines of best-arm work narrow the claim that a similarity-aware
selector could make here.

* Saad, Blanchard, and Verzelen's [Covariance-adaptive best arm
  identification](https://proceedings.neurips.cc/paper_files/paper/2023/hash/e82ef7865f29b40640f486bbbe7959a7-Abstract-Conference.html)
  allows dependent arm rewards to be sampled together and estimates covariance
  to reduce identification effort. Gupta, Joshi, and Yağan's [correlated
  multi-armed bandit model](https://arxiv.org/abs/2109.04941) uses prior
  conditional-reward bounds to avoid sampling non-competitive arms. Therefore,
  “rows are correlated” or “sample related rows together” is not a new
  contribution by itself.
* Schur, Lago, and Fiez's [The Price of Knowledge: Optimal Algorithms for
  Costly Bandits](https://proceedings.mlr.press/v337/schur26a.html) treats
  observations as optional actions with heterogeneous costs and develops
  cost-adjusted information measures. Wu et al.'s [CAET](https://proceedings.mlr.press/v258/wu25c.html)
  already handles cost-aware pairwise pure exploration. A new selector cannot
  claim the first cost-aware correlated or pairwise allocation rule.

The project-specific measurement model remains narrower and more awkward than
these baselines. A probe is a complete configuration row on one registered
question, and an edge probe executes both complete endpoints unless exact
eligible cells are already cached. Each cell returns a terminal reward and a
retry-dependent charge; the charge is not known from the row alone. The target
is a row mean over a finite question bank, followed by deployment on held-out
questions. The cache may share an already-paid anchor cell across several
comparisons, but it does not create a free observation or a workflow-prefix
reuse.

This gives a defensible Algorithm 2 boundary rather than a novelty claim:
adapt correlated-arm allocation and cost-adjusted information scoring to a
finite question-indexed cell ledger with response-dependent prices, while
requiring complete-row confirmation. A practical control should include a
covariance-adaptive or correlated-arm allocation (when its assumptions can be
made explicit), CAET-style pairwise allocation, and direct row racing. CG-RTE
may only be credited for an improvement if it lowers **unique eligible cell
charges** at equal held-out quality and equal error protection. A narrower
confidence interval, a larger raw correlation, or fewer nominal probes is not
enough.

The risk is especially high when retry paths make endpoint charges unequal or
when the covariance model is learned after the edge was selected. The safe
fallback is the conservative sum of endpoint/residual radii and a direct
probe. Any covariance-based score must reserve confidence for model selection
and report a separate calibration cost. No implementation or experiment is
claimed by this note.
