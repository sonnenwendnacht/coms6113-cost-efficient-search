# Mentor-paper v2 boundary

The mentor's newer [Efficient Cost-Aware LLM Evaluation via Bayesian Bandit
Gittins Indices](https://arxiv.org/html/2609.25645) is the closest outer
baseline. It treats each complete configuration as a row arm, allows partial
evaluation, models heterogeneous per-row costs, recommends with a lower
confidence bound, and reports near-zero simple regret at a small fraction of
exhaustive evaluation cost.

The paper's assumptions are materially different from the retry trace. Its
row scores are conditionally iid within an arm; arms are independent Markov
chains; local-stage batch costs are predetermined; the posterior is Gaussian;
and the per-example row cost is a fixed API-price proxy. Its experiments use
precomputed complete response matrices rather than generating a verifier-
gated trajectory online.

For a retry row `r=(m0,m1,m2)` and question `q`, our observation is instead

```text
tau_rq = verifier-gated reached attempts
Y_rq   = final gold correctness after tau_rq
C_rq   = sum of realized solver/verifier input charges through tau_rq
```

Rows sharing a model coordinate can have correlated `(Y,C)` on the same
question, and later attempts are missing-not-at-random because the verifier
only reaches them after earlier failure. These violate the independent-arm,
fixed-cost, and separable-stage assumptions behind a direct Gittins transfer.

The paper must be cited as the primary baseline. HAPR's claim must be narrower:
structure-aware cost-sensitive pure exploration for complete retry rows under
verifier-censored, path-dependent feedback, using observed same-question
paired anchors and held-out confirmation. If an implementation only adds a
similarity prior over independent row means, it is likely incremental; it
must exploit the path-level censoring/coordinate-sharing distinction and
include a direct GittinsEval ablation.
