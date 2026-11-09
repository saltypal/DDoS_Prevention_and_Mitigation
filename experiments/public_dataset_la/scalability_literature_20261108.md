# Scalable detection and mitigation: bounded literature review

Date: 2026-11-08. Sources discovered with alphaXiv and primary web sources. This is not an exhaustive survey or a novelty determination. No models or mitigation policies were implemented in this review.

## Evidence and inspiration

- Canopy, NSDI2026: https://www.usenix.org/conference/nsdi26/presentation/xiao . Official abstract reports production above100Tbps through distributed dynamic load balancing and programmable-switch traffic compression. Full evaluation paper was not inspected here. This supports system partitioning, not a throughput claim for our detector.
- Graph Neural Network-Based DDoS Protection for Data Center Infrastructure: https://arxiv.org/abs/2603.13694 . Relevant full methods/limitations inspected through alphaXiv. Temporal host-flow graphs and hierarchical pooling are useful candidates; authors explicitly say inference throughput/latency were not measured. Do not repeat architecture speed claims as measurements.
- Collaborative P4-SDN DDoS Detection and Mitigation with Early-Exit Neural Networks: https://arxiv.org/abs/2509.12291 . Relevant full methods inspected through alphaXiv. Inspiration: early confident decisions and additional processing for uncertain cases. Not proof of universal hardware line rate.
- A Feature-Rich Embedded NIDS with eBPF/XDP: https://arxiv.org/abs/2609.12605 . Relevant methods inspected. Actual kernel capture/filtering with window/per-source detection; reported3Gbps replay capacity must not be presented as detector capacity. Recovery and source attribution require care.
- Cross-Domain Joint DDoS Detection in Multi-Controller SDN: https://arxiv.org/abs/2608.17507 . Relevant full methods inspected: confidence fusion/fallback, three controllers,24hosts,10runs. Promising coordination mechanism; small-scale evaluation and reliable/trusted-controller assumptions limit claims.
- THARN/Q-Mitigate, published2026-11-03: https://doi.org/10.1186/s13677-025-00786-1 . Publisher methods and limitations inspected. RL mitigation specified but not executed in simulated/real controller; throughput profiling absent. Proposed mechanism, not validated mitigation.
- Detecting and Mitigating DDoS Attacks with AI: https://arxiv.org/abs/2503.17867 . Relevant survey pages inspected: rule consolidation, learned mitigation, generalization and detection-delay gaps.
- Standards: FlowSpec https://www.rfc-editor.org/rfc/rfc8955 ; DOTS https://www.rfc-editor.org/info/rfc9132/ ; SYN defenses https://www.rfc-editor.org/rfc/rfc4987 ; destination blackholing https://www.rfc-editor.org/rfc/rfc7999 . Rule distribution, assistance signaling, protocol defense and emergency destination discard are distinct mechanisms.

## Provisional engineering direction

Dataset investigation is complete. Prepared data, shared crossover features, graph windows and evaluation splits remain pending. No universal-network guarantee is established.

Compare flow-statistical, temporal and bounded graph experts, plus an optional SDN-control expert when telemetry exists. Compare graph aggregates against a sampled-neighborhood GNN before retaining complexity. Raw identifiers can define graph connectivity but must not become learned identity shortcuts or label-oracle features. Keep unrelated captures in separate namespaces and timelines. Budget active entities, edges, windows, neighborhoods, state expiry, queue size and expert execution. A gate that evaluates every expert does not reduce expert computation; test conditional execution and graph-building costs end to end.

Mitigation families: selective filtering; rate limits/shaping; connection/SYN admission; application quotas/challenges; scrubbing diversion; traffic engineering/anycast; controller/flow-table protection; quarantine; anti-spoofing/reflection hardening; upstream ACL/FlowSpec coordination; emergency blackholing; moving-target defense; resource scaling/cache shielding. This is a major-family taxonomy, not every published variant. Rules, optimization, bandits/RL and multi-agent methods select actions rather than constitute new packet-enforcement mechanisms.

First policy proposal: observe, verify persistent evidence, apply temporary scoped rate limiting, escalate to bounded drop/diversion if service remains impaired, then expire/recover with hysteresis. Tune timing and thresholds experimentally. Measure benign goodput, service latency, detection-to-enforcement delay, recovery, rule churn and controller load. Static labeled CSVs lack action-conditioned rewards and cannot validate mitigation policies alone. A saturated upstream link requires upstream enforcement/assistance.
