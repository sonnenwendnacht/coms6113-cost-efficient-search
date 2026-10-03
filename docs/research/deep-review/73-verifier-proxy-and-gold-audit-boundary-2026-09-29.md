# Verifier proxy versus gold-audit boundary

## Source

Ao et al., *Best Arm Identification with LLM Judges and Limited Human Audits*, arXiv:2601.21471: [paper](https://arxiv.org/html/2601.21471).

The paper studies best-arm identification when a cheap proxy or LLM judge is available but ground-truth labels are expensive. It gives an impossibility construction: proxy observations can be identical under two instances with different best arms, so proxy-only selection cannot guarantee the correct arm. Its correction uses selectively audited ground-truth outcomes, inverse-propensity weighting, and anytime-valid confidence sequences under adaptive auditing.

## Consequence for retry profiling

The answer-key-blind verifier can control whether a retry is reached, but a verifier pass is not the same as final benchmark correctness. A search method that uses only verifier outcomes must be described as optimizing verifier utility or expected path cost unless a verifier-to-gold calibration assumption is made. If final correctness is the target, some gold-scored audit observations are necessary.

For this project, the cleanest protocol is:

- use verifier events and realized path charges for online reach and cost accounting;
- use `final_correct` only after a paid complete search cell, or on the independent held-out audit set;
- keep audit inclusion probabilities positive and recorded if audits are adaptively allocated;
- use inverse-propensity or a conservative bound only when gold audits are selectively sampled;
- fail closed to direct complete-row racing when calibration, support, or audit weights are insufficient.

This makes the current answer-key-blind deployment verifier a valid stopping mechanism while avoiding the false claim that its pass signal identifies the best accuracy row. The issue is an identification limit, not a reason to expose answer keys during deployment.
