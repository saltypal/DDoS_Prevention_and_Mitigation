"""Explicit frozen base-model crossover, using one matched test cohort per source.

This stage never chooses a new model from final-test scores. Combined model final
evaluation must use its separately persisted calibrator/threshold and inference bundle.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.special import logit
from sklearn.linear_model import LogisticRegression
from sdn_ddos.models.benchmark import resolve_prepared
from sdn_ddos.models.orchestrate import locate_benchmark, score_column
from sdn_ddos.models.inference import ClassifierBundle, EnsembleBundle, DomainMixtureBundle
from sdn_ddos.evaluation.metrics import evaluate, choose_threshold
from sdn_ddos.runtime.run import write_json, sha256


def freeze_candidates(config, run):
    root, ledger = locate_benchmark(config['benchmark_root'])
    scope = json.loads((root / 'resolved_config.json').read_text()).get('scope')
    if scope in ('resource_pilot', 'prefix_smoke_only'):
        raise RuntimeError('Pilot models are not eligible for final evaluation; complete reviewed matched training first')
    frozen = []
    for record in ledger:
        if record['status'] != 'complete':
            continue
        model = root / 'models' / f'{record["condition"]}-{record["family"]}'
        frozen.append({'condition': record['condition'], 'family': record['family'],
                       'bundle_sha256': sha256(model / 'bundle.json'), 'selection_metrics': record['development_metrics']})
    if not frozen:
        raise RuntimeError('No eligible trained models')
    champions = {}
    for condition in sorted({r['condition'] for r in frozen}):
        candidates = [r for r in frozen if r['condition']==condition]
        champions[condition] = max(candidates, key=lambda r: r['selection_metrics']['average_precision'] or -1)['family']
    manifest = {'candidates': frozen, 'champions_selected_from_development': champions,
                'benchmark_ledger_sha256': sha256(root/'reports'/'benchmark.json'), 'test_rows_per_source': config['test_rows'],
                'selection_frozen': True, 'source_revision': json.loads((root/'environment.json').read_text())['revision']}
    combination_records = []
    search = Path(config['benchmark_root'])
    for filename, kind in [('ensemble-development.json','ensemble'), ('moe-development.json','moe')]:
        hits = list(search.rglob('reports/' + filename))
        if len(hits) != 1:
            raise RuntimeError(f'Final freeze requires exactly one executed {filename}; found {hits}')
        source = hits[0].parent.parent
        for record in json.loads(hits[0].read_text()):
            condition = record.get('condition', 'mixture')
            model_name = f'{condition}-{record["name"]}' if kind == 'ensemble' else record['name']
            directory = source / 'models' / model_name
            if not (directory / 'bundle.json').exists():
                continue  # Calibrated individual baselines are already represented above.
            combination_records.append({'kind': kind, 'condition': condition, 'name': record['name'],
                                        'run_name': source.name, 'model_directory': model_name,
                                        'files': {p.name: sha256(p) for p in directory.iterdir() if p.is_file()},
                                        'development_metrics': record})
    manifest['combinations'] = combination_records
    # Freeze architecture selection using only calibrated development comparisons at the stated FPR.
    systems = {}
    for condition in champions:
        eligible = [r for r in combination_records if r['condition']==condition and
                    r['development_metrics'].get('benign_fpr') is not None and
                    r['development_metrics']['benign_fpr'] <= config.get('benign_fpr_limit',0.01)]
        systems[condition] = max(eligible, key=lambda r: (r['development_metrics']['recall'],
                                                         -r['development_metrics']['benign_fpr'])) if eligible else None
    manifest['combination_selection_from_development'] = systems
    write_json(run.root / 'manifests' / 'frozen-candidates.json', manifest)
    return manifest


def base_crossover(spark, config, run):
    from pyspark.sql import functions as F
    if config.get('frozen_candidates'):
        frozen_path = Path(config['frozen_candidates'])
    else:
        hits = list(Path(config.get('benchmark_root', '/kaggle/input')).rglob('manifests/frozen-candidates.json'))
        if len(hits) != 1:
            raise ValueError(f'Attach one frozen-candidate manifest, found {hits}')
        frozen_path = hits[0]
    manifest = json.loads(frozen_path.read_text())
    if not manifest.get('selection_frozen') or manifest['test_rows_per_source'] != config['test_rows']:
        raise RuntimeError('Frozen evaluation contract missing or changed')
    root, ledger = locate_benchmark(config['benchmark_root'])
    if sha256(root/'reports'/'benchmark.json') != manifest['benchmark_ledger_sha256']:
        raise RuntimeError('Benchmark changed after freeze')
    prepared = resolve_prepared(config)
    tests = {}
    for source, (_, path) in prepared.items():
        data = spark.read.parquet(str(path)).filter("split='test'").orderBy(F.sha2('row_id',256)).limit(config['test_rows']).toPandas()
        if data['target'].nunique()!=2:
            raise RuntimeError(f'{source} matched final-test cohort lacks a class')
        data.to_parquet(run.root/'scores'/f'{source}-test-cohort.parquet',index=False)
        tests[source] = data
    results=[]
    for record in manifest['candidates']:
        condition,family = record['condition'],record['family']
        directory=root/'models'/f'{condition}-{family}'
        if sha256(directory/'bundle.json')!=record['bundle_sha256']:
            raise RuntimeError('Frozen model bundle changed')
        model=ClassifierBundle(directory,spark)
        cohort=root/'cohorts'/condition
        calibration=pd.read_parquet(cohort/'calibration.parquet')
        thresholds=pd.read_parquet(cohort/'threshold.parquet')
        raw_cal=score_column(directory/'calibration-scores.parquet',calibration)
        calibrator=LogisticRegression(C=1,max_iter=300).fit(logit(np.clip(raw_cal,1e-6,1-1e-6))[:,None],calibration['target'])
        raw_threshold=score_column(directory/'threshold-scores.parquet',thresholds)
        threshold=choose_threshold(thresholds,calibrator.predict_proba(logit(np.clip(raw_threshold,1e-6,1-1e-6))[:,None])[:,1],config.get('benign_fpr_limit',0.01))
        for source in (['lan'] if condition=='lan' else ['ton','bot']):
            with run.stage(f'final-{condition}-{family}-to-{source}'):
                raw=model.predict(tests[source])
                scores=calibrator.predict_proba(logit(np.clip(raw,1e-6,1-1e-6))[:,None])[:,1]
                results.append(dict(train_condition=condition,test_source=source,family=family,
                                    scope='matched bounded final-test cohort',**evaluate(tests[source],scores,threshold)))
                tests[source][['row_id']].assign(score=scores).to_parquet(run.root/'scores'/f'{condition}-{family}-to-{source}.parquet',index=False)
                write_json(run.root/'reports'/'frozen-base-crossover.json',results)
    combination_results=[]
    for record in manifest.get('combinations', []):
        runs = [p for p in Path(config['benchmark_root']).rglob(record['run_name']) if p.is_dir() and (p/'models').is_dir()]
        if len(runs)!=1:
            raise RuntimeError(f'Cannot resolve frozen combination run {record["run_name"]}: {runs}')
        directory=runs[0]/'models'/record['model_directory']
        for filename, expected in record['files'].items():
            if sha256(directory/filename)!=expected:
                raise RuntimeError('Combination model changed after freeze')
        if record['kind']=='moe':
            model=DomainMixtureBundle(directory,spark=spark)
        else:
            model=EnsembleBundle(directory,root,spark)
        for source in (['lan'] if record['condition']=='lan' else ['ton','bot']):
            with run.stage(f'final-{record["condition"]}-{record["name"]}-to-{source}'):
                prediction=model.predict(tests[source])
                combination_results.append(dict(train_condition=record['condition'],name=record['name'],test_source=source,
                                                **evaluate(tests[source],prediction['score'],model.info['threshold'])))
                write_json(run.root/'reports'/'frozen-combination-crossover.json',combination_results)
    return results
