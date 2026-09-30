# Structured-row bandit overlap

Two adjacent structured-bandit lines further narrow the claim:

- Mussi et al., *Factored-Reward Bandits with Intermediate Observations*, ICML
  2024: [PMLR](https://proceedings.mlr.press/v235/mussi24a.html). It models
  multi-stage actions with observable intermediate effects and derives
  structure-aware regret algorithms.
- Vannella, Proutiere, and Jeong, *Best Arm Identification in Multi-Agent
  Multi-Armed Bandits*, ICML 2023: [PMLR](https://proceedings.mlr.press/v202/vannella23a.html).
  It treats a global action as a complete vector of component actions and
  develops fixed-confidence structured BAI.

These papers rule out “the configuration is a vector” or “use intermediate
stage structure” as novelty by themselves. Their assumptions differ from our
target: they do not model a verifier that censors later retry stages, a
path-dependent API charge tied to that censoring, or an answer-key-hidden final
correctness target. They belong in related work and, where compatible, in the
baseline discussion.

The safe scope remains outer identification of one complete retry policy row,
using direct complete-row observations and a conservative cost ledger. Any
stage-level claim must be labeled an extension or a separate runtime-policy
problem.
