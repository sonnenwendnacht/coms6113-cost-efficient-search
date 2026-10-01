# Runner gap before Experiment 2

Updated: 2026-09-30 23:48 ET

The existing `scripts/replay_experiment1_nine_model.py` is safe for the completed Experiment 1 rectangle, but it is not an Experiment 2 runner.

## What it already guarantees

* It validates exactly one cell for every row and question in the declared 200/200 rectangle.
* It keeps selector reward separate from held-out `final_correct`.
* It commits a selector checkpoint before attaching audit results.
* It binds replay identity to trace, metadata, selector reward, and source files.
* It supports a filtered 27-row rectangle only if a separate trace and metadata file declare exactly those rows; it must not be pointed at the old 729-row metadata while silently filtering.

## What Experiment 2 needs in a new runner

Do not overload the old replay script to reinterpret its 200 search questions. Create a separate protocol-aware runner with an immutable manifest containing:

* row subset and ordered model snapshots;
* calibration, race, confirmation, and final-audit question IDs;
* natural versus forced-retry mode and verifier version;
* the registered sparse edge panel and anchor seed;
* method list, parameters, global error level, non-inferiority margin, and practical saving threshold;
* absolute dollar caps frozen before fresh outcomes;
* model coefficients and prompt/checker hashes;
* a source digest and a checkpoint identity.

The runner must expose separate functions for `profile`, `confirm`, and `audit`. `audit` must reject any call before a frozen row and must never provide answer keys to a selector. Every paid cell needs a ledger record even when the verifier stops after the first attempt. A partial row cannot become a calibration pair or a finalist.

The first implementation should be tested on invented data only. Reuse of the old 729-row trace is appropriate for validating rectangle filtering, cost accounting, and leakage checks, but not for evidence or parameter selection.
