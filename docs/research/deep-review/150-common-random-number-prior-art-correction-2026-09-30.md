# Common-random-number prior-art correction

Updated: 2026-09-30 22:12 ET

The latest literature pass changes how Experiment 2 should be framed. Evaluating two rows on the same question is a form of **common random numbers**: the question is the shared scenario, and the row is the simulated system. This is established ranking-and-selection methodology, not a new contribution. Nelson and Matejcik explicitly combine common random numbers with indifference-zone selection and multiple-comparison control, including a conservative Bonferroni procedure ([Management Science](https://pubsonline.informs.org/doi/10.1287/mnsc.41.12.1935)). Görder and Kolonko develop Bayesian ranking and selection with correlated observations, missing data when systems have different numbers of observations, and covariance-aware adaptive allocation ([paper](https://arxiv.org/abs/1410.6782)). Common-random-number Bayesian optimization is also established ([paper](https://arxiv.org/abs/1910.09259)).

## Consequence

CRPR should not be presented as novel because it pairs questions, uses one-slot neighbors, or transfers correlation. Its cross-block residual idea is a hypothesis that must beat these established common-random-number ranking-and-selection baselines. The nearest safe baseline should be an implementation of cost-aware correlated ranking and selection with missing observations; call it **CW-CRN-R&S** in the experiment plan, not a claimed publication contribution.

## Retry-specific extension worth testing

The retry setting adds a concrete complication that the baseline papers do not automatically solve:

* one arm is a complete ordered retry row, not a single model;
* a question can stop after an accepted attempt, so later outcomes are censored by deployment behavior;
* the charge is a response-dependent whole-cell path cost, even though each model's token coefficient is known;
* the selector observes the verifier signal while answer-key correctness is held back;
* a forced-retry stress stratum and a natural early-stop stratum estimate different targets.

The next experiment should therefore test whether a **cost-weighted missing-data CRN allocator** reduces paid row-question cells per correctly selected complete row. The allocator may use paired differences and covariance estimates, but it must pay every opened complete cell, use a global error budget, and directly confirm finalists. No residual transfer across question blocks should be enabled in the first implementation. A cross-fitted transfer arm can be added only as a separately labelled ablation.

## Revised experiment decision

1. Implement CW-CRN-R&S and direct paired racing first, using the same calibration, confirmation, and final-audit blocks.
2. Include the established common-random-number Bayesian allocation baseline when its assumptions can be stated and matched.
3. Compare each method at matched realized profiling dollars and report final correctness, verifier pass, retry reach, false-pass/false-reject rates, and cold deployment cost.
4. Treat CRPR as a stress-test ablation. It earns attention only if it saves cells over CW-CRN-R&S and direct paired racing after simultaneous error control and direct confirmation.
5. If no method reliably beats the common-random-number baseline, make the paper contribution the retry-aware cost ledger, censored-reach analysis, and a careful negative result rather than forcing a new algorithm claim.

This correction makes the experiment more credible: it tests a real retry-specific resource-allocation question while removing a similarity claim that the literature already covers.

