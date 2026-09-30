# Resumable checkpoint

Updated: 2026-09-29 20:28 ET (research-only window; no experiments launched).

## Research branch

- Algorithm branch: `research/algorithm2-sequential-comparison`.
- Main experiment branch: `research/experiment1-nine-models`.
- The algorithm branch contains CW-PLR, CACR, and the gated SCCR prototype,
  synthetic iid/smooth/permuted controls, the pilot trace-locality diagnostic,
  and the expanded related-work boundary. The latest substantive algorithm note is `7d94ca5`; checkpoint metadata is
  refreshed by `8403897`. Source-audit commits after the earlier implementation
  checkpoint add notes 19--71.
- Run `python -m unittest discover -s tests -q` for the current offline test
  suite (38 tests).

## Research-only window

- Through 2026-09-29 18:40 ET, no new experiments, replays, tests, or model/API
  calls were launched. The existing long trace was left untouched.
- Source-audited notes now cover the validity limits of paired similarity,
  cost/reward dependence, robust structured pure exploration, categorical BO
  prior art, and a concrete falsification plan. The synthesis is in
  `docs/research/deep-review/11-research-synthesis-2026-09-29.md`.
- The mentor-paper audit is in
  `docs/research/deep-review/12-mentor-gittinseval-audit-2026-09-29.md`; it
  records GittinsEval's Gaussian independent-arm assumptions and the exact
  retry-row differences that require a separate baseline or reduction.
- A candidate theory formulation for combining same-question covariance with
  outcome-dependent complete-row charges is in
  `docs/research/deep-review/13-correlated-resource-bai-theory-2026-09-29.md`.
- The constrained-BAI overlap audit is in
  `docs/research/deep-review/14-constrained-bai-audit-2026-09-29.md`; it rules
  out outcome-dependent cost alone as the novelty claim.
- Note 15 corrects cost-feasibility directions, optional-stopping claims, and
  the distinction between checker control and offline `final_correct` search
  reward. Note 16 gives one coherent structured correlated-KG candidate with
  217 categorical features, a residual, top-two pairing, and a cost model.
- Notes 17--32 audit covariance-adaptive stopping, cost-aware KG/Pandora,
  hierarchical and transfer BAI, generative proxies, spectral graph BAI,
  common-random-number ranking, contextual BAI, finite-population confidence
  sequences, offline-evidence bias, paired-racing and hub-anchor designs,
  verified retry-cost semantics, hub break-even/stream accounting, and a
  complete-row hub-anchored Algorithm 2 protocol, and hard-cap reservation
  bounds. They narrow the defensible claim to
  complete retry-row observations with same-question covariance and realized
  path cost; generic similarity, KG-per-cost, paired elimination, and silent
  switching between fixed-set and population targets are prior art or protocol
  errors.
- Note 33 audits the replay contract: the current full trace supports a
  leak-free counterfactual selector benchmark, but not a live shared-hub
  ledger, strict equal-dollar caps, registered question streams, or direct
  final confirmation for surrogate-row selectors.
- Note 34 specifies the next ledger-backed hub oracle: registered question
  streams, explicit initial cache, hard/soft reservation semantics, direct
  confirmation, and separate search versus audit fields.
- Note 35 requires a cached-incumbent baseline before claiming that a shared
  hub saves calls; fresh-comparator reuse is only a diagnostic.
- Note 36 audits three new 2026 papers on cost-aware multi-objective LLM
  configuration search, cost-aware LLM dueling, and budgeted multi-attribute
  verification. They narrow the claim to shared-question, complete-row,
  path-dependent retry charges.
- Note 37 audits contextual-dueling overlap. Contextual or graph structure,
  paired comparisons, and cost-aware allocation are established components;
  any claim must require the complete retry-row arm, answer-key-blind
  solver/verifier coupling, endogenous early stopping, and a matched
  cached-incumbent comparison.
- Note 38 audits structured BAI and feedback-graph overlap. A hub is a
  same-question covariate/control variate, not free side feedback about an
  unpulled candidate; direct candidate observations and final confirmation
  remain required.
- Note 39 audits adaptive generate-rank-verify. Within-question generation
  versus verification allocation is established; the remaining boundary is
  outer identification of one complete retry row with endogenous path charge
  and a shared-row ledger.
- Note 40 audits hidden-verifier retry and resample/reroute work. It adds a
  fail-closed support gate: a row transfer must have direct paired evidence
  on a registered fold and held-out direct confirmation; pointwise oracle
  maxima and full-trace replay do not license a deployable selector.
