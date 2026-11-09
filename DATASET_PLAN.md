# SDN DDoS dataset: 48-hour collection plan

Decision date: 2026-11-07, Asia/Calcutta.
Status: design configuration finalized; implementation and runtime verification pending. Capture results and novelty remain unverified.
Canonical project: `D:\Bunker\BaseCamp\WirelessCommunication\DDoS_Prevention_and_Mitigation`.
Historical reference: `D:\Bunker\BaseCamp\WirelessCommunication\DDoS_Prevention`.

Final setup configuration: [dataset_v1.json](experiments/topology_dataset/configs/dataset_v1.json).
Paper-to-design attribution and ongoing decisions: [Journal.md](Journal.md).
Notebook/version/artifact tracking: [KAGGLE_RUNS.md](KAGGLE_RUNS.md).

## 1. Decision and contribution

Collect FOUR topology families: star/campus baseline, balanced hierarchical tree, ring, and two-spine fabric. Provision seven OVS switches, sixteen traffic hosts, and one Ryu controller in every family. Place the traffic hosts on four fixed attachment switches. Use the same application services, policy, observation points, software versions, and workload catalogue.

The contribution to investigate is a measured topology-transfer dataset with a separate, controlled path-length experiment. The release should let a reader distinguish topology, path length, propagation delay, load, identity, and observation-point effects.

Combining topology families, adding controller metrics, varying link settings, and releasing a dataset are established practices. The proposed differentiation is their controlled combination with matched nominal scale, independent evaluation groups, verified mixed-traffic labels, causal features, and usable raw evidence. A first-ever or publication-novelty claim requires additional comparison and experimental results.

Research questions:

1. At a fixed training budget, does training on several structures improve detection on an unseen structure?
2. Does a detector change its decisions when the route crosses more switches, including when propagation delay and the target bottleneck are held comparable?
3. Which traffic, controller, and resource feature groups transfer, and at what collection cost?

The two-day deliverable is the dataset, provenance, quality report, split manifests, feature dictionary, executed generation notebook, and a small baseline check. Preserve the existing nine LA2 algorithms and team ownership for subsequent full training. Kafka, live mitigation, additional controller products, and a large scale sweep follow this release.

## 2. Literature and decision ledger

This is a bounded closest-work review of primary dataset descriptions, methods, released scripts, and foundational network designs. Some full texts or artifacts were inaccessible. Sources were not experimentally reproduced. Search coverage does not establish an exhaustive review of all SDN research.

