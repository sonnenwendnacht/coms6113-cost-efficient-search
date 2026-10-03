# Explicit row coordinates and reproducibility

The retry-row similarity relation must be defined from the configuration
content, not from the current position in a sorted list. The replay script
already decodes slash-separated IDs into explicit slot tuples for the
structured CW-PLR/CACR/SCCR methods, but the default `graph_residual_racing`
and `similarity_annealed_ucb` paths infer base-`side` digits from the integer
arm index.

That inference is safe only if configuration enumeration, model-level sorting,
and slot order are all fixed forever. Renaming a model, changing lexical
sorting, or reading a shuffled trace can silently turn a one-slot neighbor
into a two- or three-slot neighbor. A positive result under that mismatch
would be uninterpretable.

Before treating the graph method as Algorithm 2, pass one immutable
`row_slots[config_id]` mapping to every structured selector, validate that all
Cartesian combinations are represented exactly once, and record the mapping
hash in the run metadata. The Hamming graph, coordinate features, covariance
strata, and any structural prior must use those explicit tuples. This is a
reproducibility fix, not a new algorithmic contribution, and it should be
tested on a deliberately shuffled configuration list before any large replay.
