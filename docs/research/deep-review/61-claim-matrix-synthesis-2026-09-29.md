# Claim matrix synthesis after the expanded audit

The related work now separates into three families:

1. **Per-query execution policies.** PromptWise, InflationAgent, C3PO,
   Bayesian Self-Escalation, MCPP, BATS, ModelSwitch, and RoR choose or stop
   within one incoming task, usually with calibrated signals or precomputed
   draws.
2. **Query-level routers and ensembles.** PILOT, BaRP, RouterEval,
   LLMRouterBench, ThriftLLM, and related routing work choose one model or a
   model set per item, often with full or broad per-item matrices.
3. **Outer cost-aware bandit/HPO.** Cost-aware BAI, DBCARE, the 2026
   multi-objective LLM configuration work, EcoTune, and generic structured
   bandits allocate profiling effort across configurations or hyperparameters.

The defensible gap is the intersection: recommend one complete retry row
globally after limited profiling, where final correctness is obtained only
after the verifier-gated trajectory, charge is path-dependent, and row cells
on the same question can be compared through paid paired anchors. The
algorithm must transfer only observed residuals or a calibrated structural
effect, then confirm the chosen row on fresh questions.

The 2026 multi-objective LLM configuration paper is a useful anchor because it
explicitly treats configurations as independent arms and names structural
information among models/prompts/decoding parameters as future work. That
supports a structured-row extension as a research question, not as proof that
the extension is novel. The paper's independent-arm method, EcoTune-style
token-aware HPO, and DBCARE should be primary outer baselines.

The manuscript should therefore avoid “first cost-aware routing,” “first
budgeted retries,” “first use of similarity,” and “first path-dependent LLM
cost.” A precise conditional claim is stronger: under the registered
finite-population and charge-bound assumptions, a reach-aware hub-anchored
paired racing procedure can lower profiling spend or improve held-out
complete-row identification at matched spend.
