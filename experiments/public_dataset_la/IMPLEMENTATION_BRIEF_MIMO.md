# Kaggle DDoS data and detector implementation brief

Date: 2026-11-09, Asia/Calcutta. Status: approved direction from user; implementation not started by this brief. Canonical decisions live in Journal.md; this file is the implementation contract, not another project copy.

## 1. Objective and boundaries

Build reproducible Kaggle data products for NF-ToN-IoT-v3, NF-BoT-IoT-v3 and LAN-SDN-NIDS; compare diverse classifiers, selected ensembles and a gated mixture of experts. Choose using development evidence with frozen final tests. No claim of universal detection, best-ever performance, novel source dataset, mitigation effectiveness or distributed scalability follows from these experiments.

Canonical root: D:/Bunker/BaseCamp/WirelessCommunication/DDoS_Prevention_and_Mitigation. Preserve existing investigation notebooks, historical outputs, legacy repository and topology experiment. All new computational work stays under experiments/public_dataset_la/. Run data processing, plotting computations, fitting and evaluation on Kaggle. Local machine holds source, briefs, compact reports and optionally verified Parquet downloads. Never train locally to substitute for a Kaggle run.

Implementation owner: one OpenCode MiMo v2.6 worker. Codex owns architecture, research, review and acceptance. Luna High may execute bounded tests, Kaggle operations and bookkeeping. No other Codex subagents. The user's Sol Medium consultation is optional, assessment only, capped at five minutes if invoked; fixes remain with MiMo. Do not silently change model or provider.

Observed CLI: OpenCode v2.0.16; stored OpenCode Console Personal authentication; model catalog exposes opencode/mimo-v2.6-flash-free. This establishes neither inference entitlement nor equivalence to a distinct non-Flash MiMo v2.6 model. Before implementation verify intended variant with the user if unresolved, run one bounded connectivity probe, record exact returned model/provider and stop on access failure. No paid fallback, installation, provider cycling or credentials in outputs. Only one source-code writer at a time. No worker may submit notebooks until reviewed source and preflight gates pass.

## 2. Existing evidence and input contracts

Read Journal.md latest entries, KAGGLE_RUNS.md, input_manifest.json, build_investigation_notebook.py, check_investigation.py and the v2 retrieved reports selectively. Do not recursively ingest all run artifacts. Existing stable investigation identity: satyapaladugu/sdn-public-dataset-investigation. Preserve its purpose; EDA and preprocessing are separate purposes with stable identities to resolve before upload.

Inputs observed, not permanently guaranteed:

| Source | Access | Observed rows | Owner |
|---|---|---:|---|
| NF-ToN-IoT-v3 | seyhed/nf-ton-iot-v3, observed v1 | 27,520,260 | Prithvi |
| NF-BoT-IoT-v3 | seyhed/nf-bot-iot-v3, observed v1 | 16,933,808 | Roydon |
| LAN-SDN-NIDS | https://doi.org/10.21950/QMAXKP, observed v3.0; five raw topology CSVs | 1,125,059 | Satya |

LAN official API: https://edatos.consorciomadrono.es/api/access/datafile/{id}; Linear55750, Mesh55751, Star55752, Subnets55753, Tree55754. Verify release metadata, official hashes and mounted files each run. Consolidated Parquet55755 is a lineage reference, never additional examples. Source mounts are read only; temporary downloads outside saved output. Respect original attribution and redistribution terms; derived datasets private by default and license metadata must not imply unrestricted source licensing.

NF sources have the same 55-column schema; LAN raw CSVs have 47 columns. BoT contains missing/nonfinite rates. LAN raw NaNs differ from zero-filled aggregate; row-level normalized lineage remains unverified. Default exclude new_mac_ratio pending creator-method ambiguity. Existing reports are evidence, not fitted preprocessing artifacts.

Primary label: normalized original DDoS ->1; benign and other original attacks ->0. Preserve original attack family, original binary label, benign flag and target consistency checks. Other attacks are not benign. Do not silently relabel DoS as DDoS. Record excluded/ambiguous rows with reasons and class/source totals.

