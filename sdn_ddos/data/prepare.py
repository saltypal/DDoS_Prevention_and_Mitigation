"""Sanitize measurements, establish protected partitions, and persist observational Parquet."""
import json
from sdn_ddos.features.contracts import feature_contract, LABELS
from sdn_ddos.runtime.run import write_json


def sanitize(raw, source, run):
    from pyspark.sql import functions as F
    contract = feature_contract(source, raw.columns)
    target = 'Attack' if source != 'lan' else 'label'
    data = raw.withColumn('attack_family', F.lower(F.trim(F.col(target))))
    data = data.withColumn('attack_original', F.col(target))
    data = data.withColumn('original_binary_label', F.col('Label') if source != 'lan' else F.lit(None).cast('string'))
    unknown = data.filter(F.col('attack_family').isNull() | ~F.col('attack_family').isin(sorted(LABELS[source]))).groupBy('attack_family').count().collect()
    if unknown:
        raise RuntimeError(f'Unknown labels require audit: {unknown}')
    data = data.withColumn('target', (F.col('attack_family') == 'ddos').cast('double'))
    data = data.withColumn('is_benign', F.col('attack_family').isin('benign', 'normal'))
    if source != 'lan':
        inconsistent = data.filter(F.expr('try_cast(Label as double)').isNull() |
                                   (F.expr('try_cast(Label as double)') != (~F.col('is_benign')).cast('double'))).count()
        if inconsistent:
            raise RuntimeError(f'{inconsistent} original binary/family label inconsistencies require audit')
    expressions = []
    for name in contract['numeric']:
        value = F.expr(f'try_cast(`{name}` as double)')
        expressions.append(F.sum(F.when(value.isNull() | F.isnan(value) | (F.abs(value) == float('inf')), 1).otherwise(0)).alias(name))
    quality = data.agg(*expressions).first().asDict()
    write_json(run.root / 'reports' / f'{source}-undefined-numeric.json', quality)
    for name in contract['numeric']:
        value = F.expr(f'try_cast(`{name}` as double)')
        data = data.withColumn(name, F.when(value.isNull() | F.isnan(value) | (F.abs(value) == float('inf')), F.lit(None).cast('double')).otherwise(value))
    for name in contract['categorical']:
        data = data.withColumn(name, F.when(F.trim(F.col(name)).isin('', 'NaN', 'nan', 'null'), '__missing__').otherwise(F.trim(F.col(name))))
    from sdn_ddos.features.derived import derive
    data, contract = derive(data, source, contract)
    predictors = contract['numeric'] + contract['categorical']
    # JSON serialization avoids delimiter collisions and preserves explicit nulls.
    vector = F.to_json(F.struct(*[F.col(c).alias(c) for c in sorted(predictors)]), options={'ignoreNullFields': 'false'})
    data = data.withColumn('feature_group', F.sha2(vector, 256))
    if source in ('ton', 'bot'):
        start, end = 'FLOW_START_MILLISECONDS', 'FLOW_END_MILLISECONDS'
        data = data.withColumn('time_start', F.expr(f'try_cast({start} as double)') / 1000)
        data = data.withColumn('time_end', F.expr(f'try_cast({end} as double)') / 1000)
        keys = ['IPV4_SRC_ADDR', 'IPV4_DST_ADDR', 'L4_SRC_PORT', 'L4_DST_PORT', 'PROTOCOL']
        data = data.withColumn('session_group', F.sha2(F.to_json(F.struct(F.col('source'), *[F.col(c) for c in keys], F.floor(F.col('time_start') / 60).alias('minute'))), 256))
    else:
        # LAN temporal values are creator-exported; topology is the primary partition unit.
        data = data.withColumn('time_start', F.expr('try_cast(timestamp_1 as double)'))
        data = data.withColumn('time_end', F.expr('try_cast(timestamp_2 as double)'))
        data = data.withColumn('session_group', F.sha2(F.to_json(F.struct('src_MAC', 'dst_MAC', 'subflow_id', 'topology')), 256))
    keep = predictors + ['row_id', 'source_ordinal', 'source_file_hash', 'source', 'topology', 'attack_family',
                         'target', 'is_benign', 'attack_original', 'original_binary_label', 'feature_group', 'session_group', 'time_start', 'time_end']
    write_json(run.root / 'contracts' / f'{source}-features.json', contract)
    return data.select(*keep), contract


