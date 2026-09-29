# Runtime verifier and switching overlap

Three papers make the deployment-side boundary explicit:

* [BATS](https://arxiv.org/abs/2511.17006) gives a budget tracker and a
  policy that decides whether to deepen a promising path, pivot, or start a
  new attempt under tool/token budgets. It measures path-dependent cost and
  verifier-aware scaling for a fixed agent workflow.
* [ModelSwitch](https://arxiv.org/abs/2504.00762) uses consistency to stop one
  model and switch to a complementary model during repeated sampling. It is a
  direct prior for non-prefix model complementarity and verifier-gated runtime
  switching, but is per-question inference with a fixed sampling budget.
* [Budget-aware Test-time Scaling via Discriminative Verification](https://arxiv.org/abs/2510.14913)
  allocates fixed compute between self-consistency and a cheaper discriminative
  verifier. It shows that verifier selection itself changes the cost-quality
  frontier.

These methods should be described as execution-side baselines or motivation,
not as outer row-search competitors. HAPR keeps the verifier and retry policy
inside each complete candidate row and asks a different question: which row
should be profiled and recommended before deployment under sparse paid cells?
If the project later lets the verifier or runtime switch adaptively, the
problem changes and these methods become direct baselines. The current claim
must not say that path-dependent cost, model complementarity, or budget-aware
verification is new in isolation.
