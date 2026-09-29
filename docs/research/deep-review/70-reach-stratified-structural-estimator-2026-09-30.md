# Reach-stratified structural estimator

The most concrete Algorithm 2 form is a robust paired linear model over
complete-row utility, with reach used as an observed stratum rather than as an
independently sampled retry arm.

For a chosen profiling utility `U(c,q)=Q(c,q)-lambda*K(c,q)`, pair a candidate
row `c` with a paid hub `h` on the same question and define

```text
D(c,h,q) = U(c,q) - U(h,q).
```

Use a predeclared row feature vector `phi(c,h)` containing one-hot changed
model coordinates, registered two-slot interactions, and an intercept. Fit
the residual model only on paid pairs:

```text
D(c,h,q) = phi(c,h)^T beta + epsilon(c,h,q).
```

The feature model is a prior for choosing the next complete row, not a score
for an unpulled deployment row. For a candidate with design vector `x_c`, use
an elliptical radius `sqrt(x_c^T V^{-1} x_c)` plus a predeclared residual
allowance `rho`; add a finite-population term for the current question block.
If the target is a population rather than the registered finite benchmark,
question blocks must be sampled with known probabilities and the estimator must
use those weights. A fixed benchmark permutation needs no inverse-probability
correction.

After both rows have run, record their attempt-reach masks and verifier
signals. Estimate covariance and residual scale separately by observed
`(R_h,R_c)` strata. Do not condition a candidate's *unpulled* prediction on a
reach mask it has not yet produced, and do not impute a missing retry outcome.
If a stratum has too few pairs, pool it conservatively or disable the transfer
for that edge. The primary row utility remains the complete final score and
realized charge.

At each block, select the candidate/block with the largest conservative
reduction in the top-row confidence width per reserved maximum charge. Open a
complete row on the preassigned questions, update `V`, residual bounds, reach
strata, and cost ledger, and eliminate only when simultaneous upper/lower
bounds separate by the registered tolerance. Finish with a fresh direct block
for the proposed row.

This estimator has a clear failure switch. If the residual allowance `rho` is
large, paired covariance is nonpositive, reach strata shift across question
blocks, or the structural design is rank-deficient, it falls back to direct
cost-aware row racing. The claim is then conditional on observed structural
fit and paired variance reduction, not on Hamming distance alone.
