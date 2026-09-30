# AgentTTS and combinatorial test-time allocation overlap

[AgentTTS](https://arxiv.org/html/2508.00890) searches tuples of model and
budget choices for multi-stage tasks using an LLM-guided archive and execution
feedback. It explicitly addresses interdependent allocations, verifier/fusion
behavior, and non-monotonic test-time scaling, and compares against BO, random
search, and AgentHPO.

This is a major direct prior for combinatorial workflow configuration search.
Its reported resource objective is primarily FLOPs and its search assumes
trial feedback for candidate configurations. The remaining HAPR distinction
is narrower: each trial is a complete verifier-gated retry row; later calls
may not occur, the charge is the realized API input-token ledger, the final
gold label is hidden from the verifier and search policy, and a paid
same-question hub can provide a paired residual for choosing the next row.
AgentTTS-style trial search should be a baseline, and HAPR must not claim
generic BO/random/agent-guided combinatorial search as novel.
