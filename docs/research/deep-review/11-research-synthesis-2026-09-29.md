# Research synthesis: what Algorithm 2 can honestly claim

Prepared 2026-09-29 during the no-experiment research window. This memo
turns the source audit into a decision for the project. It is not a result
report and does not claim that the proposed method is new.

Editorial correction: the conservative protocol below asks for direct
confirmation before deployment, but a structured Bayesian selector may rank
an unmeasured row by model-based prediction. That prediction is not an
observed cell or an exact cache hit. See [the inference corrections](15-inference-corrections-2026-09-29.md)
and the structured KG candidate for the distinction.

## The problem statement to freeze

A configuration is a **complete row**: the model assigned to every solver,
verifier, and retry slot. For question `q`, one paid run returns

```text
Y(c,q) in {0,1}   deployment-valid final outcome
K(c,q) >= 0       realized input-token charge for reached calls
```

The selector never sees the answer key. The answer key is used only on the
held-out audit set. The search objective is fixed-budget recommendation:
with profiling budget `B_s`, return a directly evaluated row `c_hat` whose
mean outcome is as high as possible on the deployment question distribution.
Profiling spend, held-out quality, and cold deployment cost are separate
reported quantities. A deployment-cost constraint or utility `Y-lambda K`
must be registered as a separate objective.

This formulation prevents three common category errors:

1. A model-choice neighbor is another full cascade, not a free proxy or an
   unobserved cell estimate.
2. A known price coefficient is not the same as the realized cost of a path;
   early acceptance and retries make `K` random and potentially correlated
   with `Y`.
3. A search curve cannot be compared with an exhaustive optimum unless the
   response matrix is actually measured. The defensible comparison is quality
   at matched profiling spend, with uncertainty and a small exhaustive
   reference only where that reference was measured.

## What similarity can buy

For two rows run on the same question, the paired difference

```text
D(c,c',q) = Y(c',q) - Y(c,q)
```

has mean equal to the quality difference. Positive same-question covariance
can make `D` less variable than a difference based on independent question
samples. This is the safe role of similarity: improve a comparison between
rows that were both run. It does not fill an unmeasured row, reveal an
unreached retry, or make a path of one-slot changes telescope into a free
endpoint observation.

A Hamming neighbor is only a proposal for where such covariance might be
large. The final row recommendation still needs direct observations. If a
variance gate is used, it controls allocation or labels a comparison as
similarity-assisted; it must not be the source of the confidence guarantee.

## Recommended design: robust structured allocation with a valid fallback

The best candidate to take forward is a **robust structured pure-exploration
selector** (temporary name RS-BPE). It is a research design assembled from
existing ideas, not a new theorem yet.

1. **Precommit the evidence schedule.** Draw one outcome-independent random
   permutation of search questions and divide it into complete blocks. A
   comparison uses the same block for both complete rows. A row admitted late
   catches up on earlier blocks, or the comparison uses a disjoint cross-fitted
   block. A block is never stopped halfway because its outcomes or dollar
   total look favorable. This makes the question sample explicit and avoids
   treating adaptive cache inclusion as fresh evidence.
2. **Maintain direct row estimates and paired estimates separately.** Direct
   estimates are required for every row that could be recommended. Paired
   blocks estimate differences only. Exact cache reuse is accounting reuse,
   not an extra independent sample.
3. **Fit a small structural model only for allocation.** Use one-hot slot
   features plus a preregistered, low-order interaction set. Add a bounded
   residual or misspecification radius. The model proposes promising complete
   rows and uncertainty-reducing blocks; it never suppresses direct evidence.
4. **Choose direct versus paired work by conservative information per cost.**
   A candidate action is scored by its upper-bound reduction in uncertainty
   about the best row divided by a conservative bound on the new realized
   charge. The denominator is a scheduling quantity. Do not present
   expected-improvement-per-dollar as a guarantee; cost-aware BO shows that
   naive ratios can be arbitrarily poor.
