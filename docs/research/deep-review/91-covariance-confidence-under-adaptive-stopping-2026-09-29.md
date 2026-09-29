# Covariance confidence under adaptive stopping

Howard and Ramdas et al., *Sequential and Adaptive Inference Based on
Martingale Concentration*, give matrix/operator-norm confidence sequences for
covariance under bounded iid vector observations: [technical report](https://escholarship.org/content/qt63m9j4hw/qt63m9j4hw_noSplash_8ac28d660a25fee16eaca53d6b66e55a.pdf).

That result is useful as a design reference but does not directly certify our
sparse retry rows. It assumes a common covariance and bounded vectors at each
time. In our setting, a full vector of all row outcomes would require paying
the entire matrix; the observed vector changes with the selected pair, and
later attempts are censored by verifier outcomes. The common-covariance iid
assumption therefore fails unless we restrict the claim to a stationary,
fully observed stratum.

The safe implementation target is a pairwise or low-dimensional residual
confidence sequence based on predictable complete-row samples, with a
conservative union/stream budget. A point estimate of a full covariance matrix
may guide acquisition, but it cannot certify the control-variate gate after
adaptive stopping. If a matrix confidence set is desired, its sampling model,
boundedness, and missingness correction must be proved separately.
