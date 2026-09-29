# Similarity and workflow-search boundary

The requested use of “similar configurations” also has close prior art.

**SCOPE-Router.** [SCOPE-Router](https://arxiv.org/html/2608.12127v1) builds
correctness and cost matrices for every model–query pair, constructs
cost-aware behavior profiles, and uses a routing-consistency contrastive loss
to pull queries with similar model-suitability patterns together. This rules
out claiming profile similarity, cost-aware query matching, or contrastive
regularization as new in isolation. Its setting routes one model per query
after exhaustive matrix construction; it does not identify one complete
verifier-gated retry row from partial observations.

**AFlow.** [AFlow](https://arxiv.org/html/2410.10762) uses MCTS over
code-represented workflows, execution feedback, experience backpropagation,
and early stopping. It covers generic MCTS workflow search and verifier-aware
operators. It searches topology and prompts rather than a fixed finite retry
row set and does not use a same-question hub to reduce the cost of row
identification.

The project’s similarity claim must therefore be operational, not rhetorical:
the method should estimate a candidate row’s *paired residual relative to a
paid hub* and use that estimate only to decide which complete candidate to
open next. It must not claim that a learned embedding, graph, contrastive
loss, MCTS, or one-slot neighbor relation is novel. The required ablation is
to remove residual transfer while keeping the same question stream, cost
ledger, and direct confirmation; only a matched-spend improvement in the
complete-row setting could support the narrower claim.

## Information-boundary distinction

SCOPE-Router has a full `Y[N×K]` correctness matrix before training. HAPR/CAPR
must operate with an observation ledger containing only cells that have been
paid for, and the gold label must remain outside the deployment verifier. A
profile learned from the full matrix is therefore an offline upper bound or a
diagnostic oracle, not evidence that partial row search has succeeded.
