# Experiment 2: retry-aware cost-rationed ranking and selection

Status: protocol only; no live/API run is authorized by this record.

The historical SGFR prototype is retained for auditability, but it is not the primary next algorithm. Same-question pairing and covariance transfer are established common-random-number ranking-and-selection techniques. The required primary baseline is CW-CRN-R&S (cost-weighted common-random-number ranking with missing observations); CRPR is a separately labelled cross-fitted transfer ablation. See deep-review notes 150–153 for the prior-art correction, staged run, runner contract, and correlated-resource baseline audit.

SGFR is a candidate allocator for complete ordered retry rows. It never treats a retry suffix as a separate arm and never reuses model output or a workflow prefix. A paid cell is one complete row on one question. The prototype maintains separate diagnostics for correctness, whether a retry was reached, and realized charge. It reserves direct row exploration and confirms the finalists on questions held out from calibration and racing.

The implementation is `src/retry_search/slot_gated_factorial_racing.py`; its unit tests are `tests/test_slot_gated_factorial_racing.py`. The fixed-trace replay is `scripts/replay_sgfr_trace.py`.

## Withdrawn exploratory artifact

The first SGFR source had an empty racing candidate list and a direct-mean recommendation path. The outputs below are preserved only as a row-sampling/confirmation artifact, not as an SGFR result. On `exp1-nine-local-20260927-proper`, with the same 729 rows and 200/200 search/audit split:

- Gold-labeled profiling reaches the exhaustive audit accuracy of 38.5% at mean proxy search cost $0.25185 (budget cap fraction 0.20), but this is a fixed-trace offline label result.
- Verifier-proxy profiling reaches 20.31% at fraction 0.01 and 18.50% at fractions 0.30 and 0.50; the proxy exhaustive reference is 18.50%.
- The verifier accepted 99.93% of cells and only 2.4% reached a second attempt, so these results do not establish retry-aware superiority.

Tables and plots are under `results/runs/exp1-nine-local-20260930/sgfr-gold/` and `sgfr-proxy/`. The correction and valid confirmatory design are in deep-review note 146; prior-art boundaries are in notes 143 and 144.

## Required confirmatory design

Use a new response matrix or a registered resampling design with:

1. 200 search and 200 held-out audit questions, stratified by difficulty.
2. An ordinary early-stop stratum plus a forced-retry calibration stratum, so every retry coordinate is observed with positive probability.
3. A verifier that never sees the answer key during deployment; a separate gold confirmation block is allowed only after profiling and must be charged.
4. The same realized-cost ledger for every method, including verifier calls and failed attempts.
5. Random, uniform, Matrix UCB-E, categorical BO, arm elimination, hill climbing, Cost-SySR or equivalent similarity, direct paired racing, CW-CRN-R&S, a C-LUCB-style correlated-arm control when its bound assumptions can be registered, an SH-RR-style resource-rationing baseline, and an irace/FocusedILS-style common-question racing baseline.
6. Shuffled row-slot, question-permutation, unit-cost, and cost-permutation controls.
7. Separate reporting of profiling dollars, held-out final correctness, verifier pass rate, false-pass/false-reject rates, retry reach, and cold deployment cost.

Do not tune the budget parameter using the audit split. Do not call an unvisited row recommended. If SGFR does not beat direct paired racing at matched realized dollars, preserve that negative result.


The corrected candidate is specified as cross-fitted reach-aware pair racing (CRPR) in [deep-review note 147](../docs/research/deep-review/147-corrected-cross-fitted-racing-design-2026-09-30.md), but it remains an ablation rather than an assumed novelty claim. The old SGFR code does not implement CRPR and must not be used for a confirmatory run. The staged 27-row mechanics gate and separate runner requirements are in [notes 151](../docs/research/deep-review/151-staged-experiment2-plan-2026-09-30.md) and [152](../docs/research/deep-review/152-runner-gap-for-experiment2-2026-09-30.md).
