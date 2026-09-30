# 138: Transductive probe-design boundary (2026-09-30)

Fiez et al.'s [Sequential Experimental Design for Transductive Linear
Bandits](https://proceedings.neurips.cc/paper/2019/file/8ba6c657b03fc7c8dd4dff8e45defcd2-Paper.pdf)
already studies a learner that chooses measurement probes from one set in
order to identify the best item in a separate target set. Its RAGE-style
allocation focuses on uncertainty in target differences, and its examples
include factorial layouts with interaction features. This rules out claiming
that “measure a related configuration to infer a target configuration” is new.

The useful translation for our problem is a different measurement unit:

* a node probe is one complete row/question cell ((v,q)), with reward and
  full retry charge;
* a paired probe is ((u,v,q)), which executes both complete endpoint cells
  on the same question and returns a paired residual; and
* a target is a row mean or an unresolved row difference over the registered
  question bank.

The cost of a paired probe is the charge of any endpoint cells not already in
the exact eligible cache. Thus a previously paid anchor can be shared across
many target differences, while an edge opened from scratch pays both endpoints.
This is a costed transductive design with a response-dependent measurement
price, rather than a free graph-feedback model.

A future implementation should include an XY/RAGE-style target-difference
allocation control. CG-RTE can then be viewed as a restricted, interpretable
version that limits probes to one-coordinate Hamming edges and uses residual
gates. If the unrestricted target-difference design wins at equal realized
spend, the graph restriction is not justified. If CG-RTE wins, the evidence
must show that its edge registration and anchor reuse reduce *unique* cell
charges, not merely the width of a confidence interval.

The transductive analogy also identifies a modeling risk. Linear or factorial
features can be useful for allocation, but retry feedback may make the row
mean strongly non-additive. A feature model must be cross-validated on fresh
question blocks and treated as a proposal for where to measure, not as a
replacement for complete-row confirmation. No implementation or experiment
is claimed by this note.