5. **Use valid intervals for elimination.** For fixed question blocks, use
   bounded finite-population confidence sequences for direct means and paired
   differences. Allocate error over a predeclared edge family. If an edge is
   not trusted, use the two direct intervals. Similarity affects efficiency,
   not correctness.
6. **Reserve global exploration.** Keep a fixed fraction of blocks for rows
   selected outside the current neighborhood or surrogate optimum. This is a
   safeguard against nonlinear verifier/retry interactions, stratum reversal,
   anti-correlated neighbors, and local traps.
7. **Separate quality and cost feasibility.** Maintain a second interval for
   `K(c,q)` if deployment cost is constrained. Admit a block using a known
   worst-case charge envelope; otherwise make cell/block budget the formal
   constraint and report realized dollars afterward.
8. **Confirm before auditing.** At the search deadline, directly evaluate the
   recommended finalists on a fresh confirmation block, freeze the selector,
   and only then measure held-out audit quality. The audit set is never used
   to tune the model, gate, or budget rule.

A simpler, fully validity-first version is Conservative Paired Racing with
Successive Elimination (CPR-SE): use the fixed block schedule and confidence
sequences above, while allowing local similarity only to order the next edge.
CPR-SE is a baseline/repair, not a novelty claim. It gives us a clean control
against which the robust structural allocation can be judged.

## Novelty boundary after the literature review

The following ingredients already have close precedents and must be baselines
or explicitly cited: one-change local search and racing (ParamILS), categorical
Bayesian optimization and trust regions (COMBO, BOCS, Casmopolitan),
question-matched paired evaluation (SySRs and common-random-number ranking),
correlated best-arm identification, direct-versus-pairwise cost allocation,
robust linear pure exploration, costly reward observations, and cost-aware
Gittins/BO acquisitions. The mentor's cost-aware LLM evaluator also makes
known per-call prices and evaluation-cost accounting central prior art.

The possible contribution is narrower and conditional: characterize and
exploit **complete retry-row** correlation when the same question is run
through both rows, while the row's realized input-token cost depends on which
attempts are reached, and retain a direct-evaluation fallback when the
structural model is wrong. The source audit found no direct paper combining
all of those ingredients, but “no direct match in this bounded audit” is not
proof of priority. The paper must state this as a conditional empirical gap
until a full search and theorem are complete.

The strongest publishable outcome may be a negative result: Hamming/local
similarity helps only in smooth task strata, while endogenous retry cost and
rare hard questions defeat ungated gates. Showing when paired structure is
safe, when it is not, and how much profiling money is saved at a matched
probability of selecting an epsilon-good row would be a useful systems and
experimental-design contribution even if no new bandit theorem survives.

## Falsification plan (to run later, not during this window)

When experiments resume, preregister controls that can disprove the idea:

- smooth row effects where same-question covariance is expected;
- iid rows where similarity should provide no gain;
- permuted row labels to test whether gains depend on structure;
- stratum-reversal questions where a calibration block and the remaining
  questions rank rows differently;
- anti-correlated neighbors where pairing increases variance;
- nonlinear retry interactions in which one changed model alters later-call
  reach probability;
- matched-cost comparisons against direct uniform allocation, AgentOpt
  selectors, SySRs-style synchronization, CACR/SCCR, robust structured BO,
  and a fixed-budget resource-aware BAI baseline.

The primary table should report selection quality versus **actual profiling
charge**, not just number of cells. It should include the chance of selecting
an epsilon-good row, mean and quantiles of search dollars, held-out quality,
selected-row cold cost, and the number of paid cells. Confidence intervals
must cover independent seeds and questions. No response-matrix optimum should
be claimed when the matrix is incomplete.

## Decision

Do not implement MATRE or a simulated-annealing variant as the main claim:
categorical trust regions, Hamming neighborhoods, and annealed local search
are already close to COMBO, Casmopolitan, ParamILS, and related work. Keep
RS-BPE as the candidate extension, CPR-SE as the validity-first baseline,
and CACR/SCCR as heuristic ablations. Do not describe any of them as novel
until the falsification suite and a complete prior-art check support that
wording.
