# Candidate Algorithm 2: Cost-Weighted Control-Variate Top-Two

The current candidate name is **CW-CV-TT**. It is a gated adaptation, so a
bad similarity estimate cannot make the method claim more evidence than direct
racing.

1. **Register scouts.** Pre-register a small uniform scout block, an anchor
   candidate set, the row-slot mapping, question permutations, confidence
   shares, and the profiling budget. Execute complete rows only.
2. **Fit the pilot.** On a pilot split, estimate paired residual variance,
   anchor covariance, per-cell realized charges, and a frozen control-variate
   coefficient `beta`. Use cross-fitting when the anchor mean is not already
   known from a fully profiled block.
3. **Gate the sidecar.** For each leader/challenger pair, require the upper
   confidence bound on
   `(sqrt(c_D*v_R) + |beta|*sqrt(c_Z*v_Z))^2` to be below the lower bound on
   `c_D*v_D`, using conservative charge bounds. If it fails or its support is
   weak, use direct CW-PTT pairing.
4. **Allocate.** If the gate passes, allocate complete-row residual blocks and
   anchor-mean samples in proportion to the square roots of cost times
   variance. Keep a random direct-scout floor and charge all realized path
   costs.
5. **Stop safely.** Use a global or stream-charged confidence sequence for
   adaptively opened pairs, enforce the quality and cost objectives separately,
   and stop only when the directly observed leader beats all surviving rivals
   by the registered tolerance.
6. **Confirm.** Run an independent direct complete-row confirmation block for
   every finalist and recommend only a row whose simultaneous quality and cost
   intervals satisfy the declared objective. Otherwise report the result as
   exploratory.

The method uses configuration similarity only to decide where a complete
measurement may be unusually informative. It never reuses workflow prefixes,
fills an unexecuted retry, or recommends a row based solely on a graph
prediction. Its publishable hypothesis is an empirical cost-to-quality gain in
the gated regime, compared with CW-PTT, SySRs, independent resource-aware BAI,
and random/uniform allocation.
