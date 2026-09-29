# Partial-feedback and cost-aware BAI overlap

Several recent papers close the gap between “we do not have a response matrix”
and generic similarity-based search. They must be treated as direct baselines
or scope boundaries.

* [PILOT: Adaptive LLM Routing under Budget Constraints](https://aclanthology.org/2025.findings-emnlp.1301/)
  treats each LLM as an arm for an independent query stream. It observes
  feedback only for the selected model, uses a shared query--LLM embedding
  space, and combines preference-prior LinUCB with a budget policy. This is a
  strong partial-feedback and cost-aware routing baseline. It does not select
  one benchmark-wide complete retry row: a retry row couples several model
  calls, verifier feedback, reach, and charge for the same question.
* [BaRP](https://arxiv.org/html/2510.07429v1) learns a routing policy from
  bandit feedback with prompt context and a cost--quality preference. It tests
  REINFORCE and standard contextual bandits, but its arm is still one model for
  one query. Flattening each slot of a retry row into this setting loses the
  endogenous continuation and the shared row recommendation target.
* [Cost Aware Best Arm Identification](https://arxiv.org/abs/2402.16710)
  gives a direct cost-aware identification objective and Chernoff-style
  allocation/stopping rules. [DBCARE](https://arxiv.org/abs/2505.20583)
  instead balances misidentification risk and sampling cost without requiring
  a fixed budget. These establish that “find the best arm cheaply” is not the
  contribution by itself.
* [Best Arm Identification in Generalized Linear Bandits via Hybrid
  Feedback](https://arxiv.org/abs/2605.05745) combines absolute and relative
  observations with cost-aware likelihood-ratio stopping. [Fusing Reward and
  Dueling Feedback](https://arxiv.org/html/2504.15812v1) similarly chooses
  between absolute and pairwise feedback. A same-question hub comparison is
  related to their relative-feedback channel, but our two row outcomes are
  correlated benchmark executions with hidden correctness and endogenous
  verifier-gated costs; they are not independent duels with a fixed preference
  probability or a known generalized-linear feature map.
* [Efficient Graph Bandit Learning with Side-Observations and Switching
  Constraints](https://ojs.aaai.org/index.php/AAAI/article/view/33854) and
  [Near Optimal Best Arm Identification for Clustered
  Bandits](https://proceedings.mlr.press/v267/yash25a.html) cover graph or
  cluster structure. A neighboring row in our problem does not reveal its
  correctness label when another row is executed, so HAPR must not call a
  guessed similarity relation a side-observation graph or a shared-mean
  cluster.

The defensible distinction is therefore an information and action contract,
not a list of ingredients. HAPR receives only paid cells
`(row, question)` and may use a paid hub to form a paired residual on questions
that both rows actually ran. It uses that residual to select the next complete
row action and then directly confirms the recommendation. A contextual router
or graph BAI method that predicts an unpulled row from features is a useful
baseline, but its prediction is not a deployment observation and cannot by
itself certify the chosen row under hidden gold labels.

The main ablations should consequently include: independent cost-aware BAI;
PILOT/BaRP-style contextual routing; a relative-feedback or dueling baseline;
and HAPR with residual transfer disabled. All must use the same registered
questions, hard/soft budget convention, and direct-confirmation rule.
