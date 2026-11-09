# Project journal

## DEVELOPMENT SPLIT CORRECTION — LAN pilot evidence, 2026-11-09

LAN classifier pilot v1 stopped in matched-cohort construction before fitting because the earliest chronological third of Star development contained no DDoS. Failure evidence is preserved in experiments/public_dataset_la/runs/lan-classifier-pilot-20261109-v1/retrieved/. Primary topology partitions and Subnets final test remain fixed. Replace ONLY internal development slicing with StratifiedGroupKFold over connected components linking equal selected-feature hashes and session groups, separately per source. This provides disjoint selection/calibration/threshold groups with class-coverage checks, without claiming independent episodes or temporal independence between these internal subsets. No final-test scores were inspected to make this correction. NF primary chronology/embargo boundaries are unaffected; source data preparation jobs continue untouched.

Public source-code execution and private data products remain distinct. LAN private Dataset creation was accepted at https://www.kaggle.com/datasets/satyapaladugu/lan-sdn-nids-prepared and status reports ready; dataset reattachment/layout readback is still pending. Flat Parquet assets and a checksummed directory-layout manifest preserve native data types without creating another full local copy (payload uses hardlinks). Original LAN CC-BY-4.0 attribution retained.

---

## FULL LAN DATA READY — 2026-11-09

Pinned-source LAN preparation v1 completed at satyapaladugu/sdn-ddos-lan-preparation. All1,125,059rows persisted and verified by local Parquet FOOTER metadata (no local analytical processing);94/94manifest members match. Retained DDoS counts train4196/development999/test1632. Quarantined overlap observations remain in the product with their reason and family, rather than being silently deleted. Saved output319,250,260bytes before the extra native log/retrieval metadata; clean Parquet311,941,276bytes in32files. Verified local copy is under experiments/public_dataset_la/runs/lan-preparation-kaggle-20261109-v1/retrieved/. Available local capacity permitted this~319MBcopy. Six source-stage entries complete. Dataset layout publication remains separately verified, not inferred from notebook completion.

Updated modular prefix preflight v2 also completed,98/98artifact hashes match, Parquet footers confirm5000ToN/5000BoT/25000LANrows. Generated software-fixture model preflight completed12/12 fit/save/reload/score paths on Kaggle; no DDoS accuracy claim. Model wall times include startup and saved outputs: Spark families~30–49s each on400fixture training rows; Python challengers~2–6s. Full source ToN and BoT preparation v1 submitted independently, same pinned source27fa7ef0162a4810dfba1579f951ffa6cda26ff3. These jobs do not depend on unfinished model presentation edits.

Operational retrieval discovered Windows default-codepage failure in Kaggle CLI native-log writing. Preserved error logs, then retrieved through the same official SDK with UTF8 writes and bounded parallel downloads; no remote run was restarted. Explicit SDK version labels returned404; latest-session retrieval is therefore checked against the expected pinned Git revision and protected by not updating a notebook until retrieval finishes. Signed file URLs/credentials are not persisted.

Source now includes strict score alignment, prediction/memory diagnostics, source-specific FPR threshold guards, and artifact-based LA views. Increased proposed development cohort from30k to300k because BoT has only51,989benign observations in16.9Mtotal; a30kcohort divided three ways is inadequate for source-specific benign-FPR estimation. Exact observed counts still gate threshold fitting. Numeric transformations remain fitted inside training folds. LAN classifier pilot may run on20kmatched training observations while the two larger sources prepare; final comparison budgets remain separately reviewed and resource-pilot models cannot open final tests.

---

## EXECUTION UPDATE — verified modular Kaggle prefix preflight

Actual stable identity: https://www.kaggle.com/code/satyapaladugu/sdn-ddos-modular-prefix-preflight , version1, pinned commit9214fee8e09c6414df63b9e659cdb592622459e4. Completed and retrieved;94/94 manifest entries verified, no failed hashes. Typed prefix Parquet readback counts: ToN5000, BoT5000, LAN25000 (five5000-row source prefixes). Runtime: Python3.13.18,4CPUs, Spark4.0.1; all17recorded stages complete. Prefix scope includes heavily quarantined chronology boundaries and does not establish viable full-source splits or classifier accuracy.

Core runtime package constraints now use the versions actually observed in this preflight; full dependency resolution remains recorded per run. Full NF source SHA256 pins copied from verified source-input manifests into configuration. Retrieved evidence: experiments/public_dataset_la/runs/modular-kaggle-preflight-20261109-v1/retrieved/verification_summary.json. Native kernel log returned zero bytes; incremental cell/module logs and executed-cell notebook provide tested evidence. Do not promise unavailable bootstrap stdout capture.

Luna's bounded review confirmed an extra-score-ID integrity gap and flagged diversity correlations depending on physical row order. Accepted both: shared strict score/cohort identity validation now rejects extras/missing/duplicates and all diversity inputs align by row_id. A new regression fixture covers shuffled and wrong/extra rows. Local contract checks now6/6pass. Current new modules include OOF ensemble/domain-MoE orchestration, trusted bundle inference, frozen base/combination evaluation, and LA1/LA2 artifact views; these new model paths remain unexecuted on real datasets. Source-specific preparation launchers share one implementation and permit independent recoverable runs. Old inline EDA builder retired; its original source remains in Git history.

Luna operational monitoring hit its account usage limit after retrieving preflight evidence. Main thread performs the remaining bounded operational checks directly; no alternative subagent/provider was invoked. Next runs: updated pinned source smoke, generated model-contract preflight (no accuracy evidence), and independently saved full-source preparation after runtime checks. Full preparation must stop visibly on class/overlap/quarantine problems.

---

## EXECUTION — 2026-11-09: modular Kaggle pipeline begins

User explicitly authorized direct implementation and completion of the dataset, classifier, ensemble/MoE and LA1/LA2 work. Earlier MiMo attempts produced no deliverables; direct Codex implementation is now active. User approved a PUBLIC SOURCE-ONLY repository and explicitly selected authenticated GitHub owner saltypal after API identity verification. Repository: https://github.com/saltypal/DDoS_Prevention_and_Mitigation . Source/data separation is enforced by .gitignore; bulk runs, data and captured paper text are not published.

Implemented initial modular acquisition, chunked stable-row ingestion, native feature contracts, binary-target audits, numeric sanitation, chronology/topology partitions with conflict/overlap quarantine, typed Parquet readback checks, development-only plots, incremental runtime/cell capture, eight Spark/four Python classifier adapters, isolated bounded fitting, matched cohort construction and development metrics. Initial ensemble/gating primitives exist; experiment orchestration and final inference qualification remain pending. Initial benchmark budget50k training rows/condition and30k development rows is a RESOURCE PILOT, not a final full-scale result. No final test is read by candidate selection. Data methods fail visibly on lost class coverage; no silent random splitting.

Generated thin GitHub-backed Kaggle notebooks for prefix preflight, engineering EDA, preprocessing and classifier pilot. Original inline EDA prototype preserved under ignored run evidence. Dependency ranges are provisional; remote preflight must verify Java17+, Spark and managed Python before full jobs. Local synthetic contract checks passed5/5, plus nbformat/AST checks on4notebooks; Luna recorded source hashes and logs under experiments/public_dataset_la/runs/modular-preflight-20261109/logs/. These checks establish no public-data accuracy or remote runtime success.

Next gate is a pinned-source private Kaggle CPU prefix preflight on both NF mounts and the official five LAN files. Verify persisted artifacts and resolve any JVM/data issues before full preparation/training. All later LA1/LA2 presentation results must reference actual saved runs; unexecuted stages are not results.

---

## CURRENT ARCHITECTURE — 2026-11-09: modular repository and Kaggle orchestration

User now requests one modular canonical codebase published to GitHub, fetched/cloned by Kaggle notebooks, with notebooks invoking modules. This supersedes earlier requirements for substantial inline notebook implementations. Keep explanations, configuration, plots and interpretation visible in notebooks; move reusable scientific logic into the existing sdn_ddos package. The newly created engineering EDA notebook is an initial inline prototype, not yet refactored into this architecture or executed on Kaggle.

Preserve existing sdn_ddos topology.py, manifest.py and controller_launcher.py. Proposed package additions: data/ (sources, schemas, labels, quality, splits, preprocessing, artifacts); features/ (native, common contract, derivatives); analysis/ (profiles, plots); models/ (Spark and Python adapters, selection, ensemble, moe); evaluation/ (metrics, calibration, crossover); runtime/ (environment, logging, provenance). Each stage accepts explicit configuration/input artifact manifests and returns saved output manifests. Experiment-specific notebooks, configs, launch scripts and results remain under experiments/public_dataset_la; topology experiments remain under experiments/topology_dataset. Mitigation is a later scoped addition, not an implemented capability.

GitHub holds source, dependencies, small configuration and documentation. Raw datasets, Parquet, checkpoints, predictions, bulky figures/logs, caches and credentials are excluded from Git. Kaggle mounts data, clones the source repository to a disposable checkout outside /kaggle/working, resolves a selected latest revision once, records/checks out that exact commit, installs the package into the active kernel and runs modules in stage order. Source must not change mid-run; a resume uses the recorded commit and compatible input artifacts. Results persist under /kaggle/working/experiments/<experiment>/runs/<run-id> and versioned saved outputs/private Kaggle datasets. Maintain KAGGLE_RUNS.md.

Read-only verification in this turn: canonical folder contains no .git repository and git remote -v cannot resolve a remote. GitHub CLI was not found on PATH. GitHub publishing has not occurred. Repository owner/name and authenticated publishing route must be established before the first push; do not invent a remote or expose local data. Next design increment: convert the EDA slice to source acquisition/profiling/logging modules and a thin notebook, then implement preprocessing after split contracts pass review.

---

## CURRENT PLAN — 2026-11-09: Kaggle data finalization, selected ensembles and MoE

This entry supersedes the fixed nine-model portfolio, predetermined LR/RF/GBT stack, model-based team assignments and deferred-MoE-only decisions below. User requested research/planning and a detailed MiMo implementation brief before implementation. No preparation/training job or new Kaggle Dataset was launched in this turn.

Implementation contract: [IMPLEMENTATION_BRIEF_MIMO.md](experiments/public_dataset_la/IMPLEMENTATION_BRIEF_MIMO.md). Canonical notebook/run ledger remains KAGGLE_RUNS.md. Implementation uses one OpenCode MiMo v2.6 worker; Codex reviews. Only Luna High Codex subagents may be used for operational/testing work. Optional Sol Medium assessment is limited to five minutes if used; it is not an implementation owner. No model switch occurred during this planning turn.

### Dataset ownership and execution

