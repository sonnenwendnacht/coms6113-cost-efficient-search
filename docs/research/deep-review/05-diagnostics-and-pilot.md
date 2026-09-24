# Exact diagnostics and a falsifiable first experiment

Prepared 2026-09-23. The calculations below use invented finite populations, not model outputs. The experiment protocol is proposed and has not been run.

## Reproduce the calculations

~~~bash
python3 scripts/research_diagnostics.py --output /tmp/coms6113-diagnostics.json
diff results/diagnostics-2026-09-23.json /tmp/coms6113-diagnostics.json
~~~

The [script](../../../scripts/research_diagnostics.py) uses exact fractions and enumeration for its identities; JSON displays decimal summaries. There are no API calls, random trials, or fitted parameters. The fixed-sample binomial limit is a floating-point analytic calculation. The [output](../../../results/diagnostics-2026-09-23.json) is a small reviewed diagnostic artifact.

## Nine checks and their meaning

| Diagnostic | Exact setup/result | What it establishes; what it does not |
| --- | --- | --- |
| Shared-prefix paired comparison | Of 100 questions, 90 stop: 80 correct and 10 wrong. Ten reach different suffixes; A solves 2 and B solves 8. Scores .82/.88; conditional gap .60 becomes overall gap .06. Paired-difference variance .0564 versus .2532 for two independent single-question scores. Shared pair costs 3.2 invented units versus 5.2 separately. | Reach weighting, pairing and accounting can matter. The 4.49 variance ratio and cost saving are properties of this chosen example, not measured method improvements. |
| Family screening | Enumerate all 1,024 binary outcome completions of those 10 unfinished cells: all scores lie in [.80,.90], below a known .93 incumbent. | One prefix record can bound many completions. These are possible outcome completions, not 1,024 empirically implemented model configurations. Equal feasibility is assumed. |
| Failure conditioning | One retry solves 74/100 questions overall. Initial A and B each solve 80, but their failure sets differ: retry accuracy is .10 after A and .90 after B. Final scores .82 and .98. | Using standalone retry accuracy would wrongly predict .948 for both. The previous execution history determines the relevant population. |
| Selective continuation bias | True population gap .06. Selecting two known positive reached differences estimates .10. Averaging estimates over all 45 uniform two-of-ten samples gives .06. | Hand-picked continuations can bias a naive mean; a stated random design preserves its target here. Outcome-dependent stopping still needs separate analysis. |
| Partial revelation bounds | Reveal two successful suffix-B cells and leave eight unknown: the complete finite score lies in [.82,.90]. Enumerate all 256 completions to check this. | Pointwise bounds remain sound without imputing unobserved responses. Population sampling uncertainty must be added separately. |
| One-edit failure | Two assignments differ only in the planner. Invented scores change from 1 to 0. | Hamming distance one implies no nontrivial universal accuracy bound. |
| Rare expensive branch | A .01-reach branch adds 1,000 units when reached: 10 expected extra units. | A small bound on accuracy effect does not imply a small cost effect. |
| Zero observed reach | Zero reaches in 100 iid questions has a one-sided 95% fixed-sample binomial upper limit of about .029513. | Zero observed is not zero possible. This fixed-n interval is not valid under arbitrary repeated inspection without adjustment. |
| Unequal-cost allocation | Two independent normal means have variance 1 and per-sample costs 1/9. At budget 90, integer counts 27/7 minimize variance among positive-count allocations: .179894 versus .222222 for equal counts or equal dollars. | Neither equal counts nor equal spending is universally optimal. This is two-mean variance minimization, not a best-arm identification optimality claim. |

The nine diagnostic cases test assumptions; they do not estimate a performance distribution.

## A staged pilot

### Stage 0: fix the semantics before spending

Use two models, one initial attempt and one possible retry: four assignments. A deployable checker controls stopping; a separate hidden scorer evaluates the final emitted output. If the checker rejects a correct first answer and the retry makes it wrong, final quality is zero. If it accepts an incorrect first answer, the retry never executes.

Define whether retries change the model, failure feedback, or random draw. Pin output/token/time caps. Record both checker acceptance and benchmark correctness. Use intentionally failing tools, wrong accepted answers, rejected correct answers, budget interruption, and changed prompts to test the trace and cache semantics.

The existing replay scaffold checks some accounting behavior but is not a real checkpoint engine. Do not label it an implementation of the proposed allocation procedure.

### Stage 1: measure whether useful structure exists

For a minimal two-stage workflow, allow two models at each stage and one retry only at the second stage. This gives three model-choice slots and eight assignments. Keep the stop policy fixed. Stage one could produce a plan and stage two an answer/repair, but the actual benchmark and checker remain a group decision.

For a representative development sample, acquire complete traces for this small space with all possible legal sharing. Preserve hidden cells behind a replay interface for exploratory search simulations. These inspected development traces cannot subsequently become untouched confirmatory data; use separate frozen search and audit data for confirmatory comparisons in Stages 2–3. Measure:

- The fraction of spending in reusable prefixes.
- Reach rates by divergence depth, with uncertainty.
- Paired score differences and their variance; compare with independently sampled questions.
- Conditional continuation quality by full preceding state/model history.
- Output-token variation, checker errors, and failure/timeout spending.
- Quality and cost intervals for whole prefix families.
- Model replicate variability on a separately specified subset.

Question-level pairing is essential; aggregate model accuracies cannot reveal whether errors coincide. Preserve question difficulty proxies and subgroup labels for diagnosis, but do not retrospectively redefine the primary target.

