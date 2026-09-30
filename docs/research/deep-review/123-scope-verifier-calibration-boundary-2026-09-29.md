# 123: SCOPE verifier-calibration boundary (2026-09-29)

## What SCOPE provides

Badshah, Emami, and Sajjad's **SCOPE: Selective Conformal Optimized Pairwise
LLM Judging** calibrates an uncertainty threshold so that the error rate among
accepted pairwise LLM judgments is bounded under exchangeability. It uses a
bidirectional preference-entropy signal to reduce position bias and a labeled
calibration set to maximize coverage at a target risk.

This is relevant because a verifier can be confidently wrong. A raw PASS/RETRY
rate is not a calibrated probability of final correctness.

## Why it is not a drop-in verifier for Algorithm 2

Our deployment verifier evaluates one solver response against the question; it
does not compare two candidate responses with a human preference label. More
importantly, a verifier decision controls whether a retry is reached, so
abstention changes both the future reward and the future charge of the cell.
SCOPE's accepted-set risk guarantee does not automatically cover this
endogenous retry path.

To use a SCOPE-like control, we would need:

1. a development/calibration set with gold final correctness labels;
2. a fixed uncertainty score for the verifier, or a bidirectional/repeated
   verifier query whose extra cost is included in the cell ledger;
3. an exchangeability or distribution-shift assumption between calibration and
   deployment questions; and
4. a path-aware analysis of how abstaining or forcing a retry changes cost and
   final correctness.

Without these, `verifier_pass` is an observable proxy, not a certified gold
reward. Selectors should be evaluated in two modes: verifier-visible selection
followed by independent gold audit, and explicitly labeled gold-visible oracle
replay. The new `--selector-reward` switch enforces this distinction in the
replay code.

## Positioning

SCOPE should be cited as a verifier reliability/calibration control and a
possible future extension. It does not make the outer complete-row search
problem novel, and it does not validate a selector that directly consumes
`final_correct` during deployment.

Source: Badshah, Emami, and Sajjad, “SCOPE: Selective Conformal Optimized
Pairwise LLM Judging,” arXiv:2602.13110v4 (2026):
https://arxiv.org/abs/2602.13110
