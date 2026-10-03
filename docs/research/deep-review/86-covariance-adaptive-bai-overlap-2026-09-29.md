# Covariance-adaptive BAI overlap

## Primary source

Saad, Blanchard, and Verzelen, *Covariance Adaptive Best Arm Identification*,
arXiv:2306.02630v2: [paper](https://arxiv.org/html/2306.02630).

This paper is a close theoretical precedent. Its game protocol lets the learner
query a subset of arms in a round and observe a joint reward vector. It estimates
unknown covariance, uses empirical variance of pairwise differences, and gives
successive-elimination guarantees whose cost can improve when a useful arm pair
has small difference variance. The authors explicitly state that adaptive
correlation exploitation, rather than independent-arm UCB, can reduce the
comparison complexity.

## Difference from our setting

The protocol does not give us a free simultaneous observation of several rows.
Running two complete retry rows on one MathQA question still pays both full
workflow charges. The same question is a common covariate, and the pairwise
residual can have lower variance, but there is no free side observation of an
unpulled row. In addition, our row cost is a stochastic verifier-gated path
charge, final correctness is a separate answer-key score, and later attempts
are absent by an endogenous stopping rule.

Therefore covariance-adaptive BAI is a mandatory baseline and a warning against
claiming a new covariance estimator. CW-CV-TT can only claim a retry-specific
extension if it handles additive realized workflow charges, separate cost and
quality certification, and complete-row observations without importing the
paper's simultaneous-query or fixed-distribution assumptions.

The clean empirical comparison is: covariance-adaptive pair elimination with
its own assumptions, direct CW-PTT/SySRs, and the gated control-variate sidecar.
Any gain that disappears when pair calls are charged separately is a protocol
artifact rather than a contribution.