- Note 41 formalizes one complete row observation as `(Q,K,R)`, explains why
  retry slots are not independently sampleable attributes, and states the
  conditional theorem target plus its failure conditions.
- Note 42 defines the fair baseline and claim matrix: cached-incumbent
  paired racing is the required control, verifier-only and per-question
  generate/verify methods are separate scopes, and exhaustive trace cost is
  not selector money saved.
- Note 43 audits direct workflow-search overlap from workflow portfolios and
  Agent-UCT. Cost-aware workflow search, held-out workflow evaluation, and
  prefix-aware UCT are prior art; the remaining candidate is a conditional
  no-prefix paired complete-row result under matched cached-incumbent spend.
- Note 44 separates per-question adaptive compute allocation from the
  project’s global-row target. A deployment policy that chooses retry budget
  per question is a different action space and must be a labeled extension or
  baseline.
- Note 45 audits LLMSelector. Static module assignment, coordinate updates,
  and monotonicity are prior art; verifier-controlled retry reach and hidden
  correctness invalidate direct transfer of its theorem.
- Notes 46--47 audit budget-aware agentic routing, model/verifier serving,
  self-healing workflows, profile/contrastive similarity, and MCTS workflow
  search. They require the manuscript to say complete-row profiling rather
  than generic agentic routing, and to treat full-matrix similarity as an
  offline oracle rather than partial-observation evidence.
- Note 48 audits contextual partial-feedback routing (PILOT and BaRP),
  cost-aware best-arm identification, hybrid/dueling feedback, graph
  side-observations, and clustered BAI. These are direct baselines or claim
  boundaries for any similarity-plus-budget method.
- Notes 49--51 audit stateful workflow planners, serving schedulers,
  hierarchical autotuning, FlowCompile, foundation-model programs, and
  AgentTTS. Online policy selection, workflow proxies, path-dependent cost,
  and combinatorial search are established; HAPR remains an outer sparse
  complete-row identification protocol.
- Notes 52--54 audit Resample-or-Reroute, routing-gap identifiability, and
  Router-R1. Verifier-gated per-question retries, stochastic matrix
  non-identifiability, and sequential RL routing must be explicit baselines
  or assumptions rather than claimed novelties.
- Note 55 formalizes a reach-aware execution ledger and nonanticipating
  question blocks. It requires finite-population confidence sequences or
  fresh confirmation after adaptive opening, and forbids imputing an
  unexecuted continuation.
- Note 56 audits BATS, ModelSwitch, and discriminative verification. Runtime
  budget awareness, model complementarity, and verifier-cost tradeoffs are
  established execution-side baselines, separate from outer row profiling.
- Note 57 adds InflationAgent, RouterEval, LLMRouterBench, ThriftLLM, CAPS,
  and learned cascades. Retry-aware routing, response-matrix benchmarks,
  model-set selection, and verifier allocation must all be represented in the
  baseline matrix before making a row-search claim.
- Note 58 audits semantic-nearest-neighbor reliability, PromptWise, C2MAB-V,
  Bayesian self-escalation, and CascadeDebate. Similarity, Lagrangian
  quality-cost control, and learned stopping are established; the remaining
  candidate is sparse fixed-row identification with a paid ledger.
- Note 59 consolidates the current HAPR protocol: registered rows and splits,
  paid hub ledger, reach-aware residuals, nonanticipating blocks, conservative
  reservations, simultaneous bounds, direct confirmation, and matched
  cached-incumbent controls.
- Note 60 records verifier blind spots as a validity requirement: report
  answer-key-based held-out correctness and false-accept/reject rates separately
  from verifier PASS rates, and keep the audit independent of search decisions.
- Note 61 synthesizes the claim matrix into execution-policy, query-router,
  and outer-BAI/HPO families. It gives the manuscript a precise intersection
  claim and lists the broad novelty wording to avoid.
- Note 62 audits EcoTune and unified routing/cascade theory. Token-aware
  expected improvement, dynamic fidelity, and per-query optimal cascade are
  required baselines rather than standalone Algorithm 2 novelty.
- Note 63 derives the hub break-even condition. Positive similarity is not
  enough: a shared hub must reduce paired uncertainty per candidate charge and
  be compared against a baseline with the same cached incumbent.
