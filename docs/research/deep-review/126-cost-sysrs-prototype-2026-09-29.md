# 126: Cost-SySRs prototype (2026-09-29)

The repository now contains `run_cost_sysrs`, a source-level direct baseline
for the hybrid design. It evaluates every active complete row on a fixed
question block, removes one empirical loser, and repeats while budget remains.
It supports a cell budget or a realized-cost budget and reports incomplete
blocks and overshoot explicitly.

The module is intentionally labeled a heuristic. Its radius is diagnostic, its
cost budget uses observed row charge averages to choose a block size, and a
realized charge can cross the target inside a synchronized block. It does not
claim a fixed-confidence guarantee, a strict hard cap, or a savings result.

The corresponding tests are added but were not run during the research-only
window. The module does not reuse workflow prefixes, model outputs, verifier
state, or unpulled cells; its only structural operation is synchronized
question selection for active rows.

The implementation records a stop reason. If the realized-dollar budget cuts
through a block, cells from that partial block are ignored for selection. A
previous complete phase may produce a provisional common-prefix recommendation;
if none exists, the result explicitly has no recommendation. This prevents an
unobserved or partially observed row from winning by construction.

This gives later comparisons a transparent Cost-SySRs control before adding
the EGCR Phase B. The eventual fair experiment must still use the common
realized-dollar ledger and verifier-visible reward contract from notes 119 and
122.
