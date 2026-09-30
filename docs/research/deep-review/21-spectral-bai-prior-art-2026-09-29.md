# Spectral BAI prior-art boundary (2026-09-29)

Research-only source audit; no experiments, traces, replays, or model calls.

Kocák and Garivier, *Best Arm Identification in Spectral Bandits*,
arXiv:2005.09841: [paper](https://arxiv.org/html/2005.09841), already gives a
fixed-confidence best-arm framework with a graph over arms. The means are assumed
to obey a known weighted-Laplacian smoothness constraint

`mu^T L mu <= R`,

so strongly connected arms are known to have similar means. Their SpectralTaS
strategy computes graph-constrained information-optimal allocations and uses an
adaptive Track-and-Stop rule. This establishes that a similarity graph by itself
is not a new contribution.

The result is still a useful baseline for our setting. Its assumptions use
independent arm observations with a known graph regularity set and do not model
same-question paired noise, checker-triggered retries, or realized per-cell
token charges. A model-similarity graph learned from the search data is not the
same as their fixed constraint unless its estimation uncertainty is incorporated.

Therefore, a defensible comparison should include a graph/spectral allocation
baseline when feasible, or state that the proposed method is outside SpectralTaS
because the graph is only a soft prior and costs are observed at the complete
retry-row cell level. Any novelty claim should come from combining that soft
structure with paired-question covariance and a cost-aware certificate rather
than from graph smoothness alone.