- Note 64 audits the mentor's updated GittinsEval paper (arXiv:2609.25645).
  Independent row arms, fixed per-example costs, and precomputed matrices are
  direct baseline assumptions; HAPR's only defensible extension is the
  verifier-censored, path-cost, cross-row-dependent retry setting.
- Note 65 states the conditional structural-BAI theorem target: a low-
  dimensional row feature model with residual uncertainty, paired covariance,
  and explicit no-free-lunch/permutation controls. SySRs remains a mandatory
  similarity baseline.
- Note 66 positions the method as censored structural best-row identification
  and adds the required verifier-calibration condition for any
  deployment-adaptive variant: runtime PASS/FAIL signals alone cannot support
  an accuracy guarantee.
- Note 67 audits the current replay implementation. The graph selector is a
  heuristic predictor and can recommend an unpulled row; it still lacks
  hard-charge reservations, anytime bounds, reach strata, and direct search-
  time confirmation. It must not be described as certified HAPR yet.
- Note 68 corrects the information boundary: the runtime verifier is
  answer-key blind, but a benchmark selector may receive `final_correct` after
  paying for a complete cell; only held-out cells remain hidden. This aligns
  HAPR with the current replay and GittinsEval, and removes hidden-gold labels
  as a false novelty claim.
- Note 69 finds a reproducibility defect: default graph selectors infer
  Hamming coordinates from numeric arm order. Every structured selector must
  use and record an immutable explicit row-slot mapping.
- Note 70 derives a concrete reach-stratified structural estimator: paired
  complete-row utility residuals, explicit coordinate features, observed reach
  strata, cost-normalized acquisition, and a direct-racing fallback when fit
  or covariance is weak.
- Note 71 separates profiling spend, held-out quality, deployment path cost,
  hard deployment caps, and scalar tradeoffs. It defines the fair frontier and
  prevents search cost from being conflated with cold deployment cost.
- Note 72 audits SIREN's winner's-curse correction. It requires us to label
  finite search-set selection quality separately from the held-out performance
  of the full budgeted search procedure, with actual paid profiling spend on
  the main curve.
- Note 73 audits limited-gold best-arm identification. Verifier passes can
  control retry reach but cannot by themselves identify the best accuracy row;
  calibration or positive-probability gold audits are required for an accuracy
  claim.
- Note 74 audits finite-bank inference. Search-bank winner quality, held-out
  bank quality, and future-task procedure quality are distinct estimands; a
  heterogeneous MathQA allocation needs an explicit finite-population design or
  disjoint audit rather than generic iid error bars.
- Note 75 specifies confidence accounting for adaptively opened similarity
  edges: pre-register a sparse edge family or charge each new independent
  stream, while using the full graph only as a non-certified acquisition model.
- Note 76 gives the exact finite-bank decomposition `Delta = rho * delta` for
  a paired row difference, including the low-reach early-exit rule, finite-
  population corrections, and the requirement to charge uniform rejection
  screening.
- Note 77 specifies CW-PTT, a no-prefix complete-row paired Top-Two control,
  and narrows Algorithm 2 to a certified structural sidecar that prioritizes
  direct comparisons but cannot recommend an unobserved row.
- Note 78 audits missing-outcome bandits. Verifier-gated absent retries are
  outcome-dependent missingness, so reached-only averages and zero imputation
  are invalid without a declared observation model or positive-probability gold
  audits.
- Note 79 states the counterfactual boundary: unexecuted retry correctness is
  not identifiable from deployment logs without a validated continuation model
  or randomized forced continuation, so Algorithm 2 must recommend only after
  direct complete-row confirmation.
- Note 80 audits cost-based stopping. Since realized charge can correlate with
  reach and correctness, dollar-stopped runs need all-prefix confidence
  sequences; a fixed-sample interval is valid only for a pre-registered,
  nonadaptive confirmation block.
- Note 81 derives the pairing cost–variance break-even. Similarity should guide
  paired allocation only when residual covariance beats the cost-optimal
  independent allocation; heterogeneous-cost and low-covariance cases are
  required negative controls.
- Note 82 clarifies that known per-attempt coefficients do not make a complete
  retry-row charge known: verifier reach makes total cost random and correlated
  with quality. Profiling and deployment constraints must use realized charges
  and separate cost confidence bounds.
- Note 83 proposes the strongest current no-prefix candidate: a complete-row
  anchor control variate. A pilot-frozen residual can reduce paired variance,
  but only when its anchor cost and mean uncertainty satisfy an explicit
  break-even condition; otherwise CW-PTT remains the fallback.
