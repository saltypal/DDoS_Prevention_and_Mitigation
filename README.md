# Multi-source DDoS detection research

Canonical source for Kaggle experiments on **NF-ToN-IoT-v3**, **NF-BoT-IoT-v3**, and **LAN-SDN-NIDS**.
Current implementation is under development; no trained public-data model or production-ready detector is claimed.

## Responsibilities

- `sdn_ddos/data`: acquisition, stable source row IDs, typed sanitation, protected splits, Parquet.
- `sdn_ddos/features`: source-native predictor contracts and identifier exclusions. NF and LAN semantics are not assumed equivalent.
- `sdn_ddos/analysis`: full-table Spark summaries and bounded development plots.
- `sdn_ddos/models`: eight Spark classifiers, four Python boosting challengers, OOF combination/gating methods.
- `sdn_ddos/evaluation`: metrics retaining benign and other-attack subgroups.
- `sdn_ddos/runtime`: run identity, logs, manifests and notebook output capture.
- `experiments/public_dataset_la`: notebook launchers, configurations, research and run records.
- Existing topology/controller modules and `experiments/topology_dataset` preserve earlier SDN work.

## Execution

Use the notebooks in `experiments/public_dataset_la/notebooks/` on Kaggle CPU with internet enabled.
Each clones this repository, resolves latest source once, records the commit and invokes installed modules.
Set `REVISION` in the notebook to an exact commit for reproduction. Never update source during a running experiment.
First run `00_modular_preflight.ipynb`, then engineering EDA, full preprocessing, and the bounded classifier pilot.
Attach the two NF sources; LAN files are acquired from the official release with checksum verification.
Attach version-specific full preparation outputs to the benchmark. Prefix smoke outputs are rejected as training inputs.

Python setup: `python -m pip install -e '.[spark,boost,notebooks]'`. Spark needs Java17+.
Scientific processing is restricted to Kaggle; local fixture checks are explicitly marked as such.
The package logs actual dependency/runtime versions; declared ranges are not an environment lock or a reproducibility claim.

Run artifacts are written to `/kaggle/working/experiments/public_dataset_la/runs/<run-id>/`.
Data, credentials, checkpoints, bulk plots/logs and predictions are excluded from Git.
See `KAGGLE_RUNS.md` for actual notebook versions/status/retrieval, and `Journal.md` for decisions and references.

## Scientific scope

Primary target: DDoS versus non-DDoS. Non-DDoS attacks remain separately identifiable and are not called benign.
Split policy fails visibly if chronological/topology partitions lose class coverage; no automatic random-split fallback.
Completed-flow detection is not an early-warning claim. Cross-source LAN scoring requires a separately verified feature contract.
Ensemble/MoE improvement, arbitrary-network generalization, live mitigation and multi-machine scalability remain unproven.

LA1 owners: Prithvi—ToN; Roydon—BoT; Satya—LAN. LA2 uses matched training inputs and reports failures and costs as well as detection scores.

## Data attribution

[NF-v3 source and methods](https://staff.itee.uq.edu.au/marius/NIDS_datasets/),
[NF-v3 temporal methods](https://arxiv.org/abs/2503.04404),
[ToN-IoT](https://research.unsw.edu.au/projects/toniot-datasets),
[BoT-IoT](https://research.unsw.edu.au/projects/bot-iot-dataset),
[LAN-SDN-NIDS](https://doi.org/10.21950/QMAXKP).
This repository publishes source code, not redistributed raw datasets; original data terms and attribution still apply.
