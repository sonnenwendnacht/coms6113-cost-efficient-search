# 131: Pre-registered question blocks for adaptive edges (2026-09-29)

Adaptive graph decisions can quietly bias a finite-bank mean if an edge is
opened only on questions that look cheap or easy. A safer design is to draw a
global random permutation of the registered search questions before any
outcome is observed and partition it into fixed blocks (B_1, B_2, \ldots).
At phase (t), an edge set chosen from the past may run its complete endpoint
rows on (B_t). A newly opened edge starts on a fresh block; it never chooses
questions by current reward, verifier result, or realized cost.

This gives every active edge a declared sampling design. Exact cached cells can
be reused only when the row, question, prompt version, model snapshot, and
deployment stopping rule match; reuse must be recorded as zero new search
charge rather than silently treated as a new observation. If several paths use
the same block, their residuals are correlated and a path interval must use a
joint covariance estimate or a conservative sum of widths.

The block rule does not solve outcome-dependent retry cost. It prevents question
selection bias in quality estimates, while the ledger still needs to record
the full realized cascade and the soft-versus-hard budget distinction from
notes 127 and 129. It also does not make graph edges free: direct endpoint
sampling remains the fallback when anchor reuse or residual variance does not
cover the extra calls.

No implementation or experiment is claimed by this note.
