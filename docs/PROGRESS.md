# Resumable checkpoint

Updated: 2026-09-29 19:39 ET (research-only window resumed; no experiments launched).

## Research branch

- Algorithm branch: `research/algorithm2-sequential-comparison`.
- Main experiment branch: `research/experiment1-nine-models`.
- The algorithm branch contains CW-PLR, CACR, and the gated SCCR prototype,
  synthetic iid/smooth/permuted controls, the pilot trace-locality diagnostic,
  and the expanded related-work boundary. The latest pushed algorithm commit
  is `200bbed`; source-audit commits after the earlier implementation
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
- The latest main branch is `02ba91f` and the algorithm branch is
  `200bbed`; both are pushed and included in PR #4.
- The current Algorithm 2 checkpoint is pushed on
  `research/algorithm2-sequential-comparison` and is included in PR #4.

## Long local trace

- Run ID: `exp1-nine-local-20260927-proper`.
- Status observed at 2026-09-29 23:35 UTC: `241,200 / 291,600` cells
  (`82.72%`), still running in PID `8763`.
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
