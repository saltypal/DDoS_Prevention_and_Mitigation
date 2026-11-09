"""Development-only OOF comparisons, with explicit domain-expert training for NF MoE."""
from pathlib import Path
import json
import time
import joblib
import numpy as np
import pandas as pd
from scipy.special import logit
from sklearn.linear_model import LogisticRegression
from sdn_ddos.models.benchmark import execute_fit
from sdn_ddos.models.combine import ProbabilityMean, WeightedMean, FeatureGate, grouped_folds
from sdn_ddos.evaluation.metrics import evaluate, choose_threshold
from sdn_ddos.runtime.run import write_json, sha256
from sdn_ddos.evaluation.alignment import align_scores as score_column


def locate_benchmark(root):
    hits = list(Path(root).rglob('reports/benchmark.json'))
    if len(hits) != 1:
        raise ValueError(f'Expected one version-specific benchmark, found {hits}')
    return hits[0].parent.parent, json.loads(hits[0].read_text())


def select(ledger, condition, root, maximum=3):
    entries = [r for r in ledger if r['condition'] == condition and r['status'] == 'complete']
    entries.sort(key=lambda r: (r['development_metrics']['average_precision'] or -1, -r['seconds']), reverse=True)
    chosen, columns = [], []
    canonical_rows = pd.read_parquet(root / 'cohorts' / condition / 'selection.parquet', columns=['row_id'])
    for entry in entries:
        scores = score_column(root / 'models' / f'{condition}-{entry["family"]}' / 'selection-scores.parquet', canonical_rows)
        # Diversity is a development criterion, not a test-dependent choice.
        if columns and any(np.std(scores) > 0 and np.std(other) > 0 and abs(np.corrcoef(scores, other)[0, 1]) > 0.995 for other in columns):
            continue
        chosen.append(entry['family'])
        columns.append(scores)
        if len(chosen) >= maximum:
            break
    if not chosen:
        raise RuntimeError(f'No successful base models for {condition}')
    return chosen


def oof_matrix(table, experts, directory, config, run):
    """Each expert specifies its training cohort and family; held-out groups are excluded globally."""
    directory.mkdir(parents=True, exist_ok=False)
    matrix = np.full((len(table), len(experts)), np.nan)
    assignments = np.full(len(table), -1, dtype=int)
    for fold, (train_indices, heldout_indices) in enumerate(grouped_folds(table, config.get('folds', 3))):
        heldout = table.iloc[heldout_indices].reset_index(drop=True)
        heldout_path = directory / f'fold-{fold}-heldout.parquet'
        heldout.to_parquet(heldout_path, index=False)
        assignments[heldout_indices] = fold
        feature_groups, sessions = set(heldout['feature_group']), set(heldout['session_group'])
        for column, expert in enumerate(experts):
            train = pd.read_parquet(expert['train'])
            train = train[~train['feature_group'].isin(feature_groups) & ~train['session_group'].isin(sessions)].reset_index(drop=True)
            if train['target'].nunique() != 2:
                raise RuntimeError(f'OOF {expert["name"]} fold {fold} lacks class coverage')
            training = directory / f'fold-{fold}-{column}-train.parquet'
            train.to_parquet(training, index=False)
            request = {'family': expert['family'], 'contract': expert['contract'], 'train': str(training),
                       'predict': {'heldout': str(heldout_path)}, 'output': str(directory / f'fold-{fold}-expert-{column}')}
            print('OOF', fold, expert['name'], 'fit rows', len(train), 'heldout', len(heldout), flush=True)
            outcome = execute_fit(request, config.get('fit_timeout_seconds', 600))
            write_json(directory / f'fold-{fold}-expert-{column}-status.json', outcome)
            if outcome['status'] != 'complete':
                raise RuntimeError(f'OOF fit failed: {outcome}')
            matrix[heldout_indices, column] = score_column(Path(request['output']) / 'heldout-scores.parquet', heldout)
    if (assignments < 0).any() or not np.isfinite(matrix).all():
        raise RuntimeError('Incomplete OOF score matrix')
    scores = table[['row_id', 'feature_group', 'session_group']].copy()
    scores['fold'] = assignments
    for index, expert in enumerate(experts):
        scores[expert['name']] = matrix[:, index]
    scores.to_parquet(directory / 'oof-scores.parquet', index=False)
    write_json(directory / 'experts.json', experts)
    return matrix


