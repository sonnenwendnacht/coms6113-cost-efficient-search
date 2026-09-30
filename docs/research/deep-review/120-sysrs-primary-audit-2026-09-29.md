# 120: SySRs primary-paper audit (2026-09-29)

## What SySRs already establishes

The ICML 2026 paper **Cutting LLM Evaluation Costs with SySRs** formalizes an
LLM score matrix with one row per model and one column per test prompt. It
samples the same without-replacement prompt block for every active model in a
successive-rejects phase, then eliminates the worst empirical mean. Its
guarantee explicitly improves with between-model correlation and does not need
the correlation strength as a hyperparameter.

This is closer to our problem than generic graph BAI. It rules out claiming
that synchronized same-question blocks, paired comparisons, or
hyperparameter-free similarity exploitation are new by themselves.

## Exact retry-row gap

SySRs treats each matrix entry as one bounded score draw and budgets a fixed
number of model/prompt evaluations. Our entry is a complete retry workflow:

- one question can reach a different number of attempts for different rows;
- each reached solver and verifier call has a different coefficient and input
  length;
- the final charge is therefore realized after the path, not a fixed unit;
- the deployment checker is answer-key blind, while final correctness is an
  evaluator-only audit outcome.

The direct baseline should therefore be a **Cost-SySR** implementation: keep
SySRs' synchronized successive-reject schedule, but charge every complete row
question cell in a realized-dollar ledger and freeze recommendations at common
dollar checkpoints. The baseline must be included before claiming that a local
Hamming graph or an edge gate helps.

## Required positioning

Algorithm 2 can be framed as an extension only if it demonstrates something
that Cost-SySRs does not:

1. cost-aware phase allocation under unequal, path-dependent cell charges;
2. a cross-fitted gate that uses measured row similarity to choose which active
   rows receive further paired blocks; and
3. a valid independent held-out audit of the complete selected row.

The first item is a resource-allocation extension, the second is a gated
allocation heuristic until proved, and the third is an evaluation contract.
None should be presented as a new synchronized bandit principle.

## Source

Lyu, Nejma, Wegel, Yang, and Dorner, “Cutting LLM Evaluation Costs with
SySRs: A Bandit Algorithm that Provably Exploits Model Similarity,” ICML 2026:
https://arxiv.org/abs/2606.07726
