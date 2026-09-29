# Routing-gap identifiability and repeated draws

[How Much of the Routing Gap Is Real?](https://arxiv.org/html/2607.03436)
shows that a single correctness observation for each `(question, model)` is
not enough to identify a stochastic routing matrix. It recommends repeated
fresh draws and separates reproducible single-commit performance from gains
available through sampling, aggregation, or verifier recovery. Cross-model
dependence also changes the attainable oracle envelope.

This is a warning for both the mentor-style matrix view and HAPR. The current
local trace uses deterministic decoding as an explicit controlled assumption;
it must not be described as evidence that model responses are intrinsically
consistent. If the project moves to stochastic APIs, it needs repeated draws
or a noise model, and the paired confidence sequence must include label noise.
The response matrix is then a finite replay artifact, not an immutable truth.

The paper does not solve outer complete-row profiling: it studies the gap for
per-question routing and repeated draws, whereas HAPR recommends one fixed
retry row. It nevertheless must be cited whenever a matrix, deterministic
cell, or “same question gives the same answer” assumption is used.