Choose sample size from the precision needed for a declared practical difference and the paid budget. A small pilot estimates feasibility; it should not be advertised as a powered confirmatory study. Use bounded-cost arithmetic to calculate a maximum bill before execution.

### Stage 2: compare allocation under the same engine

Freeze the candidate set, checker, objective, budget grid, splits, recommendation rule, hyperparameters and failure rules. Start with expected quality under one deployment-cost cap; report latency alongside it. Bound or separately model deployment randomness, especially for tail-latency claims.

Minimum comparison set:

| Method | Explicit specification required |
| --- | --- |
| Random configuration search | Uniform candidate sampling without replacement, a fixed registered question allocation per candidate, and the same recommendation/audit rules. Report how partial last allocations are handled. |
| Uniform allocation | Cycle through all candidates on matched question batches until the dollar reservation rule prevents further work. No elimination is performed. Equal sample counts are not equal dollars. |
| Paired elimination | A SySRs-style synchronized schedule on common questions, adapted to the dollar cap and common cache. Preserve an original-protocol reproduction separately; the adaptation does not inherit the original theorem automatically. |
| Cost-aware independent-arm allocation | Reproduce GittinsEval under its proxy-cost assumptions, then identify any engineering adaptations for actual charges explicitly. Include actual budget stopping consistently. |
| Existing workflow search/profiling | AgentOpt's relevant method and VineLM-style profiling where interfaces/semantics can be reproduced. Document any unavailable implementation. |
| Proposed allocation | Exact-prefix structure plus valid partial-completion bounds, with one frozen acquisition heuristic and global exploration. |

The first screening experiment can use the first three baselines and the candidate to test whether there is any signal. A publication claim requires the closest relevant baselines, including suitable workflow profilers and stronger surrogate methods such as LRF/BO when the candidate claims to outperform their transfer mechanism.

Separate two effects with a two-by-two experiment:

| | Uniform/paired allocation | Proposed allocation |
| --- | --- | --- |
| Reuse off | Measure independent execution expense | Measure adaptive selection without prefix savings |
| Reuse on | Strong cache-enabled baseline | Combined method |

“Reuse off” disables physical reuse of completed workflow calls; provider prompt caching is measured separately. Use the same target configurations and deployment semantics. On frozen replay, maintain a separate counterfactual execution/cache ledger for each method. In live experiments, interleave or randomize run order where feasible to avoid provider drift being confounded with method.

Record algorithm compute time, checkpoint storage, state serialization and scheduler overhead. A search method that saves API charges but imposes large human/runtime costs needs that tradeoff reported.

### Stage 3: separate selection from the final audit

Use development data for design, search data for allocation, and untouched audit questions for the final comparison. A question must not migrate between these roles. Freeze all recommendations at the registered budget checkpoints before releasing their audit scores to researchers who could tune the method.

Evaluate selected configurations on the same audit questions and retain paired per-question differences. If several replicates share a question, account for that clustering; do not treat copied prefixes or duplicated cells as independent observations. Report uncertainty due to the audit questions and variation across search seeds separately. Select a primary budget/outcome before the confirmatory run and account for multiple comparisons when making claims across many budgets or tasks.

At small scale, report finite-benchmark regret and false-elimination/coverage rates against the exhaustive reference. Hide its unrevealed entries from the policy. At larger scale, report held-out comparisons plus any valid whole-space certificate; do not substitute “best evaluated configuration” for the true optimum.

Report quality, deployment expense and constraint violations separately. A method should not look better because it quietly picks an infeasible expensive configuration. If no candidate is certified feasible within budget, distinguish the pragmatic recommendation from a certified result.

### Stage 4: decide whether to continue

Continue toward larger model/stage/retry spaces only if structure-aware allocation improves the primary matched-dollar comparison beyond cache-enabled paired allocation at a useful effect size, with acceptable uncertainty and no hidden audit/tuning advantage.

Otherwise diagnose:

1. Is prefix execution actually expensive enough to matter?
2. Do early stops bound enough families?
3. Are suffixes almost always reached, leaving broad intervals?
4. Is conservative uncertainty the bottleneck?
5. Are rare expensive or high-value continuations being missed?
6. Does ordinary paired elimination already capture the whole practical gain?

A negative result is useful for choosing a different contribution; it is not a reason to weaken the baseline.

## Cost reporting and break-even

For each isolated search run, log every actual charge, including failed API attempts, tools, paid judges, initialization and pilot evidence exposed to that method. Log unpaid logical implications separately from physical invocations. Record provider discounts in a pricing snapshot; do not confuse a predicted token bill with the actual bill.

Independent audit, common reference construction and development costs need separate totals even if excluded from the headline search budget. If tuning our acquisition rule consumed substantial data/spending, report it. Give baseline tuning comparable treatment.

For two choices of search procedure, if the more expensive procedure spends an extra ΔB to find a configuration that saves Δc per deployed request at comparable acceptable quality/latency, its incremental monetary break-even is ΔB/Δc requests when both quantities are positive. Include differing recurring checker charges. This is an accounting calculation, not a guarantee of future workload size or distribution stability.

## Evidence required for a paper claim

The final artifact should contain a precise problem and algorithm, a claim-to-assumption map, independently reproducible spending ledgers, strong equal-dollar baselines, component ablations, held-out outcomes with uncertainty, and cases where the approach does not help. A theorem should analyze the actual adaptive observation rule; an empirical claim should use the actual deployment stopping rule.

No pilot benchmark run, paid model call, or method-performance comparison has yet been performed.
