# Research assessment: buying useful evidence about retry configurations

Prepared 2026-09-23. **Status: source review, checked mathematical analysis, and proposed experiments. No empirical advantage or novelty has been established.**

The central judgment is that this is configuration search, as Junzhe proposed. The scientifically interesting complication is that testing one configuration can partly evaluate many others, and the next useful measurement need not be a complete configuration run. A strong project would establish when this structure reduces the money needed to make a reliable deployment decision.

The strongest candidate direction is **adaptive evaluation of shared prefixes and continuations, with valid bounds on unfinished configurations and fair accounting of every paid execution**. This is narrower than “similar configurations help.” It remains a research hypothesis: the allocation rule, practical efficiency, and separation from existing work must be established.

## Reading this assessment

| Note | What it establishes |
| --- | --- |
| [01: GittinsEval audit](01-gittinseval-audit.md) | Mentor paper assumptions, finite-benchmark posterior, exact cost proxies, theorem limits, pinned implementation questions |
| [02: Workflow prior art](02-workflow-prior-art.md) | AgentOpt, VineLM, SySRs, and partial FlowCompile review; existing overlap, execution semantics, counterexamples |
| [03: Formulation and inference](03-formulation-and-inference.md) | Definitions, derivations, adaptive partial-observation bounds, feasibility and regret certificates, limitations |
| [04: Related theory](04-related-theory.md) | Structured/resource-constrained/linked/multi-fidelity bandits and algorithm configuration |
| [05: Diagnostics and pilot](05-diagnostics-and-pilot.md) | Reproducible invented examples, minimal experimental design, fair baselines, decision gates |

GittinsEval, AgentOpt, and VineLM were read through their appendices. Selected SySRs theory/proofs and three public repositories were inspected. Reading depth for other papers is stated individually; downloaded does not mean fully reviewed. Public repository snapshots are pinned, but not assumed to be the revisions that generated published figures. The mathematics in note 03 and the exact diagnostic arithmetic received a separate assistant review. That is a useful check, not external peer review.

## 1. Your interpretation is right, with three important distinctions

For a fixed workflow and fixed retry rules, a configuration is the complete set of model choices at every possible invocation. This is analogous to a hyperparameter setting. One question gives one observation of its performance. The question is an experimental unit; it is not another recommendation arm.

An abstract model–question matrix remains useful. With stochastic generation, a cell has a distribution or a recorded replicate, not an intrinsically fixed value. Temperature zero alone does not establish determinism. Reusing a recorded result is legitimate in a frozen replay experiment, but is not an independent new sample.

The project is primarily **best-configuration identification**, a bandit problem concerned with the quality of the final recommendation. It is not primarily cumulative-reward maximization during search. Nor does a fixed workflow require learning an internal reinforcement-learning policy. Learning a state-dependent routing policy would substantially enlarge the scope.

The first distinction is between **what we recommend** and **what we measure**. We recommend a complete configuration. We may purchase a prefix, two continuations from the same checkpoint, or a new question. Several configurations may learn from that purchase. Structured experimental design already makes this distinction; we must specialize it carefully to execution dependencies.

The second is between **finite benchmark quality** and **future-task quality**. Knowing every cell of one benchmark determines its empirical row means. It does not remove uncertainty about future tasks, provider variability, or a changed deployment distribution.

The third is between **price rates** and **the cost of an execution**. An API tariff can be known while output length, number of reached retries, tool use, and failures remain unknown. Existing observations also change the incremental price of our next measurement. Treating each configuration as having one known fixed pull cost loses these features.

## 2. What the mentor's paper actually contributes

