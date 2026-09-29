# September 2026 prior-art audit (2026-09-29)

This note records a source check prompted by papers posted in August and
September 2026. No experiment, replay, or model/API call was launched.

## Cost-aware multi-objective configuration evaluation

[Xue et al., Cost-Aware Multi-Objective Bandits](https://arxiv.org/abs/2608.04333)
models an LLM configuration as an arm evaluated on a validation sample. It
studies both budgeted online selection and fixed-budget Pareto identification.
Its online CoHV-UCB uses optimistic hypervolume per cost; its fixed-budget
CoPSI progressively eliminates configurations with deterministic known costs.
The paper explicitly treats the validation reward vector as i.i.d. per arm and
uses a fixed per-configuration cost for the Pareto problem.

This rules out several broad claims for our project. We cannot claim to be the
first to combine LLM configuration search with multiple objectives, a dollar
budget, hypervolume, or cost-aware elimination. If we later make latency,
deployment cost, and accuracy a vector objective, CoHV-UCB/CoPSI belongs in
the baseline set. The remaining distinction is narrower: one row action is a
complete retry execution on a particular question, its charge depends on the
answer-key-blind stopping path and prompt lengths, and two rows evaluated on
the same question produce correlated evidence that can be reused by a hub.

The paper's experimental protocol is also a useful control: it separates a
profiling split from a held-out evaluation split and uses a fixed cost proxy
for its main identification problem. Its discussion treats structural
information among models/prompts/decoding choices as future work. That is
evidence for our narrower direction, not permission to call generic structure
new: we must show a gain from the shared-row protocol under a matched
cached-incumbent baseline.

## Cost-aware dueling feedback for LLMs

[Gharat et al., Cost-Aware Best-LLM Identification using Dueling
Feedback](https://arxiv.org/abs/2609.30360) studies pairwise model comparisons
with known arm costs and a Condorcet-winner assumption. Its DCTAS algorithm
uses a cost-aware Track-and-Stop allocation and a generalized likelihood-ratio
stopping rule. A duel costs the sum of two known model costs and returns one
Bernoulli winner; the paper proves asymptotic cost optimality under its
preference-matrix model.

This is very close in spirit to paired racing, so “we compare configurations
pairwise under unequal costs” is not a novelty claim. It is a strong baseline
for an adaptation in which a row is a complete retry configuration and the
pairwise observation is based on two answer-key-blind quality signals on the
same question. The adaptation is not automatic: the existing DCTAS model has
fixed arm costs, independent duels, and a Condorcet winner, while our runner
has question-clustered outcomes, path-dependent complete-row charges, and no
deployment-time answer key. We should report which assumptions are changed
and avoid importing its confidence guarantee without a new proof.

## Budgeted multi-attribute verification

[Xue et al., Test-Time Scaling via Budgeted Multi-Attribute
Verification](https://arxiv.org/abs/2609.34322) treats each fixed query-answer
pair as an arm with several separately sampled verification attributes under a
global budget. It combines cost-aware allocation with anytime-valid
certification. This is adjacent to our solver/verifier setup, but its arm is a
query-answer pair and its objective is to certify many answers; it does not
select one complete model row or reuse one row's answer as a control across
other rows.

It is useful prior art for the answer-key-blind verifier discussion: a
deployment checker can be an observable attribute, while final correctness is
an offline audit label. It does not license using the MathQA key to stop a
retry or to train a live selector.

## Structured search in multi-agent systems

[MASPOB](https://arxiv.org/abs/2603.02630) already combines a bandit UCB
rule, a topology-aware graph-neural surrogate, and coordinate ascent to search
prompt combinations in a fixed multi-agent workflow. Its problem is prompt
optimization with a workflow graph and a strict evaluation budget, rather
than complete model-choice rows with retry-dependent charges. It nevertheless
rules out presenting coordinate ascent, a graph surrogate, or “one-slot
changes are similar” as a standalone novelty. For our first Algorithm 2, a
transparent categorical similarity prior is easier to audit than a learned
GNN; any learned surrogate would need to beat MASPOB-style baselines and be
calibrated on held-out question folds.

## Revised claim boundary

The following phrases are already occupied and should be avoided as the sole
contribution:

- cost-aware LLM configuration bandits;
- budgeted multi-objective configuration selection;
- cost-aware dueling or pairwise best-model identification;
- anytime budgeted verification;
- generic similarity graphs, control variates, or common-question pairing.

The defensible remaining question is conditional and more specific:

> When complete retry configurations are evaluated on a shared, registered
> question stream, can a paid hub or other reusable same-question evidence
> reduce the dollars needed to identify an epsilon-good row under
> path-dependent execution charges, compared with a cached-incumbent direct
> or dueling baseline?

The paper must demonstrate that condition empirically and state exactly which
parts are an application-specific protocol versus a theorem. It should cite
the three papers above even if the first experiment remains single-objective.
