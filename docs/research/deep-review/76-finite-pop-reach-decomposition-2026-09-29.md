# Finite-population reach decomposition

For two complete rows `a` and `b`, let `r(q)` indicate that the shared prefix reaches their first differing choice on question `q`, and let `d(q)=Y_a(q)-Y_b(q)` be the final correctness difference on reached questions. For a fixed registered question bank of size `N`, write

```text
M       = sum_q r(q)
rho     = M / N
delta   = (1/M) sum_{q:r(q)=1} d(q)       (undefined when M=0)
Delta   = (1/N) sum_q r(q)d(q) = rho*delta.
```

This identity is exact for the finite bank. A uniform sample of questions estimates `rho`; a uniform sample from the reached subset estimates `delta`. Their finite-population variances carry the usual `(N-n)/(N-1)` and `(M-m)/(M-1)` corrections. If an upper confidence bound for `rho` is at most `epsilon`, then `|Delta| <= epsilon` already, so no reached-only mean is needed. If no question reaches the divergence, `delta` is not identifiable and must not be imputed.

## Protocol implications

- Rejection screening is valid only when questions are drawn uniformly until they reach the divergence, and every prefix-screening call is charged.
- Selecting “easy” reached questions after looking at outcomes biases `delta`; use recorded inclusion probabilities or a direct paired row sample.
- The same decomposition applies to cost differences, but cost intervals need explicit token caps or tail assumptions.
- If `m` reached continuation pairs are obtained by rejection screening, the
  paid charge is approximately
  `m * E[C_prefix] / rho + m * E[C_cont,a + C_cont,b | reached]`, not just the
  continuation charge. Prefix cost can correlate with reach and question
  difficulty, so the ledger must record every failed screening call.
- The reach probability is row-pair- and checker-specific. It cannot be transferred across a different verifier, retry policy, or model randomness coupling.
- Same-question pairing alone is not a stochastic coupling. The simplification
  `D=0` before the divergence requires deterministic decoding or shared
  exogenous randomness up to that point. With independent API sampling, define
  and estimate the complete paired difference directly; do not claim that an
  unreached suffix would have produced the same score.

This gives a cleaner finite-bank version of the reach-stratified estimator and provides a useful early-exit rule for low-impact row differences. It is a derivation and protocol condition, not a new theorem claim.