Keep metadata separate from predictors: source dataset/version/file/hash/row ordinal, source_row_id, capture/episode when recoverable, timestamps with units, endpoints, topology, original labels, split/group IDs. Stable row ID = SHA256(source file SHA256 + separator + original logical row ordinal); do not use unstable Spark partition numbering. Derivative records retain parent row/window IDs. Do not expose raw endpoint values in plots/logs unnecessarily.

## 3. Notebook and data architecture

First increment contains TWO engineering notebooks, each with explicit ToN, BoT and LAN stages. This satisfies investigation then independent preprocessing for all three without six duplicated engineering implementations:

- notebooks/02_engineering_eda.ipynb: source architecture/dictionary, full-table Spark quality and summaries, bounded and explicitly sampled expensive plots, event/split feasibility, leakage risks and candidate transformations. No global fitted cleaning before split.
- notebooks/03_engineering_preprocessing.ipynb: audit reproduction, label normalization, split/group contracts, deterministic sanitation, train-fitted transformations, derivatives and persisted Parquet/transforms/manifests.
- notebooks/la1_prithvi_ton.ipynb, la1_roydon_bot.ipynb, la1_satya_lan.ipynb: AFTER methodology acceptance, standalone presentation notebooks reproducing dataset explanation, EDA, split decisions, preprocessing and finalization. At least five substantive plots each; more where useful. Inline preprocessing is visible, not hidden behind project helper imports. Explain measured inferences and limitations beside plots.
- notebooks/04_classifier_benchmark.ipynb, 05_ensemble_comparison.ipynb, 06_moe_comparison.ipynb: later research training stages; source-specific LA2 presentation views come after results. Dataset ownership does not constrain model families to three per person.

Use existing investigation instrumentation where appropriate. Shared notebook-generation/observability utilities may avoid source duplication, but generated standalone notebooks must expose scientific preprocessing. Do not rerun expensive data work merely to render presentation notebooks: attach version-pinned artifacts, reproduce essential checks and show exact upstream provenance; provide rebuild mode and loading mode explicitly.

Remote flow: managed raw inputs -> engineering EDA reports -> frozen split/feature method -> preprocessing Parquet and fitted transforms -> saved notebook outputs/private versioned Kaggle Dataset -> benchmark -> OOF scores -> ensemble/MoE -> immutable evaluation. Save all important outputs on Kaggle and verify downstream reattachment before declaring persistence complete.

## 4. Preprocessing specification

