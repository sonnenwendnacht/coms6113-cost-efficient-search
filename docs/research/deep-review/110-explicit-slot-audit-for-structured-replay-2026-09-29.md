# Explicit slot audit for structured replay

The row graph is meaningful only when each configuration has an immutable tuple
of model-choice slots. Numeric row order is not a safe substitute.

## Finding

`row_slots_from_config_ids` decodes explicit slash-separated configuration IDs
and the replay passes those slots to CACR and SCCR. `run_cw_plr`, however, has no
`row_slots` argument and calls `_hamming_neighbors(incumbent, k)` directly. Its
neighbor graph is therefore derived from the integer row index. The replay sorts
configuration IDs lexicographically before constructing the matrix, so this
index order is not guaranteed to preserve the generator's Cartesian-product
coordinates.

A CW-PLR result can consequently be labeled “local racing” while proposing
nonlocal or incorrect neighbors. A permuted-index control would not repair this:
without an explicit slot map, the canonical and permuted graphs are both
arbitrary.

## Gate before any structured result

- Add an explicit `row_slots` argument to CW-PLR, validate uniqueness and slot
  width, and use it for all neighbor proposals; or decode and validate the row
  IDs inside the selector.
- Record a hash of the row-slot map in the run manifest.
- Run a source-level fixture check in which row IDs are shuffled while slots stay
  fixed; the structured proposal sequence must remain unchanged.
- Keep the numeric-index version only as a deliberately mislabeled/random-graph
  ablation.

This is a reproducibility correction, not an empirical claim. No experiment was
started for it. Until the mapping is explicit, do not compare CW-PLR as a
faithful Hamming-similarity algorithm or use it to support Algorithm 2 novelty.
