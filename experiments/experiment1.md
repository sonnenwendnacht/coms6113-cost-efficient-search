# Experiment 1: retry-aware ordered rows

Experiment 1 is the first live pilot of the group proposal. A row is an
ordered triple of solver models: the original attempt, retry 1, and retry 2.
With three solver choices and repeated choices allowed, there are `3^3 = 27`
rows. A fixed Qwen 1.5B verifier decides whether deployment stops after each
attempt. It sees the question, options, and candidate response, but never the
MathQA answer key. The evaluator compares the final parsed choice with the
key only after the workflow ends.

The primary spending ledger is exactly

```
cost = sum(coefficient_model * input_tokens(call))
```

for every solver and verifier call that was reached. The local pilot uses
versioned proxy coefficients of `1e-7`, `3e-7`, and `5e-7` USD per input token
for Qwen 1.5B, 3B, and 7B. These numbers make the cost tradeoff concrete; they
are not claims about an API provider. Output tokens, cache discounts, latency,
and any other term contribute zero to this primary ledger. Input lengths are
counted with the tokenizer of the model making that call, including retry
history and verifier context.

The search source is a deterministic sample from MathQA train; the independent
audit is a deterministic sample from MathQA dev. MathQA test is reserved for a
later confirmation run. The local runner writes every trace under
`results/runs/<run-id>/`, which is intentionally ignored by Git. Each trace
cell contains the reached attempts, answer/checker decisions, input-token
ledger, and final correctness, but the search replay sees only cells selected
under its budget.

The replay compares random allocation, uniform allocation, UCB1, a
cost-normalized UCB, confidence arm elimination, and a small categorical
kernel Bayesian-UCB baseline. All methods stop at the same cumulative realized
cost budgets (25%, 50%, 75%, and 100% of exhaustive search-split evaluation),
then the selected row is scored on the untouched audit questions. The kernel
baseline is our dependency-free implementation; it is labelled as
AgentOpt-inspired rather than presented as a reproduction of AgentOpt's
Bayesian implementation.

Run on the GPU host with the runtime that contains `torch`, `transformers`, and
`accelerate`:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
  /home/gabi/zhengtong/data/runtime/ministral/bin/python \
  scripts/run_experiment1_local.py \
  --search-n 20 --audit-n 10 --run-id exp1-local-YYYYMMDD
```

The command records model config hashes, dataset hashes, selected-question
hashes, every cell's calls, and replay aggregates. A provider/API run is a
separate experiment: it requires a pinned endpoint, model snapshots, current
pricing, and an explicit budget; no API result is silently substituted for the
local proxy result.

## Interpretation of the recorded pilot

The first run is useful for checking the workflow and spending ledger, but its
accuracy table is not ready to support a method claim. The solver output cap
was too short for many local answers: 501 of 810 final answers were not
parseable, and 510 solver calls reached the cap. The verifier accepted 798 of
915 verifier calls, including many responses whose final choice could not be
parsed. The next run must raise the output limit, tighten the answer format,
and report parse failures separately before comparing search methods.

The replay policies are small in-repository baselines inspired by the ideas in
AgentOpt; they are not executions of AgentOpt's package. The eight repeats are
not eight independent model experiments: only random allocation changes with
the seed. The replay currently optimizes final observed accuracy under a
profiling budget, rather than a full deployment cost-accuracy frontier.

## Expanded nine-model comparison

The next run is specified in `configs/experiment1-nine-model.json` and uses
nine distinct solver models, so the ordered retry space has `9^3 = 729` rows.
It reserves 200 MathQA train questions for search and 200 MathQA dev questions
for the final held-out evaluation. Every `(selector, parameter setting)` is a
separate reported entry, following the layout of AgentOpt Table 7. The report
will include mean held-out accuracy, mean search evaluations, realized search
cost, and savings against exhaustive search, plus a plot of accuracy against
realized search cost for each selector family.

The expanded runner is deliberately blocked until nine distinct solver
checkpoints or API adapters are supplied. The current machine has four usable
local generative checkpoints (Qwen 1.5B/3B/7B and Ministral 8B); the other
local folders are embedding or reranking models and cannot stand in as solver
models. Relabeling those four checkpoints as nine models would invalidate the
comparison. Use `scripts/run_experiment1_nine_model.py --help` for the exact
model-path and proxy-cost inputs required for the run.