1. Parse with explicit versioned schema. Count raw/parsed/rejected records; stop on unexpected schema or unexplained row loss. Record malformed rows, invalid timestamps, target inconsistencies, NaN/+Inf/-Inf per field, impossible counts/durations and source-specific conventions. Nonfinite numeric values become missing with provenance, never arbitrary huge constants. Distinguish undefined rates from true zero.
2. Freeze target and predictor exclusions before model training. Exclude labels, topology/source identities, raw IP/MAC/ports and timestamps from primary predictors. Audit selector-like IDs, DNS transaction IDs and simulator artifacts individually. Protocol and legitimate flags are categorical/bit-semantic features, not arbitrary ordinal numbers. Retain excluded fields only in metadata. Recompute duplicate hashes on selected native and common representations.
3. Separate source-row identity, exact-record duplicates, feature-vector duplicates and capture/session groups. Conflicting target groups: quarantine all members with counts; evaluate/report selection bias. Prevent selected-feature duplicates across partitions by retaining later holdout observations and purging matching earlier observations. Predeclare this rule; maintain untouched pre-cleaning audits. Different original attack families with the same binary target are recorded, not automatically contradictory binary labels. Recheck collisions after transformations without using test scores to redesign features.
4. LAN initial split: Linear+Tree+Mesh train, Star development, Subnets final test. NF: approximately60/20/20 chronological capture/episode blocks only after coverage/provenance feasibility. No unconditional random rows. If episode identity unavailable, label evaluation as time-block transfer; do not claim independent episodes. Group/purge boundary-spanning sessions and time-derived feature overlap; determine embargo from actual feature windows/timeouts. Stop for review if class coverage collapses or source chronology cannot support the intended claim.
5. Freeze split manifests before inferential EDA/model selection. Full-dataset descriptive quality/label counts may be reported; development plots and feature/threshold choices use training/development only. Do not inspect final-test feature importance, error cases or labels to optimize models.
6. Fit numeric median imputation on training only and preserve missingness flags where meaningful; all-missing train fields are dropped with explicit registry. Compare against justified zero interpretation only where measurement definition supports it. Standardize numeric inputs for LR/SVM/MLP/FM; trees use a separate unscaled pipeline. Fit categorical vocabularies on training; reserve unknown category. No target encoding in initial increment. All preprocessing refits independently within OOF folds.
7. Preserve heavy tails initially. No blanket IQR deletion, winsorization or dropping attack bursts as outliers. Optional nonnegative log1p or training-quantile clipping is an ablation with range and clipping counts. Never invent packet data. Class weights or recorded training sampling address imbalance; no default SMOTE across incompatible categorical/physical flow fields. Tests retain recorded class mix.
8. Candidate mathematical derivatives: directional total bytes/packets, mean bytes per packet, directional asymmetry, validated rates and IAT variability where required measurements exist. Specify units, direction, denominator=0 behavior and missingness. Check dimensions and recompute against source measurements. Metadata/time-based features must be causal with disjoint capture namespaces; completed-flow features imply end-of-flow detection, not guaranteed early warning. No fabricated traffic sequence or graph from unrelated rows.
9. Native NF and native LAN views remain separate. Common crossover registry records feature name, source field, extractor definition, observation unit, direction, units, missingness and proof of equivalence. LAN hop/aggregated OpenFlow observations may not equal bidirectional NetFlow records. Fail closed if no adequate shared representation. Any common window alternative is a separate reviewed experiment and requires compatible timestamp/capture provenance. Availability masks alone do not cure semantic mismatch.

Persist typed cleaned observational Parquet plus metadata/split manifests, and model-ready Parquet per training condition/transform version. Do not store nine redundant feature-table copies: reuse identical pipeline artifacts by hash. Distinguish deterministic sanitation from fitted preprocessing. LA1 must show both and identify training rows used to fit each statistic. LA2 loads those artifacts for final fits, but OOF still fits preprocessing inside each fold.

## 5. Revised finite model portfolio and matrix

Train all TWELVE candidates in each feasible condition, replacing the previous fixed nine and predetermined LR/RF/GBT stack:

| Backend | Candidates | Reason |
|---|---|---|
| Spark ML | LogisticRegression, DecisionTreeClassifier, RandomForestClassifier, GBTClassifier | linear reference; interpretable tree; bagging; boosting |
| Spark ML | NaiveBayes(gaussian), LinearSVC, MultilayerPerceptronClassifier, FMClassifier | probabilistic reference, margin, neural nonlinear, pair interactions |
| Kaggle Python | HistGradientBoostingClassifier, XGBoost, LightGBM, CatBoost | efficient histogram boosting and established strong tabular competitors |

48 condition/family configurations =12 x [ToN,BoT,ToN+BoT,LAN], before search/refits/ensembles. Eight Spark families preserve Big Data ML coverage; four Python challengers run bounded equal-budget cohorts, never collect44M rows to the driver. Gaussian NB is continuous; FM is factorization machine, not expert router. Verify installed API support before committing runtime dependencies. No RBF SVM/KNN at full scale; no temporal CNN/LSTM without genuine sequence contract.

Use a common training row manifest per condition for ALL candidates. ToN/BoT/mixture comparisons use equal total rows; mixture source allocation recorded. Resource preflight measures representative1k/5k/20k then larger feasible cases, fit time, peak memory and batched inference; select final common row budget from evidence. Allow one fixed smoke configuration then at most five development configurations per family initially, with equal declared time budgets. Log timeouts/failures as results. Additional champion-scale runs are separate from matched comparison. Predeclare exact limits in run configuration before launch; no unbounded train-everything sweeps.