def calibrated_result(name, raw, tables, config, destination):
    calibrator = LogisticRegression(C=1.0, max_iter=300)
    calibrator.fit(logit(np.clip(raw['calibration'], 1e-6, 1-1e-6))[:, None], tables['calibration']['target'])
    scores = {part: calibrator.predict_proba(logit(np.clip(values, 1e-6, 1-1e-6))[:, None])[:, 1] for part, values in raw.items()}
    threshold = choose_threshold(tables['threshold'], scores['threshold'], config.get('benign_fpr_limit', 0.01))
    result = evaluate(tables['selection'], scores['selection'], threshold)
    result.update(name=name, scope='development only; final tests unopened', calibration='reserved-development Platt scaling')
    destination.mkdir(parents=True)
    joblib.dump(calibrator, destination / 'calibrator.joblib')
    write_json(destination / 'metrics.json', result)
    from sdn_ddos.evaluation.plots import diagnostics
    diagnostics(tables['selection'],scores['selection'],destination/'diagnostics',threshold,calibrated=True)
    for part, values in scores.items():
        tables[part][['row_id']].assign(raw_score=raw[part], score=values).to_parquet(destination / f'{part}-scores.parquet', index=False)
    return result


def ensembles(config, run):
    root, ledger = locate_benchmark(config.get('benchmark_root', '/kaggle/input'))
    results = []
    for condition in config.get('conditions', ['ton', 'bot', 'mixture', 'lan']):
        with run.stage(f'{condition}-oof-ensembles'):
            cohort = root / 'cohorts' / condition
            info = json.loads((cohort / 'cohort.json').read_text())
            train = pd.read_parquet(cohort / 'train.parquet')
            tables = {part: pd.read_parquet(cohort / f'{part}.parquet') for part in ('selection', 'calibration', 'threshold')}
            chosen = select(ledger, condition, root, config.get('maximum_members', 3))
            experts = [{'name': family, 'family': family, 'contract': info['contract'], 'train': str(cohort / 'train.parquet')}
                       for family in chosen]
            oof = oof_matrix(train, experts, run.root / 'oof' / condition, config, run)
            scores = {part: np.column_stack([score_column(root / 'models' / f'{condition}-{family}' / f'{part}-scores.parquet', table)
                                             for family in chosen]) for part, table in tables.items()}
            estimators = {'equal_mean': ProbabilityMean(), 'weighted_mean': WeightedMean(),
                          'stack': LogisticRegression(C=1.0, max_iter=500)}
            for name, estimator in estimators.items():
                estimator.fit(oof, train['target'].to_numpy())
                raw = {part: estimator.predict_proba(values)[:, 1] for part, values in scores.items()}
                destination = run.root / 'models' / f'{condition}-{name}'
                metrics = calibrated_result(name, raw, tables, config, destination)
                joblib.dump(estimator, destination / 'combiner.joblib')
                write_json(destination / 'bundle.json', {'members': chosen, 'condition': condition, 'contract': info['contract'],
                           'source_benchmark': str(root), 'training_hash': sha256(cohort / 'train.parquet'),
                           'threshold': metrics['threshold'], 'scope': info['scope']})
                results.append(dict(condition=condition, **metrics))
            # Same calibrated evaluation protocol for each chosen constituent.
            for index, family in enumerate(chosen):
                raw = {part: values[:, index] for part, values in scores.items()}
                destination = run.root / 'models' / f'{condition}-single-{family}'
                metrics = calibrated_result(f'single-{family}', raw, tables, config, destination)
                identity = ProbabilityMean().fit(oof[:, [index]], train['target'].to_numpy())
                joblib.dump(identity, destination / 'combiner.joblib')
                write_json(destination / 'bundle.json', {'members': [family], 'condition': condition,
                           'contract': info['contract'], 'threshold': metrics['threshold'], 'scope': info['scope']})
                results.append(dict(condition=condition, **metrics))
            write_json(run.root / 'reports' / 'ensemble-development.json', results)
    return results


