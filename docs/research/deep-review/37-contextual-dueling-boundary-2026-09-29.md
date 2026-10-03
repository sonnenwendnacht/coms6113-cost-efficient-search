# Contextual dueling boundary (2026-09-29)

The MathQA question can be treated as a context, and two complete rows on the
same question can be treated as a contextual duel. This reduction is useful,
but it is not new by itself.

## Existing contextual dueling settings

[Saha et al., Contextual Dueling Bandits](https://arxiv.org/abs/1502.06362)
studies pairwise feedback when the best action can depend on a context.
[Mehta et al., Kernelized Offline Contextual Dueling Bandits](https://arxiv.org/abs/2307.11288)
chooses informative contexts for preference feedback and gives UCB-style
regret bounds. [Verma et al., Neural Dueling Bandits](https://arxiv.org/abs/2407.17112)
uses neural reward models for contextual preferences. These works mean that
“questions are contexts and we compare two models” should not be presented as
a new bandit formulation.

## Why our target is still different

Our first target is a fixed finite benchmark winner, not a policy that chooses
a different model for each future context. A question is sampled once for a
registered finite-population estimate, and both rows' complete retry
executions are observed on that same question. The row charge is a random or
path-dependent sum of solver and verifier input-token charges, and a
deployment verifier can stop retries before later calls. Existing contextual
dueling formulations generally use a stationary preference model and do not
carry a stateful retry ledger or a hard dollar reservation for a complete row.

This distinction changes what can be claimed:

- if the goal becomes a per-question routing policy, use contextual-dueling
  assumptions and contextual regret metrics;
- if the goal remains one fixed row for deployment, use finite-population
  paired comparisons and report question-level simple regret or selection
  error;
- a shared hub is a reusable control/reference in the second setting, not a
  contextual policy that chooses the arm separately for each question.

## Baseline implication

At minimum, include a contextual-dueling or cost-aware dueling adaptation as a
conceptual baseline, then state why its independent stationary duel and
fixed-arm-cost assumptions do not certify our retry-row ledger. Do not claim
that a Hamming graph, a pairwise winner signal, or a question context alone
creates the contribution. The plausible gap remains a finite-population,
complete-row, path-cost protocol with explicit shared evidence and valid
budget accounting.