Native suite: all12 on four conditions. Common-view suite, only after alignment acceptance: all12 on the four compatible conditions and evaluate each trained model on each compatible source (train-condition x test-source matrix). If LAN incompatible, explicitly mark cells N/A and run NF crossover plus native LAN; never silently report a full three-domain matrix. A ToN+BoT mixed model evaluated on ToN is known-source testing. Separate leave-one-source-out experiment excludes destination from experts, transformations, calibration, router and tuning. No using destination statistics for zero-adaptation claims.

## 6. Selection, ensembles and MoE

Development selection: compare PR-AUC, DDoS recall at benign-FPR operating points1%,0.1%,0.01% where benign counts support estimation, MCC, calibration and inference cost. Report numerator/denominator and confidence uncertainty; do not claim a tiny FPR from too few benign observations. Choose operating constraint and latency budget before tuning, then maximize macro source recall subject to them, with worst-source recall and cost as tie breakers. Report full trade-off curves if no acceptable feasible model. No accuracy-only winner or single pooled score hiding source failure.

Select up to four complementary candidates from grouped OOF performance, pairwise error correlation, source/family failures and cost. Always retain best single as baseline. Compare equal probability average, validation-weighted nonnegative average, and regularized LR stack on exactly the same OOF matrix; hard voting optional diagnostic. All scores join by row_id/fold_id/model/pipeline hash, with no missing or duplicate predictions. Default three feasible group folds; stop if adequate training/class coverage cannot be obtained. A training-row score from a model fitted on that row cannot train the stack.

MoE experiment: use up to three domain specialists plus optional pooled generalist, all exposing DDoS probability on the SAME accepted feature contract. For each OOF fold refit expert preprocessing/models excluding the held-out groups in all sources; score held-out rows with every eligible expert, including off-domain experts. Train a small softmax gate on runtime feature vector x using mixture binary cross-entropy on these OOF probabilities: p(y=1|x)=sum_e softmax(g(x))_e * p_e(x). Labels supervise detection loss during training; dataset ID is neither gate target nor input. Gate feature transforms fit training folds only. Group-cross-validate gate regularization on OOF development structure; freeze experts, then refit them on designated full training. Keep calibration/threshold data separate from gate fitting.

Compare dense gating, top-2 routing and a static average of the SAME experts. Dense MoE evaluates all experts and has no conditional-compute saving. Top-2 must select experts before expert inference, renormalize weights and evaluate only selected experts; measure batching/dispatch costs. Record expert utilization, entropy, collapse, routing regret versus evaluator-only oracle, source failure and uncertainty. Oracle is an analysis bound, never runtime input. Hard top-1 is optional only after soft gate works. If no shared LAN contract, initial MoE is NF-only; LAN specialist stays separate with explicit limitation. Do not route using source identity to claim unknown-network adaptation. Gate/generalist fallback policy is validated development configuration, not automatic confidence safety.

Use source/capture-group bootstrap intervals when independent groups support them; disclose unsupported uncertainty with few groups. Fit/calibrate/threshold/select on development only, including within-source and development crossover results. Final tests scored once after freeze; report all frozen candidates without selecting architecture retrospectively from test scores.

Metrics artifacts: TP/FP/FN/TN, precision/recall/F1, exact PR-AUC convention (AP versus trapezoid), ROC-AUC, MCC, balanced accuracy, benign-only FPR, false DDoS calls for each other attack family, per-source/topology, Brier/reliability, throughput/batch size, latency scope, fit/predict time, memory and model size. Separate preprocessing time from scoring and total. Spark local executor on Kaggle does not prove multi-node scaling. Save row-level held-out scores with provenance for paired analysis, respecting storage.

## 7. Persistence and local storage

One existing KAGGLE_RUNS.md map, one stable identity per notebook purpose, versions for revisions. User authorized Kaggle CLI; verify account/access and check suitable existing identities before creating new ones. Do not interrupt healthy runs. Private output Dataset(s) may be created from version-specific saved notebook outputs; preflight supported API/UI path before bulk publication, and do not put credentials in notebooks. Verify terms before redistribution. A local CLI upload requires local files; do not imply it publishes remote files magically. If remote dataset creation path is unavailable, retain saved version outputs as upstream inputs and report Dataset publication pending.

