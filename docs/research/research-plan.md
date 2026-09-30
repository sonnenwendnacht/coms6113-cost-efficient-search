# Research plan: paying for the measurements that change the decision

Prepared 2026-09-23. **Status: research proposal, not experimental findings.** The repository's synthetic accounting checks are software checks; they do not establish that a search method works. Benchmark, models, spending budget, and research roles remain group decisions.

Follow-up: use the [detailed assessment](deep-review/README.md) and [formal inference note](deep-review/03-formulation-and-inference.md) for the current proposal. They refine the prior-art boundary, give valid partial-execution bounds, and distinguish unknown exact regret from a conservative whole-space certificate. This initial plan remains as context, not an approved experiment specification.

## 1. The question in plain language

The project is configuration search: choose which model runs at each step and retry, learn which combinations are useful, and spend as little as possible learning that. The analogy to hyperparameter search is accurate. The workflow setting adds structure: configurations can share work, later attempts are reached only for some questions, and the price of the next measurement depends on work already done.

The row of the response matrix is a **complete configuration**; a column is a benchmark question. A measurement reveals the configuration's final answer quality and the cost/latency of its executed path on that question. Choosing a row is the bandit decision in the basic formulation. Choosing a question too is a richer experimental-design problem; it does not automatically make each matrix cell a separate arm.

This is primarily a final-recommendation problem: evaluations cost money so we can choose a good configuration later. Maximizing reward accumulated during evaluations is a different objective. Begin with a fixed collection of configurations, not a learned policy that changes model choices in response to arbitrary intermediate states.

**Working hypothesis:** at the same search-dollar budget, comparing configurations on matched questions, reusing their identical execution prefixes, and accounting for how often their differing parts are reached can improve the quality of the final recommendation. Improvement must persist against baselines given the same execution cache and observations.

## 2. What is already known, and where a contribution could remain