[GittinsEval](https://arxiv.org/abs/2609.25645v1) treats configurations as arms and reveals uniformly selected missing questions within a chosen row. Different question outcomes contribute to row uncertainty; it does not explicitly target questions using a learned difficulty model. The working observation model is Gaussian, and the target used for its decisions is the finite benchmark row mean.

Its contribution is more specific than recognizing unequal prices: a Bayesian Gittins-based allocation/stopping framework and an extension that can recommend incompletely evaluated configurations. The optimality result for required completion does not automatically establish optimality of the optional-completion heuristic or our shared-execution setting.

The checked experiments charge a fixed per-row proxy derived from token prices and assumed output/input ratios. For example, GSM8K uses input rate plus twice output rate; AlpacaEval uses a factor of eight. Question-specific token lengths and actual provider invoices are not represented. These numbers support relative proxy-cost comparisons, not a claim that every question's real dollar charge is known.

The [audit](01-gittinseval-audit.md) ties these statements to the paper and pinned code. It also records reproduction questions about batch defaults, the recommendation penalty, a reference-model row, and budget overshoot. These are differences between inspected descriptions/artifacts; they do not establish which code produced a paper result or that a reported result is wrong.

For us, reproducing a small result is useful, but extending its theorem by substituting checkpoint costs into an index is unjustified: observations can now affect several candidates and the action cost depends on history.

## 3. What is already known

| Tempting contribution claim | Existing overlap | What remains to establish |
| --- | --- | --- |
| Search model combinations; change one model at a time | [AgentOpt](https://arxiv.org/abs/2604.06296v2) includes combination search, one-role neighbors, statistical surrogates and request caching | Whether execution structure improves the next measurement decision |
| Share prefixes and account for conditional retries | [VineLM](https://arxiv.org/abs/2605.23914v1) already does checkpointed sparse cascade profiling | Allocation driven by valid uncertainty, compared against its profiling method |
| Exploit similar outcomes through matched questions | [SySRs](https://arxiv.org/abs/2606.07726v1) already exploits paired outcome correlation | Additional value beyond synchronized paired elimination with the same cache |
| Compose workflow estimates from component profiles | [FlowCompile](https://arxiv.org/html/2605.13647v1) already profiles/composes components, including bounded retries | Which additional true execution to buy when composition is uncertain |
| Handle unequal or random evaluation costs | [Resource-constrained best-arm identification](https://proceedings.mlr.press/v238/li24c.html) already studies such costs | Shared, state-dependent observations and their decision value |
| Stop expensive bad configurations early | [LeapsAndBounds](https://proceedings.mlr.press/v80/weisz18a.html) and [Procrastinating with Confidence](https://arxiv.org/abs/1902.05454v3) already study costly algorithm configuration | Partial workflow outcomes with a justified relation to final utility |

This overlap is substantial. A publishable result cannot rest on a new name for caching, a similarity graph, or ordinary successive elimination. The direct empirical challenge is whether our allocation beats a strong paired method running on the same execution engine. The theoretical challenge is whether we can characterize useful execution structure without assuming a globally smooth accuracy landscape.

## 4. Replace “nearby configurations” with a precise structural relationship

There are three different relationships:

1. **Assignment similarity:** only one model choice differs.
2. **Execution overlap:** the same state and computation are shared until a known divergence.
3. **Outcome correlation:** the two configurations tend to succeed on the same questions.

The first guarantees neither of the other two. Changing the first planner can change every later prompt and turn perfect accuracy into zero. Changing many never-reached retry slots changes nothing. Outcome correlation can exist without a reusable prefix; prefix reuse can exist without much correlation among reached suffix outcomes.

The second gives an exact fact. Consider two configurations identical until the retry where they differ. Let R indicate that the deployable checker actually reaches that retry, p be its probability, and d the difference in final quality conditional on reaching it. For scores in [0,1],

~~~text
overall quality difference = p × conditional quality difference
absolute overall quality difference ≤ p.
~~~

Thus, if at most 2% of tasks reach the changed slot, the quality difference cannot exceed two percentage points. In practice p is estimated, so elimination must use a valid upper confidence bound, not the observed frequency alone.

This remains true if the checker accepts wrong answers: early termination makes the two results equal, not necessarily correct. It fails if the supposedly shared configurations use different earlier stopping rules, overwrite the stopped answer, or do not actually share the same execution distribution.

Pairing also gives Var(Y_a−Y_b) = p Var(d | reached) + p(1−p) E[d | reached]². This can be small. A confidence procedure must actually exploit that variance before we claim a statistical efficiency gain; ordinary range-based Hoeffding bounds do not.

There is a cost caveat. A rarely reached suffix can still be very expensive. A 1% branch with an extra cost of 1,000 units contributes 10 expected units. Quality reach bounds alone do not imply cost or latency equivalence.

## 5. A stronger opportunity: bound a whole family before finishing it

Suppose many configurations have the same prefix and differ only afterward. On each question:

- If the prefix terminates, every compatible configuration has the same final score.
- If continuation is needed, every unfinished final score remains somewhere in [0,1].

This gives simultaneous lower and upper bounds for the whole family without predicting unseen answers.

An exact invented example makes the distinction clear. On 100 questions, a shared prefix terminates on 90, but only 80 stopped answers are correct. Ten need continuation. Every completion has finite-benchmark accuracy between 80% and 90%. If a known feasible competitor scores 93%, all these completions can be ruled out without buying their suffixes. We do not fill the 90 stopped cells as successes.

For sampled future tasks, add sampling uncertainty. For adaptively selected continuations, **do not average only the completed cells**. Note 03 provides a conservative valid alternative: keep every registered question in the denominator, retain unknown cells as intervals, and apply simultaneous concentration to the conceptual complete rows. Adaptively revealing cells then narrows an already valid interval; it does not pretend that selected completions are a representative sample.

This construction permits rigorous conservative screening, but does not guarantee useful speed. More prefixes reduce uncertainty about the prefix distribution; they do not remove the genuine width contributed by unfinished suffixes. If that width is large or competitors are close, continuations must be evaluated. The basic bounds may also be too conservative at practical sample sizes.

## 6. The smallest coherent method to investigate

Use a finite registered candidate set and a fixed deployable checker. Start by maximizing expected final quality under one expected deployment-cost cap. Report latency; add a hard latency requirement only after its measurement semantics are reliable. Preserve a general formulation in the theory note without making the first experiment solve every objective.

Maintain two records: a ledger of physical search calls and a record of each configuration's cold deployment behavior. Preserve question ID, full state, model/prompt/checker versions, replicate identity, acceptance, final correctness, token charges, and incomplete executions.

Then repeatedly:

1. Update valid intervals for configurations and compatible families.
2. Retain a clearly feasible incumbent when one exists.
3. Remove a family only if its best possible quality cannot improve the incumbent beyond the chosen tolerance, or its minimum possible cost already violates the cap.
4. Choose between a fresh shared prefix, finishing a reached checkpoint, and a globally informative comparison.
5. Reserve enough budget for the maximum permitted action charge; reconcile actual charges afterward.

The open design question is step 4: expected reduction in decision uncertainty per incremental dollar is an objective for an allocation heuristic, not a solved formula. Its forecasts may guide measurement, while conservative bounds govern elimination. Begin with a transparent fixed heuristic and a registered global-exploration schedule. Develop more elaborate surrogates only if the pilot shows that the simpler method leaves useful savings unrealized.

Do not try to add a novel Gaussian process, graph neural network, state-dependent runtime policy, new bandit theorem, and whole-frontier optimization simultaneously. The first substantive contribution should have one source of improvement that survives an ablation.

## 7. How to evaluate without a brute-force response matrix

The main performance curve is **held-out quality of the selected configuration versus money spent finding it**, together with deployment cost, latency and constraint violations.

At each registered budget, freeze each method's recommendation. Evaluate those recommendations on the same independent held-out questions, with paired uncertainty estimates. Keep audit data hidden until all recommendations relevant to that comparison are frozen. A complete matrix is unnecessary for comparing the actual decisions made by competing search methods.

Separate these expenses:

- Search: every purchased prefix, failed attempt, continuation, search-time checker/judge, and method-specific initialization.
- Independent audit: the cost of measuring frozen recommendations.
- Reference construction and development: exhaustive small spaces, shared datasets, tuning and implementation experiments.
- Deployment: the charge and latency for a new request using the selected configuration.

Report both actual total project spending and each method's isolated search bill. If one physical replay store serves several methods, each starts with the declared initial knowledge; later methods do not inherit free answers or free cache state from earlier ones.

Without an exhaustive reference, exact global regret is unknown. Two honest alternatives remain:

1. Report a statistically supported comparison against specified baselines.
2. When simultaneous bounds cover the entire registered candidate set and the recommendation is certified feasible, report a **conservative upper bound** on its shortfall from the best feasible candidate:

~~~text
max(0, largest quality upper bound among possibly feasible candidates
       − recommendation's quality lower bound).
~~~

This certificate may be wide. It is not measured exact regret, and excluding unexplored configurations invalidates a global claim. Small exhaustive spaces remain useful for evaluating regret, coverage and false elimination directly.

Give every main baseline the same legal checkpointing and result reuse. Provider prompt caching is a separate billing feature; it is not the same as reusing a completed experiment. Use a cache-on/cache-off study to measure execution savings, and compare allocation methods with cache-on to measure search intelligence.

Random search must specify both candidate sampling and how many questions each candidate receives. Include synchronized paired elimination, a cost-aware independent-arm method, and the relevant workflow profiler. Otherwise a win may simply reflect beating an avoidably weak implementation.

## 8. What would falsify the idea

The idea becomes weak if shared prefixes are cheap, most tasks reach the divergence, continuation interactions destroy useful predictions, or simple paired elimination matches our results after receiving the same cache. It also weakens if valid bounds remain too wide to eliminate anything at affordable budgets, or if bookkeeping/computation exceeds the saved execution expense.

Rare retries have a subtle tradeoff: their maximum effect is small, but resolving a tiny nonzero effect can require many parent tasks. The target should be an explicit practically meaningful tolerance, not exact ranking at arbitrary precision. Likewise, certifying configurations exactly on cost boundaries may be impossible within a fixed budget.

Report failures on adversarial cases rather than tune them away. A useful systems result needs measured wall time and overhead; a useful algorithm result needs equal-dollar comparisons and valid uncertainty. A positive synthetic result alone establishes neither.

## 9. Concrete next work and mentor questions

The [pilot protocol](05-diagnostics-and-pilot.md) starts with four configurations for semantics and eight for a minimal two-stage comparison, then scales only after an observed structural signal. Before paid execution the group must choose the benchmark/checker, model snapshots, deployment cap/tolerance and spending limit.

The questions worth taking back to the mentor are specific:

1. Is the main target the finite benchmark winner or expected performance on future questions?
2. Is success defined by the final emitted answer, or by any correct intermediate answer? Which stopping signal exists at deployment?
3. Should the primary outcome be best quality under a deployment cap, a fixed utility, or a frontier? What difference is practically negligible?
4. For GittinsEval reproduction, which commit/configuration generated the reported batch and recommendation behavior, and which rows belong in AlpacaEval?
5. Can the group obtain VineLM's profiling code/traces and confirm its checker and conditional-sampling semantics?
6. Is the intended contribution reliable adaptive profiling, a new theoretical complexity result, or an empirical systems improvement? These require different evidence.

No messages have been sent to the mentor or teammates. These are prepared discussion points, not external requests.

The current recommendation is to pursue the partial-execution allocation hypothesis through the small falsifiable pilot. If it does not beat cached paired evaluation, revise the claim before building a larger system. If it does, the next theoretical target is an instance-dependent description of when a purchased prefix or continuation resolves many plausible candidates cheaply—not an assumption that all one-edit neighbors are similar.
