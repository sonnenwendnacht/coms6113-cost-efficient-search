# Direct workflow-search overlap: portfolios and Agent-UCT

The search found two papers that are closer to our outer problem than generic
bandit or routing work.

**Workflow portfolios.** Abdolmaleki, Jasin, and Wang's [Designing Agentic AI
Workflow Portfolios under Imperfect Selection and Compute Cost](https://arxiv.org/html/2609.18126v1)
represents an executable workflow as a sequence or graph that may include
verification and bounded revision. It optimizes a finite pool or an implicit
workflow class under recurring compute cost, uses held-out deployment tasks,
and recognizes that workflow variety can matter even when one workflow has
the best average score. This directly overlaps with complete workflow
selection, held-out evaluation, and compute-aware deployment.

Its decision is different: it chooses a *portfolio* and how many times each
workflow is executed for one incoming task, then a selector chooses among the
resulting answers. Its main costs are recurring workflow-level constants and
its optimization uses integer/LP/dual pricing tools. It does not study a
finite-budget best-row identification process in which each paid profiling
action is one answer-key-blind, verifier-gated execution and later calls may be
absent. We must cite it and compare the objectives, rather than claim that
complete workflow selection under cost is new.

**Agent-UCT.** Li et al.'s [Agent-UCT](https://arxiv.org/html/2607.24162v2)
searches discrete workflow configurations with UCT and an explicit marginal
cost penalty. Its WTB execution substrate records deterministic question-level
prefix materialization and reuses cached states; sampling-based evaluation
tracks item-level reuse. It is the strongest adjacent search baseline when
workflow prefixes are legal.

The project requirement deliberately excludes prefix materialization and
continuation reuse. HAPR/CAPR should therefore be framed as a complementary
no-prefix design: it pays complete rows, uses a same-question hub only as a
statistical covariate/control variate, and tests whether paired differences
reduce *profiling* spend. That distinction is not enough by itself for a
novelty claim. Agent-UCT should be included as a prefix-enabled upper-bound or
separate scope lane where feasible, and the no-prefix claim should be tested
against direct cached-incumbent paired racing.

## Revised novelty boundary

The contribution cannot be “agentic workflow optimization under cost,”
“configuration search over multiple model slots,” “held-out workflow
evaluation,” or “cost-aware UCT.” Those are now explicit prior art. The only
remaining candidate is a conditional result about the *allocation of direct
complete-row observations* when:

1. a row contains a verifier-controlled retry cascade;
2. row correctness is hidden from the search policy;
3. row charge is a realized path-dependent token cost;
4. same-question paired evidence is reused across rows without prefix reuse;
5. a ledger enforces equal spend and direct confirmation; and
6. the method beats a matched cached-incumbent row-search baseline.

If HAPR/CAPR does not beat that baseline, the honest result is a protocol and
diagnostic study, not a new search algorithm. If it does, the paper should
state the result only for the tested finite-row and verifier setting.