| Source | Inspected evidence and implication |
|---|---|
| [Ahuja et al., dataset release, 2020](https://data.mendeley.com/datasets/jxpfjc64kr/1) | Creator documentation reports ten Mininet topologies, Ryu, merged flow/port telemetry, and 30-second monitoring. It does not specify all graph families or demonstrate topology holdout there. Multi-topology capture already exists. |
| [LAN-SDN-NIDS, 2026](https://www.mdpi.com/2306-5729/11/8/195), [original release](https://doi.org/10.21950/QMAXKP) | Publisher-indexed methods and released topology/orchestration scripts were inspected. Linear has 6 switches/19 traffic hosts, tree 7/21, star 5/11, mesh 4/12, and subnet 6/18, plus capture hosts. Topology and scale vary together. The paper explicitly reports no topology holdout. Five topology files and a consolidated release exist. This is the closest comparison for our controlled design. |
| [SDN-IoT/Kaggle-associated paper, 2025](https://www.techscience.com/CMES/v145n3/65006/html) | Describes single, ring, linear, tree and mesh capture. Reports a random 80/20 split and a separate tree deployment demonstration. Exact per-family scale and complete executable generation artifacts were not established. More graph names alone would not distinguish our release. |
| [InSDN, 2020](https://researchrepository.ucd.ie/server/api/core/bitstreams/f0050518-5407-4b43-81d8-2607e9c8dab4/content) | Methods describe ONOS, OVS, Mininet, routed subnets, and PCAP/CICFlowMeter extraction. Completed-flow information must be separated from data available at an early prediction deadline. |
| [HLD-DDoSDN, 2024](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0297548) | Methods describe one vSwitch/64 hosts and POX. Attack and benign observations are collected at different locations. Our collection must use the same observation rules for both classes. |
| [SDN-SlowRate-DDoS, original DataPort record](https://ieee-dataport.org/documents/sdn-slowrate-ddos-dataset) | Describes a physical ONOS network with two spines/four leaves and 23 slow-read experiments varying attacker/victim counts. Dataset download is subscription gated. A small leaf-spine graph itself is established. |
| [Customizable DDoS generation, 2025](https://rgu-repository.worktribe.com/OutputFile/2801592) | Indexed accepted-manuscript methods describe hierarchical SDN and configurable bandwidth/latency. Direct PDF returned 403. Treat as a prior-art lead against novelty from configurable settings. |
| [SDN-2M author repository](https://github.com/LKHoang-Zipris/SDN_2M_Dataset) | README describes a two-switch testbed and a CSV release without an official split. Complete collection reconstruction was not established. Useful release-completeness comparison. |
| [Al-Fares et al., SIGCOMM 2008](https://cseweb.ucsd.edu/~vahdat/papers/sigcomm08.pdf) | Foundational commodity fat-tree design. A full k=4 instance has 20 switches and 16 hosts. Our small two-spine graph should be named a leaf-spine fabric, with its exact graph released. |
| [Jellyfish, NSDI 2012](https://www.usenix.org/system/files/conference/nsdi12/nsdi12-final82.pdf) | Random interconnects bring a graph-seed and routing dimension. Defer these additional experiments under the 48-hour budget. |
| [Cisco campus reference](https://www.cisco.com/c/en/us/td/docs/solutions/CVD/Campus/cisco-campus-lan-wlan-design-guide.html), [Google Jupiter](https://research.google/pubs/jupiter-rising-a-decade-of-clos-topologies-and-centralized-control-in-googles-datacenter-network-2/) | Ground the hierarchical campus and redundant fabric roles. They are architecture precedents. |

Revisit the novelty wording if closer work already demonstrates matched-scale topology transfer, matched-delay path interventions, and equivalent release evidence. Preserve the useful dataset even if its contribution is methodological replication or extension.

## 3. Exact topology graphs

Switches are s1 through s7. The sixteen traffic hosts attach four each to s4, s5, s6, and s7 in every family. Those switches are the four primary observation anchors. Record all seven switches' controller/port state. Preserve each actual active forwarding footprint in metadata.

| ID | Graph edges | Links | Anchor-to-anchor shortest switch-hop counts |
|---|---|---:|---|
| T1 star/campus baseline | (1,2),(1,3),(1,4),(1,5),(1,6),(1,7) | 6 | 3 |
| T2 balanced tree | (1,2),(1,3),(2,4),(2,5),(3,6),(3,7) | 6 | 3 or 5 |
| T3 ring | (1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,1) | 7 | 2, 3, or 4 |
| T4 two-spine fabric | (1,l),(2,l) for l in {3,4,5,6,7} | 10 | 3 |

These counts were checked with an in-memory graph traversal, not a Mininet run. A switch-hop counts each forwarding switch traversed, including source and destination attachment switches. Also record inter-switch edges traversed and IP hops where routing occurs.

Matching provisioned device counts does not equalize link count, active forwarding footprint, bisection bandwidth, or redundancy. Those structural differences are measured properties of the families. The primary comparison uses an identical target access bottleneck, fixed observation anchors, and the same nominal per-link settings. It does not claim an equal-cost network comparison or a pure causal effect of graph shape.

Some provisioned switches carry no workload traffic under a particular route. Record this explicitly. Do not inflate sample counts using idle switches or repeated controller context.

Use deterministic simple paths, reverse-path consistency, explicit ARP handling, and installed zone policies. Select between the two fabric spines with a stable flow hash. Avoid ordinary Layer-2 flooding on cyclic graphs. Keep forwarding configuration common across benign/attack cases. Do not periodically flush tables only during one attack class.

Logical roles:

- s4: two external client generators and two isolated reflector hosts. The reflectors can expose several explicit lab protocol services.
- s5: four ordinary enterprise clients. Role schedules include HQ and branch-like traffic, with declared access-link delays.
- s6: public web proxy, public DNS, a bounded protocol-test target, and a legitimate service probe.
- s7: two private application servers, an internal DNS/NTP host, and a database.

Rotate which eligible client host acts as an attack source independently of topology. Public/private service roles remain explicit in the policy. Same-seed workload replays use the same identities across families; the seed's data are assigned consistently to evaluation partitions.

## 4. Main collection matrix

Preserve the legacy target catalogue:

BENIGN, UDP_FLOOD, ICMP_FLOOD, TCP_SYN_FLOOD, TCP_ACK_FLOOD, TCP_RST_FLOOD, HTTP_FLOOD, SLOW_HTTP, DNS_AMPLIFICATION, NTP_AMPLIFICATION, SSDP_AMPLIFICATION, UDP_AMPLIFICATION, MIXED_DDOS.

| Factor | Fixed choice |
|---|---|
| Topology families | Four graphs above |
| Traffic scenarios | Thirteen legacy classes |
| Offered-load bands | Low and high |
| Independent workload realizations | Three, with seeds 101, 202, 303 |
| Episode timing | 30 s baseline, 60 s scenario observation, 30 s recovery |
| Observation cadence | Nominal 1 s, with actual times and lateness retained |
| Main episodes | 4 x 13 x 2 x 3 = 312 |
| Scheduled episode time | 37,440 s = 10.4 h, before setup/teardown and runtime overhead |

Run whole topology batches and shuffle scenario/load order inside each seed block. Reset scenario processes, connection state and applicable temporary rules between episodes. Resume at completed episode boundaries. A partially completed episode retains its evidence and is marked partial; a replacement receives a distinct attempt ID.

Baseline nominal bottleneck C is 1 Mbit/s, subject to preflight calibration. Set transit links to 10C and ordinary access links to at least 2C. All main inter-switch links initially have 1 ms one-way propagation delay. Set an explicit common target queue limit of 100 packets. Persist actual qdisc configuration and achieved delay/rate.

For packet-volume scenarios, low and high total offered load target 0.6C and 1.2C. Record actual attempted and delivered rates. For connection/request scenarios, use 0.6 and 1.2 of the relevant configured or measured request/connection capacity, with workload-specific units. Do not equate connection load with bytes/s.

Freeze one shared reference per workload on T1 before the main experiment. Use the instrumented service's configured concurrent-request limit for connection-capacity workloads. For rate-capacity workloads, accept a reference with at least 99% successful completions and achieved rate at least 95% of offered rate over a 30-second check. Record service configuration, units, criterion, reference value, resource state, attempted/achieved rate and background allocation. Use this same reference in every topology. The ordinary background allocation is 0.2 of the reference, with the scenario adding 0.4 at low load or 1.0 at high load. BENIGN uses legitimate scenario traffic for those allocations. Topology-specific achieved rates are outcomes. Per-topology capacity normalization would be a separate experiment.

If the pilot cannot sustain the offered rates with collection enabled, choose one lower C for every topology/scenario before main capture. Store the selected configuration and freeze it. Any later change creates a separate version/domain with a manifest entry. Host CPU saturation must be distinguishable from the intended link/service bottleneck.

The BENIGN scenario contains legitimate traffic mixtures in both load bands, including flash crowds, bulk transfers, ordinary DNS/UDP/ICMP, connection churn, and slow clients. Classify these as benign from generator provenance even when congestion occurs. Every attack episode retains concurrent legitimate service probes and background workloads.

Thirty baseline seconds reveal existing load. Sixty active seconds cover a bounded slow-HTTP attempt but cannot establish long-duration persistence. Record this scope. An attack mechanism can be observed even if the target remains available; capture attack success and legitimate-service degradation separately from the attack-attempt label.

### Mechanism gates

- SYN, ACK and RST scenarios require the corresponding observed TCP behavior, not a generic TCP connection load.
- Slow HTTP requires observed incomplete/slow request state and server logs.
- Amplification requires an actual request/response reflector path, measured response/request ratio, and target delivery. Protocol-specific fixtures declare their implementation and limitations. Ordinary UDP fan-in cannot satisfy this gate.
- MIXED_DDOS requires simultaneous observed components. Store all component labels in ground-truth sidecars.
- Ground truth combines schedules, successful generator execution, endpoint/port/time bindings, reflector/service logs and observed packets. A class without verification remains an unresolved collection failure. Retain its partial evidence.

## 5. Separate path-length intervention

Use T3 and the fixed pair s4 -> s6:

- Short path: [s4,s5,s6], three forwarding switches.
- Long path: [s4,s3,s2,s1,s7,s6], six forwarding switches.

Both are simple paths in the same graph. Fix source, victim, workload seed, observation point, common victim access bottleneck, queue configuration and forwarding semantics.

Collect three conditions: legitimate flash crowd, UDP_FLOOD and TCP_SYN_FLOOD. Run each with both paths, both propagation modes, and all three seeds. This is 3 x 2 x 2 x 3 = 36 extra episodes, or 1.2 scheduled hours.

Within each workload/seed block, reproducibly shuffle the four path/propagation cells using a Python random generator seeded from SHA256 of the configuration ID, workload seed and condition. Reset between cells and save both planned and actual order with the paired-realization ID. This reduces condition-order confounding with runtime drift.

Serialize the ordering payload as the JSON array `[config_id, integer_workload_seed, condition_string]` with ASCII escaping, separators `(',', ':')`, and UTF-8 encoding. Convert the first eight SHA256 digest bytes to an unsigned big-endian integer for `random.Random`. Start from short/natural, short/matched, long/natural, long/matched, then shuffle. Store the actual Python version and resulting order.

Propagation modes:

1. Natural: 1 ms on every inter-switch edge, with unchanged access delays.
2. Matched propagation: keep each host access delay at 1 ms, and assign 8 ms total propagation across the chosen inter-switch path. The short path's two inter-switch edges each use 4 ms; the long path's five edges each use 1.6 ms. Verify an unloaded probe's actual end-to-end delay before capture. These modes control configured propagation, not queueing/processing delay under load.

Total matrix: 348 episodes and 11.6 scheduled hours, before overhead. Record guest and host elapsed times when using emulation. Do not use virtual-clock acceleration to advertise shorter real capture time.

## 6. Features, observation scope and labels

Keep raw telemetry, packet-derived sufficient statistics, generator ground truth and model features as separate logical tables.

Primary analysis unit: one ingress/service/observation-window record at a declared anchor. Also release flow-prefix/window records and per-port/controller observations. Identical packets seen at successive switches are related observations, with run/window/flow identities retained.

The requested legacy 29-column view gets an explicit mapping:

- timestamps/experiment/window/switch/endpoint/protocol/service fields derive from measured or registered context;
- window duration uses elapsed monotonic time;
- packet and byte counters use a declared direction and L2/L3 byte convention;
- flow count means distinct five-tuples within the declared window, with active/new-flow counts separate from OpenFlow rules;
- rates divide matching counters by their actual interval;
- SYN/ACK/RST use parsed flag bits;
- handshake completion tracks matched connection cohorts with a declared trailing horizon, preserving censored/incomplete state;
- flow-table size and Packet-In derive from controller/switch observations;
- the old CPU proxy name is a deprecated compatibility alias to a measured controller CPU field with an explicit definition;
- intensity, attacker count and background configuration stay in ground-truth/experiment metadata;
- label, family and data source are separate provenance/target fields.

The wider feature registry attempts the existing 40 LA2 behavioral features. Mandatory groups are traffic counts/rates, packet-size/IAT summaries, TCP control/state, diversity/cardinality, table/Packet-In behavior, controller process load, queue drops and directional link utilization. Additional flow-age, entropy, table-churn, queue backlog and stats-round-trip metrics are retained only with a verified observation source. Retransmission/fragmentation estimates identify their estimator and visibility limitations.

For every feature, publish source, unit, direction, observation scope, formula, sampling interval, availability time, missingness and reset behavior. Unsupported values are null with a reason. A missing sensor is distinct from a zero event count. Feature count is an outcome of verification.

Measure the controller process once per interval and join its global context explicitly. Record request/reply IDs, actual counter intervals, reconnect epochs, stale observations, partial multipart replies, and telemetry age. Features are emitted with their real ready-at time. No completed future flow data are attributed to an earlier detection deadline.

Use the same packet/telemetry observation rules for benign and attack records. Offline labels are joined from ground truth. A globally active attack does not make every unrelated flow or switch window malicious. For mixed windows, preserve component labels and the observed attack share in the sidecar, with MIXED_DDOS assigned only where multiple components are actually observed.

Store topology identity, route, hop counts, workload seed, run ID, IP/MAC identities, generator parameters and oracle attack shares as audit metadata. The primary baseline excludes these. Runtime-available topology context can later be assessed in a separately declared feature ablation.

## 7. Evaluation manifests and falsification

Because workload seeds are paired across families, all records sharing a seed's exact scheduled realization must remain consistently partitioned. For the initial benchmark, seed 101 supplies training campaigns, 202 development campaigns, and 303 test campaigns. Do not claim a 70/15/15 row split for this measured release.

For each leave-one-family-out fold:

1. Fit on seed-101 episodes from the other three families.
2. Tune only on their seed-202 episodes.
3. Evaluate on seed-303 episodes from the held-out family.
4. Report same-family seed-303 results as a separate reference.

Release all raw groups, including held-out-family seed-101/202 episodes, and mark their benchmark eligibility. They are excluded from that fold's fit/tuning. Three realizations per cell give limited independent coverage; report this directly. A future collection should add schedule realizations before making broad generalization claims.

Compare single-family and mixed-family training with matched row and episode budgets. Primary questions can be checked initially with the existing Random Forest and a rate-based baseline. The full nine-model suite follows dataset acceptance, with the original team assignments preserved.

Later ablations use traffic-only, traffic plus controller, and traffic plus controller/resources. Retain feature groups based on development evidence. Report every topology fold, per-class recall, macro F1, benign false alarms including flash crowds, feature missingness, service goodput/latency, and collection overhead. Do not select features from the final held-out topology.

Discriminating outcomes include no benefit from mixed training, strong topology-dependent false positives, loss of a presumed hop effect after matching propagation, or overhead dominating a feature group's benefit. Preserve all of these outcomes in the release.

## 8. Runtime, artifact persistence and 48-hour schedule

The destination was empty at this research checkpoint. Kaggle CLI authentication works as satyapaladugu. No matching SDN/Mininet/DDoS notebook was found across the paged owned-kernel inventory. WSL currently has Mininet 2.3.0 and OVS 3.7.1 with OVS already active; Ryu and QEMU are absent from the probed PATH/module environment.

Keep WSL for local correctness pilots. Full collection remains targeted to Kaggle CPU. First test native Mininet/OVS capabilities there. If they are unavailable, test a pinned QEMU TCG Linux guest with its own kernel and OVS. QEMU system emulation is documented; hosted viability is unverified. See [QEMU](https://www.qemu.org/docs/master/system/introduction.html) and [Kaggle notebook documentation](https://www.kaggle.com/docs/notebooks).

The Kaggle documentation inspected during the operational refresh described 12-hour CPU sessions and up to 20 GB saved output. Treat runtime CPU/RAM, available disk, process capabilities and persistence as measured preflight inputs. Use one sequential collection job and a CPU configuration matched to actual availability. QEMU host/guest clock drift, CPU contention and collector overhead are acceptance measurements.

Use two stable private notebook identities under the authenticated account: sdn-ddos-topology-capture and sdn-ddos-dataset-build. Preflight and successive topology batches are versions of the capture identity. Source comes from one versioned bundle built from the canonical project. Never update a healthy running version solely to revise code or prints.

Suggested capture batches are T1, T2, T3, T4 and the path intervention. Each main topology contributes 78 episodes and 2.6 scheduled hours. Run a pilot to estimate actual episode and reset/boot/export times. Require the projected remaining capture and retrieval to fit the reserved 20-hour collection envelope. If it does not fit, report a deadline risk before full launch. Any reduced-duration protocol must be frozen before main capture and keep all four families, classes and independent groups.

Persist each completed episode atomically, with checksum and status. Avoid publishing a dataset version until required partitions and counts reconcile. Checkpoint every episode, save structured cell logs incrementally, and preserve failure tracebacks and rejected windows.

Runtime outputs: `/kaggle/working/experiments/topology_dataset/runs/<run-id>/`.
Local retrieval: `<project>/experiments/topology_dataset/runs/<run-id>/`.
Maintain one `KAGGLE_RUNS.md` map when implementation begins, recording source/config/image hashes, notebook version, input dependencies, run/batch status, paths and retrieval verification. Version-specific saved outputs are the persistence boundary. Attach the preceding saved run inventory for continuation, preserving each version's results.

Store continuous telemetry and compact sufficient statistics. Retain a ten-second header capture at the victim for every episode, plus bounded preflight reference captures. Use snaplen sufficient for the parsed headers, with original packet lengths retained. Full-length continuous multi-vantage packet captures can exceed the storage budget. Record truncation and the scope of recomputation supported by retained evidence. Budget the complete saved bundle at 12 GiB and verify actual sizes during the first batch.

At four anchor observations per scenario second, the main matrix contains 74,880 scenario-phase anchor-window opportunities and the intervention 8,640, or 83,520 total. Including the 30-second baseline and 30-second recovery phases gives 167,040 all-phase opportunities. Actual valid records and flow-prefix counts depend on observations and missingness. Controller context replicated across rows does not create independent samples. Raw event/packet volume must be reported as measured; no million-row target is imposed.

| Elapsed window | Required work and evidence |
|---|---|
| 0-4 h | Pin source/environment, bootstrap Ryu, run a WSL correctness pilot, test native or guest Kaggle capture and retrieve one evidence artifact. Gate: actual hosted traffic, telemetry, timing, readability and persistence. |
| 4-10 h | Implement/verify all four graphs, service paths, labels and feature sources; freeze capture protocol. Run all class mechanism checks and a collector enabled/disabled comparison. |
| 10-30 h | Sequential versioned topology and path-control capture, with per-episode checkpoints and retrieval after each batch. |
| 30-40 h | Spark validation/Parquet construction, legacy view and feature registry, disjoint manifests, reference feature reconciliation and baseline check. |
| 40-48 h | Repair/retry only affected failures, verify final retrieval/hashes and fresh-kernel notebook execution, package documentation and actual counts. |

If both hosted execution routes fail, the Kaggle requirement remains unsatisfied and the 48-hour target is at risk. No evidence currently justifies guaranteeing hosted execution or all thirteen mechanisms within that deadline. Preserve the concrete failure and revise the execution decision explicitly rather than relabeling a local or fabricated result as a Kaggle capture.

## 9. Acceptance and release contents

Dataset acceptance requires:

1. All four topology files match their graph, attachment and policy definitions; actual paths are verified.
2. Every accepted class has observed mechanism evidence in every required topology/load group. Concurrent benign labeling is independently checked.
3. Packet/byte/rate/flag/flow semantics reconcile against reference traces over declared intervals. Counter reset, empty window, stale telemetry and incomplete handshake behavior are checked.
4. All required raw partitions are present; partial/failed episodes and missing sensors are explicitly identified. Duplicate episode/window identities are rejected.
5. Evaluation groups and feature exclusions prevent run, schedule, identity or evaluator-truth leakage.
6. Instrumentation overhead, host/guest resource state and actual bottlenecks are reported.
7. Executed generation/build notebooks, package/runtime manifests, source hashes, configuration, graphs, raw logs, labels, Parquet/CSV views, feature dictionary, quality report and retrieval checks are usable from the release.

Use the existing project package names for reusable implementation and the established team notebook/model ownership. New experimental configuration, notebooks and results live under `experiments/`. This file is the single canonical dataset plan; update it with accepted implementation decisions and measured deviations.

## 10. Setup finalization record - 2026-11-07

The user requested an ongoing journal and explicit paper attribution. Journal.md now records that mapping, future milestone states and the full project route. The JSON configuration freezes the four exact graphs, sixteen-host layout, thirteen labels, 348-episode matrix, path intervention, observation contract, seed groups and runtime/artifact targets. KAGGLE_RUNS.md distinguishes planned notebook identities and expected outputs from submitted versions and verified files.

Implementation should consume the JSON design contract and persist a separate preflight-resolved configuration. Exact installed patch versions, actual guest image/backend and sustainable bottleneck capacity are measured preflight outputs. The hop intervention uses seed 303 for the primary prediction report, with its other seeds retained for declared development or physical measurements. Configuration changes must update this plan and the journal together before capture. The journal is the decision/execution record; it does not introduce a competing experimental protocol.

An assessment-only review verified graph connectivity, route validity, hop counts, matrix arithmetic and group-split consistency. Its two accepted clarifications freeze shared workload capacity references on T1 and randomize hop-condition order reproducibly. Runtime and dataset acceptance remain pending.
