# Workflow structure: what is already known and what remains worth testing

Prepared 2026-09-23. This is a source audit and mathematical analysis, not an empirical result or a novelty claim. Read alongside the other deep-review notes. No model calls were made. Original examples below are invented counterexamples, not benchmark measurements.

The user's interpretation is correct for the proposed scope: choosing a fixed model assignment for each workflow invocation is configuration optimization. The promising extra structure is that **one execution can reveal outcomes for several configurations, and the cost and relevance of another observation depend on the execution state already obtained**. Counting changed model assignments is an unreliable substitute for this structure.

## Reading depth and reproducibility

| Source | Material actually inspected | Evidence locations |
| --- | --- | --- |
| [AgentOpt v2](https://arxiv.org/abs/2604.06296v2) | All 24 PDF pages, including Appendix A; selected current upstream code | §§3.1, 4.4, 5.1–5.3, 6; Algorithms 1–6; Tables 6, 7, 10, 11 |
| [VineLM v1](https://arxiv.org/abs/2605.23914v1) | All 16 PDF pages, including Appendix A | §§3.3–3.5, 4.2–4.4, 5.2–5.4; Appendix A.2–A.4 |
| [SySRs v1](https://arxiv.org/abs/2606.07726v1) | Main formulation/algorithm/theory, selected proof and implementation sections; not a full experimental reproduction | §§3–5; Algorithm 1; Theorem 5.1; Lemma B.2 and its proof; current `bai_algs.py` |
| [FlowCompile v1](https://arxiv.org/html/2605.13647v1) | Abstract, §3, selected §4, Appendices A, B, L; partial reading only | §3.2–3.4; Algorithm 1; Appendix B.3; limitation concerning upstream input shifts |

The three local PDFs are pinned by `papers/manifest.json`. Public upstream snapshots were downloaded as source archives into ignored `.cache/deep-workflow/`; none of their scripts, dependencies, or serialized datasets were executed.

- AgentOpt: [`08b2d2c7fe370c884d956afbe540a09abc163c27`](https://github.com/AgentOptimizer/agentopt/tree/08b2d2c7fe370c884d956afbe540a09abc163c27).
- SySRs: [`ed01a431aedb439ac8ba5726b54fbefae5dc6119`](https://github.com/zifanlyu/llm-bandits-sysrs/tree/ed01a431aedb439ac8ba5726b54fbefae5dc6119).

These are repository snapshots retrieved for this audit, **not verified paper-release commits**. VineLM's PDF, arXiv page, author publication page, and targeted searches did not expose a public implementation that could be pinned. This does not establish that no code exists; obtaining the authors' implementation remains a concrete next step.

## Source findings

### AgentOpt

AgentOpt optimizes complete role assignments and reports quality/cost/latency tradeoffs. Its bandit arm is a combination; a pull executes it on one question. Plain Matrix UCB-E uses row means and observation counts, with a matrix-cell budget; it does not statistically transfer observations between rows. The LRF variant adds transfer through matrix factorization. Hill climbing explicitly changes one role at a time; Bayesian optimization uses a surrogate. Identical HTTP calls are cached, retaining measured latency. Its MathQA configuration binds one answer model and one critic model across repeated rounds. [Paper, §§3.1, 4.4, 5.1–5.3, 6.1, pp.5–11](https://arxiv.org/pdf/2604.06296v2).

Therefore, neither configuration search, local one-coordinate moves, matrix estimation, nor identical-call reuse is an open novelty claim. The reported UCB search budget is a count of observations, while dollar spending is an evaluated outcome. Distinguish “optimize deployment cost” from “allocate profiling by marginal dollar cost.” Plain UCB's displayed selection formula contains neither a cost denominator nor a prefix-reach term. [Algorithms 1–2, pp.9; Tables 4–7, pp.20–21](https://arxiv.org/pdf/2604.06296v2).

### VineLM

VineLM already exposes invocation-specific choices, shared-prefix checkpoints, random cascade profiling, and descendant-success fill-in. It reconstructs path success from prefix success and continuation success conditional on failure of that entire prefix; sparse deep conditional rates receive rank-one smoothing. Expected cost discounts unreached calls; its latency annotation instead sums reached-stage conditional means. Runtime control repeatedly searches the remaining trie after observing elapsed time. [§§3.3, 4.2–4.3; Appendix A](https://arxiv.org/pdf/2605.23914v1).

The paper explicitly recognizes decision errors near feasibility boundaries (§3.5), prefix reuse as variance reduction (§4.2), and the relevance of reached-population continuation value (§5.2). These are substantial overlaps with our initial idea. Its described offline sampler is random; the inspected method does not specify an uncertainty-driven choice among competing continuation measurements. Its recursion and fill-in require absorbing success; monotone accuracy is an explicit assumption (§3.4). The link between benchmark correctness and a deployable stopping signal remains to be resolved before reproduction. The paper's own profiling comparison separates checkpointed exhaustive evaluation from independent root-to-leaf evaluation (Table 2). [pp.5–8, 10–11, 15–16](https://arxiv.org/pdf/2605.23914v1).

### SySRs

SySRs is best-arm identification under a fixed number of model–question evaluations. In each pre-scheduled phase, all surviving models receive the same uniformly sampled questions without replacement; the empirical worst is eliminated. The phase sizes are fixed by the budget, although the surviving set adapts. Its error bound uses the variance of the **paired score difference**, so positively correlated scores help without knowing correlation beforehand. It permits stochastic scores, beyond a deterministic response matrix. [§§3–5, Algorithm 1, Theorem 5.1](https://arxiv.org/pdf/2606.07726v1).

Its published hardness term has the form `i * [2 Var(Y_best-Y_i) + (2/3)(1+gap_i)gap_i] / gap_i²`, maximized over competitors. Thus, shrinking disagreement is already an established way to improve identification. The stated budget/theorem does not account for heterogeneous workflow execution charges, reusable checkpoints, or choosing whether to acquire another prefix versus another continuation. Adapting the schedule to these actions requires a new analysis; its theorem is not a certificate for any algorithm that happens to pair questions. [§5; Appendix B.1–B.2](https://arxiv.org/pdf/2606.07726v1).

### FlowCompile: additional direct overlap

FlowCompile profiles workflow components using filtered reference-model traces, composes those profiles into a quality/latency proxy, prunes locally dominated component choices, and enumerates the remaining configuration space. Bounded retries are unrolled; conditional branches are weighted by estimated execution probability. The proxy assumes approximate frontier/ranking preservation and is explicitly an approximation. Upstream-induced input shifts are acknowledged as a limitation. [§3; Appendices A, B.3, L](https://arxiv.org/html/2605.13647v1).

This makes component-profile reuse and probability-weighted retry composition insufficient novelty claims. Our direction would need to establish something about **which additional true execution to purchase under uncertainty**, or validity under interactions the proxy does not capture. We have not audited its code or reproduced its experiments.

## Implementation audit: important for an honest baseline

These observations concern the pinned code, not proof of how the paper's experiments ran.

| Observation | Source evidence | Consequence for our implementation |
| --- | --- | --- |
| Plain UCB selects one row from its mean plus `sqrt(a/n)`, then random unobserved cells; stopping counts cells. | AgentOpt [`matrix_ucb.py`, `_ucb_plain_next_batch`, `_target_observation_count`](https://github.com/AgentOptimizer/agentopt/blob/08b2d2c7fe370c884d956afbe540a09abc163c27/src/agentopt/model_selection/matrix_ucb.py#L66) | Add a separate physical spending stop to an adapted baseline; do not call row UCB a shared-prefix acquisition rule. |
| Cost/latency scalarization uses running min/max normalization when weights are nonzero. | AgentOpt [`base.py`, constructor and `_combined_objective`](https://github.com/AgentOptimizer/agentopt/blob/08b2d2c7fe370c884d956afbe540a09abc163c27/src/agentopt/model_selection/base.py#L743) | For comparisons use a fixed externally defined utility or fixed constraints. An observed outlier should not redefine the scientific objective. |
| Runtime exceptions are logged and omitted from normal returned sample lists. Matrix selection separately inserts a zero-score placeholder when a cell returns no score. | AgentOpt [`base.py`, `_evaluate_agent`, asynchronous counterpart](https://github.com/AgentOptimizer/agentopt/blob/08b2d2c7fe370c884d956afbe540a09abc163c27/src/agentopt/model_selection/base.py#L855), [`matrix_ucb.py`, `_record_cells`](https://github.com/AgentOptimizer/agentopt/blob/08b2d2c7fe370c884d956afbe540a09abc163c27/src/agentopt/model_selection/matrix_ucb.py#L160) | Specify timeouts, API errors, retries, labels and charged costs once for every method. Silent denominator changes can distort rankings. |
| Arm elimination consumes the same ordered dataset batches but uses separate per-arm standard errors. | AgentOpt [`arm_elimination.py`, `_select_sequential`, `_is_dominated`](https://github.com/AgentOptimizer/agentopt/blob/08b2d2c7fe370c884d956afbe540a09abc163c27/src/agentopt/model_selection/arm_elimination.py#L60) | A shared question order is not yet a paired-difference confidence interval. Shuffle once per run and preserve question IDs even after failures. |
| The cache key hashes payload and optional request path, excluding `stream`; it has no explicit experiment repetition identity. | AgentOpt [`cache.py`, `_make_cache_key`](https://github.com/AgentOptimizer/agentopt/blob/08b2d2c7fe370c884d956afbe540a09abc163c27/src/agentopt/proxy/cache.py#L36) | Cache semantics must distinguish a reused random draw from an independent replicate. HTTP equality alone does not certify tool/environment-state equality. |
| Current SySRs code uses a shared task permutation and an additional finite-task budget-reallocation helper. | SySRs [`bai_algs.py`, `smart_successive_rejects_wo_replacement_no_budget_limit`](https://github.com/zifanlyu/llm-bandits-sysrs/blob/ed01a431aedb439ac8ba5726b54fbefae5dc6119/bai_algs.py#L737) | Record whether a reproduction uses paper Algorithm 1 or the code's finite-task extension. |

There are also paper-level denominator questions. AgentOpt Appendix Table 6 describes 199 questions and 81 combinations but reports 16,168 brute-force evaluations; `199*81=16,119`. Table 7 describes 200 questions and 81 combinations but reports 14,961 evaluations; `200*81=16,200`. Some MathQA reported accuracies are not multiples of `1/200`, despite the exact-match description. These are **unresolved reporting/reproduction questions**, not evidence of misconduct and not evidence of a particular cause. Obtain run-level counts and task IDs before treating the tables as a complete rectangular response matrix. Current exception handling suggests one possible denominator issue but does not establish the historical explanation. [AgentOpt, pp.11–12, 21, 24](https://arxiv.org/pdf/2604.06296v2).

## Our analysis: three meanings of “similar”

1. **Assignment similarity:** configurations differ in one chosen model. This is known before execution but offers no universal bound on outcome difference.
2. **Execution overlap:** the same task and complete execution state induce identical computation until a known divergence. This permits exact computational reuse under explicit randomness/environment semantics.
3. **Outcome correlation:** configurations tend to succeed and fail on the same questions. This can reduce paired uncertainty even when no computation can be reused.

These properties can occur separately. Two configurations differing at the first stage can still have highly correlated final scores but share no expensive prefix. Two configurations can share a costly prefix yet have almost independent suffix quality among reached cases. A one-slot change at an early planner may change all later prompts. A different late retry may never run. The proposed method should exploit the second property and measure the third, rather than assume both from the first.

An invented counterexample to Hamming-distance smoothness: a planner emits either schema A or schema B; the unchanged solver understands only A. Replacing that one planner changes final accuracy from one to zero. Conversely, replacing ten model assignments in branches that never execute changes nothing. No nontrivial global Lipschitz constant follows solely from a count of changed assignments.

An invented counterexample to global retry-model ranking: half the questions are algebra, half geometry. Prefix P fails only algebra; prefix Q fails only geometry. Continuation A solves only algebra; B solves only geometry. A and B have the same unconditional accuracy, but their rankings reverse between P's and Q's reached populations. Pooling a repair model's success across preceding histories loses the relevant quantity.

## Our analysis: exact reach identities, including imperfect checkers

Take configurations `a` and `b` identical until their first possible divergent invocation. Draw a representative question and common execution randomness for that prefix. Let `R` indicate that this invocation is actually reached under the **deployable** stop rule. Assume that stopping beforehand gives the same final output under both configurations. Let final scores lie in `[0,1]` and let `D=Y_a-Y_b`.

Then, irrespective of whether a checker is accurate:

```text
D = 0 on R=0
rho = P(R=1)
delta = E[D | R=1]
Delta = E[D] = rho * delta
|Delta| <= rho
Var(D) = rho Var(D | R=1) + rho(1-rho) delta² <= rho
```

This is a distributional decomposition, not a new theorem. Its practical value is that structure certifies a source of zero differences **before paying for both continuations**. Small reach bounds the maximum accuracy gain, while the actual paired variance determines how hard it is to resolve a small remaining gap.

If each reached continuation pair costs `k_a+k_b` and a fresh shared prefix costs `k_pre`, the expected physical expense per representative paired trial is

```text
E[k_pre + R*(k_a+k_b)].
```

Do not replace this with `E[k_pre] + rho*(E[k_a]+E[k_b])` unless suffix expectations are explicitly conditional on reaching the divergence. Prices and reach can correlate through question difficulty. Do not count the cache saving twice: each configuration's cold deployment cost still includes its own prefix. Prefix checkpoints acquired by another project/run are historical data with an acquisition cost and declared availability, not evidence of a zero-cost search from scratch.

An early stop from an incorrect accepted answer still gives exact equality between these two configurations. The shared label is zero if that final answer is wrong; it is not necessarily one. This preserves the reach-difference argument while avoiding an oracle-success assumption.

For a parent prefix `u` with reached event `R_u`, a generally valid final-accuracy identity is

```text
mu(continuation a after u)
  = E[final_score * 1{terminated before a}]
    + P(R_u=1) E[final_score under a | R_u=1].
```

The first term is common to alternatives sharing `u`. It need not equal `P(prefix produced a correct answer)`, because a checker can accept an incorrect answer or reject a correct one.

## Our analysis: why absorbing correctness needs special care

VineLM's success-anywhere semantics are a legitimate model for certain workflows, but they are stronger than “there is an LLM checker.” Our adaptation must state which setting it evaluates.

- **Correct answer overwritten:** a first attempt is correct, the checker rejects it, and refinement changes it to an incorrect final answer. Best-answer-ever success is one; final-output success is zero. More rounds can reduce accuracy.
- **Incorrect answer accepted:** a wrong first answer passes a syntax/public-test checker and execution stops. The later model could have solved it, but that model is never reached in deployment. An oracle-error cascade estimates a different workflow.
- **Same model, changed state:** an unchanged repair model receives a different failed candidate and error message after an upstream change. Reusing its earlier answer is invalid even if question ID and model name match.

These examples do not refute results under the paper's stated assumptions. They identify conditions that our benchmark must check. A deployment-faithful experiment should separately log ground-truth score, checker verdict, chosen next invocation, and retained final answer. A perfect-checker version can be an explicitly idealized ablation, but should not silently supply the main algorithm's retry signal.

Two further distinctions matter when reusing an estimator or controller:

- Conditional decomposition requires representative observations **within each reached population** and sufficient observations wherever the reach probability is positive. A rank-one projection is a separate modeling assumption; if true conditional rates have higher rank, more data do not make an enforced rank-one model exact. Zero observed reaches also does not establish zero population reach.
- Expected deployment cost across all questions differs from expected remaining cost for a request known to have reached `u`. If a plan only appends a suffix after `u`, then `E[C_extended-C_stop]=P(R_u) E[C_suffix|R_u]`. Once `R_u=1` is known, the expected remaining bill is the conditional quantity. Likewise, a sum of conditional mean stage latencies is not a worst-case or high-probability latency guarantee. These distinctions must be explicit in any runtime adaptation; this audit does not assert an implementation bug in unavailable VineLM code.

## Our analysis: what an additional research contribution would need

Combining cached execution with SySRs is an essential baseline and a sensible first implementation. By itself, it is a straightforward composition of known methods. A more specific research target is:

> Under a fixed profiling-dollar budget, choose which representative prefix or matched continuation to measure next, using its incremental execution cost and its ability to change the final configuration decision; maintain valid uncertainty despite shared observations and conditional reach.

The distinction from the inspected random cascade profiler is **allocation**, rather than the trie or the conditional-success identity. The distinction from SySRs is **the observation and spending model**, rather than pairing alone. A strong result might characterize when acquiring a new representative prefix is more valuable than extending an already sampled one. It might also derive an elimination rule that remains valid for ordinary imperfect checker behavior. None of this has yet been established as novel across the broader literature.

There are two allocation levels:

1. Explore prefixes to estimate how often a difference matters, create representative reached states, and cover different configuration families.
2. At reached states, compare continuations to learn which model assignment is useful within that conditional population.

A purely local neighbor walk can miss a better region. Starting with an all-cheap assignment is not a guarantee that improving single changes can reach the best assignment. For example, two roles may require compatible protocols: both `(A,A)` and `(B,B)` work, but `(A,B)` and `(B,A)` fail. If `(B,B)` is better, a strict improving one-change walk started at `(A,A)` cannot discover it. Retain global proposals or explicitly restrict the claimed candidate pool.

### Precision about uncertainty

For independent estimators from two deliberately separated sample streams, let `rho_hat` estimate reach from `n` representative prefixes and `delta_hat` estimate the reached-population paired mean from `m` representative reached states. Writing `v=Var(D|R=1)`, a calculation gives

```text
Var(rho_hat * delta_hat)
  = delta² rho(1-rho)/n
    + rho² v/m
    + rho(1-rho) v/(n*m).
```

This illustrative expression shows two different uncertainties. It is **not** automatically the variance formula for a shared adaptive reservoir: the estimators there can be dependent. It also does not make reached samples free. If each qualifying state must be obtained by screening fresh prefixes, obtaining one such state takes `1/rho` prefixes on average in the simple independent-trial model. Charge that screening unless the state is already legitimately available.

If sampling favors cheap/easy reached questions, the conditional mean changes. An arbitrary average of those selected continuations is not `delta`. A first implementation can avoid this by using uniformly sampled question/replicate streams and fully paired observations; later selective schemes require recorded selection probabilities, overlap conditions, and appropriate weighted/adaptive inference. Reused cached copies are correlated observations and never increase the number of independent sampled questions or prefix replicates.

The conservative alternative is to maintain intervals for reach and for conditional differences and propagate their entire product set, including both endpoints and zero when appropriate. With simultaneous valid intervals, this gives a valid interval for the overall difference; replacing reach with its point estimate does not. If questions are sampled adaptively or stopping depends on the data, ordinary fixed-sample intervals inspected repeatedly are insufficient.

### Small reach is not automatically an easy exact-identification problem

Suppose two configurations differ only on a fraction `rho` of tasks and their conditional difference remains fixed as `rho` shrinks. Their overall gap also shrinks like `rho`. Although unconditional paired variance is at most of order `rho`, resolving the sign to fixed confidence may still need order `1/rho` representative trials, rather than fewer trials. Structure is especially useful for an **epsilon-optimal** target: a reliably tiny reach probability may certify that an accuracy difference cannot matter at the chosen tolerance. It may also help dollar efficiency when expensive common prefixes are shared among many continuations.

For cost-constrained selection, however, rare execution is not enough. A rare suffix may have enormous cost or latency. Require bounds or measure their tails. An accuracy-equivalence claim does not certify either cost feasibility or latency reliability.

## What would count as evidence beyond implementation

The minimum comparison set should share one execution engine, one cache policy, one scoring/checker policy, and one charged-spending ledger:

| Comparison | Question it resolves |
| --- | --- |
| Random configuration proposals with equal-dollar stopping | Is adaptive selection useful at all? |
| Uniform or synchronized evaluation with exact reuse | Do gains exceed computational reuse and shared questions? |
| SySRs-style synchronized elimination with exact reuse | Does our acquisition improve on an existing strong correlation-aware baseline? |
| AgentOpt-style UCB allocation with exact reuse and dollar stopping | Does reach/continuation information help beyond ordinary configuration allocation? |
| Random cascade profiling plus VineLM-Lite/full estimation under matched semantics | Does adaptive profiling improve decisions over the nearest trie profiler? |
| Proposed method without reach allocation, without pairing, and without cache reuse | Which mechanism causes any gain, and are the interactions real? |

If comparing a static per-invocation plan against a runtime-adaptive policy, report it as a policy-class comparison. It cannot isolate profiling quality. Similarly, granting one method richer retry assignments or access to benchmark correctness changes the problem.

Useful stress axes are divergent-slot position, actual reach probability, conditional continuation correlation, model price ratios, prefix expense, non-monotone refinement, checker error, and incompatible cross-stage assignments. These directly test the user's similarity hypothesis and its failure cases. Merely increasing the number of models does not isolate any of them.

For a small enumerated space, use an independently collected exhaustive reference to assess search behavior while hiding unrevealed entries from each search method. For a larger space, compare the recommendations on held-out questions and report measured quality, deployment spending, and constraint violations at equal search-dollar checkpoints. Neither the best observed configuration nor the best searched neighbor proves a global optimum.

## Questions left open by this audit

- Obtain VineLM's profiler/checker code and clarify whether sparse-profiling termination uses ground truth, deployable feedback, or a success-anywhere offline metric. Do not infer this from a workflow name.
- Obtain AgentOpt's exact paper-release commit, benchmark agents, raw per-question completion/error records, and cache-aware cost reconstruction.
- Compare against the exact finite-sample and dollar-budget versions of synchronized elimination before proposing a more complicated method.
- Resolve whether saved-prefix pair sampling gives enough extra information per dollar after accounting for screening and rare reach. This is an empirical and theoretical question, not a guaranteed benefit of structure.
- Inspect broader structured best-arm identification, correlated-arm feedback, adaptive experimental design, and common-random-number simulation optimization before claiming the acquisition rule is new. This note does not constitute an exhaustive novelty search in those areas.

The actionable next step is a small, rigorously accounted comparison in which **the cache and paired evaluation already work for every strong baseline**. If the proposed allocation cannot beat that comparison, a new name for the combined machinery would not establish a research contribution.