- Note 84 audits correlated-bandit and resource-constrained BAI prior art. The
  anchor/control-variate ingredients are established; only their conditional
  combination for complete verifier-gated retry rows remains a defensible
  project-specific hypothesis.
- Note 85 freezes the current Algorithm 2 candidate, CW-CV-TT: pilot-frozen
  complete-row control variates, a conservative break-even gate, direct CW-PTT
  fallback, global confidence accounting, and independent final confirmation.
- Note 86 audits covariance-adaptive BAI. It is a close prior for pairwise
  residual elimination, but assumes joint subset queries; our distinction is
  paid complete rows, endogenous verifier paths, and separate quality/cost
  certification. It must be a baseline, not a novelty claim.
- Note 87 specifies anchor selection. Candidate hubs and control coefficients
  must be chosen on a pilot or cross-fitted fold, with multiplicity charged and
  a direct CW-PTT fallback when no hub passes the conservative gate.
- Note 88 freezes the claim matrix after the covariance audit. Paired residuals
  are established; the possible contribution is only a gated, paid complete-row
  cost adaptation, and any stronger novelty claim depends on equal-dollar
  comparisons, permutation controls, and held-out evidence.
- Note 90 audits PROBE, a direct generative-proxy control-variate BAI prior.
  Generic OLS residualization and variance certification are not novel; the
  remaining boundary requires expensive complete-row anchors, endogenous retry
  costs/missingness, and separate verifier-blind gold evaluation.
- Note 91 audits matrix covariance confidence sequences. Their iid common-
  covariance assumptions do not transfer to sparse verifier-censored rows, so
  CW-CV-TT should certify low-dimensional residual streams rather than rely on
  a plug-in full covariance matrix.
- Note 92 states the conditional CW-CV-TT theorem target. A delta-correct
  charge bound would require complete traces, predictable sampling, pilot-fixed
  coefficients, valid residual confidence sets, and separate cost feasibility;
  the current project has not proved it and remains empirical.
- Note 93 audits MLA-UCB's LLM surrogate-reward model selection. Cheap-proxy
  control variates are already demonstrated, so the only remaining boundary is
  the expensive complete-row, verifier-censored, path-cost setting with hidden
  final correctness.
- Note 94 audits factored-reward and multi-agent vector-action BAI. A vector of
  model choices or intermediate-stage structure is not novel by itself; the
  remaining scope is complete retry-row identification with verifier censoring
  and path-dependent cost.
- Note 95 audits delayed-feedback and cascading BAI. Early verifier stopping
  and partial feedback are established; the remaining boundary must include
  complete-row identification, same-question configuration covariance, and
  realized path-cost accounting.
- Note 96 audits CABAI and cost-aware LLM dueling. Cost-aware proportions and
  fixed-confidence dueling are direct baselines; the possible gap is only their
  extension to complete retry rows with outcome-linked path costs.
- Note 97 audits resource-constrained BAI, multi-fidelity BAI, and TRIPLE prompt
  similarity. A hard cap, cheap fidelity, or generic similarity transfer is not
  novel; the defensible boundary is complete retry rows with realized,
  verifier-gated outcome-linked charges and blind held-out evaluation.
- Note 98 separates the current realized-spend replay from a safe hard-cap
  protocol. A true cap requires a deterministic upper bound on each complete
  row/question charge and a reservation before launch; mean-cost estimates are
  not enough.
- Note 99 audits linear and factor-graph BAI. Shared slot effects can be a
  useful AFGR baseline, but only complete-row cross-fitting and coverage checks
  can justify using it; factorization is not itself novel.
- Note 100 derives Cost-SySR, a direct complete-row adaptation of synchronized
  successive rejects with phase targets based on realized or safely reserved
  retry cost. Synchronized pairing is prior art; the retry-cost extension stays
  conditional pending equal-dollar controls and valid adaptive confidence.
- Note 101 specifies the Cost-SySR confidence contract. The local trace is
  deterministic (`do_sample=False`) and targets a finite search bank; valid
  adaptive elimination additionally needs complete synchronized blocks, no late
  admission, and an anytime or pre-sized simultaneous confidence rule.
- Note 102 defines similarity as measured paired residual variance, not Hamming
  distance. It requires registered edge streams, fixed question permutations or
  cross-fitting, and warns that cost-based question selection changes the
  estimand when charge and correctness are correlated.
