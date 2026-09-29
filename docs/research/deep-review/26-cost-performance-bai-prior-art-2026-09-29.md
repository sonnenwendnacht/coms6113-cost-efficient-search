# Cost-performance BAI prior art (2026-09-29)

Research-only source audit; no experiments, traces, replays, or model calls.

Harding and Kandasamy, *Balancing Performance and Costs in Best Arm
Identification*, NeurIPS 2025: [paper](https://papers.nips.cc/paper_files/paper/2025/hash/b0dfe8236981ba84b4d98a7ed0426f0b-Abstract-Conference.html), define a risk objective that adds sampling cost to a penalty for recommending a suboptimal arm. They study both misidentification probability and simple regret, derive lower bounds, and propose DBCARE with near-matching polylogarithmic guarantees. This formalism avoids choosing a fixed budget or confidence level in advance.

This is directly relevant to our quality-versus-search-cost curves. A method that merely tunes a budget or reports an accuracy/cost tradeoff is not novel at the objective level. The defensible boundary is the observation structure: a paid action is a complete retry row on a question, costs are realized along checker-controlled paths, and same-question rows can be paired. Any cost-performance evaluation should include a risk-style scalar or area/utility summary in addition to the curve, and should compare against a DBCARE-like independent-arm cost-performance policy where feasible.

