"""Matched-cohort development benchmark. Final tests are not read by model selection."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import pandas as pd
from sdn_ddos.models.classifiers import FAMILIES
from sdn_ddos.runtime.run import write_json, sha256
from sdn_ddos.evaluation.metrics import evaluate
from sdn_ddos.evaluation.alignment import align_scores


def resolve_prepared(config):
    root = Path(config.get('prepared_root', '/kaggle/input'))
    manifests = {}
    for source in ('ton', 'bot', 'lan'):
        hits = list(root.rglob(f'{source}-prepared.json'))
        if len(hits) != 1:
            raise RuntimeError(f'Expected one version-pinned {source} preparation manifest under {root}; found {hits}')
        manifest = json.loads(hits[0].read_text())
        if manifest['scope'] != 'full':
            raise RuntimeError('Prefix smoke artifacts cannot supply benchmark data')
        manifests[source] = (manifest, hits[0].parent.parent / 'parquet' / source)
    return manifests


def cohorts(spark, config, run):
    from pyspark.sql import functions as F
    manifests = resolve_prepared(config)
    tables = {source: spark.read.parquet(str(item[1])) for source, item in manifests.items()}
    result = {}
    budget = config['train_rows']
    dev_budget = config.get('development_rows', 30000)
    for condition in config.get('conditions', ['ton', 'bot', 'mixture', 'lan']):
        sources = ['ton', 'bot'] if condition == 'mixture' else [condition]
        contracts = [manifests[s][0]['contract'] for s in sources]
        if len(sources) == 2 and any(contracts[0][k] != contracts[1][k] for k in ('numeric', 'categorical')):
            raise RuntimeError('NetFlow schemas do not match')
        train_parts, dev_parts = [], []
        for source in sources:
            table = tables[source]
            train = table.filter("split = 'train'")
            development = table.filter("split = 'development'")
            if condition == 'mixture':
                # Global purging for the pooled condition: tests influence only predeclared overlap auditing.
                others = tables['ton'].unionByName(tables['bot'])
                holdout = others.filter("split IN ('development','test')").select('feature_group').distinct()
                train = train.join(holdout, 'feature_group', 'left_anti')
                contradictions = others.groupBy('feature_group').agg(F.countDistinct('target').alias('n')).filter('n > 1').select('feature_group')
                train = train.join(contradictions, 'feature_group', 'left_anti')
                development = development.join(contradictions, 'feature_group', 'left_anti')
                tests = others.filter("split = 'test'").select('feature_group').distinct()
                development = development.join(tests, 'feature_group', 'left_anti')
            # Equal total training budget. Hash sort is deterministic and label-independent.
            train = train.dropDuplicates(['feature_group', 'target']).orderBy(F.sha2(F.concat_ws(':', F.col('row_id'), F.lit(str(config.get('seed', 42)))), 256)).limit(budget // len(sources))
            dev = development.orderBy(F.sha2('row_id', 256)).limit(dev_budget // len(sources))
            train_parts.append(train.toPandas())
            dev_parts.append(dev.toPandas())
        train = pd.concat(train_parts, ignore_index=True)
        if len(train) != budget:
            raise RuntimeError(f'{condition}: requested matched budget {budget}, obtained {len(train)}. Reduce the common budget explicitly after resource review.')
        development = pd.concat(dev_parts, ignore_index=True).sort_values(['source', 'time_start', 'row_id']).reset_index(drop=True)
        if train['target'].nunique() != 2:
            raise RuntimeError(f'{condition}: training cohort lacks a class')
        # Three chronological subsets per source prevent pooled source ordering from defining purposes.
        sets = {'selection': [], 'calibration': [], 'threshold': []}
        for _, group in development.groupby('source', sort=True):
            cut1, cut2 = len(group) // 3, 2 * len(group) // 3
            for name, frame in zip(sets, [group.iloc[:cut1], group.iloc[cut1:cut2], group.iloc[cut2:]]):
                if frame['target'].nunique() != 2:
                    raise RuntimeError(f'{condition}/{name} lacks class coverage; revise development protocol explicitly')
                sets[name].append(frame)
        path = run.root / 'cohorts' / condition
        path.mkdir(parents=True)
        train.to_parquet(path / 'train.parquet', index=False)
        for name, pieces in sets.items():
            pd.concat(pieces, ignore_index=True).to_parquet(path / f'{name}.parquet', index=False)
        metadata = {'condition': condition, 'contract': contracts[0], 'train_rows': len(train),
                    'sources': sources, 'equal_requested_budget': budget, 'scope': config.get('scope', 'pilot'),
                    'hashes': {p.name: sha256(p) for p in path.glob('*.parquet')},
                    'source_manifests': {s: manifests[s][0] for s in sources}}
        write_json(path / 'cohort.json', metadata)
        result[condition] = (path, metadata)
    return result


def execute_fit(request, timeout=600):
    request_path = Path(request['output']).with_suffix('.request.json')
    write_json(request_path, request)
    log_path = request_path.with_suffix('.log')
    environment = dict(os.environ, OMP_NUM_THREADS='2', OPENBLAS_NUM_THREADS='2', MKL_NUM_THREADS='2')
    start = time.monotonic()
    with log_path.open('w', encoding='utf-8') as log:
        try:
            process = subprocess.Popen([sys.executable, '-u', '-m', 'sdn_ddos.models.worker', '--request', str(request_path)],
                                       stdout=log, stderr=subprocess.STDOUT, env=environment, start_new_session=os.name != 'nt')
            try:
                code = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                if os.name != 'nt':
                    import signal
                    os.killpg(process.pid, signal.SIGKILL)
                else:
                    process.kill()
                process.wait()
                return {'status': 'timeout', 'seconds': time.monotonic() - start, 'log': str(log_path)}
        except Exception as error:
            return {'status': 'launch_failed', 'error': str(error), 'log': str(log_path)}
    return {'status': 'complete' if code == 0 else 'failed', 'exit_code': code,
            'seconds': time.monotonic() - start, 'log': str(log_path)}


def benchmark(spark, config, run):
    with run.stage('matched-cohorts'):
        inputs = cohorts(spark, config, run)
    # Stop the parent JVM before child fits to avoid competing driver allocations.
    spark.stop()
    ledger = []
    for condition, (path, metadata) in inputs.items():
        for family in config.get('families', FAMILIES):
            with run.stage(f'fit-{condition}-{family}'):
                destination = run.root / 'models' / f'{condition}-{family}'
                request = {'family': family, 'train': str(path / 'train.parquet'), 'contract': metadata['contract'],
                           'predict': {name: str(path / f'{name}.parquet') for name in ('selection', 'calibration', 'threshold')},
                           'output': str(destination), 'cohort_hashes': metadata['hashes']}
                print('LAUNCH FIT', condition, family, 'timeout', config.get('fit_timeout_seconds', 600), flush=True)
                outcome = execute_fit(request, config.get('fit_timeout_seconds', 600))
                record = dict(condition=condition, family=family, **outcome)
                if outcome['status'] == 'complete':
                    table = pd.read_parquet(path / 'selection.parquet')
                    scores = align_scores(destination / 'selection-scores.parquet', table)
                    record['development_metrics'] = evaluate(table, scores, calibrated=False)
                ledger.append(record)
                write_json(run.root / 'reports' / 'benchmark.json', ledger)
                print('FIT OUTCOME', record, flush=True)
    return ledger
