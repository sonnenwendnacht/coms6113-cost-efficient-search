# Experiment 2: nine-model Algorithm 2 replay
This is the completed 9-model, 729-row replay of the similarity-annealed UCB Algorithm 2 prototype. It uses the completed local Experiment 1 trace as the immutable response matrix; it does not regenerate model calls or claim a fresh provider run. Each selector result is checkpointed before its held-out accuracy is attached.
## Run definition
- Rows: 9 ordered solver choices × 9 × 9 = **729 complete retry rows**.
- Search matrix: **200** questions; held-out audit: **200** disjoint questions.
- Selectors: Random, Matrix UCB-E, and similarity-annealed UCB (Algorithm 2), each at 7 budgets and 8 seeds: **168 selector runs**.
- Primary cost: realized local proxy charge, coefficient × input tokens, including reached verifier and retry calls.
- Search saw answer-key correctness on revealed cells (offline labeled profiling); audit labels were attached only after each recommendation.
## Main results
| Selector | Budget | Mean audit accuracy | Mean search cells | Mean search cost | Savings |
|---|---:|---:|---:|---:|---:|
| random | 0.01 | 37.69% | 1600 | $0.09062 | 98.9% |
| random | 0.025 | 37.69% | 3800 | $0.21543 | 97.4% |
| random | 0.05 | 37.69% | 7400 | $0.41857 | 94.9% |
| random | 0.1 | 38.50% | 14600 | $0.81388 | 90.1% |
| random | 0.2 | 38.50% | 29200 | $1.65034 | 79.9% |
| random | 0.3 | 38.50% | 43800 | $2.47410 | 69.9% |
| random | 0.5 | 38.50% | 73000 | $4.10369 | 50.0% |
| matrix_ucb_e | 0.01 | 25.25% | 1458 | $0.08071 | 99.0% |
| matrix_ucb_e | 0.025 | 28.50% | 3646 | $0.20948 | 97.4% |
| matrix_ucb_e | 0.05 | 33.50% | 7291 | $0.41690 | 94.9% |
| matrix_ucb_e | 0.1 | 36.81% | 14581 | $0.84810 | 89.7% |
| matrix_ucb_e | 0.2 | 36.88% | 29161 | $1.70240 | 79.3% |
| matrix_ucb_e | 0.3 | 36.88% | 43740 | $2.59736 | 68.4% |
| matrix_ucb_e | 0.5 | 38.50% | 72900 | $4.34982 | 47.0% |
| similarity_annealed_ucb | 0.01 | 34.50% | 1458 | $0.07292 | 99.1% |
| similarity_annealed_ucb | 0.025 | 36.12% | 3646 | $0.17618 | 97.9% |
| similarity_annealed_ucb | 0.05 | 36.06% | 7291 | $0.34011 | 95.9% |
| similarity_annealed_ucb | 0.1 | 37.69% | 14581 | $0.68036 | 91.7% |
| similarity_annealed_ucb | 0.2 | 38.50% | 29161 | $1.39199 | 83.0% |
| similarity_annealed_ucb | 0.3 | 38.50% | 43740 | $2.18038 | 73.4% |
| similarity_annealed_ucb | 0.5 | 38.50% | 72900 | $3.74333 | 54.4% |
| Brute-force reference | 1.00 | 38.50% | 145,800 | $8.20715 | 0.0% |

At the 0.20 cell fraction, Algorithm 2 reaches the exhaustive audit score: **38.50%**, at mean search cost **$1.39199** (83.0% below exhaustive). Random reaches the same score at 0.10 but costs $0.81388; at 0.20 it costs $1.65034. Matrix UCB-E reaches the score at 0.50 and costs $4.34982. These are fixed-split offline replay results, not a publication claim or API-price result.

## Deployment-visible reward check

The same Algorithm 2 implementation was also replayed using only the answer-key-blind verifier pass as its search reward. On that separate replay, the best held-out accuracy was **21.88%** at the 0.025 cell fraction; at 0.10 and above it selected rows with **18.50%** held-out accuracy, while the verifier-proxy exhaustive reference was also only **18.50%**. This gap matters: the 38.50% result above uses gold correctness during search and is therefore an offline diagnostic, not a deployment claim.

The verifier-proxy artifacts are retained under `results/runs/exp1-nine-local-20260930/proxy-similarity/`.
## Checkpoint and provenance
- Immutable source trace: `/home/gabi/agentic_6113/results/runs/exp1-nine-local-20260927-proper/traces.json` (729 × 400 completed workflows).
- Selector checkpoint: `/home/gabi/agentic_6113/results/runs/exp2-nine-model-algorithm2-20261003/selector-checkpoint.jsonl` (168 newline-committed records).
- Partial graph-residual checkpoint, excluded from the primary table: `/home/gabi/agentic_6113/results/runs/exp2-nine-model-algorithm2-20261003/selector-checkpoint-with-partial-graph.jsonl`.
- Table/plot copies: `findings/experiment2-nine-model-algorithm2-selector-table.csv`, `findings/experiment2-nine-model-algorithm2-accuracy-search-cost.png`, and `findings/experiment2-nine-model-algorithm2-accuracy-search-cost.pdf`.
The raw source trace was generated from local models and uses the answer-key-blind verifier, but the completed Experiment 1 run naturally reached retries in only 2.42% of workflows. Therefore this replay tests allocation over complete rows and realized costs; it does not establish that Algorithm 2 solves the retry-censoring problem. A forced-retry, cross-fitted CRPR run remains a separate follow-up.