| Primary source | Existing idea that our paper cannot claim as new | Required comparison or implication |
| --- | --- | --- |
| [GittinsEval, Xie et al., v1](https://arxiv.org/html/2609.25645v1) | Cost-aware allocation across configurations, stopping, and anytime recommendations. Its arm-specific price proxy is constant across questions; it evaluates fixed response matrices. | Reproduce its setting before extending it. Sharing information across arms changes its independent-arm model, so its optimality theorem does not automatically apply. |
| [AgentOpt, v2](https://arxiv.org/abs/2604.06296v2) | Configuration search, one-role-at-a-time hill climbing, Bayesian optimization, matrix-based estimation, and reuse of identical calls. | Include an adapted configuration-search baseline. Merely changing one model at a time is already covered. |
| [VineLM, v1](https://arxiv.org/abs/2605.23914v1) | Execution tries, checkpoint reuse, cascade profiling, and treatment of early-termination selection effects. | Compare profiling allocation with equivalent execution reuse. Its runtime replanning is a different policy class unless explicitly included in our target. |
| [SySRs, Lyu et al., v1](https://arxiv.org/abs/2606.07726v1) | Matched-question comparisons exploit similarity among model responses. | Include a paired-comparison baseline; response similarity alone is not a novelty claim. |
| [BanditEval](https://arxiv.org/abs/2407.06172), [PromptEval](https://arxiv.org/abs/2405.17202) | Estimating unobserved responses through response-matrix structure or configuration information. | Compare a structure-aware predictor if we claim statistical transfer, rather than only independent-arm search. |
| [Random Search](https://jmlr.org/papers/v13/bergstra12a.html), [Hyperband](https://jmlr.org/papers/v18/16-558.html), [BOHB](https://proceedings.mlr.press/v80/falkner18a.html) | Random configuration selection and adaptive allocation of evaluation resources. | Number of sampled questions can be an evaluation resource; reducing retry limits changes the configuration and is not automatically a faithful cheaper approximation. |

The possible contribution is narrower: **how to select the next matched workflow measurement when its information and incremental price depend on a shared prefix and a conditional retry path**, with valid uncertainty and evidence that this reduces total search expense. This is a hypothesis to investigate against the sources above, not an established novelty claim. It is also possible that a careful baseline already solves the useful part of the problem.

## 3. Define the experiment before designing the algorithm

Let `S` be the number of configurable stages and `R` the maximum number of retries per stage. There are `A = R + 1` possible attempts per stage, including the initial attempt. For `M` models at every slot, a fully specified static assignment has at most `M^(S A)` possibilities. Actual control flow may leave many slots unused. Different retry limits produce different configurations; state clearly whether those limits are searched or held fixed.

For configuration `x`, question `q`, and run randomness `z`, record:

- `Y(x,q,z)` in `[0,1]`: final benchmark score.
- `C(x,q,z)`: deployment cost of all executed calls, including unsuccessful attempts and the checker.
- `L(x,q,z)`: end-to-end deployment latency under a specified concurrency and timeout policy.
- A trace of invocation states, model snapshots, token usage, checker decisions, and failures.

The targets are `mu(x) = E[Y]`, `c(x) = E[C]`, and `ell(x) = E[L]`, over the stated question population and, when applicable, model randomness. A fixed finite response matrix instead defines empirical means over a particular benchmark. Keep these estimands distinct.

**Provisional primary objective:** maximize `mu(x)` subject to prespecified deployment cost and latency caps. Report actual performance and constraint violations, not only a single combined score. A utility `mu(x) - lambda*c(x) - eta*ell(x)` is a useful secondary analysis when `lambda` and `eta` are fixed before evaluation. A Pareto frontier can be secondary; auditing a larger recommended set has a real cost.

The runtime checker must be available at deployment. Benchmark answer keys are used to score final outputs, not to tell the workflow when to retry. For example, SQL execution errors are observable but a syntactically valid answer may still be wrong. An oracle checker using ground truth is permissible only as a separately labeled idealized experiment. Checker calls and false acceptance/rejection belong in the cost and quality analysis.

Determinism is an experimental convention to check, not a property guaranteed by temperature zero. First use a frozen, replayable benchmark with recorded outputs; then repeat a small set of cells to quantify real variability. A deterministic retry with an identical prompt and state is redundant. A useful deterministic retry must change the model, input, or failure feedback. If fresh model samples are intended, record replicate/seed identity and treat them as distinct observations.

## 4. Two different uses of similarity

**Exact reuse:** two configurations ask for the same computation from the same complete state. Its result can be reused under the experiment's semantics. A cache key must include the question and replicate, prompt and messages, model snapshot and decoding settings, tool/environment state, workflow/checker versions, and relevant prefix state. Identical model names alone are insufficient. Changed earlier outputs usually invalidate reuse of everything downstream. Side effects and external state must be replayable or isolated.

Reusing one stochastic prefix is a valid coupling of two suffix experiments only when that prefix has the correct deployment distribution for both configurations. It creates correlation; it does not produce two independent prefix samples. Copying a result into many equivalent rows must not multiply the sample size. Independent questions or independently generated prefix replicates remain the statistical units.

**Statistical transfer:** use observations of one configuration to predict another. Hamming distance (how many model assignments differ) is a possible feature, not a guarantee. An early planner change can alter all later prompts, while a late retry change may affect almost no questions. An additive model, kernel, graph, or low-rank predictor needs validation on configurations and questions excluded from its fit. Model-based predictions should guide exploration initially; they should not justify irreversible elimination until their uncertainty is calibrated.

Start with exact reuse plus paired comparisons. Add statistical transfer only if pilot data show that it predicts held-out differences and improves on these stronger baselines.

## 5. A concrete structural fact to build on

Consider configurations `a` and `b` whose execution is identical until a particular slot. Couple their common prefix on a representative question/run. Let `R_ab` indicate that execution reaches the first slot where they can differ. If execution terminates before that slot, both configurations have the same final result and deployment cost under this coupling.

For bounded final scores, define `D = Y(a,q,z) - Y(b,q,z)`. Then:

```text
D = 0 if R_ab = 0
E[D] = P(R_ab = 1) * E[D | R_ab = 1]
|E[D]| <= P(R_ab = 1)
E[D^2] <= P(R_ab = 1)
```

These are elementary identities under the stated coupling, **not a claim of a new theorem**. They show why the *position and reach probability* of a change are more informative than counting changed slots. Similar decompositions hold for cost differences and utility differences, but bounds require explicit maximum suffix costs/latencies. The quality bound does not by itself establish deployment feasibility.

For a common prefix costing `C_pre` and two suffixes, the physical profiling expense of a matched pair is:

```text
C_pair = C_pre + 1{R_ab = 1} * (C_suffix_a + C_suffix_b)
```

A prefix already available under the experiment's allowed cache can reduce *incremental* expense. However, the deployment cost for each configuration still includes its own common prefix. A cached prefix is not a free deployment prefix. Measured profiling latency after a checkpoint also excludes work that a fresh deployment must execute.

**Selection trap:** failed or reached questions are a selected population. The average quality of a retry among reached cases is not its unconditional quality, and it need not transfer to a different preceding model. The identity requires a reach rate measured for the same prefix on representative questions. Maintain the full parent denominator, including the questions that stopped early. Questions stopped by workflow logic are different from incomplete evaluations that the search algorithm interrupted; the latter need explicit missing-data handling.

The clean first implementation samples fresh questions uniformly for each matched comparison and records a zero difference when the differing slot is never reached. A later two-phase implementation may sample a representative pool of prefixes and randomly select reached checkpoints for suffix evaluation. It must preserve the parent denominator and known selection probabilities; selecting only apparently promising failures is biased. Arbitrary adaptive item selection is outside the first implementation.

## 6. Proposed algorithm, small enough to test

1. Fix the configuration set, randomized question stream, deployment objective, and dollar checkpoints. Reserve a pilot and a final audit split before exploring results.
2. Use a small, charged initialization with stage/model coverage. Group configurations by exact shared prefixes. Store every physical invocation in an append-only ledger.
3. Maintain configuration-level quality/cost estimates and direct matched differences between relevant candidate pairs. Record reach counts from their parent samples. A paired difference is preferable to subtracting means measured on unrelated question sets.
4. Keep a mix of globally sampled configurations and comparisons between a promising incumbent and relevant neighbors. Pure local search can miss interactions and disconnected high-performing regions.
5. For the next comparison, estimate decision-relevant uncertainty reduction divided by *expected newly incurred dollars*. Use reach rates and observed prefix/suffix costs; the next complete workflow's price is generally unknown. This acquisition rule is a proposed heuristic until analyzed. Include a minimum global-exploration fraction fixed using development data.
6. Execute a fresh matched question, sharing only valid common state. Update all affected statistics with their dependence preserved. Cache hits are zero new paid calls but are not fresh independent evidence.
7. Initially prioritize or suspend candidates rather than permanently eliminate them. For formal elimination, derive simultaneous, time-uniform confidence bounds for the actual adaptive design and bounded quantity. Ordinary fixed-sample intervals inspected repeatedly do not provide a valid guarantee. Uncalibrated regression uncertainty is not a certificate.
8. At each registered budget checkpoint, freeze one recommendation under the same rule used by baselines. If no configuration is supported as feasible, report that outcome. Evaluate frozen recommendations on the independent audit set.

The first rigorous target could be confidence-controlled comparison of two configurations with a shared prefix, including variable measurement cost. A guarantee for an entire adaptive trie search is a separate, harder target. GittinsEval's independent-arm theorem cannot be reused merely by replacing its costs with cached costs.

## 7. How to evaluate without building the full response matrix

We do not need the true best configuration to establish that one search method gives better recommendations than another under the same budget.

**Large-space protocol:** give each search method the same deployment problem, candidate set, dollar budget, allowed cache, initialization policy, and access to question labels. Search on development questions only. At fixed budget checkpoints, freeze recommendations and audit them on the same held-out questions, with fresh deployment runs or valid auditable trace replay. Compare paired quality differences, deployment cost and latency, and feasibility rates. Report uncertainty and search-seed variability separately from question-sampling variability.

Audit data must never return to search, prior fitting, stopping, or method tuning. Restrict the number of checkpoint recommendations per method in advance so one method cannot win by submitting many candidates and choosing afterward. Deduplicate identical audit configurations fairly. If many checkpoints share one audit set, account for multiple comparisons or name one endpoint as primary. Fix the audit size or a valid sequential audit rule before observing its outcomes.

Without an exhaustive reference, do **not** report true simple regret, global optimality, or recall of the true Pareto frontier. A pooled best observed configuration is only an observed comparator and is subject to selection bias; any post-hoc winner needs another untouched evaluation set. Report absolute held-out performance and differences between prespecified methods instead.

**Small-space protocol:** exhaustively construct a reference for a deliberately small configuration/question set. Algorithms see only observations they pay to reveal; the reference is hidden from search. Then report finite-benchmark simple regret, identification probability, and known-reference frontier coverage. Building this reference costs money and must be disclosed separately. A full finite benchmark still does not reveal the population optimum.

Replaying a frozen matrix is useful for many independent search seeds, but it tests allocation on that matrix, not fresh model variability. If reference data were collected with physical prefix sharing, make the same state and marginal-cost model available to all replayed methods. No method may receive unqueried matrix entries through a predictor, cached feature, or price estimate.

## 8. Three cost ledgers and a deployment break-even calculation

| Ledger | Includes | Purpose |
| --- | --- | --- |
| Search | Charged initialization, pilot/prior calibration used by that run, failed requests that are billed, checker/tool calls, newly executed prefixes/suffixes, repeated samples, and tuning under the declared protocol | Horizontal axis for search-method comparison |
| Audit/reference | Held-out evaluation, exhaustive reference construction, and replication used only for reporting | The real expense of producing evidence; never hidden as free search data |
| Deployment | Fresh per-request execution of the chosen configuration, including unsuccessful attempts and ordinary production cache assumptions | Value of the recommendation after search |

Also report optimizer CPU time, storage, and total wall-clock time. Do not invent a dollar conversion for local compute; either state the actual charge or report resources separately. Price tables and billing policies must be versioned. Input length can be known ahead of a call, while output length, retries, failures, and cache billing generally cannot; distinguish expected prices from realized spend.

Initialize each trial cold unless warm-start knowledge is a named experiment. Shared precomputed data are either supplied equally and declared external prior information, or their acquisition is charged. Physical cached outputs may be reused across research trials for economy, but each trial must be charged its counterfactual isolated cost unless shared history is part of the task.

Because cost is uncertain, reserve a maximum payable amount before launching an action, based on token caps and bounded tool/attempt counts. If it cannot fit, stop or choose a smaller admissible action. A cap based only on average predicted cost can overrun the budget. Log unspent money and any overrun; compare against realized spending rather than quietly granting extra budget.

For comparable deployment quality, if search method A spends `B_A` and recommends mean deployment cost `c_A`, versus B with `B_B, c_B`, then the difference after `N` deployment requests is:

```text
total_A - total_B = (B_A - B_B) + N * (c_A - c_B)
```

When A costs more to search but saves money per deployment, its break-even volume is `(B_A-B_B)/(c_B-c_A)`. This is meaningful only when quality and latency constraints are met; cheaper incorrect answers are not equivalent savings. Audit expense is included in an additional all-in project-cost report.

## 9. Baselines and ablations

Every baseline receives the same feasible configurations, question split, checks, cap policy, and cache privileges. Document changes needed to adapt published algorithms; an adaptation is not an exact reproduction.

| Method | What it answers |
| --- | --- |
| Random configuration search, fixed prespecified question batch per sampled configuration | Does adaptive search beat a practical, strong random search procedure? Charge each actual run and use the same recommendation rule. |
| Uniform sampling of configuration/question pairs | Does adaptive allocation beat spending measurements without preference? |
| Uniform-dollar allocation across configurations | Does improvement survive comparison with a cost-aware equal-allocation baseline? Equal counts and equal dollars are different. |
| Cost-accounted successive halving / AgentOpt arm elimination | Does the method improve on screening poor configurations early? |
| GittinsEval | Does execution-aware structure add value beyond cost-aware independent-arm allocation? Include its frozen-matrix setting and clearly marked workflow adaptation. |
| SySRs-style matched comparisons | Is there a gain beyond variance reduction from asking models the same questions? |
| AgentOpt one-coordinate hill climbing and structure-aware BO or matrix estimation | Is the gain more than a familiar configuration-search method? Use equal partial-evaluation access where supported. |
| VineLM-inspired cascade profiling with a fixed target policy class | Does adaptive measurement allocation improve on existing sparse profiling? Separate profiling from advantages of runtime replanning. |
| Exhaustive evaluation, small spaces only | Provides a hidden finite-benchmark reference and a cost ceiling, not the only serious baseline. |

Core ablations: identical algorithm with (i) exact reuse disabled, (ii) paired questions replaced by independent questions, (iii) reach-aware allocation removed, (iv) price awareness removed, and (v) optional statistical transfer removed. The main algorithm comparison should leave exact reuse **enabled for all methods**; otherwise an execution-engine benefit is incorrectly credited to the search rule. A deliberately uncorrected survivor-only estimator can demonstrate a failure mode in synthetic diagnostics, not serve as the principal competitor.

## 10. Pilot, failure criteria, and milestones

**Milestone 1 — Agree on semantics and reproduce a small reference.** Choose one workflow with a deployable checker; two models and one retry give four single-stage assignments. Keep prompts and checker fixed. Record model snapshots, call caps, dataset split hashes, and prices. A fully enumerated small trace set should verify stopping rules, cache equivalence, failure accounting, and the reach identity. First use synthetic traces to find accounting errors; label them synthetic.

**Milestone 2 — Measure whether useful structure exists.** On a budgeted pilot, compare one-slot neighbors with randomly selected pairs, stratified by change position and reach rate. Estimate paired-difference variance and realized shared-prefix savings. Measure checker mistakes, stochastic repeatability, early-stage interaction effects, and the discrepancy between predicted and actual costs. Use pilot data for design decisions, not final performance claims.

**Milestone 3 — Test the smallest algorithm.** Implement matched-question allocation with exact prefix reuse and independent configuration estimates, then compare random search, equal allocation, elimination, and paired-comparison search. Add the reach-aware acquisition rule as one isolated change. Use multiple prespecified search seeds and the small hidden exhaustive reference.

**Milestone 4 — Stress the failure cases.** Vary models, stages, retry limits, reach probabilities, price ratios, and output-cost variability. Include synthetic cases with strong early-stage interactions and wrong similarity assumptions. Rare suffixes can reduce both their importance and the data available to estimate them. Check whether deep, low-reach changes are wrongly discarded when they improve feasibility or matter on a high-value task subgroup.

**Milestone 5 — Held-out real evaluation and paper decision.** Freeze protocol and code before final audits on larger spaces. Include at least one additional workflow if the claim is meant to generalize beyond the first task. Report negative results and uncertainty. Release reproducible splits, trace schema, price snapshots, and permitted artifacts; dataset and provider terms determine what raw outputs can be shared.

Stop or narrow the hypothesis if matched comparisons do not reduce uncertainty per dollar, prefix savings disappear under equal cache access, reach-aware allocation does not beat paired search, or gains require oracle checkers/test leakage. If exact reuse helps but the search rule does not, report an execution-accounting finding rather than invent an algorithmic contribution. If Hamming similarity fails but prefix-conditioned structure works, use the latter and discard unsupported transfer.

The next team decision is the smallest deployment-realistic workflow and an approved experiment budget. The actionable work before paid experiments is to specify its states, checker, labels, trace fields, and four-configuration reference protocol, then reproduce the strongest applicable published baseline.
