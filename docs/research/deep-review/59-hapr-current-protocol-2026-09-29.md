# HAPR current protocol and stopping contract

After the overlap audit, the Algorithm 2 candidate should be written as a
protocol rather than a collection of similarity heuristics.

## Registered inputs

Register a finite row set `C`, a search question set `S`, a disjoint held-out
set `E`, a deployment cost cap (or explicitly a soft target), tolerance
`epsilon`, confidence `delta`, model-price coefficients, tokenizer/prompt
limits, and a question permutation. A row is the complete ordered assignment
of solver models and verifier policy for every possible retry slot. The
verifier never receives the answer key.

## Ledger and hub

Choose a hub `h` using a cost-only rule or an independent calibration fold.
Execute `h` completely on a predeclared initial block and store
`(Q,K,R,V)` for every question. A candidate action always executes a complete
row on a fresh question block. If the hub cell is already paid, form
`D_Q=Q_c-Q_h` and `D_K=K_c-K_h`; otherwise the cell is not eligible for a
paired estimate. The ledger must make the reuse visible and must charge the
hub once. A cached-incumbent baseline receives the same legal reuse.

## Allocation and stopping

1. Give every surviving row an initial direct block so no row starts with a
   similarity-only label.
2. Maintain simultaneous finite-population confidence sequences for the
   paired quality residual, paired cost residual, absolute hub quality, and
   each reach stratum used in the report. Use an anytime-valid construction or
   predeclared blocks when opening blocks adaptively.
3. Reserve the conservative maximum charge of the next complete-row action
   before starting it. If a maximum cannot be established from pinned prompt
   and tokenizer limits, label the experiment a soft cap and report overshoot.
4. Select the next row/block by expected confidence-width reduction per
   reserved charge, with a fallback to direct cost-aware racing when the
   residual covariance is weak or unstable. Similarity can affect this
   priority only; it cannot create a cell.
5. Eliminate a row only when its simultaneous utility upper bound is below the
   incumbent lower bound, or its conservative cost lower bound violates the
   deployment constraint. For a hard cap, a candidate with no feasible
   reservation is not silently treated as observed.
6. Stop only after one row remains within tolerance, or after a registered
   maximum budget. Execute a fresh direct confirmation block for the proposed
   row, then evaluate it once on `E` without hub transfer.

The utility form `Q-lambda*K` is allowed as a secondary frontier report. The
primary result should also report quality subject to a cost cap, because a
single lambda can hide infeasibility and does not represent every deployment
objective. Search spend, confirmation spend, cold deployment cost, held-out
quality, and uncertainty are separate fields.

## Required controls

Compare against random/uniform allocation, independent cost-aware BAI,
synchronized paired elimination, a cached-incumbent row-search baseline, and
the strongest relevant runtime or workflow-search baseline. Remove residual
transfer as an ablation. Add an adversarial split in which one-edit rows have
weak or sign-reversed correlation. Report the hub's amortization separately:
if the cached-incumbent baseline already has the same hub cells, any HAPR gain
must come from lower paired variance or better allocation, not from pretending
that a rerun was free.

The conditional claim is: under predeclared finite-population sampling,
bounded charges, valid simultaneous confidence sequences, and direct final
confirmation, HAPR can reduce profiling spend or improve recommendation
quality at matched spend for this complete-row retry problem. It is not a
claim of universal row prediction, a new confidence-sequence theorem, or a
runtime routing policy.
