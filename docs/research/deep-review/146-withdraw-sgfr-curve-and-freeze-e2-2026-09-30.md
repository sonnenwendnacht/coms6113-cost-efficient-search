# Withdraw the first SGFR curve and freeze a valid Experiment 2 design

Updated: 2026-09-30 17:42 ET

## Correction to the previous update

The first SGFR implementation and its 56-run gold/proxy replay were audited on CPU after the GPU became unavailable. The source has two correctness defects that invalidate the claim that those runs tested slot-gated racing:

1. `observed_pairs` was built from every predeclared one-slot edge, not only the pairs actually paid during calibration. The later racing candidate list was therefore empty.
2. Even if that filter is corrected, the full-block residual `mean(candidate - incumbent)` plus the incumbent mean is algebraically the candidate's direct mean on the same questions. It cannot provide information about a row that was not already directly evaluated. The final recommendation also sorts directly observed rows by their direct mean.

The curves under `results/runs/exp1-nine-local-20260930/sgfr-gold/` and `sgfr-proxy/` remain preserved as an exploratory row-sampling and confirmation artifact, but must not be described as evidence for SGFR, a gate benefit, or a publication result. The earlier SGFR statements in notes 143 and `experiments/experiment2-sgfr.md` are superseded by this correction.

Additional implementation issues are being corrected before any new replay: the reserve threshold was an absolute total rather than a post-calibration allocation; cost-budget row blocks could overshoot by more than one cell block; and the wrapper's resume identity did not include the SGFR source hash.

## Valid Experiment 2 design

The old 200-question audit is now contaminated for confirmatory use because selector methods and budgets have been inspected. It remains valid for fixed-trace exploratory comparisons only. A confirmatory run needs three disjoint blocks:

- **Calibration/search:** adaptive profiling questions. The selector may see their paid verifier outcomes and, in a separate labeled diagnostic, their final correctness.
- **Selection confirmation:** a fresh, charged block used only to compare the final directly observed candidates. It is still profiling data, not the final audit.
- **Final audit:** a never-exposed block used once after one row is frozen. No method or parameter may be chosen using this block.

The deployment-faithful primary selector uses answer-key-blind verifier outcomes. `final_correct` is attached only after the row is frozen. A limited-gold calibration arm may be reported as a secondary supervised diagnostic, but it cannot be the primary deployment claim.

Use both a natural early-stop stratum and a pre-registered forced-retry stress stratum. They estimate different targets and must be reported separately. A future trace should record every solver/verifier slot output and its would-have-been charge so the same trace can be evaluated under natural and forced policies; unobserved suffix correctness cannot be reconstructed from ordinary early-stop logs.

Use random, uniform, Matrix UCB-E, categorical Bayesian optimization, arm elimination, hill climbing, SySRs, direct paired racing, and a cost-aware resource-rationing baseline. Add shuffled row-slot, question-permutation, unit-cost, and cost-permutation controls. Every method receives the same realized-dollar ledger and the same cached-incumbent rules.

With 200 final-audit questions and accuracy near 38.5%, a simple binomial 95% half-width is about 6.9 percentage points. That is pilot-scale. Report paired question-level differences and randomization/bootstrap intervals rather than treating eight deterministic allocation seeds as independent model replications. A rough 5-point paired comparison with discordance near 0.2 needs on the order of 600 audit questions; the actual discordance and target gap must determine the final sample size.

The paper's narrow claim should remain conditional: complete retry rows, question-indexed paired outcomes, verifier-censored reach, response-dependent realized charge, and a finite search bank. Generic graph similarity, conditional parameter screening, paired comparisons, and racing are established prior art. If the corrected structural method does not beat direct paired racing at matched realized dollars, preserve that negative result.

Primary validation references: [Cawley and Talbot on selection overfitting](https://www.jmlr.org/papers/v11/cawley10a.html), [Dror et al. on statistical testing for NLP](https://aclanthology.org/P18-1128/), and [Kuchibhotla and Zheng on confidence sequences under adaptive sampling](https://proceedings.mlr.press/v139/kuchibhotla21a.html). These justify the evaluation design; they are not novelty claims.
