# Hard-cap reservation under bounded retries (2026-09-29)

Research-only derivation from the current runner. No generation, replay, or
experiment was launched.

## Why a row action needs a reservation

One paid action is a complete row on one question. It can reach at most three
solver attempts, and every reached attempt is followed by one verifier call.
The number of calls is decided by the answer-key-blind verifier, so the action
must reserve for the worst permitted path before it starts. Checking only
`spent + expected_cost <= budget` can overspend when a cheap first attempt
triggers two retries.

## A conservative bound for this runner

The runner fixes `max_new_tokens` for solver calls and `64` for verifier calls.
Retry solver prompts include at most the last 1200 characters of the previous
solver output and 400 characters of verifier feedback. Verifier prompts include
at most the last 3000 characters of the candidate response. For a fixed row,
question, model snapshot, and tokenizer, define `T_{m}(text)` as the exact
input-token count produced by the model's chat template. A conservative action
bound is

```text
K_max(c,q) = sum_{attempt=1..3} [
  coeff(solver_attempt) * T_solver_attempt(max_prompt_attempt)
  + coeff(verifier) * T_verifier(max_verifier_prompt)
].
```

The maximum prompt strings use the known problem/options plus the largest
allowed output and feedback slices. Because the generation cap bounds the
number of output tokens, the truncation slices can be bounded without knowing
their realized text; the implementation should still compute the bound with
the actual pinned tokenizer and include chat-template overhead. If a provider
has hidden tokenization, tool calls, or a larger response than the local cap,
the bound is unavailable and the run must use a soft cap with overshoot
reported.

For a hard cap, admit a new action only when

```text
spent + reserved_for_in_flight + K_max(c,q) <= B.
```

After completion, replace the reservation by the realized ledger charge and
return any unused reserve. A pair action reserves the sum of both complete-row
bounds. The same rule applies to the final direct confirmation; it cannot be
silently exempted from the search budget.

## What to report

Report the declared bound, the realized charge, the reservation utilization,
and any overshoot. Distinguish a tariff coefficient from a bound on a complete
cell. With the current deterministic local decoding, a fixed cell is
deterministic conditional on the runner and question, but its charge is still
unknown until the verifier path and prompt lengths are observed. If outputs are
stochastic in a provider deployment, reserve a worst-case bound or explicitly
switch to a soft expected-cost objective.

