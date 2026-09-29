# Current selector implementation gap

A read-only audit of `src/retry_search/selection_sweep.py` shows that the
current graph-residual selector is a useful hypothesis diagnostic, but it is
not yet the full CS-BRI/HAPR protocol.

* `run_sweep` receives a complete search matrix and reports realized cell
  costs, but it has no internal hard-dollar reservation. A fraction is a cell
  count, so the realized spend can differ substantially across settings.
* `graph_residual_racing` chooses an anchor, builds same-question edge
  residuals, and can telescope them along a graph path. It reports the
  extrapolated row even when that row has no direct cells; in that case
  `selected_observed_accuracy` is `None`. This is a prediction, not a paid
  deployment observation or a certificate.
* The radius is a heuristic sample-variance expression. It is not an
  anytime-valid finite-population confidence sequence, does not account for
  simultaneous edges, and does not include reach/path strata or verifier
  calibration.
* The selector does not reserve a conservative maximum charge before opening
  a complete row, and it does not execute a fresh direct confirmation block
  before recommendation. Held-out evaluation by the caller is therefore a
  useful audit, but it does not repair a missing search-time confirmation
  contract.
* `similarity_annealed_ucb` uses Hamming-weighted same-question rewards and can
  recommend an unobserved row. This is an appropriate ablation, but it should
  be labeled a similarity predictor rather than HAPR.

The implementation can support the research comparison as a leak-free
counterfactual matrix replay. Before any paper claim of certified HAPR, add a
separate ledger-backed mode with registered blocks, complete-row action
reservations, reach-aware paired bounds, direct confirmation, and explicit
soft-cap reporting when a maximum charge is unavailable. Do not silently
reinterpret the current replay output as that stronger algorithm.
