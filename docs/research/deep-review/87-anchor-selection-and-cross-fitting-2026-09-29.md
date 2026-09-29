# Anchor selection and cross-fitting

Selecting the anchor after seeing the same residuals creates a second winner's
curse. A safe hub protocol is:

1. Pre-register a finite anchor candidate set and split the search questions
   into pilot and allocation folds.
2. Run every candidate anchor as a complete row on the pilot. Estimate
   `beta`, residual variance, covariance, and realized charge there.
3. Select an anchor for each leader/challenger pair using only pilot data, and
   freeze that choice before opening the allocation fold. Charge a fresh hub
   cell when it was not already observed.
4. Use the allocation fold for residual racing and reserve a separate direct
   confirmation fold. If a cross-fitted design is used instead, fit each
   coefficient and anchor mean without the fold on which its residual is
   scored.

If several anchors are allowed to compete, the break-even gate and confidence
budget must cover the entire candidate set. A point estimate of the best
observed anchor is not a certificate. If no anchor passes the conservative
gate, the algorithm must revert to direct CW-PTT.

This split is more expensive than reusing all cells, but it keeps the control
variate's mean and coefficient independent of the residual it is used to
certify. It also makes the source of any savings measurable: hub setup,
allocation, and final confirmation are separate ledger entries.
