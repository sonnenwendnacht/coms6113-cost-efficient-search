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

## 2026-09-29 research extensions

The later notes are a dated research record, not a claim that the current
prototype is novel or statistically certified:

| Note | What it establishes |
| --- | --- |
| [08: Similarity theory](08-similarity-theory-2026-09-29.md) | Validity limits of paired row racing and a conservative block design |
| [09: HPO alternatives](09-hpo-alternatives-2026-09-29.md) | Robust structured BO/pure exploration alternatives and prior-art boundaries |
| [10: Similarity-gated exploration](10-similarity-gated-row-exploration-2026-09-29.md) | A temporary heuristic design and its counterexamples |
| [11: Research synthesis](11-research-synthesis-2026-09-29.md) | Candidate contribution, falsification plan, and novelty limits |
| [12: GittinsEval audit](12-mentor-gittinseval-audit-2026-09-29.md) | Exact differences between the mentor paper's arm model and complete retry rows |
| [13: Correlated-resource BAI theory](13-correlated-resource-bai-theory-2026-09-29.md) | A conditional theory target combining paired observations and realized charges |
| [14: Constrained-BAI audit](14-constrained-bai-audit-2026-09-29.md) | Why outcome-dependent cost alone is already covered by prior work |
| [15: Inference corrections](15-inference-corrections-2026-09-29.md) | Corrections for cost intervals, optional stopping, finite-population streams, and search reward semantics |
| [16: Structured correlated KG](16-structured-knowledge-gradient-2026-09-29.md) | One coherent model-based Algorithm 2 candidate using complete-row observations only |
| [17: Correlated BAI and stopping](17-correlated-bai-and-stopping-2026-09-29.md) | Same-question covariance, pseudo-reward limits, and time-uniform stopping requirements |
| [18: Cost-aware KG boundary](18-cost-aware-kg-boundary-2026-09-29.md) | Existing cost-aware KG/Pandora, hierarchical KG, proxy correction, and the narrower novelty boundary |
| [19: Generative proxy boundary](19-generative-proxy-boundary-2026-09-29.md) | Why a learned row proxy needs paired calibration and residual correction |
| [20: Transfer-BAI structural boundary](20-transfer-bai-structural-boundary-2026-09-29.md) | Why the 217-feature map is a working prior unless its transfer relation is certified |
| [21: Spectral BAI prior art](21-spectral-bai-prior-art-2026-09-29.md) | Why a similarity graph and Track-and-Stop allocation are established baselines |
| [22: Common-random-number ranking](22-common-random-number-ranking-2026-09-29.md) | Why same-question pairing is a CRN ranking-and-selection baseline |
| [23: Contextual BAI boundary](23-contextual-bai-boundary-2026-09-29.md) | Why question difficulty makes the target either finite-population or contextual BAI |
| [24: Finite-population confidence sequences](24-finite-population-confidence-sequences-2026-09-29.md) | Validity for registered MathQA permutations, paired streams, and adaptive opening |
| [25: Offline-evidence bias boundary](25-offline-bias-boundary-2026-09-29.md) | Why prior traces and similarity models need a shift/bias assumption |
| [26: Cost-performance BAI prior art](26-cost-performance-bai-prior-art-2026-09-29.md) | Why accuracy-versus-search-cost is already a formal BAI objective |
| [27: Cost-aware paired racing design](27-cost-aware-paired-racing-design-2026-09-29.md) | A transparent candidate combining paired CSs, finite MathQA streams, and realized charges |
| [28: Hub-anchor paired racing](28-hub-anchor-paired-racing-2026-09-29.md) | Reusing already-paid cheap row cells for many paired comparisons |
| [29: Retry cost semantics](29-retry-cost-semantics-audit-2026-09-29.md) | Verified distinction between known price coefficients and path-dependent cell charges |
| [30: Hub-anchor break-even](30-hub-anchor-break-even-2026-09-29.md) | Cost-saving condition and confirmation requirements for a shared complete-row anchor |
| [31: Hub-anchored Algorithm 2 protocol](31-hub-anchored-algorithm2-protocol-2026-09-29.md) | A complete-row, no-prefix protocol with reservations, fallback, and falsification gates |
| [32: Hard-cap reservation](32-hard-cap-reservation-2026-09-29.md) | How bounded retries and tokenizers produce a defensible action charge bound |
| [33: Replay protocol audit](33-replay-protocol-audit-2026-09-29.md) | Why the current full trace is a leak-free offline benchmark but not yet a live hub ledger or strict equal-dollar comparison |
| [34: Ledger-backed hub specification](34-ledger-backed-hub-spec-2026-09-29.md) | Concrete oracle, manifest, reservation, confirmation, and reporting contract for Algorithm 2 |
| [35: Hub amortization baseline](35-hub-amortization-baseline-2026-09-29.md) | Why reuse must be compared with a cached-incumbent baseline and how to state the break-even condition |
| [36: September 2026 prior-art audit](36-september-2026-prior-art-audit-2026-09-29.md) | New cost-aware LLM configuration, dueling, and budgeted verification papers that narrow the claim boundary |
| [37: Contextual dueling boundary](37-contextual-dueling-boundary-2026-09-29.md) | Why treating questions as contexts and row comparisons as duels is established, with a narrower retry-ledger gap |
| [38: Structured feedback-graph boundary](38-structured-feedback-graph-boundary-2026-09-29.md) | Why structured BAI and feedback graphs are prior art, while a hub supplies a paired covariate rather than free candidate feedback |
| [39: Generation-verification prior art](39-generation-verification-prior-art-2026-09-29.md) | Why adaptive generate-rank-verify is established for one prompt, leaving only the outer complete-row identification boundary |
| [40: Hidden-verifier retry boundary](40-hidden-verifier-retry-boundary-2026-09-29.md) | Why answer-key-blind retry traces and resample/reroute support gates are established, requiring fail-closed row-level identification |
| [41: Complete-row arm formalization](41-complete-row-arm-formalization-2026-09-29.md) | A precise `(Q,K,R)` trajectory model, row-level target, paired hub observation, and conditional theorem/failure conditions |
| [42: Baseline and claim matrix](42-baseline-and-claim-matrix-2026-09-29.md) | A fair comparison matrix separating outer row selection, cached incumbents, verifier-only allocation, and per-question retry control |
| [43: Direct workflow-search overlap](43-direct-workflow-search-overlap-2026-09-29.md) | Workflow portfolios and Agent-UCT are close outer baselines; the remaining candidate is no-prefix, path-cost, paired complete-row profiling under matched spend |
| [44: Per-question budget allocation boundary](44-per-question-budget-allocation-boundary-2026-09-29.md) | Adaptive test-time compute allocates a budget per incoming question; the project’s global-row target must remain separate |
| [45: LLMSelector monotonicity boundary](45-llmselector-monotonicity-boundary-2026-09-29.md) | Static module-assignment search is prior art; verifier-gated retries invalidate its monotonicity and answer-key assumptions |
| [46: Agentic routing and serving overlap](46-agentic-routing-and-serving-overlap-2026-09-29.md) | Sequential budget-aware routing, model/verifier serving, and self-healing retries are established; the remaining scope is outer complete-row profiling |
| [47: Similarity and workflow-MCTS boundary](47-similarity-and-workflow-mcts-boundary-2026-09-29.md) | Profile similarity, contrastive routing, and MCTS workflow search are prior art; only partial-observation paired residual transfer remains candidate scope |
| [48: Partial-feedback and cost-aware BAI overlap](48-partial-feedback-and-cost-aware-bai-overlap-2026-09-29.md) | Contextual routing, cost-aware BAI, hybrid/dueling feedback, graph side-observations, and clustered BAI narrow the claim boundary |
| [49: Stateful workflow selection overlap](49-stateful-workflow-selection-overlap-2026-09-29.md) | Online budget planners, serving schedulers, hierarchical autotuning, and experience-driven routing are adjacent but target deployment policy rather than sparse complete-row identification |
| [50: Compiler and program-routing overlap](50-compiler-and-program-routing-overlap-2026-09-29.md) | FlowCompile and foundation-model programs already cover cheap workflow proxies and path-dependent backend cost; HAPR must stay a ledger-backed complete-row identification claim |
| [51: AgentTTS combinatorial-search overlap](51-agenttts-combinatorial-search-overlap-2026-09-29.md) | Multi-stage model/budget tuple search with verifier feedback is established; distinguish the hidden-label, realized-dollar, paired-row identification protocol |
| [52: Resample-or-reroute boundary](52-resample-reroute-boundary-2026-09-29.md) | Per-question verifier-gated resampling/rerouting is a mandatory close baseline; HAPR remains outer fixed-row identification from sparse paid cells |
| [53: Routing-gap identifiability](53-routing-gap-identifiability-2026-09-29.md) | Single stochastic draws do not identify a response matrix; deterministic decoding is a controlled assumption and repeated draws are required for API experiments |
| [54: Sequential RL routing overlap](54-sequential-rl-routing-overlap-2026-09-29.md) | Multi-round RL model routing with cost and stopping is established; distinguish runtime policy learning from outer sparse complete-row profiling |
| [55: Reach-aware paired estimation](55-reach-aware-paired-estimation-2026-09-29.md) | Formalizes complete execution ledgers, reach-stratified residuals, nonanticipating question blocks, and confidence requirements for path-dependent retries |
| [56: Runtime verifier and switching overlap](56-runtime-verifier-and-switching-overlap-2026-09-29.md) | BATS, ModelSwitch, and discriminative verification cover runtime budget awareness, model complementarity, and verifier-cost tradeoffs |
| [57: Retry-routing and benchmark overlap](57-retry-routing-and-benchmark-overlap-2026-09-29.md) | InflationAgent, RouterEval, LLMRouterBench, ThriftLLM, CAPS, and learned cascades broaden required runtime, matrix, ensemble, and verifier baselines |
| [58: Semantic reliability and cascade overlap](58-semantic-reliability-and-cascade-overlap-2026-09-29.md) | Semantic-nearest-neighbor reliability, PromptWise/C2MAB-V, self-escalation, and CascadeDebate cover similarity, cost-aware allocation, and learned stopping |
| [59: HAPR current protocol](59-hapr-current-protocol-2026-09-29.md) | Consolidates the registered ledger, hub, reach-aware confidence, reservation, allocation, stopping, confirmation, and baseline contract |
| [60: Verifier blind spots and audit](60-verifier-blind-spot-and-independent-audit-2026-09-29.md) | Cheap verifier passes can hide large gold-label error; held-out correctness, false-accept/reject rates, and independent audit are mandatory |
| [61: Claim matrix synthesis](61-claim-matrix-synthesis-2026-09-29.md) | Groups the expanded literature into execution policies, query routers, and outer BAI/HPO; states the narrow intersection claim and prohibited novelty wording |
| [62: HPO and cascade-theory overlap](62-hpo-and-cascade-theory-overlap-2026-09-29.md) | EcoTune and unified routing/cascade theory rule out generic token-aware EI, dynamic fidelity, and per-query optimal cascade as new |
| [63: Hub break-even and no free lunch](63-hub-break-even-and-no-free-lunch-2026-09-29.md) | Derives the covariance and ledger condition for a hub to save profiling cost, and requires a matched cached-incumbent control |
| [64: Mentor-paper v2 boundary](64-mentor-paper-v2-boundary-2026-09-29.md) | Audits the updated GittinsEval assumptions; direct transfer is invalid under verifier-censored path cost and cross-row same-question dependence |
| [65: Structural BAI theorem target](65-structural-bai-theorem-target-2026-09-29.md) | States the conditional low-dimensional row-feature model, robust confidence radius, no-free-lunch limit, and falsifiable identity/permutation controls |
| [66: Publication positioning](66-publication-positioning-censored-structural-bri-2026-09-29.md) | Names the narrow contribution as censored structural best-row identification and states the exact combination and fallback |
| [67: Current selector implementation gap](67-current-selector-implementation-gap-2026-09-29.md) | Audits the replay code and separates its heuristic graph predictor from the ledger-backed, reservation, confidence, and confirmation requirements |
| [68: Gold-visibility protocol correction](68-gold-visibility-protocol-correction-2026-09-29.md) | Separates answer-key-blind runtime verification from post-run benchmark scoring available for paid profiling cells and held-out evaluation |
| [69: Explicit row-coordinate reproducibility](69-explicit-row-coordinate-reproducibility-2026-09-29.md) | Finds that default graph selectors infer Hamming coordinates from numeric order; all structured methods need an immutable row-slot mapping |
| [70: Reach-stratified structural estimator](70-reach-stratified-structural-estimator-2026-09-29.md) | Gives a concrete paired linear residual model, reach-stratified covariance update, cost-normalized acquisition rule, and failure fallback |
| [71: Objective and frontier contract](71-objective-and-frontier-contract-2026-09-29.md) | Separates profiling spend, held-out quality, deployment path cost, hard caps, and scalar tradeoffs for fair reporting |
| [72: Procedure-level target and winner's curse](72-procedure-level-target-and-winner-curse-2026-09-29.md) | Separates finite-benchmark winner quality from fresh-task performance of the full budgeted search procedure |
| [73: Verifier proxy and gold-audit boundary](73-verifier-proxy-and-gold-audit-boundary-2026-09-29.md) | Shows why verifier-only best-row identification needs calibration or selectively audited gold outcomes |
| [74: Finite-bank versus future-task estimand](74-finite-bank-versus-future-task-estimand-2026-09-29.md) | Separates fixed-bank MathQA accuracy from future-task procedure quality and warns against unsupported adaptive-sampling error bars |
| [75: Confidence budget for adaptive edges](75-confidence-budget-for-adaptive-edges-2026-09-29.md) | Counts the multiple edge streams in the row graph and separates certified streams from uncertified model-assisted ranking |
| [76: Finite-population reach decomposition](76-finite-pop-reach-decomposition-2026-09-29.md) | Gives the exact reach-times-reached-effect identity, finite-bank corrections, and the no-reach/selection-bias rules |
| [77: No-prefix paired Top-Two control](77-no-prefix-paired-top-two-control-2026-09-29.md) | Defines a strong direct-complete-row baseline and a fail-closed structural sidecar that cannot recommend an unobserved row |
| [78: Outcome-dependent missingness](78-outcome-dependent-missingness-2026-09-29.md) | Connects verifier-gated absent retries to MNAR bandit feedback and rules out zero/imputation shortcuts |
| [79: Counterfactual retry identifiability](79-counterfactual-retry-identifiability-2026-09-29.md) | Separates observable complete-row scores from unidentifiable unexecuted retry outcomes |
| [80: Cost stopping and confidence sequences](80-cost-stopping-and-confidence-sequences-2026-09-29.md) | Explains why dollar-stopped adaptive runs need all-prefix confidence sequences rather than fixed-sample error bars |
| [81: Pairing cost–variance break-even](81-pairing-cost-variance-break-even-2026-09-29.md) | Derives when same-question pairing beats cost-optimal independent allocation and identifies required negative controls |
| [82: Known unit cost versus realized row cost](82-known-unit-cost-versus-realized-row-cost-2026-09-29.md) | Separates public per-attempt coefficients from outcome-linked complete-row charges and deployment cost bounds |
| [83: Complete-row anchor control variate](83-complete-row-anchor-control-variate-2026-09-29.md) | Proposes a no-prefix, complete-row hub estimator with pilot-frozen coefficients, cost break-even, and fail-closed controls |
| [84: Correlated-bandit prior-art boundary](84-correlated-bandit-prior-art-boundary-2026-09-29.md) | Audits correlated-arm and resource-constrained BAI prior art and narrows the defensible retry-row claim |
| [85: CW-CV-TT candidate algorithm](85-cw-cv-top-two-algorithm-2026-09-29.md) | Gives the gated step-by-step Algorithm 2 candidate with direct-racing fallback and final confirmation |
| [86: Covariance-adaptive BAI overlap](86-covariance-adaptive-bai-overlap-2026-09-29.md) | Audits a close covariance-aware BAI theory and clarifies the paid complete-row, stochastic-path-cost difference |
| [87: Anchor selection and cross-fitting](87-anchor-selection-and-cross-fitting-2026-09-29.md) | Specifies pilot selection, cross-fitting, multiplicity, and fail-closed handling for adaptive hubs |
| [88: Claim matrix after covariance audit](88-claim-matrix-after-covariance-audit-2026-09-29.md) | Separates established paired-bandit facts, conditional cost claims, and the empirical burden for a publishable result |
| [90: Generative-proxy control-variate overlap](90-generative-proxy-control-variate-overlap-2026-09-29.md) | Audits PROBE and rules out generic OLS/control-variate residualization as novelty |
| [91: Covariance confidence under adaptive stopping](91-covariance-confidence-under-adaptive-stopping-2026-09-29.md) | Separates iid matrix confidence-sequence theory from sparse, verifier-censored row observations |
| [92: CW-CV-TT theorem target](92-cw-cv-tt-theorem-target-2026-09-29.md) | States the conditional delta-correctness target and the assumptions still missing from a proof |
| [93: LLM surrogate-reward overlap](93-llm-surrogate-reward-overlap-2026-09-29.md) | Audits MLA-UCB's LLM model-selection surrogate and rules out cheap-proxy control variates as new |
| [94: Structured-row bandit overlap](94-structured-row-bandit-overlap-2026-09-29.md) | Audits factored-reward and multi-agent vector-action BAI and narrows configuration-vector novelty |
| [95: Cascade and delayed-feedback overlap](95-cascade-and-delayed-feedback-overlap-2026-09-29.md) | Audits partial-feedback and cascading BAI priors and narrows early-stopping novelty |
| [96: Cost-aware BAI and dueling overlap](96-cost-aware-bai-and-dueling-overlap-2026-09-29.md) | Audits CABAI and cost-aware LLM dueling and requires them as direct baselines |
| [97: Cost resources, multi-fidelity, and similarity boundary](97-cost-resource-and-similarity-boundary-2026-09-29.md) | Audits resource-constrained BAI, multi-fidelity BAI, and TRIPLE prompt similarity; narrows Algorithm 2 to complete retry rows with realized outcome-linked charges |
| [98: Hard-cap and realized-cost protocol](98-hard-cap-and-realized-cost-protocol-2026-09-29.md) | Separates the current overshooting realized-spend replay from a safe hard-cap wrapper with complete-row charge reservations |
| [99: Factorized row-model boundary](99-factorized-row-model-boundary-2026-09-29.md) | Audits linear and factor-graph BAI; treats factorial sharing as a guarded baseline unless complete-row calibration passes |
| [100: Cost-synchronized successive rejects](100-cost-synchronized-successive-rejects-2026-09-29.md) | Derives a complete-row, cost-aware SySRs adaptation and separates established synchronized pairing from the retry-cost hypothesis |
| [101: Confidence contract for Cost-SySR](101-confidence-contract-for-cost-sysr-2026-09-29.md) | Specifies finite-bank, block, admission, and anytime-confidence conditions needed for valid synchronized elimination with random retry charges |
| [102: Measured similarity and edge selection](102-measured-similarity-edge-selection-2026-09-29.md) | Defines residual-variance edge validation, multiplicity control, and the cost/question-selection failure mode |
| [103: Gold visibility and selector target](103-gold-visibility-and-selector-target-2026-09-29.md) | Separates offline post-cell answer-key correctness from verifier-only deployment feedback |
| [104: Gated complete-row racing decision](104-gated-complete-row-racing-decision-2026-09-29.md) | Recommends a cross-fitted gate among Cost-SySR, hub-anchored, and direct cost-aware racing with fail-closed fallbacks |
| [105: Algorithm 2 state machine and prototype gap](105-algorithm2-state-machine-and-prototype-gap-2026-09-29.md) | Separates the heuristic matrix replay from a ledger-backed, gated, confidence-aware complete-row algorithm |
| [106: No-free-lunch for unmeasured rows](106-no-free-lunch-for-unmeasured-rows-2026-09-29.md) | Proves why Hamming similarity and observed covariance cannot certify an unobserved row without a structural bias bound |
| [107: Multiobjective complete-row recommendation](107-multiobjective-complete-row-recommendation-2026-09-29.md) | Separates profiling spend, held-out quality, deployment cost, and Pareto/constraint targets |
| [108: Replay oracle and budget normalization audit](108-replay-oracle-and-budget-normalization-audit-2026-09-29.md) | Distinguishes post-hoc full-matrix replay from an online cell oracle and flags mixed cell-versus-dollar budget curves |
| [109: Realized-dollar curve protocol](109-realized-dollar-curve-protocol-2026-09-29.md) | Defines event ledgers, checkpoint reconstruction, overshoot handling, and parameter-pair reporting at common profiling dollars |
| [110: Explicit slot audit for structured replay](110-explicit-slot-audit-for-structured-replay-2026-09-29.md) | Finds CW-PLR still infers Hamming neighbors from numeric row order and requires an explicit row-slot map before structured claims |
| [111: Explicit slot fix and regression gate](111-explicit-slot-fix-and-regression-gate-2026-09-29.md) | Records the CW-PLR/replay repair, its syntax-only verification, and the remaining equal-dollar and permutation-control gate |
| [112: Graph-similarity prior-art boundary](112-graph-similarity-prior-art-boundary-2026-09-29.md) | Audits graph-feedback, clustered-BAI, and structured-BAI overlap and restricts Algorithm 2 to paid paired evidence with graph-guided challenger ordering |
| [113: Edge-gated complete-row racing](113-edge-gated-complete-row-racing-2026-09-29.md) | Specifies the five-stage Algorithm 2 candidate: cross-fitted edge screen, cost gate, paid paired racing, direct stop, and independent audit |

The 2026-09-29 review window launched no new experiments, tests, replays, or
model/API calls. The active long trace was left untouched.

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
