# Factorized row models: useful baseline, weak novelty claim

## Primary structured-BAI precedents

- Soare, Lazaric, and Munos, *Best-Arm Identification in Linear Bandits*,
  [NeurIPS 2014](https://proceedings.neurips.cc/paper_files/paper/2014/hash/f8d84caae48546d0934d637ab54f7086-Abstract.html), and Jedra and
  Proutiere, *Optimal Best-arm Identification in Linear Bandits*,
  [NeurIPS 2020](https://proceedings.neurips.cc/paper/2020/hash/7212a6567c8a6c513f33b858d868ff80-Abstract.html), already use a shared feature
  vector to estimate many arm means and allocate samples for best-arm
  identification.
- Vannella, Proutiere, and Jeong, *Best Arm Identification in Multi-Agent
  Multi-Armed Bandits*, [ICML 2023](https://proceedings.mlr.press/v202/vannella23a.html), treats a global action as a Cartesian product of component actions, gives it a factor-graph reward, and derives a structured fixed-confidence BAI rule.

These papers rule out claiming that one can write a row as three model
coordinates, fit shared slot effects, or use a factor graph as the contribution.
They also show why a factorized model can reduce the nominal 729-arm search
space when its assumptions are correct.

## Why the retry setting is not automatically covered

Our observation is one scalar final correctness and one realized complete-row
charge per question. We do not observe a separate reward for each solver slot,
and a later retry is not run after a verifier accepts an earlier attempt. Thus a
factor model such as

```text
mu(m1,m2,m3) = intercept + slot1[m1] + slot2[m2] + slot3[m3]
               + selected two-slot interactions
```

is a statistical hypothesis about final row means, not a consequence of the
workflow. The verifier can make slot effects strongly context-dependent, and an
early acceptance can make the observed cost depend on the same latent event that
controls correctness. A model that shares samples across rows can therefore be
more efficient, but it can also produce overconfident rankings if its additive or
low-order interaction assumption fails.

## Guarded AFGR baseline

A defensible implementation is **Adaptive Factorial Graph Racing (AFGR)** as an
explicit baseline or fallback candidate:

1. Pre-register a complete-row covering design and a permutation of the search
   questions. Every observation still runs the full row; there is no prefix or
   component-response reuse.
2. Fit main effects, then selected two-slot interactions, using only completed
   search cells. Include question-block effects or use matched-question
   differences so task difficulty is not mistaken for a row effect.
3. Cross-fit by question blocks. Use the held-out search blocks to measure
   prediction error and calibration of row-mean intervals. Do not use the audit
   split to choose the model.
4. Use a cost-aware linear/factorized BAI allocation only while the predictive
   residual and coverage checks beat a direct-row baseline. Otherwise fall back
   to direct cost-aware paired racing.
5. Directly probe and confirm the final row. A fitted mean for an unpulled row is
   a proposal, not a publishable recommendation.

The acquisition can be a confidence-width or expected-winner-change score per
predicted complete-row charge, with a random scout reserve. If a hard profiling
cap is claimed, the block must also satisfy the deterministic reservation rule
in note 98; a mean cost prediction is not enough.

## What would count as a meaningful result

The interesting empirical question is not whether the factor model predicts
held-in search cells. It is whether, at equal realized profiling dollars, AFGR
reaches a given held-out row-selection quality with fewer **complete** row calls
than direct cost-aware BAI, while its coverage remains calibrated under row
interactions and verifier-censored costs. Required controls are a permuted-slot
model, an interaction-heavy synthetic control, direct paired racing, and the
structured-BAI baseline where its assumptions are satisfied.

Until those checks pass, the paper should describe AFGR as a guarded structured
baseline. The candidate contribution remains the retry-specific observation and
cost protocol, not generic factorial sharing.
