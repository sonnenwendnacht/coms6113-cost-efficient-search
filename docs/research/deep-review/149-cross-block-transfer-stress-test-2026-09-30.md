# Existing-trace stress test for cross-block transfer

Updated: 2026-09-30 18:12 ET

This is a CPU-only diagnostic on the completed local Experiment 1 trace. It made no model, GPU, or API calls. It is not a new experiment and cannot be used as a confirmatory result because the old audit split has already been inspected during selector development.

## Calculation

For every pair of complete rows that differs in exactly one of the three model slots, calculate the mean `final_correct` difference on the 200-question search block and on the 200-question old audit block. There are 8,748 such pairs. Compare the absolute difference between those two block means, grouped by the changed slot. The two blocks contain different questions; without difficulty labels, this is a distribution-shift diagnostic, not a paired-question correlation estimate.

| Changed slot | Mean absolute search-to-old-audit shift | Same sign of the two block differences |
| --- | ---: | ---: |
| Original solver (slot 0) | 5.37 percentage points | 82.5% |
| First retry (slot 1) | 0.44 percentage points | 76.1% |
| Second retry (slot 2) | 0.10 percentage points | 90.3% |

The first slot dominates the variance in the existing trace, so its transfer error is also the largest. Retry-slot differences are small partly because the verifier accepts almost every attempt and only about 2.4% of workflows reach a second attempt; the small shifts do not prove that retry transfer is safe.

## Consequence for CRPR

The next run must not use one global residual mean. It should register difficulty/reach strata before outcomes, estimate residuals within each stratum, and disable transfer when a calibration-versus-race drift check fails. The original-solver edge family deserves the largest direct-exploration reserve. Forced-retry questions are needed to distinguish a genuinely quiet retry slot from one that is merely rarely reached. The final audit must be new and untouched.

This diagnostic is also a reason to keep the direct paired-racing control: if a stratum-aware residual cannot beat it at matched realized dollars after its reserve and multiplicity correction, there is no case for adding cross-block transfer.

