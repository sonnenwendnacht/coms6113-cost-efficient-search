# Correlated-bandit prior-art boundary for the anchor idea

## Primary sources

- Liu and Bubeck, *Most Correlated Arms Identification*, COLT 2014: [PMLR](https://proceedings.mlr.press/v35/liu14.html). It adaptively identifies correlated arms rather than sampling uniformly.
- Boda and Prashanth, *Correlated bandits or: How to minimize mean-squared error online*, ICML 2019: [PMLR](https://proceedings.mlr.press/v97/boda19a.html). It estimates covariance structure, uses a successive-rejects-style best-arm method, and gives error bounds.
- Li and Cheung, *Best Arm Identification with Resource Constraints*, AISTATS 2024: [PMLR](https://proceedings.mlr.press/v238/li24c.html). It studies heterogeneous resource consumption and distinguishes deterministic from stochastic pull costs.

## Boundary

The generic ingredients of the proposed anchor method—control variates, correlated observations, adaptive pair choice, and cost-aware elimination—are established. We must not present those ingredients as Algorithm 2's novelty.

The remaining conditional scope is their combination for a finite set of **complete retry rows**, where each observation is a whole solver–verifier execution, later attempts are reached endogenously, the final score is answer-key based but unavailable to the deployment verifier, and realized path cost is stochastic. The method also has to compare against SySRs-style paired elimination and resource-constrained BAI under the same ledger.

The anchor should therefore be described as a candidate instantiation of known correlated-bandit/control-variate ideas, with a retry-row-specific observation model and an empirical cost-to-quality test. A theorem would need to make those assumptions explicit; without that evidence the safe claim is an engineering hypothesis, not a new general bandit result.
