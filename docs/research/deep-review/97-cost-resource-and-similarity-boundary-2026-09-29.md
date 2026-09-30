# Cost resources, multi-fidelity, and similarity overlap

## Primary sources

- Li and Cheung, *Learning with a Budget: Identifying the Best Arm with
  Resource Constraints*, [arXiv:2602.24146](https://arxiv.org/html/2602.24146).
  BAIwRC gives each arm a reward and one or more random resource consumptions,
  permits arbitrary reward--consumption correlation, and proposes Sequential
  Halving with Resource Rationing (SH-RR). Its model has an unknown arm
  distribution over `(R,D_1,...,D_L)`, a bounded/sub-Gaussian reward, bounded
  resource consumptions, a unique best arm, non-anticipatory stopping, and a
  cumulative resource constraint that must hold with certainty. It is a direct
  baseline for a hard profiling cap when a row's realized charge is random.
- Poiani et al., *Optimal Multi-Fidelity Best-Arm Identification*,
  [arXiv:2406.03033](https://arxiv.org/abs/2406.03033). Multi-fidelity BAI
  allocates cheaper lower-fidelity observations under known fidelity costs and
  a known uniform bias bound to a target fidelity, with canonical
  exponential-family rewards. Treating an early retry as a ``cheap fidelity''
  is therefore not automatically novel.
- Shi et al., *Efficient Prompt Optimization Through the Lens of Best Arm
  Identification* (TRIPLE), [official NeurIPS page](https://proceedings.neurips.cc/paper_files/paper/2024/file/b46bc1449205888e1883f692aff1a252-Abstract-Conference.html)
  ([PDF](https://www.proceedings.com/content/079/079017-3161open.pdf)). TRIPLE
  formulates black-box prompt selection as fixed-budget BAI and uses embeddings
  through clustering or a learned reward map to share information among
  candidate prompts under a fixed number-of-trials budget.

## What this rules out

A paper cannot claim novelty for any of the following alone: cost-aware
successive halving, a cumulative profiling cap, lower-fidelity screening,
embedding or Hamming similarity, clustering, function approximation, or
allocating more samples to uncertain candidates. Each has a direct precedent.
TRIPLE is especially close to the original intuition that similar categorical
configurations should share evidence: its candidates are discrete prompts and
its budget is the number of paid LLM evaluations.

## Retry-row boundary

The project can still pose a different observation model, but the distinction
must be explicit. A paid observation is a **complete retry row on one question**.
The row's final correctness is produced by a verifier that cannot see the answer
key, while its charge is the sum of the input-token charges of every reached
solver and verifier call. Thus the charge is random and can be correlated with
the final correctness through verifier reach; an unexecuted later attempt is a
missing continuation, not a zero or a cheap fidelity measurement. The selector
must recommend a complete row, and held-out questions remain untouched until
after recommendation. Unlike TRIPLE's trial count, the search ledger must
charge realized input tokens and reached calls.

This differs from ordinary multi-fidelity BAI in two ways that matter for a
claim: an early stopping prefix is not a controlled, biased approximation to a
fixed target, and the missing later attempt cannot be imputed without an
assumption about counterfactual verifier behavior. If the method does use an
explicit lower-fidelity surrogate, it must define the target, bound its bias,
and compare against the multi-fidelity baseline at equal realized dollars.

It also differs from BAIwRC's hard-budget formulation. BAIwRC requires the
cumulative resource constraint to hold with certainty and analyzes stochastic
resource consumption. Our initial experiment reports expected/realized search
spend and recommends after a cap; it does not yet provide a feasible-policy
proof under a hard cap. We must either (a) implement a reservation rule that
never overspends the remaining cap, or (b) call the result a fixed-realized-
spend empirical comparison and avoid a hard-budget theorem.

## Algorithm-2 consequence

The strongest defensible candidate remains a gated complete-row procedure:

1. Use the Hamming graph only to propose a challenger; every endpoint is paid
   as a complete row/question evaluation.
2. Use same-question paired residuals or a complete-row anchor only after a
   pilot verifies covariance and a conservative cost--variance break-even
   inequality. Otherwise fall back to direct cost-aware BAI (including SH-RR,
   CABAI, and a cost-aware dueling/Track-and-Stop baseline).
3. Charge each decision by the **realized** new input-token cost and enforce a
   reservation for the worst-case next block if claiming a hard cap.
4. Confirm the recommended row with a fresh search block, then evaluate it once
   on the held-out audit split. Never use the audit split to tune similarity,
   fidelity, temperature, or stopping parameters.

The possible contribution is therefore not “similar rows share samples.” It is a
conditional extension of resource-constrained and correlated BAI to complete
retry rows with verifier-gated, outcome-linked charges and a separate blind
held-out evaluation. The paper should state this as a hypothesis until a
formal model, equal-dollar baselines, and negative controls support it.
