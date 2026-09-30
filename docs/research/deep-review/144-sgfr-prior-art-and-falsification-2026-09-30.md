# SGFR prior-art boundary and falsification plan

Updated: 2026-09-30 14:42 ET

The slot-gated factorial racing idea must be evaluated as a state-conditional profiling policy, not as a new name for ordinary feature screening.

## Closest prior art

- Hierarchical parameter-space kernels treat a parameter as inactive when an ancestor condition is false and assign a distance accordingly. Hutter and Osborne, *A Kernel for Hierarchical Parameter Spaces*, https://arxiv.org/abs/1310.5738. Our retry slot is different: it is active conditionally on the previous response and question, so its value cannot be declared globally irrelevant.
- irace already samples conditional parameters, races configurations on common instances, and shifts effort toward surviving candidates. López-Ibáñez et al., *The irace package*, https://iridia.ulb.ac.be/~mbiro/paperi/LopDubPer-etal2016orp.pdf. SGFR must compare against an irace/FocusedILS-style common-question racer with an explicit reach-aware condition.
- fANOVA already estimates main and interaction importance from configuration-by-instance data. Hutter, Hoos, and Leyton-Brown, https://proceedings.mlr.press/v32/hutter14.html. A slot-importance screen by itself is established; our candidate would need the paired complete-row ledger, separate reach/charge response, and a valid cost rule.
- Group-testing BO identifies active coordinates by testing coordinate groups. Hellsten et al., *Leveraging Axis-Aligned Subspaces for High-Dimensional BO with Group Testing*, https://arxiv.org/html/2504.06111v1. A pooled SGFR calibration block is therefore a baseline or ablation, not automatic novelty.
- Overlapping additive BO models and learns low-order interaction graphs. Rolland et al., https://proceedings.mlr.press/v84/rolland18a.html. A fixed Hamming graph or factorial feature model is established structure.

## What is still testable

The project-specific observation is endogenous: a retry coordinate becomes active because an earlier model response failed the verifier, and the same event changes both the reward observation and the amount charged. A defensible experiment can test whether a policy that separately estimates

`quality effect | retry reached`, `retry reach`, and `realized complete-row charge`

reduces profiling dollars at equal held-out accuracy. The claim is empirical and conditional on the measured verifier/retry process. It is not a theorem from the use of a graph or a gate.

## Falsification controls

1. Compare SGFR with random, uniform, Matrix UCB-E, Bayesian optimization, arm elimination, hill climbing, Cost-SySR, irace/FocusedILS-style racing, and an fANOVA or active-dimension screen.
2. Keep a direct-row exploration reserve and require direct fresh confirmation. SGFR may never recommend a row whose complete configuration was not paid for.
3. Use separate question blocks for calibration, adaptive allocation, and confirmation. Cross-fitting is required; it does not by itself make the method novel.
4. Run forced-retry, ordinary early-stop, shuffled-slot, and question-permutation controls. A suffix gate that only works when retries are rarely reached is not evidence of retry-aware quality.
5. Report quality, reach, realized charge, verifier pass rate, false-pass rate, search spend, held-out accuracy, and cold deployment cost separately. A small mean retry residual cannot hide a rare expensive continuation.
6. Reject the method if direct paired racing matches it at equal dollars, if a changed verifier reverses the gate, if it fails under forced retries, or if its advantage disappears under shuffled slots/questions.
