# Generative-proxy prior-art boundary (2026-09-29)

This is a research-only source audit. It adds no experiments, traces, selector
replays, or model calls.

## Primary source

Ma, Qin, Zhu, and Zuo, *Best-Arm Identification with Generative Proxy*,
arXiv:2607.06879 (2026):
[paper](https://arxiv.org/html/2607.06879).

## What it establishes

The paper studies fixed-confidence best-arm identification when each costly reward
is paired with a cheap, correlated proxy. The proxy's marginal mean is estimated
offline and treated as known, while its correlation with the costly reward is
learned from the same paired observations. A control-variate adjustment reduces
the effective residual variance by the factor `1-rho^2` when the correlation is
known. The paper's PROBE algorithm uses a one-sided OLS residual-variance
certificate and phase elimination; it explicitly warns that a plug-in estimate of
the residual variance is anti-conservative and can invalidate correctness.

The key separation is between abundant proxy-only data and scarce paired
proxy/reward data. The latter pairing is what makes variance reduction possible;
an offline predictor's ranking accuracy alone does not provide a fixed-confidence
certificate. PROBE therefore pays a calibration cost and keeps a conservative
upper certificate while allocating future samples.

## Boundary for complete retry rows

For COMS6113, a configuration row is a full retry workflow. A possible proxy is a
cheap score or feature computed for the same question/configuration pair—for
example, a smaller evaluator or a model-derived estimate of whether the solver
answer will pass. A vector of row features or a model-similarity prior is not
automatically this kind of proxy. It becomes a useful proxy only after measuring
its relationship to the final held-out quality signal on paired search questions.

This prior art rules out claiming novelty for “use a cheap correlated estimate to
divide expected improvement by cost” or for plug-in residual-variance gating. A
defensible Algorithm 2 can instead make the following narrower contribution:

1. Treat each complete retry row as the paid action and preserve the realized
   token charge, including checker-triggered attempts.
2. Use row-structure features to form a prior over complete rows, and use a
   separately calibrated same-question proxy/pair signal only when it passes a
   conservative residual-variance check.
3. Use a confidence sequence or phase-elimination certificate on direct final
   quality, with an explicit hard cap/reservation ledger, to choose the final row.

The proxy itself may be deployed as a baseline (PROBE-like variance reduction) or
as one component of a structured correlated acquisition rule. Any claimed gain
should be measured against a proxy-assisted baseline, an independent-arm
cost-aware method, and a direct paired sampler at equal realized search cost.

## Relevance to benchmark design

The paper's same-unit pairing maps most naturally to evaluating two rows on the
same question. If the benchmark is a fixed finite list, the protocol must state
whether the goal is the average on that list or a random task distribution. For a
random task target, sample questions in a way that supports i.i.d./martingale
concentration. For a fixed list, use a finite-population confidence argument or
report the search as an empirical fixed-budget comparison; do not silently invoke
the i.i.d. proxy theorem.

