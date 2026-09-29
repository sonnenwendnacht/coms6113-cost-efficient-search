# Sequential RL routing overlap

[Router-R1](https://arxiv.org/html/2506.09033) casts multi-model calls as a
 sequential reinforcement-learning policy: actions select models or stop,
 rewards combine exact-match outcome with model price/token cost, and the
 number of rounds can vary. It is therefore a direct baseline for any claim
 that a cost-aware RL patchwork is new.

The outer target remains different. Router-R1 learns a runtime policy for each
incoming question; HAPR profiles a finite set of complete retry rows before
deployment and recommends one row from sparse answer-key-blind observations.
HAPR's candidate mechanism is paired residual evidence from questions that
both rows actually executed, not an RL state representation or a learned
online router. If the project later adds a sequential-RL baseline, it must
share the same profiling budget and held-out evaluation split.
