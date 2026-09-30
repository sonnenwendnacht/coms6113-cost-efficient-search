# 132: PROBE proxy-assisted BAI boundary (2026-09-29)

The 2026 preprint [Best-Arm Identification with Generative
Proxy](https://arxiv.org/abs/2607.06879) introduces PROBE. It pairs each
costly reward with a cheap correlated proxy, estimates the reward-proxy
relation online, and uses a conservative residual-variance upper certificate
plus a one-round lag in phased elimination. The paper explicitly warns that a
plug-in residual variance estimate can be anti-conservative and break the
identification guarantee.

This is directly relevant to row similarity. A previously measured anchor row
can act as a proxy for a candidate row on matched questions, with the paired
residual playing the role of PROBE's control-variate residual. Our setting is
different in several ways, but these differences must be stated precisely:

* PROBE treats the proxy's marginal mean as known from offline data. An anchor
  row's mean is usually unknown and must itself be estimated from complete
  retry cells, unless it has already been paid for and certified.
* A proxy query is cheap in PROBE. Running an anchor configuration is another
  full solver/verifier/retry cascade, so row similarity only helps through
  anchor reuse or a lower residual variance that justifies fewer candidate
  cells.
* PROBE's cost is attached to a costly reward pull. Our cell charge is a
  question- and output-path-dependent sum of model input-token charges, and
  retry reach couples the charge to the observed deployment behavior.
* Our target is a finite registered question-bank mean with paired question
  blocks, while PROBE's standard model is an arm-level stochastic stream.

The defensible Algorithm 2 direction is therefore a **proxy-BAI adaptation
with an unknown, paid anchor and endogenous cell costs**, not a new idea of
using correlation. It should inherit the conservative design principle:
calibrate an upper bound on residual uncertainty, use that bound to choose the
next block, and separate the block used to calibrate the bound from the block
used to eliminate a row. A raw residual plug-in followed by elimination is not
enough for a correctness claim.

Required conceptual controls are PROBE-style residualized elimination, raw
paired elimination, direct row sampling, and a deliberately ungated graph
variant. The primary comparison must include the anchor's already-paid versus
not-paid cases. Report whether any reduction comes from amortization, lower
residual variance, or simply a weaker stopping rule.

Potential failure modes are an unknown or drifting anchor mean, residuals that
change with question difficulty, retry paths that make the proxy much more
expensive than expected, and reuse of the same questions for calibration and
elimination. No implementation or experiment is claimed by this note.