def partition(data, source, config, run):
    from pyspark.sql import functions as F
    if source == 'lan':
        data = data.withColumn('split', F.when(F.col('topology').isin('Linear', 'Tree', 'Mesh'), 'train')
                               .when(F.col('topology') == 'Star', 'development').otherwise('test'))
        boundaries = {'train': ['Linear', 'Tree', 'Mesh'], 'development': ['Star'], 'test': ['Subnets'],
                      'scope': 'one held-out topology; not universal generalization'}
    else:
        invalid = data.filter(F.col('time_start').isNull() | F.col('time_end').isNull() |
                              F.isnan('time_start') | F.isnan('time_end') |
                              (F.abs(F.col('time_start')) == float('inf')) | (F.abs(F.col('time_end')) == float('inf')) |
                              (F.col('time_end') < F.col('time_start'))).count()
        if invalid:
            raise RuntimeError(f'{invalid} invalid timestamps require a documented quarantine policy')
        cuts = data.approxQuantile('time_start', [0.6, 0.8], 0.0001)
        if len(cuts) != 2 or cuts[0] >= cuts[1]:
            raise RuntimeError('Cannot establish chronological partitions')
        embargo = config.get('embargo_seconds', 60)
        data = data.withColumn('split', F.when(F.col('time_end') < cuts[0] - embargo, 'train')
                               .when((F.col('time_start') > cuts[0] + embargo) & (F.col('time_end') < cuts[1] - embargo), 'development')
                               .when(F.col('time_start') > cuts[1] + embargo, 'test').otherwise('quarantine_boundary'))
        boundaries = {'quantile_cuts_seconds': cuts, 'embargo_seconds': embargo,
                      'scope': 'chronological blocks; episode independence not established'}
    # Contradictory binary labels are quarantined, not resolved by majority vote.
    groups = data.groupBy('feature_group').agg(F.countDistinct('target').alias('targets'), F.count('*').alias('observations'))
    duplicate_report = groups.agg(F.count('*').alias('unique_selected_feature_groups'),
                                 F.sum(F.col('observations') - 1).alias('duplicate_selected_feature_rows'),
                                 F.max('observations').alias('largest_group')).first().asDict()
    write_json(run.root / 'reports' / f'{source}-selected-feature-duplicates.json', duplicate_report)
    conflicts = groups.filter('targets > 1').select('feature_group')
    conflicts_count = conflicts.count()
    data = data.join(conflicts.withColumn('conflict', F.lit(True)), 'feature_group', 'left')
    data = data.withColumn('split', F.when(F.col('conflict').isNotNull(), 'quarantine_conflict').otherwise(F.col('split'))).drop('conflict')
    # Keep final-test observations; purge earlier observations sharing selected features or flow groups.
    order = {'train': 0, 'development': 1, 'test': 2}
    rank = F.when(F.col('split') == 'train', 0).when(F.col('split') == 'development', 1).when(F.col('split') == 'test', 2).otherwise(-1)
    ranked = data.withColumn('_rank', rank)
    feature_max = ranked.groupBy('feature_group').agg(F.max('_rank').alias('_feature_last'))
    session_max = ranked.groupBy('session_group').agg(F.max('_rank').alias('_session_last'))
    data = ranked.join(feature_max, 'feature_group').join(session_max, 'session_group')
    data = data.withColumn('split', F.when((F.col('_rank') >= 0) &
                           ((F.col('_rank') < F.col('_feature_last')) | (F.col('_rank') < F.col('_session_last'))),
                           'quarantine_overlap').otherwise(F.col('split'))).drop('_rank', '_feature_last', '_session_last')
    counts = [row.asDict() for row in data.groupBy('source', 'split', 'attack_family', 'target').count().collect()]
    write_json(run.root / 'reports' / f'{source}-split-counts.json', counts)
    write_json(run.root / 'contracts' / f'{source}-split-policy.json', dict(boundaries, conflict_groups=conflicts_count))
    if not config.get('smoke_rows_per_file'):
        for name in order:
            labels = {row.target for row in data.filter(F.col('split') == name).select('target').distinct().collect()}
            if labels != {0.0, 1.0}:
                raise RuntimeError(f'{source}/{name} lacks binary class coverage after purging: {labels}; review split protocol, do not silently random-split')
    return data


def prepare_source(source, spark, config, run):
    from sdn_ddos.data.sources import acquire, ingest
    from sdn_ddos.analysis.eda import profile
    with run.stage(f'{source}-acquire'):
        specs = acquire(source, config, run)
    with run.stage(f'{source}-ingest'):
        raw = ingest(specs, spark, config, run)
    with run.stage(f'{source}-sanitize'):
        clean, contract = sanitize(raw, source, run)
        from pyspark import StorageLevel
        clean = clean.persist(StorageLevel.DISK_ONLY)
        print('MATERIALIZED SANITIZED ROWS', clean.count(), flush=True)
        sanitized_cache = clean
    with run.stage(f'{source}-partitions'):
        clean = partition(clean, source, config, run)
        destination = run.root / 'parquet' / source
        clean.write.partitionBy('split').mode('errorifexists').parquet(str(destination))
        persisted = spark.read.parquet(str(destination))
        rows = persisted.count()
        expected = sum(s['rows_ingested'] for s in specs)
        if rows != expected:
            raise RuntimeError(f'Row conservation failure: {rows} != {expected}')
        if persisted.select('row_id').distinct().count() != rows:
            raise RuntimeError('Duplicate source row IDs')
        for group in ('feature_group', 'session_group'):
            overlaps = (persisted.filter("split IN ('train','development','test')").groupBy(group)
                        .agg(__import__('pyspark').sql.functions.countDistinct('split').alias('n')).filter('n > 1').count())
            if overlaps:
                raise RuntimeError(f'Partition leakage: {group} has {overlaps} overlapping groups')
        write_json(run.root / 'manifests' / f'{source}-prepared.json', {'source': source, 'rows': rows,
                   'parquet': str(destination), 'contract': contract, 'scope': 'smoke_prefix' if config.get('smoke_rows_per_file') else 'full',
                   'input_sha256': [s['sha256'] for s in specs]})
    with run.stage(f'{source}-eda'):
        profile(persisted, source, contract, config, run)
    sanitized_cache.unpersist()
    return destination