Runtime root /kaggle/working/experiments/public_dataset_la/runs/<run-id>/ contains environment.json, resolved_config.json, provenance.json, cell_ledger.json, logs/, reports/, figures/, contracts/, manifests/, parquet/, transforms/, models/, scores/ as applicable; SHA256 manifests written after finalization. Keep active logs outside immutable checksum snapshot or clearly distinguish final snapshots. Verify row/schema/count/hash readback, saved version and a downstream attachment read before declaring data ready. Models include preprocessing, column order/types, target definition, source/split hashes, calibration and threshold; validate fresh-process reload.

Kaggle official docs currently describe20GB saved notebook output; verify actual runtime quota and disk before launch. Stage compressed Parquet shards and estimate total from pilot, keeping headroom for Spark spill. Avoid co-storing raw9GB CSV plus redundant transformed copies. If projected saved output exceeds quota, shard by source/stable notebook purpose with explicit manifest, never silently truncate.

Local D: measured2026-11-09 about9.64GB free (decimal). Default no bulk download until compressed manifests known. Reserve at least5GiB local free and allow at most2GiB bulk per automatic retrieval; download only if final uncompressed size plus temporary archive/extraction requirements fit, use incremental shards/checksums and stop below reserve. Otherwise retain remote data and retrieve compact reports/models as feasible. Do not download raw CSVs. User preference to keep Parquet locally is conditional on measured capacity, not a promise.

## 8. Notebook observability and acceptance

Each setup/computational cell has stable ID, purpose/start, inputs/outputs, progress, status, elapsed time and flushed logs. Setup prints actual Python, executable, package versions, source snapshot, runtime/hardware/JVM/Spark settings and intended dependencies. Save rich plots/tables separately plus incrementally captured executed notebook/cell logs where supported. Preserve tracebacks and partial outputs, no secret environment dump. Actual dependencies lock after successful managed-runtime preflight; no arbitrary latest installs during final runs.

Milestones:
1. Worker returns EDA/preprocessing source + metadata + dependency spec and minimal bounded preflight, before bulk execution. Codex reviews parse/split/fit and resource paths. Luna verifies fresh-kernel remote smoke, row conservation, nonfinite handling, IDs, no group overlap, temporal availability, no transform leakage and persistence/readback. No classifier benchmark before data method acceptance.
2. Execute full remote EDA, review source-specific findings, then revise preprocessing version and run full preparation. Deliver verified Parquet, contracts, lineage, fit metadata, split/class counts, quarantine counts and output map. Projected common feature fields must be individually justified; normalized LAN lineage verified at row level or discrepancy reported.
3. Produce three LA1 presentation notebooks with owners, five-plus substantive plots each, source architecture, methodology, before/after counts, limitations and links to saved outputs. Native topologies described from source scripts, not fabricated from NF records.
4. Resource preflight -> matched12-family benchmark -> reviewed champion set -> stack -> MoE -> frozen final evaluation. User receives metrics, figures, failure inferences and full inference bundles, all Kaggle-persisted. Later LA2 presentation assignment follows the new dataset ownership and actual results.

Worker completion format: exact source hashes/session/model; files/diff; checks and Kaggle notebook/version/run; verified artifact paths; failures; assumptions requiring review. Keep full OpenCode logs under runs/<implementation-run>/logs/. Limit repairs to two evidence-driven attempts per repeated failure, then report diagnosis. Never modify historical evidence or lower an acceptance criterion just to pass.

## 9. Research inspiration and limits

See Journal.md entry2026-11-09 for paper-to-decision mapping and current review status. This is a bounded research synthesis, not exhaustive literature or proof of novelty. Expert routing, stacking and merging sources are established methods; our scientific value must come from an honest, reproducible evaluation under dataset shift and real resource limits.
