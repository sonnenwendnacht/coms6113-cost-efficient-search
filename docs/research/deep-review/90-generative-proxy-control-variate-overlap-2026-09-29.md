# Generative-proxy control-variate overlap

## Primary source

Ma et al., *Best-Arm Identification with Generative Proxy* (PROBE),
arXiv:2607.06879v1: [paper](https://arxiv.org/html/2607.06879).

PROBE is a direct prior for control-variate best-arm search. It pairs each
costly reward with a cheap correlated proxy whose mean is estimated offline,
learns the unknown correlation online, and uses an OLS residual-variance upper
certificate rather than a plug-in variance estimate. Its phase-elimination
algorithm is designed to remain fixed-confidence correct while learning the
variance reduction.

## Consequence for CW-CV-TT

An already-paid complete retry row is not a cheap proxy in PROBE's sense. Its
full workflow charge may be as large as the candidate's, and its mean is not
known merely because a few cells were observed. A hub can help only through
amortization or cached complete cells. We must compare against a PROBE-style
control-variate baseline wherever a genuinely cheap proxy is available, and we
must not describe OLS residualization or conservative variance certification as
new by themselves.

The defensible remaining boundary is narrower than generic control variates:

- every reward and hub value is a final score from a complete retry workflow;
- the hub is a multi-row, same-question statistical anchor rather than a cheap
  scalar proxy;
- retry reach makes both path cost and later-attempt observations endogenous;
- final correctness is answer-key based while the deployment verifier is blind;
- row calls have additive realized costs rather than PROBE's cheap-proxy model.

If the implementation reduces to OLS residuals plus phase elimination under
fixed independent arm costs, it is a PROBE adaptation and should be reported
that way. A stronger project result requires an explicit censored/path-cost
estimator or an empirical break-even regime that survives PROBE, covariance-
adaptive BAI, CW-PTT, SySRs, and direct resource-aware baselines.
