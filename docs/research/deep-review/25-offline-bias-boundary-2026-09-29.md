# Offline-evidence bias boundary (2026-09-29)

Research-only source audit; no experiments, traces, replays, or model calls.

Yang, Tan, and Cheung, *Best Arm Identification with Possibly Biased Offline
Data*, UAI 2025: [paper](https://proceedings.mlr.press/v286/yang25b.html), study
fixed-confidence BAI when prior/offline observations may come from a shifted
distribution. They prove that adaptive use of offline data is impossible without
some prior knowledge of the offline-to-online bias. Their LUCB-H method adds an
adaptive bias correction, matching ordinary LUCB when offline data is misleading
and improving when it is useful.

For configuration search, mentor traces, prior benchmark questions, or a learned
row-similarity embedding are offline evidence. They may be valuable for the
structured prior, but they are not direct held-out evidence. Unless a shift/bias
bound is registered, offline predictions should influence allocation only; direct
search observations and audit questions should determine elimination and the final
recommendation. A stronger method would need a bias-calibrated residual interval
or an explicit robust-mixture model, with an independent direct-evidence fallback.

