# Corrected no-prefix algorithm: cross-fitted reach-aware pair racing

Updated: 2026-09-30 17:55 ET

The SGFR audit shows that a gate over fully measured rows cannot create savings. If both rows are measured on the same question block, then

`mean(anchor) + mean(candidate - anchor) = mean(candidate)`

on that block. The residual is useful only when it is learned on one question block and used to prioritize or predict another block. That prediction must be paid back with direct confirmation.

## CRPR candidate

Call the corrected candidate **cross-fitted reach-aware pair racing (CRPR)** until an implementation exists. It is a deliberately narrow extension of synchronized paired racing:

1. Register four disjoint question blocks: calibration, race, confirmation, and final audit. Within each block, predeclare difficulty strata and a fixed question order or random seed.
2. Choose a complete-row incumbent and a one-slot neighboring challenger. Pay both complete workflows on the calibration block. Record signed quality difference, retry-reach difference by slot, and realized charge difference. No prefix or model output is reused.
3. Cross-fit a residual model by applying calibration residuals to a held-out race block. A simple first version uses a stratum-specific mean residual; a later version can use a low-order slot model. The prediction interval must include calibration uncertainty and race-block anchor uncertainty.
4. Pay the incumbent on a race block. Pay the challenger only when its predicted upper bound can beat the incumbent lower bound, when the gate is unresolved, or when a predeclared direct-exploration reserve selects it. This is where similarity can save cells; calibration endpoints are never free.
5. Track three coupled signals: quality, probability that each retry slot is reached, and realized complete-row charge. A slot is quiet only if its cross-fitted quality and reach effects are small in every registered reach stratum and its charge effect is below a separate threshold. A rare expensive continuation must reopen the gate.
6. Require both finalists to be directly evaluated on the fresh confirmation block. The final audit is untouched until one complete row is frozen.

A cost-normalized acquisition score can be based on predicted reduction in the incumbent/challenger interval divided by the expected charge of the next complete cell. Expected charge is estimated from observed strata and must be charged with a conservative reservation; a known per-token coefficient does not make a complete retry-path charge known.

Because the allocator can inspect many edges, retry strata, and checkpoints, per-edge nominal intervals are not enough. Register the finite edge set and use one simultaneous error budget across quality, reach, and charge gates (or pay a fresh certification block for every adaptively opened edge). Record the maximum number of looks and turn off residual transfer after a predeclared calibration-versus-race drift check fails.

## Why this is different from the withdrawn code

The withdrawn implementation measured every candidate endpoint on the entire race block and then ranked direct means, so it was a row sampler. CRPR uses calibration residuals only across disjoint blocks and can leave a challenger race cell unopened. It must record every imputed recommendation as provisional and may never report an unconfirmed row as the winner.

This does not make the components automatically novel. Synchronized paired comparisons are the main baseline: [SySRs](https://arxiv.org/abs/2606.07726v1) explicitly evaluates models on shared questions and gives a correlation-sensitive best-arm procedure. The mentor's [GittinsEval](https://arxiv.org/abs/2609.25645v1) is the independent fixed-cost configuration baseline. Resource-constrained best-arm identification already handles heterogeneous pull resources, while [cost-aware cascading bandits](https://arxiv.org/abs/1805.08638) and [CascadeBAI](https://proceedings.mlr.press/v119/zhong20a.html) cover stochastic sequential feedback and random stopping. The only defensible intersection is conditional and empirical: complete retry rows, question-indexed cross-fitted residuals, verifier-censored reach, response-dependent complete-row charges, and a finite search bank.

## Required controls

- SySRs with the same calibration and confirmation reserve.
- Direct cost-aware paired racing with no residual transfer.
- Independent Gittins/UCB or categorical BO.
- An identity-feature CRPR control, a shuffled-slot control, and a question-permutation control.
- Forced-retry and natural early-stop strata analyzed separately.
- Unit costs and cost-permutation controls.
- A no-transfer version that pays every challenger race cell. CRPR must beat this at matched realized dollars to justify residual transfer.

The first confirmatory question is not whether CRPR beats exhaustive search. It is whether, at the same realized profiling spend and with direct confirmation, cross-fitted residual transfer reduces the number of challenger cells without lowering final correctness or understating path cost. If not, the correct paper result is that complete-row direct paired racing is safer than structural transfer in this setting.
