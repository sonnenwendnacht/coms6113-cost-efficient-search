# Staged Experiment 2 plan under limited compute

Updated: 2026-09-30 22:18 ET

The GPU is currently occupied, so this plan separates mechanics from evidence. The first stage is a development gate. It cannot tune parameters for, or support claims about, the later 729-row run.

## Stage A: 27-row mechanics gate

Use three model snapshots selected before outcomes from the existing model pool (the initial Qwen 1.5B/3B/7B subset is a simple choice) and all ordered triples, giving 27 complete rows. Use 200 search questions split once into 60 calibration, 80 race, and 60 confirmation questions, plus 200 untouched audit questions. Register the split and row order before reading outputs.

Use a sparse nine-edge panel rather than all 81 undirected one-slot edges: cover every retry slot, every model value, and both cheap-to-expensive and expensive-to-cheap changes. The panel is for testing the ledger and transfer invariants, not for estimating the whole graph. Compare:

* random or uniform allocation;
* direct paired racing with no transfer;
* a synchronized common-random-number baseline;
* CW-CRN-R&S, the required cost-weighted missing-observation baseline;
* CRPR as a clearly labelled transfer ablation;
* shuffled-slot and unit/permuted-cost falsification controls.

Register fixed realized-dollar caps such as 10%, 20%, and 30% of the precomputed 27-row planning cost. The cap is a comparison point, not a permission to overspend: report whole-cell overshoot separately and reserve confirmation cost before screening. Do not choose the best cap after seeing audit outcomes.

For planning only, the existing trace's fixed Qwen 1.5B/3B/7B subset would cost about `$0.31619` for 200 search questions and `$0.32393` for its old 200-question audit. Its cell costs range from roughly `$1.94e-5` to `$1.54e-4`, so a cell-count fraction is not dollar-matched. These numbers are retrospective bookkeeping, not fresh evidence. For a fresh run, freeze absolute dollar caps—or a formula based only on pre-existing model coefficients and pilot metadata—before opening questions; then report the actual ledger and overshoot.

The stage passes only if automated checks show: no audit read before freeze, no unconfirmed row selected, exact solver/verifier charge accounting, correct early-stop and forced-retry labels, valid resume identity, and no transfer when the drift check fails. A pass permits implementation work on 729 rows; it does not establish accuracy or novelty.

## Stage B: 729-row research run

Only after Stage A passes, register a new question bank and a fixed 9-model pool. Use the same four-block design and a predeclared sparse edge panel around fixed anchors; do not open all 8,748 Hamming neighbors by default. Keep natural early-stop and forced-retry strata separate. Use a new final audit, preferably large enough for the paired effect size selected in advance; the old 200-question audit remains exploratory.

The primary comparison is CW-CRN-R&S versus direct paired racing at matched realized profiling dollars. CRPR is successful only if it reduces paid cells or search spend while meeting the predeclared non-inferiority margin for final correctness and accurately reporting cold deployment cost. Otherwise retain the negative result and do not claim a new similarity algorithm.

## Risks this staging makes explicit

Twenty-seven rows cannot test multi-slot interactions or scaling. A sparse edge panel can miss a useful path. Sixty calibration questions may be too few after difficulty stratification. Selecting the three-model subset can bias the mechanics check. These are reasons to keep Stage A diagnostic and to freeze all choices before Stage B, not reasons to pool the stages.
