# Dataset explanations for LA1 / LA2

These are public captured/emulated traffic datasets. This project does not claim to have generated them or collected production traffic.

| Owner | Selected source | Collection architecture | Our selected modality |
|---|---|---|---|
| Prithvi | NF-ToN-IoT-v3 | Original ToN edge/fog/cloud lab, Windows/Linux/Kali hosts and VMs; VMware NSX/vCloud SDN/NFV management | Network PCAPs subsequently re-extracted into NF-v3 flow features; no automatic host/sensor/controller modality |
| Roydon | NF-BoT-IoT-v3 | Original BoT ESXi/vSphere lab, pfSense, Kali attackers, target VMs, Node-RED/MQTT IoT services | NF-v3 network re-extraction; not an OpenFlow controller dataset |
| Satya | LAN-SDN-NIDS | Containernet, OVS3.1.0/OpenFlow1.3, OpenDaylight Oxygen0.8.4; five topologies | Creator subflow features with packet/flow and OpenFlow observations |

LAN switch counts from inspected creator scripts: Linear6, Tree7, Star5, Mesh4, Subnets6. Containers/collectors are additional nodes. Topology scripts were inspected, not reconstructed in this project.

NF target field is `Attack`; original `Label` distinguishes benign versus any attack and must never be a predictor. LAN target is `label`.
Primary task here maps original DDoS to1 and everything else to0. DoS and other attacks are not benign; report benign-only false alarms and other-attack errors separately.

LA1 must show source release/schema/units, missing/nonfinite values, predictor exclusions, duplication, split coverage and quarantine effects, then development plots and their actual inferences.
The data pipeline preserves original labels and typed source measurements in Parquet. Learned imputation, categorical vocabulary and scaling live inside training-fitted pipelines. Do not describe sanitation as a globally fitted model transformation.

LAN uses topology holdout; NF uses chronology with a declared flow-boundary embargo and overlap purge. These protocols may fail class coverage; a failure needs review rather than a silent random split. No claim of independent-episode transfer follows without episode provenance. Full class counts are descriptive; data-driven method selection must protect final-test observations.

Models receive completed flow/subflow measurements. Offline classification does not establish detection before a flow completes or live mitigation effectiveness.
NF-v3 input schemas support NF crossover after exact contract checks. LAN shared features need observation/unit/direction verification; absent OpenFlow measurements are not manufactured.

Primary sources: [NF-v3](https://staff.itee.uq.edu.au/marius/NIDS_datasets/), [methods](https://arxiv.org/abs/2503.04404), [ToN architecture](https://arxiv.org/abs/2010.08522), [BoT original paper](https://arxiv.org/abs/1811.00701), [LAN release](https://doi.org/10.21950/QMAXKP).
