# Compiler and program-routing overlap

Two more papers are especially close to the phrase “profile cheaply, then
recommend a configuration.”

* [FlowCompile](https://arxiv.org/html/2605.13647) compiles structured LLM
  workflows by profiling sub-agents, composing a workflow-level proxy, and
  returning accuracy--latency trade-off configurations without exhaustive
  full-workflow profiling. It can route queries over the compiled set. Its
  proxy assumes decomposable sub-agent evidence and produces a Pareto set; it
  does not provide hidden-gold, verifier-gated row certification with realized
  path-dependent monetary charges or same-question paired residuals.
* [Resource-efficient Inference with Foundation Model Programs](https://arxiv.org/abs/2504.07247)
  optimizes backend assignments in programs whose control flow means that only
  executed operations incur cost, using policy-gradient and Thompson-sampling
  components. This is a direct prior for path-dependent execution cost and
  adaptive backend allocation. Its target is online per-input policy routing
  with feedback in the stream, not outer sparse profiling of one complete
  retry row when the final correctness label is held out.

These papers make two claims unsafe: path-dependent cost alone is not new, and
composing per-node profiles into a workflow proxy is not new. HAPR's narrower
claim must specify the observation ledger and decision target: a finite set of
complete retry rows, answer-key-blind executions, same-question paired
contrasts against a paid hub, conservative cost accounting, and direct
confirmation of the final recommendation. FlowCompile-style proxies and
program-routing policies are required comparison points if the method later
uses sub-agent summaries or online routing.
