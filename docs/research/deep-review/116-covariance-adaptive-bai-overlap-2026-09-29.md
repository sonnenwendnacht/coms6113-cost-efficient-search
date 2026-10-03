# 116: Covariance-adaptive BAI overlap (2026-09-29)

## Primary-paper correction

Saad, Blanchard, and Verzelen's NeurIPS 2023 paper **Covariance adaptive best
arm identification** is a direct prior-art baseline for the central statistical
mechanism we were considering. Their game protocol lets a learner query a
subset of arms in one round and observe all selected rewards. The paper uses
the empirical variance of same-round differences, sequential pair tests, and
comparisons with suboptimal but highly correlated arms. Its complexity depends
on `Var(X_i-X_j)`, not merely the sum of marginal variances.

This rules out claiming that “compare similar rows on the same questions and
use the smaller difference variance” is itself novel. It is established
covariance-aware pure exploration.

## What does not transfer directly

The paper's protocol and guarantees differ from our retry matrix in several
material ways:

- its simultaneous query cost is a count of selected arms per round, whereas
  our endpoints have different and outcome-linked dollar charges;
- its observations are stochastic draws of a multivariate arm distribution,
  while our local experiment is a finite registered question bank and may use
  deterministic decoding;
- it assumes the selected arm rewards are observed together, while our two
  complete workflows are separate paid executions whose retry reach and
  verifier path can differ;
- its confidence analysis is for bounded or Gaussian variables and does not
  handle answer-key-blind verifier censoring or unexecuted retry suffixes.

These differences support an extension study, not a new covariance mechanism.
The paper must be included as a direct baseline or cited in the methods
positioning. EGCR's remaining candidate contribution is a cost-aware,
complete-row implementation with reservations, finite-bank pairing, and an
independent gold audit. Any theorem would have to state exactly how its
confidence proof changes under realized path charges and cross-fitted row
edges.

## Algorithmic consequence

Use the covariance paper's paired sequential test as the statistical control:
for every trusted edge, report the empirical difference variance, sample count,
and confidence rule. Add our proposed cost allocation only in the acquisition
layer:

```text
choose comparison e = (a,b) by information gained per reserved dollar
run both complete rows on the next fixed question block
update the paired confidence test and realized ledger
```

If the cost-aware layer does not improve equal-dollar identification over this
covariance-adaptive control, the proposed Algorithm 2 is not supported. If it
does, the claim should be limited to the retry-cost/finite-bank setting and
should not be phrased as inventing covariance-aware BAI.

## Source

Saad, Blanchard, and Verzelen, “Covariance adaptive best arm identification,”
NeurIPS 2023: 
https://proceedings.neurips.cc/paper_files/paper/2023/file/e82ef7865f29b40640f486bbbe7959a7-Paper-Conference.pdf
