# Cost-aware BAI and dueling overlap

## Primary sources

- Kanarios, Zhang, and Ying, *Cost Aware Best Arm Identification*, RLJ 2024:
  [paper](https://rlj.cs.umass.edu/2024/papers/Paper193.html). CABAI attaches a
  cost distribution to each arm and minimizes expected testing cost; CTAS and
  Chernoff Overlap allocate pulls using cost-aware proportions.
- *Cost-Aware Best-LLM Identification using Dueling Feedback*, arXiv:2609.30360:
  [paper](https://arxiv.org/html/2609.30360). It brings cost-aware fixed-
  confidence dueling/Track-and-Stop ideas directly to LLM selection.

## Boundary for the project

Cost-aware allocation, square-root cost proportions, fixed-confidence stopping,
and dueling feedback are already available baselines. CABAI assumes an arm-level
reward/cost pair whose cost is independently distributed from the reward; our
retry row instead has a path charge coupled to verifier reach and final outcome.
The LLM dueling work does not by itself supply complete multi-attempt row
observations or verifier-censored path accounting.

CW-CV-TT must therefore compare against cost-aware BAI and dueling selectors at
the same realized profiling dollars. A possible theory gap is a cost-aware
correlated BAI model with complete-row traces and outcome-linked costs, but this
is a theorem target, not an established contribution. Any empirical gain that
comes only from ignoring cost heterogeneity is invalid.