def domain_moe(config, run):
    """NF-only domain MoE until a LAN/NetFlow common contract has been validated."""
    root, ledger = locate_benchmark(config.get('benchmark_root', '/kaggle/input'))
    mixture = root / 'cohorts' / 'mixture'
    info = json.loads((mixture / 'cohort.json').read_text())
    train = pd.read_parquet(mixture / 'train.parquet')
    experts = []
    for condition in ('ton', 'bot', 'mixture'):
        cohort = root / 'cohorts' / condition
        expert_info = json.loads((cohort / 'cohort.json').read_text())
        if any(expert_info['contract'][kind] != info['contract'][kind] for kind in ('numeric', 'categorical')):
            raise RuntimeError('Domain-expert input contracts differ')
        family = select(ledger, condition, root, 1)[0]
        experts.append({'name': f'{condition}-{family}', 'family': family, 'contract': info['contract'],
                        'train': str(cohort / 'train.parquet'), 'condition': condition})
    with run.stage('nf-domain-expert-oof'):
        oof = oof_matrix(train, experts, run.root / 'oof' / 'nf-domain', config, run)
    tables = {part: pd.read_parquet(mixture / f'{part}.parquet') for part in ('selection', 'calibration', 'threshold')}
    # Domain experts must be evaluated on every mixture-development row, including off-domain rows.
    score_matrix = {part: [] for part in tables}
    with run.stage('nf-domain-expert-full-refits'):
        for index, expert in enumerate(experts):
            request = dict(family=expert['family'], contract=expert['contract'], train=expert['train'],
                           predict={part: str(mixture / f'{part}.parquet') for part in tables},
                           output=str(run.root / 'models' / f'domain-expert-{index}'))
            outcome = execute_fit(request, config.get('fit_timeout_seconds', 600))
            if outcome['status'] != 'complete':
                raise RuntimeError(f'Domain expert failed: {outcome}')
            for part, table in tables.items():
                score_matrix[part].append(score_column(Path(request['output']) / f'{part}-scores.parquet', table))
    score_matrix = {part: np.column_stack(values) for part, values in score_matrix.items()}
    numeric = info['contract']['numeric']
    with run.stage('nf-domain-gate'):
        gate = FeatureGate().fit(train[numeric], oof, train['target'].to_numpy())
        results = []
        for name, k in [('dense_moe', None), ('top2_moe', 2)]:
            raw = {part: gate.predict(table[numeric], score_matrix[part], top_k=k) for part, table in tables.items()}
            destination = run.root / 'models' / name
            metrics = calibrated_result(name, raw, tables, config, destination)
            joblib.dump(gate, destination / 'gate.joblib')
            weights = gate.route(tables['selection'][numeric], top_k=k)
            write_json(destination / 'bundle.json', {'experts': experts, 'gate_features': numeric,
                       'utilization': (weights > 0).mean(axis=0).tolist(), 'mean_gate_weight': weights.mean(axis=0).tolist(),
                       'threshold': metrics['threshold'], 'top_k': k, 'contract': info['contract'],
                       'timing_scope': 'precomputed dense expert scores; no sparse-compute speed claim',
                       'LAN': 'not included; common observation contract unverified'})
            results.append(metrics)
        static = ProbabilityMean().fit(oof, train['target'].to_numpy())
        raw = {part: static.predict_proba(values)[:, 1] for part, values in score_matrix.items()}
        results.append(calibrated_result('same_experts_static_mean', raw, tables, config, run.root / 'models' / 'same-experts-static'))
        write_json(run.root / 'reports' / 'moe-development.json', results)
    return results
