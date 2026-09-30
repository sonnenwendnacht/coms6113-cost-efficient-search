# Agentic routing and serving overlap

The direct prior-art boundary is now broader than static model assignment.

* [Budget-Aware Agentic Routing (BAAR)](https://arxiv.org/html/2602.21227v1)
  formulates sequential model choice in a long-horizon agent as a POMDP/CMDP,
  optimizes success against trajectory cost, and mechanically prunes actions
  that exceed a remaining hard budget. It uses boundary policies and repeated
  probes to build cost-effective routing trajectories.
* [AgentRouter: Heterogeneous Model Routing for Cost-Optimal Multi-Step Agentic
  Workflows](https://arxiv.org/abs/2609.22951) assigns model tiers at each
  trajectory step under an end-to-end quality frontier. Its action space is
  dynamic step routing, not a fixed row selected before deployment.
* [Dyserve](https://arxiv.org/html/2607.02942v2) is a serving/compiler system
  that profiles complete model–verification choices for workflow nodes and
  adapts undispatched choices at runtime. It therefore covers practical
  model/verifier pairing and recovery, although its profiles are given to an
  optimizer rather than learned through a finite-arm search guarantee.
* [Self-Healing Agentic Orchestrators](https://arxiv.org/html/2606.01416v1)
  study monitor–diagnose–recover–verify loops under bounded retry budgets. The
  work is a reliability/recovery comparison, not configuration profiling, but
  it reinforces that verifier-triggered retries are established system
  behavior.

These papers rule out broad claims such as “we introduce budget-aware model
routing for retrying agents” or “we are the first to optimize model and
verifier choices jointly.” They also suggest strong deployment baselines if
the project later allows question-specific routing.

The remaining HAPR/CAPR scope is an *outer profiling problem*: before
deployment, use a finite budget to identify one complete retry row from a
declared row set. The deployment verifier is answer-key blind, while a
benchmark profiler may receive the post-run correctness score for a cell it
paid; held-out questions remain unavailable until recommendation.
The proposed mechanism is same-question paired evidence and a reusable
complete-row hub without prefix materialization. Its advantage must be shown
against a cached-incumbent row-search baseline and, where feasible, against a
BAAR/Dyserve-style deployment oracle. If the group instead wants a dynamic
per-question router, it should adopt the routing/CMDP literature directly and
stop calling that problem Algorithm 2’s global-row selector.

## Required wording change

The manuscript should say “adaptive profiling and identification of complete
retry policies” rather than “adaptive agentic routing.” The former describes
the untested outer problem; the latter is already a large literature with
several 2026 methods and deployment systems.
