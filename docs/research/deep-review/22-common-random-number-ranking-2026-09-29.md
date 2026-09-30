# Common-random-number ranking prior art (2026-09-29)

Research-only source audit; no experiments, traces, replays, or model calls.

Görder and Kolonko, *Ranking and Selection: A New Sequential Bayesian Procedure
for Use with Common Random Numbers*, arXiv:1410.6782:
[paper](https://arxiv.org/html/1410.6782), study alternatives evaluated under the
same random scenario. Their multivariate-normal model allows dependent outcomes
and unknown covariance. BayesRS takes an initial complete sample, then allocates
fixed simulation batches according to posterior covariance and pairwise dominance
probabilities until the posterior probability of correct selection is high. Their
common-random-number scheme reuses scenario seeds and produces monotone missing
patterns when alternatives receive unequal additional samples.

Evaluating two configuration rows on the same question has the same variance
reduction intuition: question difficulty is a shared random scenario, so the
variance of a difference can be much smaller than the two marginal variances.
This prior art means that paired-question Bayesian ranking alone is established.
It also warns that an unknown covariance estimate and posterior probability are
not automatically frequentist error guarantees; BayesRS uses an approximation
for incomplete observations when covariance is unknown.

Algorithm 2 should therefore either include a CRN/BayesRS-style baseline or state
why the target differs. The remaining project-specific boundary is the complete
retry-row observation unit, realized path-dependent token charge, checker control
that cannot see the answer key, and a cost ledger or confidence certificate for
the final recommendation. These details must be isolated from the generic
same-question pairing claim.

