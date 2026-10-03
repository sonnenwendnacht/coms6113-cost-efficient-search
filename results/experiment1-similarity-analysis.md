# Experiment 1 row-similarity analysis

This descriptive analysis uses the binary final-workflow correctness vectors from `experiment1-nine-model-correctness.csv`. For every pair of the 729 complete rows, phi/Pearson correlation measures whether the two rows tend to be correct on the same questions. Agreement is the fraction of questions on which their correctness bits are equal. Search and audit splits are kept separate. Pair observations are dependent, so these are finite-bank descriptive summaries rather than independent-sample significance tests.

## Exact shared-slot groups

| Split | Shared slots exactly | Pairs | Mean correlation | Mean agreement |
|---|---|---:|---:|---:|
| search | none | 186,624 | 0.064 | 0.669 |
| search | retry_2 only | 23,328 | 0.064 | 0.669 |
| search | retry_1 only | 23,328 | 0.064 | 0.669 |
| search | original only | 23,328 | 0.933 | 0.994 |
| search | retry_1 + retry_2 | 2,916 | 0.064 | 0.669 |
| search | original + retry_2 | 2,916 | 0.933 | 0.994 |
| search | original + retry_1 | 2,916 | 0.989 | 0.999 |
| audit | none | 186,624 | 0.047 | 0.670 |
| audit | retry_2 only | 23,328 | 0.047 | 0.670 |
| audit | retry_1 only | 23,328 | 0.048 | 0.670 |
| audit | original only | 23,328 | 0.921 | 0.991 |
| audit | retry_1 + retry_2 | 2,916 | 0.048 | 0.670 |
| audit | original + retry_2 | 2,916 | 0.922 | 0.991 |
| audit | original + retry_1 | 2,916 | 0.984 | 0.999 |

## Interpretation

* Sharing the **original solver** is the dominant similarity signal. Pairs sharing only that slot have correlation about 0.933 on search and 0.921 on audit, with about 99.4% and 99.1% agreement.
* Sharing **retry 1 only** or **retry 2 only** has almost no structural effect: correlation is about 0.064/0.047 and agreement about 0.669/0.670, essentially the same as pairs sharing no slots.
* The aggregate count of shared slots is misleading unless the slot is identified. Its apparent positive effect is almost entirely caused by the original solver slot.
* This supports an original-slot-aware search prior, but it does not show that retry choices can be safely inferred. The natural stopping policy rarely reaches retries, so Experiment 2 needs a forced-retry calibration stratum.

The correlation is between final correctness vectors, not between model names or costs. It reflects shared question difficulty and the deployed verifier's stopping behavior as well as model similarity.
