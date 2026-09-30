# 142: Slot-gated factorial racing candidate (2026-09-30)

The nine-model trace gives a clear warning against an unweighted Hamming
similarity assumption. A one-slot change in the original solver has much
larger search reward differences than a one-slot change in retry 1 or retry 2.
The suffix result is partly structural and partly a consequence of the
verifier stopping almost every workflow after the first attempt. A method that
uses one global graph bandwidth will therefore spend its similarity budget in
the wrong places.

## Candidate method

Use **slot-gated factorial racing (SGFR)** for the next replay. Every row is
still a complete deployment configuration; no solver output, prefix, or
checkpoint is reused. The method only changes which complete row/question
cells it pays for.

1. Draw a fixed paired calibration block. For each slot, compare complete rows
   that differ only in that slot, and record the reward residual, retry-reach
   residual, and realized charge difference.
2. Build a conservative gate for each slot from a cross-fitted residual bound.
   A slot is active only if its lower residual-importance bound exceeds a
   declared practical tolerance, or if its uncertainty remains large enough
   to justify more measurements. A suffix slot with a certified negligible
   effect is not assumed equal forever: the gate can reopen after a changed
   verifier, retry rule, or task stratum.
3. Allocate the next complete row/question block to the unresolved slot or
   interaction with the largest predicted reduction in incumbent/challenger
   interval per new realized charge. Keep a direct-row exploration reserve and
   require a fresh confirmation block for the eventual full row.
4. If an additive slot model is used for acquisition, estimate interactions
   on held-out calibration blocks and fall back to direct row racing whenever
   the interaction residual is too wide. The recommendation is always a
   complete row, not a separately deployable collection of slot effects.

The gate should track two quantities separately: quality effect and resource
effect. A retry slot can have a small mean correctness effect but a large
cost effect on the rare questions that reach it. Eliminating it because its
average reward residual is small would be unsafe.

## Required controls and failure cases

Compare SGFR with direct cost-aware racing, Cost-SySR, unrestricted
target-difference allocation, unweighted graph residual racing, and a shuffled
slot-label graph. Also run reward-only, reach-aware, and charge-aware gates.
Report unique paid cells, actual dollars, false eliminations, no-recommendation
rates, retry-reach coverage, held-out accuracy, and cold deployment cost.

The method is not new merely because it uses factorial features: combinatorial
pure exploration and algorithm-configuration racing already do that. Its
testable project-specific claim is that a **cross-fitted, slot-specific gate
using complete retry cells and response-dependent charges** saves profiling
spend when the verifier makes some coordinates conditionally inactive. It
should be rejected if a direct paired method matches it at equal dollars, if
the gate confuses rare expensive retries with negligible effects, or if its
advantage disappears under a verifier that forces later attempts.

The present trace can support the gate diagnostic but is not sufficient for a
retry-aware superiority claim. A follow-up workflow must increase retry reach
or deliberately stratify questions/checker behavior so the suffix is observed.
No model/API calls are required for this candidate; it is a replay and design
hypothesis.

## Prototype implementation

The branch prototype is `src/retry_search/slot_gated_factorial_racing.py`, exposed as `run_sgfr`. It accepts quality, realized charge, and optional reached-attempt matrices, plus a cell fraction, cell count, or realized-charge budget. Calibration and race units are complete search rows; a reserved question block is used for a final two-row confirmation. No partial row or unobserved cell is imputed, and cost-budget overshoot is reported. The accompanying unit tests cover deterministic replay, exhaustive direct selection, missing reach-channel handling, and invalid row/budget shapes. This implementation is an allocation prototype for the next replay, not a result or guarantee.
