# Claim matrix after covariance-adaptive BAI audit

The current evidence supports three different claim levels:

| Claim | Status |
| --- | --- |
| Same-question paired residuals can reduce variance | Established prior art; SySRs and covariance-adaptive BAI are direct references. |
| Hamming-neighbor metadata predicts useful pair covariance | Hypothesis; requires pilot calibration and permutation controls. |
| A control-variate hub saves dollars | Conditional; only under the explicit cost–variance break-even inequality and fair hub accounting. |
| Fixed-confidence best-row theory for retry rows with stochastic, verifier-linked path cost | Open-looking boundary, but not established by our notes; existing resource-constrained/covariance BAI must be reduced or extended carefully. |
| CW-CV-TT improves held-out selection quality per paid dollar on this retry benchmark | Empirical question; no evidence until the registered comparison is run. |

## Recommended paper positioning

Do not title the contribution “a new similarity bandit” or “a new control
variate.” Present CW-CV-TT as a gated, complete-row cost-aware adaptation and
state the central research question as:

> When does configuration similarity reduce the dollars required to identify a
> deployable retry row, after every compared workflow and every verifier-
> dependent charge is paid?

The paper earns a stronger algorithmic claim only if the method beats a
covariance-adaptive paired baseline under equal realized dollars, survives
permuted-coordinate and zero-covariance controls, and reports held-out quality
and deployment cost separately. Otherwise the valuable result is a negative or
diagnostic study showing that apparent similarity gains were prefix reuse,
selection leakage, or unequal cost accounting.
