# Finite benchmark versus future-task estimand

## Source

Wu, Nair, and Candès, *Efficient Evaluation of LLM Performance with Statistical Guarantees* (FAQ), arXiv:2601.20251v3: [paper](https://arxiv.org/html/2601.20251).

FAQ explicitly treats a benchmark as a fixed finite population and defines accuracy as the mean of the unknown labels over that bank. Its adaptive question selection is wrapped in a finite-population inference layer. The paper contrasts this target with superpopulation accuracy and warns that ad-hoc adaptive sampling without replacement does not automatically inherit its coverage result.

## Consequence for our two 200-question sets

The search set and audit set can support two different claims:

- Search-set rows estimate the finite-bank winner and drive the selector after each paid cell.
- The disjoint audit set estimates performance on that named bank. Calling it expected future-task accuracy requires an exchangeability or sampling statement that the project must write down.

This distinction matters because MathQA questions have heterogeneous difficulty. A question-adaptive or row-adaptive allocation changes which questions are observed. We must not use a generic iid standard error for an adaptively revealed, without-replacement stream. Either keep the audit untouched and use paired held-out estimates, or state a finite-population confidence method with a valid sampling design and inclusion probabilities.

The structural predictor may still use difficulty or row-similarity features as a working model. Coverage must come from the sampling/audit design, not from assuming that the predictor is correct. Historical or full-matrix traces can guide allocation only after their role and possible distribution shift are declared.

## Reporting rule

Every result table should label its estimand as one of `search-bank winner`, `held-out-bank quality`, or `future-task procedure quality`. A single “accuracy” column without that label is scientifically ambiguous. This correction narrows the claim; it does not change the proposed complete-row similarity algorithm.
