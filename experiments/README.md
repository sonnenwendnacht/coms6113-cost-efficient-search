# Experiment records

Copy `run-template.json` for each actual run. Store local outputs under `results/runs/<run-id>/`; commit only reviewed summaries and metadata that contain no credentials or restricted data.

Three ledgers are required: (1) measurements purchased by the search, including initialization and failures; (2) reference construction and independent audit spending; (3) cold deployment cost and latency of each recommended configuration. Shared caches must have the same rules for every comparison method. Do not transfer an already-populated cache between methods for free.

Before live runs, fix a maximum authorized monetary budget and reserve a conservative bound for each request's input/output/checker costs. Post-hoc token estimates cannot guarantee a hard spending cap. The toy scaffold has known integer costs and does not implement a production API budget manager.
