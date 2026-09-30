# Cost-synchronized successive rejects for complete retry rows

## Starting point

SySRs, *Cutting LLM Evaluation Costs with SySRs* ([arXiv:2606.07726](https://arxiv.org/html/2606.07726)), evaluates the remaining models on the same question block in each successive-rejection phase. This creates a joint per-question reward vector, so common task difficulty cancels in paired differences. Its budget is a fixed number of model/question evaluations.

For our setting, one arm is a complete retry row `c`. A cell still runs the full
row and returns final correctness `Y(c,q)` plus the realized input-token charge
`K(c,q)`. The same-question block is a statistical pairing only; it does not
reuse a solver response, verifier state, or retry prefix.

## Candidate: Cost-SySR

Call the direct adaptation **Cost-SySR**. It is a baseline/Algorithm-2 candidate,
not a novelty claim yet.

1. Register all candidate rows, an immutable row-slot map, a uniformly shuffled
   search-question order, and a profiling budget. If the budget cannot afford
   one complete cell for every row, state that full best-row identification is
   impossible under this protocol and use a scout subset with a separate
   coverage caveat.
2. In phase `k`, let `A_k` be the active rows and `B_k` the next common question
   block. Run every `(c,q)` for `c in A_k`, `q in B_k` as a complete workflow.
3. Choose the block size from a phase dollar target. Under realized-spend mode,
   estimate the next block charge from prior `K(c,q)` and record any overshoot.
   Under safe-hard-cap mode, choose the largest block whose sum of deterministic
   upper bounds `U(c,q)` fits the remaining budget, as in note 98.
4. Estimate each active row's mean on the accumulated common questions. Use
   paired residuals `D_ab(q)=Y(a,q)-Y(b,q)` and their empirical covariance for
   confidence widths; do not treat Hamming distance as a covariance guarantee.
5. Eliminate the row whose upper confidence bound is below the best active
   lower bound (or use SySRs' scheduled worst-mean elimination when running the
   fixed-budget exploratory version). Keep a random scout reserve so a wrong
   early elimination cannot be repaired only by local similarity.
6. Directly confirm the final row on a fresh search block, then measure it on the
   untouched audit questions. The recommendation must have direct complete-row
   observations; a model estimate for an unpulled row is not sufficient.

A cost-aware phase target can use the observed information per dollar. For an
active pair `(a,b)`, a rough gain for one common question is proportional to
`1 / Var(D_ab)`, while its expected charge is `E[K(a,q)+K(b,q)]`. The block
allocator should favor a phase or pair with larger estimated gain per charge,
subject to a minimum common block for every active row and a global scout floor.
This is an allocation heuristic until its adaptive confidence rule is proved.

## Why this is a useful test

Cost-SySR isolates the most defensible role of row similarity: question-level
correlation in **complete-row** outcomes. It does not rely on an unverified claim
that one Hamming neighbor predicts another, and it does not add path residuals
through unobserved rows. It also exposes the practical tradeoff hidden by a
fixed-cell SySRs budget: removing a high-cost row changes the dollar price of
all subsequent synchronized blocks.

The expected empirical advantage is narrower than “fewer pulls.” At equal
realized profiling dollars, Cost-SySR should reduce uncertainty in close row
comparisons when `Var(Y_a-Y_b)` is small, while cost-aware independent-arm BAI
may be better when row costs are highly heterogeneous or covariance is weak.
The same-question block can be actively harmful if expensive rows dominate the
block cost or if early verifier acceptance creates large, outcome-linked charge
variance.

## Required controls and failure cases

- Compare against original fixed-cell SySRs, cost-aware independent BAI/SH-RR,
  direct paired Top-Two, random/uniform allocation, and a Hamming-permuted
  Cost-SySR control at equal realized dollars.
- Report the neighbor-versus-random residual variance, the distribution of
  `K(c,q)`, phase utilization, and the fraction of rows eliminated per phase.
- Use search-block cross-fitting for covariance and interval calibration. A
  plug-in fixed-sample interval after repeatedly checking the phase boundary is
  not valid.
- If a row is eliminated before it has a common block, mark the procedure
  exploratory unless a simultaneous bound covers that elimination.
- Do not interpret a missing retry as a zero reward or a cheap fidelity. The
  final score is observed only after the complete row's verifier-gated execution.
- If the safe upper bounds are too conservative to use the budget, report that
  utilization loss and fall back to realized-spend comparisons rather than
  quietly treating a mean forecast as a hard cap.

## Novelty boundary

Synchronized questions, successive rejection, and correlation-dependent bounds
are established by SySRs. Cost-aware resource allocation is established by
resource-constrained BAI. The conditional project contribution would be a
carefully evaluated complete-retry-row adaptation in which the reward and the
resource charge are both generated by verifier-gated paths, with separate
held-out deployment evaluation. A paper should not claim a new bandit theorem
until it proves an adaptive cost-normalized confidence rule; otherwise present
Cost-SySR as a transparent, reproducible baseline and report its limitations.