- Prithvi: NF-ToN-IoT-v3. Roydon: NF-BoT-IoT-v3. Satya: LAN-SDN-NIDS.
- All data computation, EDA, preprocessing, training and evaluation execute on Kaggle. Versioned source remains local in the canonical repository. Kaggle saves reports, plots, typed cleaned observational Parquet, split/group manifests, model-ready Parquet, train-fitted transformers, models and predictions. Preparation is pending; investigated public sources are not newly generated data.
- First create an engineering EDA notebook and a separate engineering preprocessing notebook, each covering all three datasets. Reuse stable notebook identities across revisions. After evidence and methodology review, distill into three standalone LA1 notebooks by dataset owner. LA1 includes dataset/testbed explanation, EDA, at least five substantive plots each, exclusions, labels, split decisions, preprocessing, derivatives, finalization and artifact provenance. LA2 subsequently loads finalized artifacts for classifier experiments; OOF training still refits transformations within each fold.
- Preserve natural test distributions and original attack families. Primary target DDoS versus non-DDoS; other attacks are non-DDoS, not benign. No blanket outlier deletion/SMOTE. Median imputation and missing flags are training-fitted defaults subject to semantic audit; rate nonfinites require explicit handling. Trees and scaled models use distinct appropriate transformations. Default LAN excludes new_mac_ratio until implementation ambiguity is resolved.
- Use five raw LAN topology CSVs; consolidated Parquet is reference only. Normalize missingness to verify row-level lineage before declaring equivalence. Keep chronology, capture IDs and endpoints as split/audit metadata. Freeze held-out groups before model-selection EDA. Purge feature duplicates across partitions and quarantine contradictory binary-label groups with counts. LAN train Linear/Tree/Mesh, development Star, final Subnets; NF chronology/episode splits depend on verified coverage, with limitations disclosed.
- ToN and BoT can share a NetFlow feature contract. LAN compatibility requires separate semantic verification of observation unit, direction, units, timeouts and aggregation. No absent telemetry fabricated as zeros. Full crossover/MoE involving LAN is conditional on that gate; otherwise NF crossover/MoE and native LAN are reported separately.

### Revised models and fair comparison

Twelve candidate families, each trained in four conditions (ToN,BoT,ToN+BoT,LAN): Spark LR, Decision Tree, Random Forest, GBT, Gaussian Naive Bayes, LinearSVC, MLP, FM; Python HistGradientBoosting, XGBoost, LightGBM, CatBoost. Thus48 base condition/family configurations before tuning/refits, subject to documented runtime feasibility. This is a finite portfolio, not a promise to train every available algorithm. Eight Spark families preserve the Big Data requirement; Python challengers use the same bounded row cohorts and cannot collect the full44M NF rows into driver RAM.

Resource preflight determines common training budget; same row IDs within each condition, equal total training size for ToN/BoT/mixture comparisons. Initial search cap is five development configurations/family after smoke, with run-specific time/memory limits recorded before launch. Failures/timeouts remain in the report. Additional full-scale champion runs are separately labeled.

Select up to four complementary models using grouped OOF predictions, development PR-AUC, recall at stated benign false-alarm rates, source/family failure patterns, calibration and cost. Compare best single, equal probability mean, nonnegative weighted mean and regularized LR stack. No predetermined three winners. MoE uses compatible domain specialists and optional pooled generalist plus a small feature-driven softmax gate trained on OOF expert probabilities via detection loss. Dataset identity is neither runtime gate feature nor gate target. Compare dense mixture and top-2 conditional execution against static averaging of the same experts; report gate utilization/collapse, off-domain failures and dispatch costs. Dense mixture has no inference compute-saving claim.

Cross-source scores require common-contract refits; native LAN models cannot accept raw NF rows. Separate known-source mixture testing from leave-one-source-out evaluation, in which destination data is excluded from ALL training, transformations, gate selection, calibration and tuning. Freeze final choices before final-test scoring. Best-ever/any-network claims are unsupported; report Pareto trade-offs and residual failures. Graph and mitigation/RL remain later stages.

### Inspected literature and exact inspiration

Research used alphaXiv discovery and relevant PDF pages plus primary web documentation. This is a bounded review, not an exhaustive survey. Evidence excerpts for the three deeper method reads are under experiments/public_dataset_la/research/20261109/.

