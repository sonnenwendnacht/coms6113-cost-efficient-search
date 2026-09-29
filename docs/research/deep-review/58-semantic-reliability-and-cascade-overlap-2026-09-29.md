# Semantic reliability and cascade overlap

The strongest methodological overlap is now from systems that use similarity
or learned reliability estimates to choose a cost-quality point at runtime.

* [Cost-Aware Adaptive Reliability](https://arxiv.org/abs/2605.09121)
  unifies retry, voting, refinement, verification, and routing, then uses a
  semantic-nearest-neighbor cache to select a reliability technique per task
  with one quality--cost Lagrange parameter. It is a direct prior for
  similarity-based transfer and Pareto selection. Its cache is pre-profiled
  and its action is per-task; it does not identify a complete fixed retry row
  from sparse paid benchmark cells.
* [PromptWise](https://arxiv.org/abs/2505.18901) learns a cost-aware sequence
  of model assignments for each prompt, escalating from cheap to expensive
  models when needed. [C2MAB-V](https://arxiv.org/abs/2405.16587) handles
  combinatorial multi-model selection with cost and reward feedback. Both are
  online/per-task allocation baselines rather than outer row identification.
* [Bayesian Self-Escalation](https://arxiv.org/html/2608.24087) learns when a
  junior model should hand off during its own reasoning, and
  [CascadeDebate](https://arxiv.org/abs/2604.12262) learns confidence-based
  cascade thresholds for deliberation. These cover learned stopping and
  escalation in a fixed cascade.

HAPR must therefore avoid claiming that semantic similarity, a cost-quality
  Lagrangian, cascades, or retry escalation is novel. The remaining claim is
  narrower and testable: a sparse profiling procedure for a finite set of
  complete retry rows, with a paid-cell ledger, shared-question paired
  residuals, path-dependent charge, hidden final labels, and direct held-out
  row confirmation. The per-task methods are useful runtime baselines and
  stress tests for whether a globally selected row should be replaced by a
  future adaptive policy.
