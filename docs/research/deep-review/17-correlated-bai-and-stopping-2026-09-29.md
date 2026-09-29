# Correlated BAI and stopping validity audit (2026-09-29)

This note records a research-only audit. No selectors, model evaluations, replays, or
experiments were run for this note.

## Primary sources

- Saad, Blanchard, and Verzelen, *Covariance Adaptive Best Arm Identification*,
  NeurIPS 2023 / arXiv: [paper](https://arxiv.org/html/2306.02630).
- Gupta, Joshi, and Yağan, *Best-Arm Identification in Correlated Multi-Armed
  Bandits*, IEEE JSAIT 2021 / arXiv: [paper](https://arxiv.org/html/2109.04941).
- Howard, Ramdas, McAuliffe, and Sekhon, *Time-uniform, nonparametric,
  nonasymptotic confidence sequences*, Annals of Statistics 2021:
  [arXiv record](https://arxiv.org/abs/1810.08240).
- Kennedy and Ramdas, *Time-uniform central limit theory and asymptotic
  confidence sequences*, 2021: [arXiv record](https://arxiv.org/abs/2103.06476).

## What the covariance-adaptive result actually assumes

Saad et al. allow an adaptive subset of arms to be queried at each round. The
environment first draws a fresh reward vector, independent and identically
distributed across rounds, and reveals the selected coordinates. Their Pairwise-BAI
tests use the empirical variance of same-round differences
`X_i,t - X_j,t`. A time-indexed error schedule, roughly
`delta/(K^2 t(t+1))`, makes the pairwise empirical-Bernstein tests valid at every
round. The resulting fixed-confidence theorem permits adaptive allocation and a
stopping time, and its instance-dependent cost depends on
`Var(X_i-X_j)/gap_ij^2` rather than only marginal variances. Their algorithm also
continues querying some eliminated arms because they can provide useful covariance
information.

This is not an exact model of our benchmark yet. A MathQA question must play the
role of a fresh task draw; evaluating rows `a` and `b` on the same question creates
a paired outcome only if the task/question sampling scheme is treated as random (or
a valid finite-population/martingale argument is supplied). A fixed list of 200
questions with deterministic row outputs does not automatically satisfy the i.i.d.
vector assumption. The pair still costs both complete workflow evaluations, so its
variance reduction must be compared with the second row charge.

## A different correlated-bandit route

Gupta et al. do not observe several arms on the same round. They assume known
upper bounds called pseudo-rewards,

`E[R_l | R_k=r] <= s_{l,k}(r)`,

and extend LUCB. The bounds allow noncompetitive arms to be eliminated without
direct pulls, reducing the logarithmic sample contribution to the set of
competitive arms. The authors stress that pseudo-rewards may be loose; unknown
entries are set to the maximum possible reward, which falls back to the classical
independent-arm setting. Pilot data may estimate a bound, but the estimate needs
conservative uncertainty padding.

For our configuration rows, an embedding or fitted covariance matrix is not a
pseudo-reward certificate by itself. It may rank promising neighbors, but treating
the prediction as a proof that an unmeasured row is dominated can silently discard
the optimum. To use this route rigorously, a separate calibration split would need
to establish simultaneous upper bounds for the relevant conditional performance;
otherwise every elimination should retain a direct confirmation path.

## Stopping rule consequence

The covariance-adaptive theorem gets optional-stopping validity from a bound that is
uniform over all rounds (and all pair tests), not from stopping at a convenient
block boundary. In our setting, fixed-look empirical-Bernstein intervals are unsafe
if the next look or row is selected after seeing the previous outcomes. Candidate
implementations should therefore use either:

1. a confidence sequence for each direct row mean and pair gap, with a union/error
   budget over rows and streams;
2. an alpha-spent sequence at predeclared looks; or
3. a sample count/look schedule fixed independently of observed outcomes.

“Only stop between blocks” is useful for bookkeeping and reproducibility, but does
not itself supply statistical validity. An outcome-selected stream should be covered
simultaneously over all opened prefixes, or be replaced with disjoint cross-fitted
blocks whose inclusion is fixed before their outcomes are used.

## Implications for Algorithm 2

The safe current design is a two-layer procedure:

1. Use the structured similarity model only to prioritize a complete row or a
   same-question row pair. Inflate residual uncertainty when calibration is weak;
   if the model is unsupported, revert toward independent-arm allocation.
2. Use direct observations and time-uniform pair/row confidence sequences for
   elimination and final certification. Stop only when the leader's lower bound
   exceeds every competitor's upper bound (or report unresolved uncertainty).

This gives a real covariance-adaptive baseline without claiming that a learned
similarity estimate is an exact answer cache. Any stronger claim requires explicit
assumptions about question sampling, covariance stationarity, and the calibration
error budget.

