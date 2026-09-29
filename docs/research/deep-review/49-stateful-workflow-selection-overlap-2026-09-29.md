# Stateful workflow selection and profiling overlap

The latest workflow papers reinforce that the project must state whether it
searches an execution policy at deployment time or profiles a fixed row before
deployment.

* [MCPP, On Time, Within Budget](https://arxiv.org/html/2605.06110) uses a
  dependency-aware online planner that simulates candidate actions and replans
  under a hard budget and deadline. It includes retry continuations and
  profiles success rates and lengths before offline simulation. This is close
  to a stateful executor, but it assumes those calibrated estimates and does
  not solve sparse outer identification of one complete row with hidden final
  correctness.
* [Aragog](https://arxiv.org/html/2511.20975) predicts accuracy-preserving
  end-to-end configurations and beam-schedules model upgrades under serving
  load. It uses monotonic upgrades, exhaustive/profiled accuracy information,
  and shared prefixes. It is an adjacent serving baseline and an explicit
  reason to keep prefix reuse outside HAPR's scope.
* [Cognify/AdaSeek](https://arxiv.org/abs/2502.08056) hierarchically tunes
  workflow structure, operators, prompts, and models while moving a fixed
  search budget toward promising configurations. [EvoRoute](https://arxiv.org/abs/2601.02695)
  uses accumulated experience to select Pareto-efficient model backbones for
  each subtask. These establish that hierarchical budget allocation and online
  model routing are already active directions.

The remaining distinction is the evaluation layer: HAPR chooses a complete
retry policy from a registered finite row set before deployment, sees only
paid answer-key-blind cells, records the realized charge of each verifier-
gated execution, and uses same-question paired residuals only to prioritize
the next complete-row evaluation. MCPP/Aragog/EvoRoute can be compared as
deployment-policy or oracle-informed baselines, but they do not replace a
partial-observation identification baseline. Conversely, HAPR should not
claim to improve online routing unless that additional setting is measured.
