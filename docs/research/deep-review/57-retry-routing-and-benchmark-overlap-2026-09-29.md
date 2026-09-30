# Retry routing and benchmark overlap

Additional papers make the baseline set more complete.

* [InflationAgent](https://arxiv.org/html/2608.13571) predicts retry/token
  inflation and routes among escalation choices with first-success stopping.
  It measures true path-dependent retry cost and reports a fixed-budget
  accuracy--cost gain. It is a runtime stage/escalation policy for each query,
  not sparse identification of one complete row across a benchmark.
* [RouterEval](https://aclanthology.org/2025.findings-emnlp.208/) and
  [LLMRouterBench](https://arxiv.org/html/2601.07206) standardize large
  per-query/model response records, routing baselines, costs, and Pareto
  metrics. They are useful matrix and evaluation references, but their arm is
  one model for one item and their oracle assumes broad response coverage.
* [ThriftLLM](https://arxiv.org/abs/2501.04901) chooses a static set or
  ensemble of LLMs under a cost budget. [CAPS](https://arxiv.org/abs/2605.15513)
  reduces pairwise verifier effort through cascaded adaptive comparisons.
  [Cascaded Language Models for Cost-Effective Human--AI Decision-Making](https://papers.neurips.cc/paper_files/paper/2025/hash/10e0c427408ccc6e073d9464e2280f89-Abstract-Conference.html)
  learns confidence-gated escalation with a human fallback. These cover
  global model-set choice, verifier allocation, and cascades, respectively;
  none is a complete-row sparse profiler with a shared-question ledger.

The required comparison matrix now includes runtime escalation, per-query
routing, static model-set selection, verifier-only allocation, and outer
complete-row identification. A positive result against only random or a weak
independent-arm baseline would not establish the project claim.
