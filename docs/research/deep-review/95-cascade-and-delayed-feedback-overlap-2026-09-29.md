# Cascade and delayed-feedback overlap

Two prior lines are close to verifier-gated retries:

- Grover et al., *Best Arm Identification in Multi-Armed Bandits with Delayed
  Feedback*, AISTATS 2018: [PMLR](https://proceedings.mlr.press/v84/grover18b.html).
  It studies delayed final rewards together with partial intermediate feedback,
  including biased or unbiased estimators.
- Zhong, Cheung, and Tan, *Best Arm Identification for Cascading Bandits in
  the Fixed Confidence Setting*, ICML 2020: [PMLR](https://proceedings.mlr.press/v119/zhong20a.html).
  CascadeBAI estimates how much feedback is available after cascade
  termination and gives fixed-confidence complexity bounds.

These papers rule out treating early verifier events as an unexplored bandit
primitive. Their feedback models differ from ours: cascading-bandit reward is
an ordered-set click objective, and delayed-feedback analyses do not give the
complete-row configuration target with outcome-linked API charge. Neither
provides cross-row same-question covariance with verifier-blind final gold
correctness.

They should be included as adjacent baselines or related work. The remaining
claim is the interaction of complete retry-row identification, paired
configuration similarity, and realized path-cost accounting—not early stopping
alone.
