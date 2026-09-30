# Procedure-level target and winner's-curse control

## Source

Xu et al., *Towards Reliable LLM Evaluation: Correcting the Winner's Curse in Adaptive Benchmarking* (SIREN), arXiv:2605.05973, 2026-05-07: [paper](https://arxiv.org/html/2605.05973).

SIREN distinguishes the score of the configuration that happened to win on a tuning sample from the expected score of the full budgeted tune-then-deploy procedure on a fresh task. Its target is a budget-indexed procedure curve: run the tuner with budget `B` on a development sample, deploy the returned artifact, and average on an independent task. It freezes the post-search shortlist and separates selection evidence from held-out evaluation. The paper reports that same-data winner scores can be optimistic, especially when candidates receive unequal search effort.

## Consequence for HAPR / CS-BRI

The experiment must pre-register which of two targets it claims:

1. **Finite-benchmark winner:** the best complete retry row on the registered 200-question search set. This is a benchmark artifact and can use paid `final_correct` labels from those questions.
2. **Future-task procedure performance:** the expected held-out quality of the full search rule at profiling budget `B`, including its allocation randomness and all search charges. This needs a disjoint audit set, or repeated independent search/audit splits if the procedure curve itself is the claim.

The 200 search questions must not also be used to claim deployment accuracy. The separate 200-question audit set estimates future-task performance only under a stated exchangeability assumption. Without that assumption, report the audit as performance on a named held-out benchmark rather than as a population estimate.

The primary plot should therefore be **held-out quality of the selected row versus actual profiling spend**, with a separate table for finite-search-set selection quality. Every algorithm and parameter pair gets the same search questions, legal cache state, budget grid, and audit set. The audit remains hidden until the recommendation at each budget is frozen. If a full benchmark matrix is later built, it is a reference for finite-set regret and false elimination, not a license to reuse the audit labels during search.

## What this rules out

- Reporting the best observed search-set accuracy as if it were deployment accuracy.
- Letting a structural selector see audit rows while choosing its recommendation.
- Comparing methods at a nominal question count when their actual paid search bills differ.
- Claiming an exact population regret number from one adaptive search trace.

## Practical reporting contract

For each registered profiling budget `B`, store the frozen recommendation, paid search charge, search-set estimate, held-out audit estimate, and deployment-path cost measured on the audit run. Report confidence intervals paired across methods. Keep an exhaustive small-space run as a finite-set reference only. This separates the contribution of finding a row cheaply from the separate question of whether that row transfers to future questions.

This is a protocol correction, not a new algorithmic novelty. It protects the structural-similarity claim from a winner's-curse objection and makes the comparison with GittinsEval fair: GittinsEval's complete score matrix is a finite-benchmark surrogate, whereas the held-out curve evaluates the search procedure that produced the row.