- Note 103 separates the selector-visible reward contracts. The verifier is
  answer-key blind, while offline traces reveal `final_correct` only after a
  paid complete cell; verifier-only search can certify only the verifier proxy,
  with gold accuracy reserved for held-out audit.
- Note 104 recommends a cross-fitted, fail-closed portfolio: use a hub only
  when measured covariance and amortization beat direct cost-aware racing;
  otherwise use Cost-SySR or direct paired racing. The mode choice itself must
  be frozen before execution-fold selection.
- Note 105 defines the Algorithm 2 state machine and identifies the current
  CACR/SCCR replay gap: heuristic radii, realized overshoot, and matrix-fixture
  access are debugging behavior, not confidence-certified online selection.
- Note 106 records the no-free-lunch boundary: similarity can reduce variance
  for paid comparisons between observed complete rows, but cannot certify an
  unmeasured row without an explicit smoothness, factor, or proxy-error bound.
- Note 107 fixes the recommendation contract: profiling spend, held-out
  quality, and cold deployment cost are separate. The primary table should use
  best accuracy at fixed search spend, with cost-constrained/Pareto analyses
  registered separately.
- Note 108 audits replay fairness. The fixture validates the full rectangle and
  post-hoc audit split, but structured caps use a full-matrix cost denominator
  while standard selectors use cell fractions; equal-dollar curves require a
  common ledger/oracle wrapper.
- Note 109 defines the realized-dollar curve protocol: ordered complete-cell
  ledgers, fixed cumulative-dollar checkpoints, no credit for a block crossing a
  checkpoint, and separate reporting of overshoot, held-out quality, and cold
  deployment cost.
- Note 110 finds a structured-replay gate: CACR/SCCR receive explicit row
  slots, but CW-PLR still infers neighbors from numeric row order. It must be
  fixed or labeled as a random-graph ablation before any Hamming claim.
- Note 111 applies that repair: CW-PLR accepts explicit row slots, replay
  passes the validated map, and tests cover valid and duplicate maps. Only
  syntax/diff checks were run in the research-only window; unit tests and
  replay remain pending.
- Note 112 audits graph-feedback, clustered-BAI, and structured-BAI prior art.
  Similarity can order paid row comparisons, but a row pull does not reveal a
  neighbor; direct paired evidence, fail-closed gating, and a random-graph
  control remain required.
- Note 113 specifies Edge-Gated Complete-Row Racing (EGCR): cross-fitted
  residual screening, reserved-dollar gating, paid paired challenger races,
  direct-evidence stopping, and an independent audit. It is a conditional
  protocol proposal, not a demonstrated result or novelty claim.
- Note 114 audits SCCR against that contract: its calibration block is reused
  in the race, so its gate is not cross-fitted. SCCR remains a heuristic
  ablation until disjoint pilot/race/confirmation folds and multiplicity-aware
  edge bounds are added.
- Note 115 proposes a permutation-controlled pairing gate: compare paired
  residual variance with independent row variance, shuffle one row's question
  labels as a negative control, and require both a cross-fitted gain bound and
  a reserved-cost advantage. This remains a protocol proposal pending tests.
- Note 116 audits covariance-adaptive BAI. Difference-variance racing is
  established when multiple arms can be queried together; the remaining
  conditional boundary is endpoint-specific realized retry cost, finite-bank
  question pairing, verifier paths, and independent gold audit.
- Note 117 audits Cost Aware Best Arm Identification (CABAI). Cost-normalized
  allocation is an explicit baseline; the experiment must declare whether cell
  prices are deterministic, bounded random, or only realized, and report
  profiling spend, held-out quality, and cold deployment cost separately.
- Note 118 audits the runner's billing path. Model coefficients are known, but
  verifier/retry prompt lengths and retry reach make the complete cell charge
  realized only after execution. The current replay can claim equal realized
  spend with overshoot reporting, not a strict hard dollar cap.
- Note 119 audits budget units. Legacy selectors mix row fractions, cell
  fractions, and parameter-only settings, while structured selectors use
  realized cost fractions. The sweep now records `budget_basis`; equal-dollar
  checkpointing remains required for the main comparison.
- Note 120 audits the primary SySRs paper. Synchronized same-question blocks
  and correlation-aware successive rejects are established; the direct retry
  baseline should be Cost-SySR with realized-dollar accounting. Algorithm 2's
  remaining conditional scope is unequal path-cost allocation, cross-fitted
  gating, and independent complete-row audit.
