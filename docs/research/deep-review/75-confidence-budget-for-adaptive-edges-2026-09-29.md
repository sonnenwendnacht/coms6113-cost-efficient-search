# Confidence budget for adaptive similarity edges

## Problem

A structural selector can compare many complete rows through same-question residuals. If it creates edge streams after seeing the data, a confidence interval calibrated for one preselected edge is not enough. The edge set, time index, and any path chosen from the graph all become selection events.

For the 9-by-9-by-9 row grid, the one-coordinate Hamming graph already has
`3 * 9^2 * C(9,2) = 8,748` undirected edges (17,496 directed neighbor
relations). A union bound over every edge and every interim sample can make
early intervals too wide, but silently ignoring the multiplicity invalidates a
global certificate.

## Defensible choices

1. **Pre-register a small edge family.** Choose hub edges or a fixed sparse design before seeing outcomes, assign each edge a confidence share, and use an anytime sequence over its prefixes.
2. **Fresh stream on creation.** If an edge is opened adaptively, assign it a new independent question permutation and a confidence share that decreases with its creation index. The stream must be charged in the search ledger.
3. **Model-assisted prediction without certification.** Use all observed graph edges to rank the next measurement, but let elimination rely only on the pre-registered or freshly charged confidence streams. Fall back to direct complete-row racing when the structural certificate is too wide.

Selecting a shortest path after the fact does not require another path-count union bound if every edge interval used by the path is already simultaneous. The direct node and row means still need their own confidence budget. This separates an efficient acquisition heuristic from a valid best-row claim.

## Consequence

The paper should report both the number of structural streams opened and the confidence accounting rule. “Graph similarity” is not a free source of evidence: every paid paired edge and every adaptive stream has a measurable cost and a statistical error budget.