| Reference | Inspected evidence and relevant limitation | Project decision inspired |
|---|---|---|
| [BRIDGE and TCH-Net (2026)](https://arxiv.org/abs/2604.11324) | Relevant feature-alignment/method pages: semantic vocabulary, feature coverage, leave-one-dataset-out testing; also zero-fills missing features and uses provenance embeddings. Its pooled and LODO claims must not be conflated; no replication performed here. | Explicit feature-equivalence/coverage registry and held-out-source evaluation. We do not adopt provenance IDs as detection/router predictors or assume zero filling establishes compatibility. |
| [Exploring Robust Intrusion Detection: Feature Transferability (2026)](https://arxiv.org/abs/2602.23874) | Methods/results pages inspected: source-to-target evaluation without target adaptation, training normalization reused on target, extractor-specific behavior. Task is botnet/intrusion detection, not our exact DDoS target. | Source-by-target matrix, semantic extractor checks, source-only transforms and threshold policy; no transferring paper scores to our data. |
| [Enhanced Multi-Class DDoS Attack Identification using a Meta-Learning Ensemble (2026)](https://arxiv.org/abs/2607.16521) | Relevant methods/evaluation pages inspected: LSTM/KNN/RF with LR meta-model; balanced CIC subset and SDN experiment. Generic algorithm trains base models then predicts for meta learning; leakage-safe grouped OOF is not established by that pseudocode. | Compare heterogeneous stacking against simpler combinations. Use explicit grouped OOF instead of copying its training sequence; do not copy its models or imply its multiclass results validate our binary/cross-source setup. |
| [Sparsely-Gated Mixture-of-Experts (2017)](https://arxiv.org/abs/1701.06538) | Relevant gating and efficiency sections inspected: softmax/top-k expert selection, load and small-batch issues. Demonstrated on language tasks, not DDoS. | Compare dense and sparse routing; measure expert collapse and dispatch cost. Our frozen tabular specialist gate is an adaptation, not reproduction or a new invention of MoE. |
| [Why tree models outperform deep learning on typical tabular data (2022)](https://papers.neurips.cc/paper_files/paper/2022/hash/0378c7692da36807bdec87ab043cdadc-Abstract-Datasets_and_Benchmarks.html) | Primary benchmark abstract inspected; full experimental tables not newly audited. Medium-size tabular benchmark does not establish dominance on these network datasets. | Include strong boosted-tree challengers alongside MLP and simple models; do not assume sophistication or neural architecture means better detection. |
| [When Do Neural Nets Outperform Boosted Trees? (2023)](https://proceedings.neurips.cc/paper_files/paper/2023/hash/f06d5ebd4ff40b40dd97e30cee632123-Abstract-Datasets_and_Benchmarks.html) | Primary abstract inspected: algorithm rankings depend on data and tuning. No claim of exact performance for our cohort. | Match development/search budgets and select by measured validation trade-offs rather than paper rank. |
| [NF-v3 methods](https://arxiv.org/abs/2503.04404), [official NF releases](https://staff.itee.uq.edu.au/marius/NIDS_datasets/), [LAN release](https://doi.org/10.21950/QMAXKP) | Previously inspected source/extractor architecture and actual release audits remain baseline; measured row counts override inconsistent website totals. | Preserve source lineage, raw LAN missingness, dictionary/units and actual capture architecture; do not call every chosen dataset OpenFlow telemetry. |

Additional discovered papers not read in depth are leads only: [OmniTabBench](https://arxiv.org/abs/2604.06814), [Evaluating Tabular Representation Learning for NIDS](https://arxiv.org/abs/2605.02519). No design/performance claim depends on them. Exact generic DDoS-MoE title search had no match; foundational MoE inspiration is not evidence that no DDoS-MoE prior work exists. No novelty claim is made.

### Persistence, actual limits and next gate

[Kaggle notebook documentation](https://www.kaggle.com/docs/notebooks) currently describes20GB saved output; [dataset documentation](https://www.kaggle.com/docs/datasets) supports Notebook outputs as a dataset source. Verify runtime quota and supported authenticated publication route before bulk preparation. Saved /kaggle/working files alone are not verified persistence: require completed version, readback and downstream reattachment. Keep private outputs and verify source redistribution terms. Remote publication mechanism is not yet exercised for these prepared tables.

Local D: free space measured9,644,056,576bytes on2026-11-09; do not assume room for raw CSVs or all transformed copies. Retain at least5GiB free; automatic optional Parquet retrieval limited to2GiB and gated by compressed/uncompressed manifests plus temporary extraction space. Otherwise keep remote data and retrieve compact evidence.

OpenCode observed version2.0.16, stored Console Personal authentication, catalog model opencode/mimo-v2.6-flash-free. Inference access not probed; intended MiMo variant must be resolved before implementation if user meant a distinct model. No fallback provider or paid use authorized. Next action: confirm exact variant if needed, bounded worker preflight, implement reviewed engineering EDA/preprocessing vertical slice, remote smoke/persistence check, then full preparation and three LA1 notebooks. Benchmark/MoE implementation follows data-method acceptance. No old two-day schedule is assumed still achievable; ETA depends on run feasibility and account limits.

---

Project: SDN DDoS Detection and Mitigation with Big Data Analytics.
Setup decision: 2026-11-07, Asia/Calcutta.
Dataset delivery budget: the user requested two days on 2026-11-07, giving a calendar target of 2026-11-09 in Asia/Calcutta. The exact cutoff time was not supplied. Preparation and retries consume this budget; record the actual cutoff and remaining time before launch.
Current milestone: finalized dataset design and collection configuration.
Execution status: implementation started. Mininet construction and bounded WSL T1 ICMP forwarding passed. Kaggle capability preflight version 1 completed and artifacts were retrieved. The tested hosted image blocks native namespace/OVS capture; QEMU TCG feasibility, collectors and workload mechanisms remain pending.

## 1. Source of truth and how to use this journal

The canonical project is `D:\Bunker\BaseCamp\WirelessCommunication\DDoS_Prevention_and_Mitigation`.
The earlier project at `D:\Bunker\BaseCamp\WirelessCommunication\DDoS_Prevention` supplies reference notebooks, models and reusable source.

- [DATASET_PLAN.md](DATASET_PLAN.md) is the detailed scientific and collection plan.
- [dataset_v1.json](experiments/topology_dataset/configs/dataset_v1.json) is the finalized design configuration. It contains exact graphs, labels, timing, seeds, paths, target environments and artifact requirements.
- This journal records decisions, reference attribution, execution sequence, evidence, deviations and remaining work.
- [KAGGLE_RUNS.md](KAGGLE_RUNS.md) records notebook identities, versions, run IDs, logs, saved outputs and verified retrieval.

The configuration is a design contract. Before capture, preflight must produce a resolved configuration containing the actual environment lock, selected backend, measured capacity, source hash and accepted collector settings. Every run references both the design configuration hash and its resolved configuration hash.

Update this journal at completed milestones, consequential changes and failures. Each execution entry must include date/time, source/config identity, command or notebook/version, actual hardware, outcome, artifact paths, limitations and next action. A planned path remains marked planned until the file is found and verified.

## 2. Objective and contribution

Deliver measured SDN traffic and telemetry across four network structures, with the same nominal switch/host counts and common application roles. Add a controlled path-length experiment. Release independent evaluation groups, raw evidence, causal feature definitions and quality checks so that later ML results can be assessed on unseen network conditions.

The proposed contribution is controlled topology transfer plus a separate hop/propagation comparison with concurrent legitimate traffic and traceable labels. These are project hypotheses. Research usefulness and publication novelty require results and comparison to prior work.

The dataset milestone includes a small baseline check. Subsequent milestones retain the original LA1 analyses, the nine LA2 algorithms, Spark/Python processing, and the three-person division. Kafka, streaming detection and live mitigation follow dataset acceptance.

## 3. Which design element comes from which source

Attribution types distinguish adopted mechanisms, adaptations, gaps that motivate our evaluation, and experiments proposed by this project. None of these citations imply that we reproduced the source's results.

| Design element | Source IDs | Relationship and decision |
|---|---|---|
| Headquarters, branch-like traffic, DMZ and private-service roles | R01 | Adapt the enterprise campus separation of access, aggregation, services and perimeter. The benchmark uses logical service zones on fixed attachment switches. |
| Redundant two-spine switching fabric | R02, R03, R10 | Adapt established Clos/leaf-spine ideas. Release the exact seven-switch graph and call it a two-spine fabric. |
| Multiple SDN topology families | R04, R05, R06 | Adopt established multi-topology collection practice. Four families are chosen for budget and structural coverage. |
| Fixed provisioned switch/host counts across families | R05 | Our control addresses a limitation observed in the closest release, where topology and network size vary together. Link counts and active forwarding footprints still differ and are reported. |
| Whole-topology evaluation holdouts | R05, R06 | Our evaluation protocol addresses generalization that the inspected closest evaluations did not establish. This is an adaptation of standard held-out-domain testing. |
| Three-versus-six-switch paths in one ring | Project proposal, informed by R05/R06 | A separate intervention keeps the graph and endpoints fixed. It does not create extra topology families. |
| Natural and matched propagation settings | Project proposal, informed by R02/R11 | Separate configured propagation effects from extra forwarding stages. Verify actual latency. |
| Packet capture plus flow features and rich benign workloads | R07, R08 | Adapt capture/provenance principles. Early features use only information available by their recorded ready-at time. |
| Synchronized OpenFlow/control context | R04, R05 | Adopt combined switch/controller observations with explicit request/reply identities and telemetry age. |
| Same measurement location and rules for benign/attack observations | R09 | Our control responds to a measurement-location difference found in the inspected HLD methodology. |
| Low-rate application traffic and measured service effects | R06, R10 | Adapt the motivation for collecting connection/resource pressure alongside packet volume. A 60-second active episode has a declared bounded duration. |
| Parameterized bandwidth, delay and workload intensity | R11 | Adapt configurable testbed settings. Their availability alone is established prior work. |
| Additional random-graph families | R12 | Studied as an alternative; retained as a future graph-seed extension after the initial release. |
| Kafka ingestion and Spark processing | R13 | Architectural inspiration for the later streaming stage. Component throughput, classifier accuracy and mitigation efficacy need separate measurements. |
| Existing thirteen labels, legacy feature names, team analyses and nine models | R14 | Preserve the project baseline through explicit schema mappings and fresh measured-data evaluation. |

## 4. Finalized network and workload setup

### Four network families

All families provision s1-s7, one Ryu controller and sixteen traffic hosts. Four hosts attach to each of s4-s7. The exact edge lists are in the configuration.

| ID | Family | Inter-switch links | Shortest anchor switch hops | Experimental role |
|---|---|---:|---|---|
| T1 | Star/campus baseline | 6 | 3 | Central aggregation |
| T2 | Balanced hierarchical tree | 6 | 3 or 5 | Hierarchy and longer paths |
| T3 | Ring | 7 | 2, 3 or 4 | Cyclic connectivity and alternate paths |
| T4 | Two-spine fabric | 10 | 3 | Redundant aggregation paths |

A switch hop counts every forwarding switch traversed, including both attachment switches. Record actual paths and active forwarding footprints. Some provisioned switches may carry no workload traffic on a selected route. Matching provisioned size does not make these equal-cost networks.

| Anchor | Four traffic-host roles |
|---|---|
| s4 | Two external clients and two multi-protocol lab reflectors |
| s5 | Four enterprise clients with HQ/branch-like access profiles |
| s6 | Public web proxy, public DNS, protocol-test target, legitimate probe |
| s7 | Two application servers, internal DNS/NTP, database |

Use OpenFlow 1.3, explicit loop-free paths and consistent reverse paths. A stable flow hash selects the fabric spine. Apply declared service/zone rules and explicit neighbor resolution. Verify the paths with traffic and switch evidence. Use the same forwarding profile for benign and attack cases.

### Network settings

Requested target bottleneck C is 1 Mbit/s. Transit capacity is 10C and ordinary access capacity is at least 2C. Host access delay is 1 ms and the main experiment uses 1 ms per inter-switch edge. The target queue limit is 100 packets.

The low and high packet-volume bands target total offered load of 0.6C and 1.2C. Connection/request workloads use the same factors against a declared service-capacity reference, with their own units. Preflight measures actual rates, CPU pressure, latency and collector overhead. A sustainable lower C may be selected once before main collection and recorded in the resolved configuration.

Freeze one shared capacity reference per workload on T1 and use it across all topologies. Connection workloads use the instrumented service's configured concurrent-request limit. Rate-capacity references require at least 99% successful completions and achieved rate at least 95% of offered rate over a 30-second check. Record the reference value, units, criterion, service-configuration hash, resource state and attempted/achieved rates. Ordinary background takes 0.2 of the reference and scenario traffic adds 0.4 at low load or 1.0 at high load. BENIGN uses legitimate scenario traffic. Recalibrating the offered load separately for each topology would change the experiment.

### Thirteen-class catalogue

`BENIGN`, `UDP_FLOOD`, `ICMP_FLOOD`, `TCP_SYN_FLOOD`, `TCP_ACK_FLOOD`, `TCP_RST_FLOOD`, `HTTP_FLOOD`, `SLOW_HTTP`, `DNS_AMPLIFICATION`, `NTP_AMPLIFICATION`, `SSDP_AMPLIFICATION`, `UDP_AMPLIFICATION`, `MIXED_DDOS`.

BENIGN includes normal HTTP, bulk transfer, DNS/UDP/ICMP, slow clients, connection churn and legitimate flash crowds. Attack episodes retain legitimate probes and background traffic. Rotate eligible attacker hosts independently of topology and retain the actual source assignments.

Verify each mechanism from observed traffic and generator/service logs. Reflection/amplification needs an actual reflector request/response path and measured amplification. Protocol fixtures identify themselves. MIXED_DDOS retains all observed component labels. An attack attempt and its actual service impact are separate ground-truth fields.

### Collection matrix

| Component | Matrix | Episodes | Scheduled episode time |
|---|---|---:|---:|
| Main dataset | 4 families x 13 labels x 2 load bands x 3 workload seeds | 312 | 10.4 h |
| Path experiment | 3 conditions x 2 paths x 2 propagation modes x 3 seeds | 36 | 1.2 h |
| Total | | 348 | 11.6 h |

Each episode has 30 baseline seconds, 60 scenario seconds and 30 recovery seconds. Nominal observation cadence is one second, with actual elapsed times retained. Seeds are 101, 202 and 303. Shuffle scenario/load order inside topology/seed blocks. Resume from completed episode boundaries and preserve incomplete attempts separately.

The scenario phases provide 83,520 planned anchor-window opportunities. Baseline and recovery observation raises the all-phase total to 167,040. These are counts of scheduled opportunities, before missingness or rejection. Flow-prefix table counts may differ. Replicated global controller context is correlated evidence.

### Path experiment

Use T3, source anchor s4 and victim anchor s6. The short route is `[s4,s5,s6]`; the long route is `[s4,s3,s2,s1,s7,s6]`. Test legitimate flash crowd (label BENIGN), UDP_FLOOD and TCP_SYN_FLOOD at the high load band.

Natural propagation uses 1 ms per inter-switch edge. Matched propagation allocates 8 ms total to the inter-switch path, giving 4 ms per edge on the short path and 1.6 ms on the long path. Access delays and the target bottleneck stay fixed. Under load, queueing/processing effects are measured outcomes.

Reproducibly shuffle the four path/propagation cells within each workload/seed block. Derive the ordering seed from SHA256 of configuration ID, workload seed and condition, and use Python's random generator. Reset between cells and preserve the paired-realization ID, planned order and actual order.

The exact ordering payload is `[config_id, integer_workload_seed, condition_string]`, serialized with ASCII escaping and compact JSON separators, then encoded as UTF-8. The first eight SHA256 digest bytes become an unsigned big-endian seed for `random.Random`. The initial cell order is short/natural, short/matched, long/natural, long/matched. Record Python version and the generated order. Randomization reduces condition-order confounding with runtime drift.

## 5. Features, labels and evaluation

The primary unit is an ingress/service/anchor window. Also retain flow-prefix/window observations and switch-port/controller tables. Label each relevant entity using observed traffic and sidecar ground truth. Unrelated legitimate flows keep their benign label during an attack episode.

| Legacy fields | Final measurement rule |
|---|---|
| `timestamp_utc`, `experiment_id`, `window_id`, `window_seconds` | Real timestamps, unique run/window identities, actual monotonic interval |
| `switch_id`, `src_host`, `dst_host`, `protocol`, `application` | Observed or registered context, with aggregate/multi-source values declared |
| `packet_count`, `byte_count`, `flow_count` | Matching directional packet/byte scope and distinct five-tuples; separate rule counts |
| `packet_rate`, `byte_rate`, `flow_rate`, `mean_packet_size` | Matching counters divided by the actual interval or packet count |
| `tcp_syn_count`, `tcp_ack_count`, `tcp_rst_count` | Parsed TCP flag bits at the declared observation scope |
| `tcp_handshake_completion_ratio` | Matched connection cohorts over a trailing 10 seconds, with incomplete/censored state |
| `flow_table_size`, `packet_in_count` | Observed table entries and controller events with epoch/reset handling |
| `controller_cpu_proxy_pct` | Deprecated compatibility alias to measured `controller_cpu_pct`; the convention allows more than 100% for multiple logical cores |
| `attack_intensity`, `attacker_count`, `background_traffic_level` | Experiment/ground-truth metadata, excluded from baseline model inputs |
| `label`, `attack_family`, `data_source` | Targets and provenance, stored separately from predictor inputs |

Attempt the existing forty LA2 behavioral feature definitions with verified sensors. Core groups cover counts/rates, packet-size/IAT summaries, TCP state, cardinality/entropy, rule churn, Packet-In activity, CPU, queue drops and utilization. Keep missing sensors as null with a reason. Publish units, formulas, observation keys, visibility limits, actual sample intervals and ready-at times. Corrected definitions receive explicit schema mappings and require retraining.

Raw evidence includes continuous telemetry, packet-derived sufficient statistics, generator/server logs and ground-truth sidecars. Retain a ten-second victim header capture per episode, beginning in the scenario phase, with 160-byte snaplen and original wire lengths. Capture health records truncation and unsupported headers. This supports reference checking over retained intervals; recomputation outside those intervals depends on the retained sufficient statistics.

Paired workload realizations remain in consistent partitions. Seed 101 supplies training, 202 development and 303 test groups. For each topology fold, fit on the other three families' training groups, tune on their development groups, and evaluate on the held-out family's seed-303 groups. Same-family seed-303 results are a separate reference. Held-out-family seed-101/202 records remain released with explicit eligibility flags.

The primary prediction claim for the hop intervention uses seed 303. Other hop groups support declared development or physical-measurement analyses. The three realizations give limited independent coverage and do not support strong variance claims across arbitrary networks.

Exclude identifiers, timing identities, topology/route IDs, raw endpoint/port identities, scenario constants, generator parameters, oracle attack shares and targets from the primary baseline. A balanced derived view can sample within assigned partitions. Retain the observed class distribution in the canonical data.

## 6. Runtime and project structure

WSL supplies local correctness pilots. Full generation targets Kaggle CPU, with native Mininet/OVS tried first and a QEMU TCG Linux guest as the second route. The hosted path still needs verification.

| Component | Target and freeze rule |
|---|---|
| Controller | Python 3.11, Ryu 4.34, setuptools 57.5.0, compatible Eventlet below 0.37, inspected launcher compatibility shim |
| Capture | System Python with Mininet 2.3.0 and compatible OVS; record actual installed versions |
| Guest route | Ubuntu 24.04 LTS candidate, requested 2 vCPUs/4 GiB, isolated workload network; hash the actual prepared image |
| Analytics | Python 3.12, Java 17, PySpark 4.2.0, NumPy 1.26.4, Pandas 2.2.3, PyArrow 19.0.1, scikit-learn 1.6.1 |
| Environment lock | Resolve patch versions, package inventory, kernel/image hash and actual backend during preflight |

The research checkpoint found Mininet/OVS available in WSL, with OVS already active. Ryu and QEMU were absent from the probed environment. Kaggle CLI read access worked as `satyapaladugu`. These observations must be refreshed before launch.

Reusable implementation belongs in `sdn_ddos/` and `analytics/bda/`. Experimental configuration, notebooks and run artifacts belong under `experiments/topology_dataset/`. Historical source remains a reference; runtime bundles are revision/hash-pinned copies of this canonical project. Source/environment preparation and result storage are separate.

Planned notebook sources are `experiments/topology_dataset/notebooks/01_kaggle_capture.ipynb` and `02_kaggle_dataset_build.ipynb`. Their planned stable identities are recorded in the run map. The user's earlier Kaggle CLI instruction selects the initial submission method for this scope.

Every setup/computational cell reports purpose, inputs, progress, destination, elapsed time and outcome. Persist executed notebooks, stdout/stderr/errors, metrics and rich outputs as far as the platform exposes them. Save incremental cell logs and per-episode checkpoints before long runs. Preserve failures and document capture gaps.

Write runtime outputs under `/kaggle/working/experiments/topology_dataset/runs/<run-id>/` and retrieve them into the matching local experiment hierarchy. Verify version-specific outputs and hashes after each batch. Target a 12 GiB saved bundle and a 20-hour collection envelope including overhead/retrieval. Actual measurements decide whether the envelope is achievable.

## 7. Work from this point onward

All task states below describe the current setup checkpoint. T0 is the start of the dataset work window. Record its actual timestamp and reconcile this nominal schedule with the time remaining to the user's deadline.

| ID | Planned work | State | Acceptance evidence |
|---|---|---|---|
| P00 | Journal, configuration, detailed plan and run map | Complete | Consistent references, graphs, seeds and counts |
| P01 | Environment/bootstrap and minimal WSL traffic pilot | In progress; ICMP forwarding passed | Finish telemetry/reference checks and environment lock |
| P02 | Native or guest Kaggle capability pilot | Pending | Actual hosted traffic plus saved and locally verified artifact |
| P03 | Four topology builders and service/zone policies | Pending | Exact graph/attachment checks, route evidence, permitted/denied traffic checks |
| P04 | Benign generators and thirteen attack mechanisms | Pending | Observed mechanism, concurrent legitimate probes and labeling reconciliation |
| P05 | Packet/flow/controller/resource collectors | Pending | Counter/flag/rate reference checks, missing/reset handling, measured overhead |
| P06 | Freeze resolved collection protocol | Pending | Pilot-derived capacity, source/config/image hashes and predicted completion budget |
| P07 | Capture T1-T4 and path intervention | Pending | Completed episode manifests, checkpoints, raw evidence and per-batch retrieval |
| P08 | Spark quality checks and dataset construction | Pending | Parquet/CSV, legacy mapping, feature registry, duplicate/missingness report |
| P09 | Split manifests and small baseline check | Pending | Independent groups, feature exclusions, reconstructed metrics and reload check |
| P10 | Freeze and package dataset release | Pending | Actual counts, artifact map, hashes, executed notebooks and reproducibility instructions |
| P11 | Regenerate LA1 and execute full LA2 suite | After dataset acceptance | Fresh outputs, same team assignments and shared comparison rows |
| P12 | External dataset comparison | After dataset acceptance | Semantic/unit/label compatibility report before frozen-model evaluation or retraining |
| P13 | Kafka and Spark Structured Streaming | Later system increment | Replay, buffering, backpressure, checkpoints and recovery evidence |
| P14 | Bounded live mitigation | Later system increment | Rule expiry/rollback, attack suppression, legitimate-service protection and recovery |

| Elapsed time | Main milestones |
|---|---|
| T0 to T0+4 h | P01-P02 runtime and retrieval gate |
| T0+4 to T0+10 h | P03-P06 graph, mechanism, measurement and configuration gates |
| T0+10 to T0+30 h | P07 collection and retrieval |
| T0+30 to T0+40 h | P08-P09 Spark build and baseline checks |
| T0+40 to T0+48 h | P10 targeted recovery, packaging and delivery |

If a gate fails, retain evidence, diagnose and retry only the affected path with a distinct attempt identity. A reduced-duration protocol or changed execution host is a recorded plan revision. The current design does not establish that Kaggle capability and all class implementations can be completed within the deadline.

## 8. Coursework and later system stages

| Member | LA1 analytical focus | LA2 algorithms |
|---|---|---|
| Satya | Class/family/protocol/service overview | Logistic Regression, Decision Tree, Random Forest |
| Roydon | Traffic distributions, rates, TCP behavior, packet sizes and correlations | KNN, Extra Trees, Histogram Gradient Boosting |
| Prithvi | Switch/controller/flow-table/victim telemetry | Gaussian Naive Bayes, MLP, RBF SVM |

Preserve the five current LA1 plot purposes per member and the current LA2 analytical sections, including preprocessing, candidate selection, class errors, runtime, feature relevance, scores and saved-model inference. Replace stale data-dependent titles and interpretations with actual measured results.

Spark handles corpus loading, validation, feature tables and aggregates. Five existing estimators remain Spark ML and four remain scikit-learn. All nine share a declared comparison sample and group manifests. Fit preprocessing on training groups. Select candidates on development groups. Report all final topology folds, confusion matrices, per-class recall, macro/weighted metrics, false alarms, prediction cost and service outcomes.

The requested external dataset has 22 fields, while the existing saved models require 40 predictors. P12 first establishes a semantic contract. A common-feature retraining comparison is a separately labeled experiment when complete frozen-model inputs cannot be supplied.

The later system path is telemetry -> Kafka -> Spark Structured Streaming -> prediction -> policy -> OVS enforcement. Measure event-time handling, lag, throughput, restart/replay behavior and actual end-to-end decision delay. Mitigation evaluation compares no action, a rule baseline and model-triggered action on matched workloads, including legitimate goodput, request latency, false blocking, expiry and recovery.

## 9. References and inspection limits

- **R01. Cisco campus LAN design guide.** Architecture reference for access, aggregation, services and Internet/WAN boundaries. [Official guide](https://www.cisco.com/c/en/us/td/docs/solutions/CVD/Campus/cisco-campus-lan-wlan-design-guide.html).
- **R02. Al-Fares, Loukissas and Vahdat, 2008. A Scalable, Commodity Data Center Network Architecture.** Foundational topology/routing paper. [Author-hosted paper](https://cseweb.ucsd.edu/~vahdat/papers/sigcomm08.pdf).
- **R03. Singh et al. Jupiter Rising.** Production Clos and centralized-control precedent. [Google Research](https://research.google/pubs/jupiter-rising-a-decade-of-clos-topologies-and-centralized-control-in-googles-datacenter-network-2/).
- **R04. Ahuja, Singal and Mukhopadhyay, 2020. DDOS attack SDN Dataset.** Creator documentation of ten topologies and combined flow/port observations inspected. [Dataset DOI/release](https://data.mendeley.com/datasets/jxpfjc64kr/1).
- **R05. A Multi-Class SDN Intrusion Detection Dataset with Synchronized OpenFlow Control-Plane Telemetry, 2026 (LAN-SDN-NIDS).** Publisher-indexed methods and original scripts inspected. Direct publisher requests were rate-limited. [Paper](https://www.mdpi.com/2306-5729/11/8/195), [Dataset DOI](https://doi.org/10.21950/QMAXKP).
- **R06. Karmous et al., 2025. A New Dataset for Network Flooding Attacks in SDN-Based IoT Environments.** Full methods inspected; complete generation-code reconstruction remains unverified. [Paper](https://www.techscience.com/CMES/v145n3/65006/html), [Requested Kaggle dataset](https://www.kaggle.com/datasets/nedernido/sdn-ddos-dataset).
- **R07. InSDN, 2020.** Original dataset paper inspected for testbed, captures and feature extraction. [Author repository copy](https://researchrepository.ucd.ie/server/api/core/bitstreams/f0050518-5407-4b43-81d8-2607e9c8dab4/content).
- **R08. Sharafaldin et al., 2019. Developing Realistic Distributed Denial of Service (DDoS) Attack Dataset and Taxonomy (CICDDoS2019).** Official dataset documentation inspected. [UNB dataset and paper reference](https://www.unb.ca/cic/datasets/ddos-2019.html).
- **R09. HLD-DDoSDN, 2024. High and low-rates dataset-based DDoS attacks against SDN.** Full methods inspected. [Original article](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0297548).
- **R10. SDN-SlowRate-DDoS.** Primary dataset instructions inspected; download is subscription gated and data were not reproduced. [IEEE DataPort record](https://ieee-dataport.org/documents/sdn-slowrate-ddos-dataset).
- **R11. Gayantha, Rajapakse and Senanayake, 2025. Customizable DDoS attack data generation in SDN.** Indexed accepted-manuscript methods inspected; direct PDF returned 403. [Accepted manuscript](https://rgu-repository.worktribe.com/OutputFile/2801592).
- **R12. Singla et al., 2012. Jellyfish: Networking Data Centers Randomly.** Original paper inspected for random-interconnect tradeoffs. [USENIX paper](https://www.usenix.org/system/files/conference/nsdi12/nsdi12-final82.pdf).
- **R13. Ahmad et al., 2026. DDoS Attacks Detection and Prevention on Real-Time Streaming Data Using Machine Learning Methods With Kafka and Apache Spark.** The supplied PDF was read. Its reported model accuracies differ between discussion and conclusion; use its pipeline as architectural context. [DOI from supplied PDF](https://doi.org/10.1109/ACCESS.2026.3696041). The DOI destination was unavailable during the journal check.
- **R14. Existing project source and notebooks.** The baseline labels, feature names, LA1 plots and nine-model assignment come from the historical project. [Project reference](../DDoS_Prevention/README.md), [Analytics contract](../DDoS_Prevention/analytics/README.md).

Additional implementation references are [Mininet](https://mininet.org/overview/), [Ryu traffic monitoring](https://book.ryu-sdn.org/en/html/traffic_monitor.html), [Ryu maintenance status](https://github.com/faucetsdn/ryu), [QEMU system emulation](https://www.qemu.org/docs/master/system/introduction.html), and [Kaggle notebook documentation](https://www.kaggle.com/docs/notebooks). These are software/platform documentation, separate from dataset novelty evidence.

This reference set is a bounded closest-work review. Prior papers and artifacts were inspected with the limitations above; their numerical results were not reproduced in this project.

## 10. Decision and execution entries

### 2026-11-07 - Dataset design finalized

- User narrowed the creation deadline to two days and requested this journal with explicit source attribution.
- Selected four fixed-size topology families, 348 episodes and the separate ring path/propagation intervention.
- Retained the thirteen-class target and declared the measurement, labeling, group-split and persistence gates.
- Created the design configuration and planned Kaggle run map; reconciled the detailed plan with the journal.
- Clarified scenario-phase versus all-phase window opportunity counts.
- Static graph/matrix/document checks are recorded when completed below. Runtime environments, hosted capture, attack implementations and dataset artifacts remain pending.

### 2026-11-07 - Assessment checkpoint and accepted refinements

- An assessment-only checker verified the four connected graphs, link counts, anchor hops, simple ring routes, matched 8 ms inter-switch propagation, episode arithmetic, window counts and seed/fold consistency. No files were edited by the checker.
- Accepted the recommendation to freeze a single T1 service-capacity reference per workload so that offered traffic stays comparable across topology families.
- Accepted the recommendation to randomize paired path/propagation order reproducibly and retain actual sequence/reset evidence.
- Updated the detailed plan and configuration with both rules. Runtime, installed-environment lock, actual class mechanisms and artifact retrieval remain implementation gates.

### 2026-11-07 - Static setup validation completed

- Passed 35 static checks spanning configuration syntax, connected graphs, paths/hops, timing/window arithmetic, seed partitions, load allocation, reference IDs, local links, the 29-column legacy mapping and the original nine-model team contract.
- Verified exact shuffle-seed serialization and reproducible ordering in all nine workload/seed blocks.
- The assessment-only recheck closed both design findings. Recorded the exact serialization and initial cell ordering requested by that recheck.
- Final configuration SHA256 is `2de45877854a4b1f80324da0d2168725500b971fefd585acde1e6c94cca7fb66`.
- Evidence is saved in [design_validation.json](experiments/topology_dataset/design_validation.json). Its scope is static setup validation. It explicitly records runtime checks and generation as unexecuted.

### 2026-11-07 - Implementation started and WSL forwarding pilot passed

- User authorized implementation. Added reusable `sdn_ddos/topology.py` and `manifest.py`, an isolated Ryu compatibility launcher, and experiment-local structure/connectivity checks.
- Actual Mininet construction passed for all four families with seven switches and sixteen hosts each. Total links including host attachment are 22/22/23/26. The generated episode manifest has 348 unique deterministic identities.
- Existing root-only `/opt/sdn-ddos-ryu-venv` is usable with Python 3.11.16 and Ryu. System OVS reports 3.7.1. The earlier current-user probe did not establish this root environment's availability.
- Ran `PYTHONPATH=. python3 -B experiments/topology_dataset/pilot_connectivity.py` under WSL root. T1 used the reference Ryu learning-switch app on port 16653. Three cross-anchor pairs received all nine ICMP replies. The pilot stopped its network and controller after collection.
- Evidence: [report.json](experiments/topology_dataset/runs/wsl-connectivity-20261107T070858Z/report.json), controller log and seven switch flow dumps in the same run directory. Scope is T1 ICMP forwarding. Zone policy, cyclic-topology forwarding, attack labels and full telemetry are subsequent checks.
- Operational Kaggle capability preflight was assigned within the authorized CLI scope. Actual submission/version/output evidence belongs in KAGGLE_RUNS.md when returned.

### 2026-11-07 - Kaggle native capability result received

- Private capture notebook version 1 completed. Evidence and hashes were retrieved under `experiments/topology_dataset/runs/kaggle-preflight-20261107T071002Z/`; KAGGLE_RUNS.md records actual version and file locations.
- The CPU image provides root UID, four CPUs and Python 3.13.18, but lacks CAP_NET_ADMIN and CAP_SYS_ADMIN. A child-process network-namespace probe failed with Operation not permitted. OVS/Mininet tools, TUN, KVM and QEMU were absent.
- This run establishes capability and persistence evidence. It did not generate traffic or a dataset. Package installation alone cannot supply the missing host capabilities.
- The previously planned QEMU TCG Linux-guest route is the next feasibility experiment. Its hosted behavior and speed remain unverified. WSL remains the authorized pilot host.
- Executed notebook export was unavailable via the tested CLI path. Retrieved cell/kernel logs preserve the available execution evidence. Correct missing notebook cell IDs in the next submitted version.

Future entries will append measured execution evidence and consequential deviations here.

### 2026-11-07 - Public-data coursework scope and non-CIC hybrid recommendation

- User redirected the immediate work to existing measured datasets: three team members, five LA1 plots per member and three LA2 models per member, with preprocessing and training visible inside standalone notebooks. Custom topology collection is parked; existing code and evidence are preserved.
- Official InSDN archive was downloaded and audited: 343,889 rows, 84 columns, eight labels. It is a controlled ONOS/Mininet testbed dataset, not production traffic. Its 17 U2R rows limit rare-class inference. Archive: `experiments/public_dataset_la/data/source/InSDN_DatasetCSV.zip`; SHA256 `EE89EC66705C529FEF26B27DD18C6AA56D469006F7ADE9CD92FD4A503E320D7D`. No models trained on it.
- User requested stronger non-CIC alternatives and permitted mixing. Current recommendation, pending concrete notebook-design approval and file audit: **NF-ToN-IoT-v3 + NF-BoT-IoT-v3**, retaining separate source provenance. These are measured testbed PCAPs converted using a common nProbe schema, not invented numerical observations. Neither constitutes an SDN controller-telemetry dataset.
- **Schema harmonization inspiration:** Sarhan et al., *Towards a Standard Feature Set for Network Intrusion Detection System Datasets*, DOI https://doi.org/10.1007/s11036-021-01843-0. Use compatible extraction semantics instead of matching unrelated CSV column names.
- **Temporal analysis inspiration:** Luay et al., *Temporal Analysis of NetFlow Datasets for Network Intrusion Detection Systems*, https://arxiv.org/abs/2503.04404; official downloads https://staff.itee.uq.edu.au/marius/NIDS_datasets/. Version 3 adds flow timestamps and directional IAT statistics. Planned analyses include traffic volume, burstiness, directionality and time/source distribution. Preserve timestamps for auditing/splitting; raw capture dates are excluded as model predictors. A simple chronological split may omit classes because attacks occurred on separate days; audit coverage before selecting splits.
- **Hybrid evaluation proposal:** compare each source alone, both training sources pooled, and bidirectional held-out-source evaluation on compatible targets. Keep original labels and use a documented common Benign/DoS/DDoS subset for clean shared-label evaluation. Broader intrusion-family analysis may retain source-specific classes with explicit coverage. Mixing is a hypothesis to test, not an established accuracy improvement or a novelty claim.
- **SDN alternative:** LAN-SDN-NIDS, https://www.mdpi.com/2306-5729/11/8/195 and https://doi.org/10.21950/QMAXKP, provides five topologies and synchronized OpenFlow features. Useful for topology holdout and traffic-only versus control-plane feature ablation; retain separately rather than filling absent OpenFlow measurements into NetFlow data. Publisher direct fetch was rate-limited during this check; indexed article methods were accessible. Repository download remains to be verified.
- **Cloud DDoS alternative:** BCCC-cPacket-Cloud-DDoS-2024, https://www.yorku.ca/research/bccc/2024/05/06/new-dataset-alert-bccc-cpacket-cloud-ddos-2024/; original methods https://info.cpacket.com/hubfs/website-resources/YorkU-cPacket-MDPI-journal-article.pdf. Cloud testbed with profiled benign activities, 17 DDoS scenarios and more than 300 NTLFlowLyzer features. Distinct extractor prevents direct blind concatenation with NetFlow.
- **Additional realism check:** IoT-23, https://www.stratosphereips.org/datasets-iot23, contains labeled malware captures and real-device benign captures with Zeek connection logs; useful separate scenario-level validation candidate. It is not a ready-made schema-compatible extension.
- NF-UQ-NIDS and BigFlow-NIDS are existing hybrid precedents, not new dataset contributions; both include CIC-source data. BigFlow-NIDS author release: https://data.mendeley.com/datasets/nv729tbdgz/1. Do not describe either as entirely non-CIC.
- Acceptance before training: verify exact source versions, hashes, licenses, schemas/units, labels and source/time coverage; keep duplicates from crossing splits; fit transformations only on training data; retain source-specific and macro metrics. Proposed derived ratios and fixed-window features must use only available observations, with source timelines processed separately. No source-derived SDN counters, hops or controller metrics will be fabricated.
- Preserve assignments: Satya = Logistic Regression, Decision Tree, Random Forest; Prithvi = Gaussian Naive Bayes, MLP, RBF SVM; Roydon = KNN, Extra Trees, Histogram Gradient Boosting. Notebook implementation, full acquisition and training for the new hybrid have not started.
- Access check: authenticated Kaggle file listings expose `seyhed/nf-ton-iot-v3` (`NF-ToN-IoT-v3.csv`, 5,302,886,266 bytes) and `seyhed/nf-bot-iot-v3` (`NF-BoT-IoT-v3.csv`, 3,817,527,532 bytes). File contents, headers and correspondence with original releases remain unverified. Official links now resolve to public UQ RDM web applications; legacy direct staff-hosted CSV paths returned HTTP 404. A successful HTML response is not a verified dataset download.
- Concrete notebook layout proposed under `experiments/public_dataset_la/notebooks/`: one LA1 and one LA2 notebook per member, with inline cleaning, derivation, splitting and model preprocessing. Save outputs under unique `runs/<run-id>/` directories. Use Spark for complete-data audit and aggregation; declare an identical bounded training cohort for all nine estimators if the RBF SVM/KNN preflight prevents full-data comparison. Retain untouched source-specific evaluation sets and report actual training/test counts. Do not silently substitute a small sample for full-scale training.
- Routing update from user: only Luna delegates may be invoked from this point onward. Prior research delegation has ended; no non-Luna follow-up is authorized.

### 2026-11-07 - Kaggle-only candidate investigation implemented

- User explicitly requested an investigation notebook before choosing between LAN-SDN-NIDS and a mixture, and stated that local bulk storage is unavailable. Implemented `experiments/public_dataset_la/notebooks/01_public_dataset_investigation.ipynb` with inline acquisition, profiling, compatibility analysis, logging and report export. The companion builder and small fixture checks remain in the same experiment directory.
- The user selected investigation first; this run does not train models or publish a combined dataset. Existing source datasets attach read-only on Kaggle. LAN files download into a remote temporary cache, outside saved report outputs. Only compact evidence is retrieved locally.
- Verified official LAN Dataverse API via `requests`: https://edatos.consorciomadrono.es/api/datasets/:persistentId/?persistentId=doi:10.21950/QMAXKP. Latest observed release is3.0, unrestricted CC-BY4.0. Consolidated Parquet is83,151,362bytes. Five topology CSVs and the Parquet are alternative representations; audit both for consistency, never treat their concatenation as independent data.
- Official dictionary and readme were inspected. They describe40 measurements plus target, zero/imputation conventions, topology identifier, six labels, documented duplicate/conflicting records, and MAC-prefix ground-truth assignment. Raw identifiers/oracle values must stay outside predictors. Actual checks will verify duplicates and topology coverage, and whether timestamps exist in the released final tables.
- Input listings expose roughly20GB of attached data. NFpair and cloud CSV receive full scans; IoT-23 mirror has325M+ feature rows and receives explicitly bounded1M-row-per-scenario probes, with full metadata row counts. Scenario prefixes are not representative full-dataset samples. Feature-table labels are retained; separate aligned metadata tables are not extra examples.
- Actual local fixture checks passed: chunk coverage, counts, missing/nonfinite values, identifier exclusion, candidate contradictory labels, timestamp aggregation, output persistence, HLL uniqueness tolerance and empty-table failure. These synthetic fixtures validate auditor behavior only, not attack classification. Full remote data audit is pending execution.
- Prepared private CPU notebook identity `satyapaladugu/sdn-public-dataset-investigation`, internet enabled. User's earlier CLI authorization and explicit new notebook purpose cover submission. Luna handles validation, submission, monitoring and small artifact retrieval; source is frozen during execution. Actual versions/status belong in `KAGGLE_RUNS.md`.
- Provisional decision: LAN-SDN-NIDS primary for SDN-specific analysis, with topology holdout and traffic-only/OpenFlow ablation; NF-ToN/BoT pooling evaluated separately. A single all-source union would discard or fabricate controller features and permit missingness/source leakage. Final recommendation waits for empirical source reports.
- Additional creator-code inspection: official `expanded_flowbuilder.py` (Dataverse file55757) assigns ground truth using reserved destination-MAC prefixes; exclude these identifiers/oracles. Its `new_mac_ratio` implementation uses earlier global source-MAC sightings, while the current dictionary describes a preceding-window novelty measure. The stored final feature cannot be independently recomputed from final aggregate tables alone; treat its exact provenance as unresolved and include an ablation if selected. This is an inspected code/documentation discrepancy, not proof that a particular stored column was generated by that exact code revision. Raw PCAPs are not deposited according to the readme.
- Remote-only dataset persistence is supported by Kaggle's documented creation of datasets from notebook output files: https://www.kaggle.com/docs/datasets. Saved notebook outputs under `/kaggle/working` have a documented20GB limit: https://www.kaggle.com/docs/notebooks. A later build should save only selected compact Parquet tables, provenance, dictionary and split manifest; bulk source caches should remain outside saved outputs. Runtime file existence alone does not establish saved/published persistence; verify output retrieval/reattachment.
- Combining all candidates would change the task: LAN includes ARP/LLDP-level architectural attacks and control-plane observations that IP NetFlow tables cannot represent. Restricting to common IP-flow fields would lose that part of the SDN objective. Byte counters also require layer/encapsulation reconciliation; similarly named byte columns are not presumed interchangeable. Preserve rich SDN analysis and compatible NetFlow pooling as distinct experimental tracks unless the empirical audit establishes a justified common task.

### 2026-11-07 - Investigation v1 retrieved; source decision and focused correction

- Version1 completed; run-reported computation1425.8s, no captured cell errors. Retrieved346 files totaling10,504,028bytes, including a2,110,024byte compact archive. Archive CRC and343 archived member hashes verified; three separately saved live files differ only because final-cell logging/export finished after the archive/checksum snapshot. No input datasets or caches were downloaded locally. See `KAGGLE_RUNS.md` and run `retrieved/verification_summary.json` for exact evidence paths.
- Fully scanned NF-ToN-IoT-v3:27,520,260rows/55columns; NF-BoT-IoT-v3:16,933,808rows/55columns. Ordered schemas match exactly. BoT has51,989benign rows versus7,150,882DDoS and8,034,190DoS; its rate fields contain missing/infinite observations requiring explicit handling. ToN uses lower-case `ddos`/`dos`, whereas BoT uses `DDoS`/`DoS`; map spelling explicitly while preserving originals. These are compatible mixture candidates; a mixture's benefit is still untested.
- LAN consolidated data:1,125,059rows/41columns, six classes; five topology CSVs total the same rows, each with47columns including raw timestamps/identifiers. All six classes occur in every topology. Aggregate has12,549exact complete-row duplicates,21,425predictor duplicates,76candidate conflicting-predictor hash groups and7,606predictor hash groups crossing topologies. No missing/nonfinite measurements were observed in the aggregate. Aggregate lacks timestamps; topology CSVs retain `timestamp_1/2`.
- LAN observed classes: Normal1,083,731; Injection12,726; Linkfab8,635; Hijack8,403; DDoS6,827; PortScan4,737. Therefore accuracy alone is unsuitable; report macro/per-class metrics and false alarms. It is captured emulated SDN traffic, not independently observed production traffic.
- IoT-23 footer total325,309,946rows; inspected13,202,765prefix rows across all23scenarios. Thirteen scenarios hit the1M cap. These prefix label counts must not be portrayed as full-distribution counts.
- Cloud CSV:700,776rows/324columns, with broad `label` values Benign413,199/Attack228,469/Suspicious59,106 and2literal header records. Main review discovered `activity` as a separate finer-grained target:26distinct values in the uniform audit sample. An initial commentary inference that only broad labels were available was corrected immediately. Exact activity counts require the focused follow-up.
- Confirmed auditor bugs, fixed forversion2: the generic exclusion list omitted rawLAN `src_MAC`, `dst_MAC` and `subflow_id`; BCCC `activity` was not excluded as target metadata. V1's aggregate LAN exact audit and NF audits are unaffected. RawLAN predictor fingerprints/purity and BCCC fingerprints/purity are not valid evidence for a cleaned modeling feature set. V1 remains preserved, including exact source snapshot; no classifier used these fields.
- Version2 is a focused rerun of LAN+cloud only, on the same notebook identity afterv1completed. It excludes those identifiers, counts cloud activity labels and checks projection of the raw topology tables onto consolidated predictor/target columns. NF andIoT are not rescanned. Only Luna performs operations.
- Decision from verified v1 evidence: use LAN-SDN-NIDS as primary for the three-person SDN LA1/LA2 notebooks; preserve topology/timestamps as evaluation metadata, exclude identifier/oracle columns from predictors, and explicitly handle duplicate/conflicting records. Evaluate compatible NF-ToN/BoT combined training as a separate cross-domain study with source-specific test sets. Keep cloud/IoT separate unless a validated reduced common task is justified. Do not pool all sources by a union of columns or fill unobserved controller telemetry with zeros.

### 2026-11-08 - Dataset-stage decision superseding coursework framing

User explicitly deferred graph-aware MoE architecture and RL mitigation until after dataset finalization. Interpret "IoT and ToN" as the already-investigated NF-BoT-IoT-v3 plus NF-ToN-IoT-v3 pair; IoT-23 remains deferred. Q-Mitigate remains a later design reference, not an executed mitigation baseline. LA1/LA2/person allocation no longer defines project scope.

Selected inputs: NF-ToN-IoT-v3 (27,520,260 measured rows) and NF-BoT-IoT-v3 (16,933,808) form a provenance-preserving 44,454,068-row source pool before cleaning. Keep standalone source views and create a combined training view. LAN-SDN-NIDS remains a separate SDN dataset using all five topology CSVs (1,125,059 rows). BCCC and IoT-23 are reserved external candidates, not additional pool members now. Source investigation complete; prepared datasets, split manifests and model training pending.

Primary system-level target finalized as DDoS versus non-DDoS, retaining EVERY original attack label. Non-DDoS includes legitimate traffic and other attacks; it never means safe/benign. This updates earlier benign-only crossover proposals to support broader traffic evaluation. Report benign false alarms and confusion with other attack families separately. Preserve a DDoS-versus-benign restricted benchmark as an optional diagnostic; retain LAN's six-class target as a native SDN auxiliary view. No invented subtype labels, no treating all intrusions as DDoS, no assuming that unfamiliar observations can be reliably rejected without evaluation.

Feature views: full compatible NetFlow predictors for ToN/BoT; native LAN traffic/OpenFlow predictors; a distinct, explicitly verified common feature contract for cross-source evaluation. Exact common fields/units remain a preprocessing acceptance gate, not a guessed finalized schema. Raw endpoints/timestamps/topology/source metadata remain available outside model inputs for split checks and future graph construction. Never concatenate unrelated captures into one timeline or fabricate cross-source graph edges. Default modeling excludes raw identities, capture dates, source/topology IDs, subflow IDs, both label fields and label-oracle MAC prefixes. New-MAC-ratio implementation ambiguity remains a validation/ablation issue.

Preparation stays on Kaggle with Spark for large-table work and Parquet outputs. Preserve original and normalized labels, immutable source hashes and per-row provenance. Audit missing/nonfinite values and mathematical undefinedness; transformations that learn statistics fit training only. Identify duplicates under the actual selected predictor representation; quarantine contradictory-label groups with reported counts and prevent overlap across partitions. Compare ToN-only, BoT-only, combined training on identical source-specific tests and equal comparison budgets. Source/class weighting is explicit and training-only; untouched tests retain their recorded distributions. Cohort size follows resource preflight, not silent per-model sampling.

LAN primary split: Linear+Tree+Mesh training, Star validation, Subnets final test, with cross-topology duplicate groups purged from earlier partitions where necessary; check post-cleaning class coverage. This evaluates one unseen topology, not all possible networks. NetFlow splits use source-specific capture/time blocks with duplicate grouping and coverage checks, rather than unconditional random rows; only claim independent-episode transfer if capture provenance supports it. Cross-source test labels must remain untouched during feature/routing/model selection. Demonstrate genuinely unseen-source performance in a separate experiment excluding that source from ALL expert/gate training.

Creator architecture verification:
- BoT-IoT original paper https://arxiv.org/abs/1811.00701 sections3.1/3.2 inspected through alphaXiv. ESXi cluster/vSphere, LAN/WAN through pfSense, four Kali attacker VMs, Ubuntu/Windows/Metasploitable targets, Node-RED IoT services using MQTT/AWS connection, benign services and Ostinato. This is not documented as an OpenDaylight/Ryu OpenFlow testbed. Original features used Argus; our NF-v3 input is subsequent common nProbe extraction. Official source https://research.unsw.edu.au/projects/bot-iot-dataset .
- ToN-IoT official https://research.unsw.edu.au/projects/toniot-datasets and creator testbed paper https://arxiv.org/abs/2010.08522 inspected. Edge/fog/cloud architecture, Windows/Linux/Kali VMs/hosts; SDN/NFV management through VMware NSX/vCloud NFV. We select NETWORK captures re-extracted into NetFlow, not automatically the full host/sensor multimodal collection. Original collection architecture does not imply controller telemetry is present in NF CSVs.
- NetFlow-v3 extraction https://staff.itee.uq.edu.au/marius/NIDS_datasets/ and https://arxiv.org/abs/2503.04404 . Preserve measured CSV counts because website counts contain inconsistencies.
- LAN official DOI https://doi.org/10.21950/QMAXKP . Creator environment.md file63540 and topology scripts55758/55761/55763/55764/55766 fetched and inspected on2026-11-08. OpenDaylight Oxygen0.8.4, Containernet, OVS3.1.0, OpenFlow1.3. Forwarding-switch counts from scripts: Linear6; Tree7; Star5 (core+4spokes); Mesh4 (6inter-switch links); Subnets6 (two distribution nodes feeding four access nodes). Per-switch collector containers and service/traffic containers are additional nodes. Scripts establish connectivity; reconstruction/runtime not performed here.

Acceptance for next preparation increment: small versioned Kaggle source bundle with data dictionary/units, normalized labels/provenance, quality/quarantine report, group/split manifests, dataset hashes and recoverable remote Parquet outputs. Retrieve compact reports only. No promise of "any traffic/any network"; supported feature availability, attack coverage, unseen-source failures and later unfamiliar-traffic handling must be measured.

### 2026-11-07 - Version2 correction and raw-input decision (execution history)

### 2026-11-08 - Next-increment data and training plan

User requested a concrete next-step plan before returning to LA1/LA2. Coursework notebooks are presentation/delivery views over the same detection research experiment; this does not restore synthetic-data results or replace the system objective. This entry is the current training plan. No training or dataset publication is authorized by this planning turn alone.

1. PREPARE DATA REMOTELY. Create one preparation notebook under `experiments/public_dataset_la/notebooks/`, separate from the completed investigation notebook. Preserve the latter's stable identity and outputs. Use source-version/hash-pinned NF-ToN-IoT-v3, NF-BoT-IoT-v3 and the five official LAN topology CSVs. Output partitioned Parquet plus immutable source/label/feature registries, quality/quarantine report and row/group/split manifests. Keep ToN and BoT separate physically and create their combined training view without needlessly duplicating all rows. Retain metadata needed for future graph connectivity/time, outside predictors. Save only compact reports locally.

2. FREEZE LABELS AND FEATURE CONTRACTS. Primary target=1 for original DDoS,0 for non-DDoS; original attack family and benign status remain for subgroup evaluation. All other attacks are non-DDoS, not benign. Native NetFlow and native SDN views retain available measurements after identifier exclusion. Mathematical derivatives must use only measured quantities with explicit units and zero-denominator handling. Default LAN baseline excludes new_mac_ratio until its implementation ambiguity is resolved; include it later as an explicit ablation. Confirm raw-versus-consolidated correspondence after documented missing-value normalization. Establish a separate common-feature contract for crossover; do not force a common field when extractor semantics disagree. If tabular flow semantics cannot align, use a validated common window-level representation or restrict the crossover claim. No OpenFlow padding or fabricated graph edges.

3. FREEZE EVALUATION. LAN train=Linear+Tree+Mesh; validation=Star; test=Subnets, subject to post-cleaning class coverage. NetFlow uses approximately60/20/20 source-specific capture/time-block partitions, with boundaries chosen only after event coverage/provenance audit; do not split a single coherent episode merely to manufacture an independent-episode test. Duplicate groups under each actual feature representation must not cross boundaries. Predeclare quarantine of conflicting-label groups and report counts/label distributions. Retain fixed, natural-distribution source-specific tests. Validation handles tuning/calibration/thresholds; reserve separate validation portions or cross-fitting so those choices do not reuse their own fitted observations. Final tests are opened only after selections freeze.

4. RESOURCE PREFLIGHT BEFORE BULK FITS. Run representative1k/5k/20k training cases for RBF SVM,KNN,MLP to measure fit cost,memory,prediction cost and convergence; these are feasibility measurements, not publishable final scores. Choose and record one feasible common training-row budget for the nine-model comparison. Within each condition every algorithm gets identical row IDs. ToN-only,BoT-only and mixture use equal total comparison budgets, with source/class weights or sampling declared; mixture does not automatically get double the data. Any extra full-data scalable-model run is a separately labeled scale experiment. Test predictions are chunked and metrics accumulated across the full eligible test partitions. No need to collect44M rows into a scikit-learn driver. No wall-time estimates or fixed sample counts claimed before this preflight.

Resource clarification: full-test chunked evaluation above is the goal where the preflight supports its cost. For slow KNN/SVM paths, first freeze one common source-specific test cohort for ALL nine families, sampled by evaluation groups while retaining recorded class prevalence as closely as possible; report its coverage. Evaluate selected champions on the full eligible test partitions separately. Chunking bounds memory but does not eliminate KNN's distance-computation cost. Do not imply a sampled test is a complete-data evaluation.

5. TRAIN NATIVE BASELINES. Nine families: Logistic Regression,Decision Tree,Random Forest,GaussianNB,MLP,RBF SVM,KNN,ExtraTrees,HistogramGradientBoosting. Four training conditions: LAN native,ToN native,BoT native,ToN+BoT native. This is36 final selected model configurations before tuning/refits/calibration. LogisticRegression/DecisionTree/RandomForest use SparkML; other six use scikit-learn. Spark also performs large-data audits/aggregations; small bounded cohorts are materialized for sklearn. Fit all learned transforms within training only. Compare class weighting without contaminating test prevalence; bound tuning trials and record every trial including failures. Use early stopping where supported; incomplete/convergence-limited models must be reported honestly. Model, fitted transforms, predictor order, label map, source/split IDs and package versions are one saved inference bundle. Majority and simple rate/threshold baselines supply reference points; threshold tuning uses validation only.

6. RUN A BOUNDED CROSSOVER STUDY. Native feature models cannot consume a different schema. Select3 complementary algorithm families using validation evidence and resource cost, with explicit selection reasons (not final-test scores). Refit these families under the verified common contract in all4training conditions:12 additional final configurations. Evaluate each on the identical LAN,ToN,BoT test partitions. Initial plan therefore has48 selected configurations, not48 total fit calls: tuning/calibration adds work. A full nine-family crossover adds36 common-contract configurations instead of12 and is a later extension if resources justify it. Results must distinguish within-source, source-informed crossover, unseen-topology and truly unseen-source experiments. A genuine unseen-source claim requires that source's labels/validation and all source-trained experts be absent from model/gate selection and training.

7. PUBLISH EVIDENCE BEFORE ENSEMBLING. Per model/condition save raw confusion counts,precision,recall,F1,PR-AUC/ROC-AUC where defined,MCC,balanced accuracy,benign-only false-positive rate and other-attack confusion by family. Save probability scores and predictions keyed by row IDs for fair paired comparisons and future ensemble analysis. Include curves/threshold sweeps,calibration where probabilities are used,fit/predict/runtime/memory scope,topology/source breakdown and representative errors. Use block/group-based uncertainty estimates when independence supports them; do not bootstrap correlated rows as independent evidence. Fit speed and large offline data do not prove live throughput.

8. LA1/LA2 PACKAGING. Once inputs/splits are ready, create3LA1 notebooks with5substantive figures each, then3LA2 notebooks with3model families each. Satya: LR/DT/RF; Prithvi: GaussianNB/MLP/RBF-SVM; Roydon: KNN/ExtraTrees/HistogramGradientBoosting. Keep substantial preprocessing,derivation,encoding,scaling and training visible inline, as explicitly requested. Preparation exports observational tables,provenance and manifests, not globally fitted preprocessors. Shared source/split/feature hashes must match across notebooks. Use experiment/condition loops in each person's LA2 notebook rather than duplicating notebooks for every source. Proposed sources: `02_prepare_public_data.ipynb`, `la1_satya.ipynb`, `la1_prithvi.ipynb`, `la1_roydon.ipynb`, `la2_satya.ipynb`, `la2_prithvi.ipynb`, `la2_roydon.ipynb`. Exact Kaggle identities must be checked/reused per purpose and recorded in existing KAGGLE_RUNS.md before launch; do not overwrite the completed investigation notebook with a training notebook. Each setup/computation cell logs progress/timing and preserves outputs under versioned run directories.

9. LATER SYSTEM STAGES. Use validation/OOF predictions to compare individual experts,equal averaging and stacking, then specify/assess sparse or soft expert routing and graph experts. Architecture is not finalized in this increment. RL/Q-Mitigate and live SDN mitigation remain later; static labels do not supply action-response rewards. Only Luna delegates may perform operational support; main owns design and implementation. No new work has launched in this planning turn.

Acceptance to start LA2: recoverable remote dataset outputs, verified source/schema/units, deterministic reproducible splits with no predictor-group leakage, declared task/target/feature sets, resource-feasible comparison cohort, and successful save/reload prediction check on the selected inference bundles during implementation. Prepared data and training remain pending today; investigation v1/v2 is complete.

### Archived version2 execution evidence

### 2026-11-08 - Revised Spark-oriented candidate list and MoE selection protocol

User authorized changing model families and requested clarification of nine models per dataset and selection for MoE. Current recommendation supersedes the earlier nine-family list: SparkML LogisticRegression,LinearSVC,DecisionTreeClassifier,RandomForestClassifier,GBTClassifier,NaiveBayes(modelType=gaussian),MultilayerPerceptronClassifier,FMClassifier; plus scikit-learn HistGradientBoostingClassifier. Eight Spark families and one sklearn family. Keep nine candidates per training condition (LAN,ToN,BoT,ToN+BoT),36 native final baseline configurations before tuning. RBF SVM,KNN andExtraTrees leave the default list; FM models pairwise feature interactions, not a mixture gate. Preflight FM/MLP/GBT and assess GaussianNB constant/near-zero variance sensitivity. Actual supported runtime/version remains a preflight gate, not established by browsing docs. Kaggle Spark local execution is not a multi-machine deployment claim.

Current official Spark4.2 API references inspected: https://spark.apache.org/docs/4.2.0/api/python/reference/api/pyspark.ml.classification.NaiveBayes.html (Gaussian support for continuous features), https://spark.apache.org/docs/4.2.0/api/python/reference/api/pyspark.ml.classification.FMClassifier.html , https://spark.apache.org/docs/4.2.0/api/python/reference/api/pyspark.ml.classification.LinearSVC.html , https://spark.apache.org/docs/4.2.0/api/python/reference/api/pyspark.ml.classification.GBTClassifier.html . Earlier assertion that GaussianNB necessarily requires sklearn was incorrect. LinearSVC replaces a kernel SVM and needs separate probability calibration for probability mixtures; binary GBT/LinearSVC fit the primary DDoS/non-DDoS task, not arbitrary multiclass targets directly.

MoE selection uses held-out DEVELOPMENT data or nested cross-fitting across sources, never final crossover tests. Candidate identity is algorithm+training source+feature contract+calibration, not just algorithm name. Measure each candidate's discrimination at common benign false-alarm operating points, error patterns by source/family, calibration, runtime,memory and feature availability. Quantify paired errors/rescue cases on identical observations; a label-aware oracle-combination bound is diagnostic headroom only, not a deployable result. Prefer a small3-4expert subset providing reproducible incremental validation gain, complementarity and affordable inference; no quota forcing one expert per source. A graph expert is a later candidate, not automatically part of the nine tabular families.

Generate OOF predictions without training on scored rows/groups; use them to fit averaging/stacking/gating candidates, with independent meta-validation or nested folds for subset and gate choices. Calibrate scores using development data; avoid fitting calibration/gate and selecting it on the same observations. Compare best single model,equal average,learned static combination and conditional gate under matched budgets. Freeze experts,feature contracts,calibration,thresholds androuter before opening final test partitions. A common-feature refit is required for cross-source use; native OpenFlow experts are available only when matching real telemetry exists. Unseen-source evaluation excludes that source from ALL expert and router development. MoE is retained only if improvements over simple alternatives justify cost; complementary errors and identifiable routing context are required hypotheses, not guarantees.

Suggested future team allocation after this change: Satya LR/DT/RF; Prithvi GaussianNB/MLP/LinearSVC; Roydon GBT/FM/HistGradientBoosting. No training launched in this discussion.

### Archived version2 execution evidence (continued)

### 2026-11-08 - CURRENT DETECTOR DECISION: multiple-classifier stacking

User requested a definite architecture and clarified ensemble means multiple classifiers. This decision supersedes prior MoE/gating plans for the current detection version. Train a stacked classifier consisting of SparkML LogisticRegression,RandomForestClassifier andGBTClassifier base learners with a regularized LogisticRegression meta-classifier. All three base models process the observation; the meta-model combines their scores. There is no learned expert-selection router in this version. This is an engineering choice to evaluate, not a claim of proven optimality or improvement.

The three components represent linear,bagged nonlinear andboosted nonlinear models, with one Spark pipeline interface. Meta input is the three base-model DDoS scores, not labels,source IDs,raw IPs or metadata. Source-specific native pipelines share the same target DDoS/non-DDoS; graph features/graph models and RL mitigation remain later stages.

Keep the revised nine-family Spark-oriented study (LR,LinearSVC,DT,RF,GBT,GaussianNB,MLP,FM and sklearnHistGradientBoosting) as comparison baselines, not nine members of the production stack. Train the fixed three-base stack separately for LAN,ToN,BoT,ToN+BoT. The mixture changes training observations; stacking combines classifiers. Comparing those factors separately answers whether data mixing or classifier combination supplies any improvement.

Fit the meta-classifier using grouped out-of-fold predictions from TRAINING data only. Use three folds when class/episode coverage permits, with all transformations fitted inside each fold; record an explicit alternative if independent groups are insufficient. After generating meta-training predictions, refit the base learners on the full designated training partition. Calibration and decision thresholds use reserved development data and are frozen before final test scoring. Meta-learning must not use in-sample base predictions or final test scores. Save every fitted preprocessing/model component and their source/split hashes as one inference bundle.

Evaluate native full-feature stacks within source. Cross-source stacks must be refit using the same independently verified common-feature contract; native OpenFlow models cannot accept missing telemetry. Initial crossover uses the three fixed component families, matching the existing bounded12common-contract base configurations (four training conditions times three base families), plus their trained meta-combiners. Evaluate on fixed source-specific validation for development and untouched tests only after freezing choices. Source-trained variants compared across sources do not establish genuinely unseen-network adaptation unless the destination source is excluded from all development.

Report LR/RF/GBT individually, their equal-probability average and the trained stack under matched cohorts and operating points. Compare with the other six baseline families. Use DDoS recall/PR-AUC,benign false alarms,other-attack confusion,calibration and end-to-end prediction cost. The stack is the planned detector; if measured validation gain over the best constituent is absent or cost excessive, document that negative result and gate deployment rather than reporting an unsupported ensemble benefit. No trained models or new jobs were created in this decision turn.

### Archived version2 execution evidence (continued after decisions)

Follow-up research, 2026-11-08: [scalable graph/MoE detection and mitigation literature](experiments/public_dataset_la/scalability_literature_20261108.md). This records inspected references, evidence limits and provisional mechanisms; prepared datasets, graph construction and trained models remain pending.

- Focused version2 completed with no reported cell/run failures; run-reported elapsed305.95s. Corrected rawLAN exclusions include `src_MAC`, `dst_MAC`, `subflow_id`, raw timestamps, IPs and label. Cloud now uses `activity` as the finer target and excludes both it and broad `label` from predictors. Exact output retrieval and checksums are recorded by Luna in `KAGGLE_RUNS.md`.
- The raw topology CSV to consolidated Parquet projected hash comparison did not match before imputation. This comparison deliberately omitted preprocessing normalization and therefore does not establish a lineage fault. Main analysis of full-column moments found all36numeric finite sums consistent between the raw CSV union and aggregate. Fifteen raw columns have missing values while their aggregate versions are filled with zeros, consistent with the creator dictionary. This explains mean differences and makes unequal raw/imputed hashes unsurprising; row-level equivalence after documented normalization remains to be checked.
- Reconciliation evidence: `experiments/public_dataset_la/runs/public-investigation-20261107-v2/local_analysis/column_moment_reconciliation.json`, with hashes of the six input quality reports. This proves column-moment consistency only, not row-level identity.
- Final primary input choice: use the **five LAN topology CSVs**, retaining raw missingness and timestamps so each LA1/LA2 notebook exposes its own preprocessing. The41-column consolidated Parquet is a reference representation. Both lead to39candidate measured predictors after excluding target/topology/identifiers; temporal/topology provenance belongs outside the modeling feature matrix. Review/ablate `new_mac_ratio` because of the documented implementation ambiguity. Never add both raw and consolidated records as new examples.
- Dataset preparation remains remote. A later private Kaggle dataset may contain the selected source tables, dictionary, hashes and split metadata without local bulk transfer. Do not pre-fit preprocessing outside the six requested notebooks. No classifier results, novel data-generation claims, mitigation claims or published combined dataset exist at this checkpoint.
- Version2 persistence/retrieval verified:96files totaling7,885,276bytes; compact archive1,727,005bytes, CRC passes and93archived manifest members match. As in v1, three live files legitimately finish updating after the export snapshot. Combined two-version retrieved reports total18,389,304bytes; no bulk inputs/cache retrieved. Full cloud activity counts establish26categories plus2literal repeated-header records (`activity`); these2rows must be quarantined before modeling, and `Suspicious` is not automatically a verified DDoS label. The earlier sample-based26-category observation is now backed by a full scan.