- Note 121 gives the current Algorithm 2 design: Phase A Cost-SySRs for global
  protection, then Phase B EGCR for a small active set or sharply unequal row
  charges. The switch must be predeclared/cross-fitted, and all claims remain
  conditional on equal-dollar controls.
- Note 122 separates selector-visible verifier passes from evaluator-only
  `final_correct`. Replay now has an explicit `--selector-reward` contract;
  deployment-faithful claims require verifier-visible selection followed by a
  gold held-out audit.
- Note 123 audits SCOPE. Its conformal pairwise-judge guarantee requires
  labeled calibration and exchangeability, and does not transfer directly to a
  verifier whose PASS/RETRY action changes the retry path and charge. Treat it
  as a calibration control, not as outer-search novelty.
- Note 124 states the conditional theorem target for the Cost-SySRs/EGCR
  hybrid: an epsilon-best observed row over a registered finite bank under
  simultaneous confidence, cross-fitted gates, and safe cost reservations. It
  separates this correctness claim from any empirical dollar savings or
  verifier-to-gold transfer claim.
- Note 125 records three counterexamples where reward similarity does not save
  profiling dollars: unequal retry paths, easy/expensive question groups, and
  cost disagreement under identical rewards. EGCR needs separate quality-gain
  and cost-gain gates.
- Note 126 adds an unexecuted `run_cost_sysrs` source prototype and focused
  tests. It is a direct synchronized complete-row baseline with explicit
  realized-cost overshoot diagnostics, not a confidence-certified algorithm.
- Note 127 audits Li and Cheung's resource-constrained best-arm formulation.
  It separates a soft realized-dollar evaluation track from a strict cap that
  would require deterministic per-cell reservations, and records why partial
  retry blocks must not be ranked as complete rows.
- Note 128 proposes graph-gated cost-aware residual racing (GCRR):
  cross-fitted paired residuals on complete rows, gated before propagation,
  with similarity used for allocation/elimination rather than free neighbor
  feedback. It treats graph smoothness, paired BAI, and resource-rationed BAI
  as prior art and keeps the novelty claim conditional.
- Note 129 audits Wu et al.'s CAET (2025), which already covers cost-aware
  pairwise pure exploration. It narrows Algorithm 2's possible contribution
  to context-indexed complete rows with execution-dependent retry costs, and
  requires CAET-style allocation as a future baseline.
- Note 130 records the amortization condition: a paired edge pays both complete
  endpoints, so similarity can save money only when an already-paid anchor is
  reused across candidates or residual variance materially reduces the needed
  cells. The design is now framed as transductive allocation with direct
  fallback, not a free graph estimator.
- Note 131 specifies pre-registered random question blocks for adaptive graph
  edges, so edge opening cannot choose easy or cheap questions after seeing
  outcomes. It also requires exact cell identity for any cache reuse and joint
  covariance handling when paths share a block.
- The latest source-and-research checkpoint is `2120b5a` on the main branch
  and `d4f3464` on the algorithm branch; both are pushed and included in PR
  #4.
- The current Algorithm 2 checkpoint is pushed on
  `research/algorithm2-sequential-comparison` and is included in PR #4.

## Long local trace

- Run ID: `exp1-nine-local-20260927-proper`.
- Status observed at 2026-09-30 00:01 UTC: `243,400 / 291,600` cells
  (`83.47%`), still running in PID `8763`.
- Status file: `results/runs/exp1-nine-local-20260927-proper/status.json`.
- The runner writes resumable JSONL checkpoints. If the machine is restarted,
  resume with the same command and add `--resume --run-id
  exp1-nine-local-20260927-proper`; do not start a second run with the same
  output directory.
- This run is not complete and has not produced a nine-model result. The
  small 27-row pilot remains descriptive only.

## Next research gate

When the nine-model trace completes, run every selector only on the search
questions, enforce equal realized profiling dollars, and evaluate the chosen
complete row on the untouched audit questions. Report search spend, held-out
accuracy, cold deployment cost, and uncertainty separately. Compare CACR/SCCR
with AgentOpt selectors, synchronized paired elimination, random/uniform
allocation, direct cost-aware allocation, and the hybrid-feedback baseline.

The replay command now accepts `--include-structured` to add CW-PLR, CACR,
and SCCR at explicit realized-cost fractions. It has been smoke-tested on the
completed 27-row pilot via a local fixture; the 729-row run remains pending.
Replay validates the full config/question rectangle and decodes explicit
slash-separated retry slots before any structured selector sees a cell.
