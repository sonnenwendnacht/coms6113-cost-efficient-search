# HPO and cascade-theory overlap

Two established lines are especially relevant to the “patch together HPO and
RL” idea.

* [EcoTune](https://aclanthology.org/2025.emnlp-main.394/) defines explicit
  token-cost fidelity, a token-aware expected-improvement acquisition rule,
  and dynamic fidelity scheduling for inference-hyperparameter HPO. It is a
  strong cost-per-evaluation baseline, although its fidelities are shorter or
  smaller inference trials rather than verifier-gated complete retry rows.
* [A Unified Approach to Routing and Cascading for LLMs](https://proceedings.mlr.press/v267/dekoninck25a.html)
  derives optimal per-query routing and cascading under quality estimators and
  combines them into cascade routing. It supplies theory and a practical
  baseline for a fixed cascade; it does not solve sparse outer selection among
  complete row assignments.

These papers make “expected improvement per token,” “dynamic fidelity,”
“optimal cascade,” and “cost-quality routing” unavailable as standalone
Algorithm 2 contributions. A valid patchwork can still use their ideas as
baselines, but its new object must be the row-level observation ledger and
paired allocation under hidden final labels and endogenous retry reach.
