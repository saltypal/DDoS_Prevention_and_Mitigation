from pathlib import Path
import hashlib
import json
import requests
from sdn_ddos.runtime.run import sha256, write_json

LAN_IDS = {'Linear': 55750, 'Mesh': 55751, 'Star': 55752, 'Subnets': 55753, 'Tree': 55754}
FILENAMES = {'ton': 'NF-ToN-IoT-v3.csv', 'bot': 'NF-BoT-IoT-v3.csv'}
EXPECTED_BYTES = {'ton': 5302886266, 'bot': 3817527532}


def acquire(source, config, run):
    cache = Path(config.get('cache_root', '/kaggle/temp/ddos-public'))
    cache.mkdir(parents=True, exist_ok=True)
    specs = []
    if source in FILENAMES:
        hits = list(Path(config.get('input_root', '/kaggle/input')).rglob(FILENAMES[source]))
        if len(hits) != 1:
            raise RuntimeError(f'Expected one {FILENAMES[source]}, found {hits}')
        specs = [{'source': source, 'topology': 'none', 'path': str(hits[0]), 'expected_columns': 55,
                  'mirror': f'seyhed/nf-{source}-iot-v3', 'version_expected': 1}]
    elif source == 'lan':
        base = 'https://edatos.consorciomadrono.es/api'
        response = requests.get(base + '/datasets/:persistentId/', params={'persistentId': 'doi:10.21950/QMAXKP'}, timeout=90)
        response.raise_for_status()
        release = response.json()['data']['latestVersion']
        if (release['versionNumber'], release['versionMinorNumber']) != (3, 0):
            raise RuntimeError('LAN release changed; inspect before accepting a new source version')
        write_json(run.root / 'contracts' / 'lan_release.json', release)
        files = {entry['dataFile']['id']: entry['dataFile'] for entry in release['files']}
        for topology, file_id in LAN_IDS.items():
            path = cache / f'lan-{file_id}.csv'
            if not path.exists():
                partial = path.with_suffix('.partial')
                with requests.get(base + f'/access/datafile/{file_id}', stream=True, timeout=120) as download:
                    download.raise_for_status()
                    with partial.open('wb') as handle:
                        for block in download.iter_content(4 * 1024 * 1024):
                            handle.write(block)
                partial.replace(path)
            specs.append({'source': source, 'topology': topology, 'path': str(path),
                          'expected_columns': 47, 'version_expected': '3.0',
                          'official_checksum': files[file_id]['checksum']})
    else:
        raise ValueError(f'Unsupported source {source}')
    expected = config.get('source_sha256', {})
    for spec in specs:
        path = Path(spec['path'])
        spec.update(bytes=path.stat().st_size, sha256=sha256(path))
        if spec['source'] in EXPECTED_BYTES and spec['bytes'] != EXPECTED_BYTES[spec['source']]:
            raise RuntimeError('NF input differs from the audited source snapshot; review version before proceeding')
        if spec.get('official_checksum'):
            check = spec['official_checksum']
            digest = hashlib.new(check['type'].lower().replace('-', ''))
            with path.open('rb') as handle:
                for block in iter(lambda: handle.read(8 * 1024 * 1024), b''):
                    digest.update(block)
            if digest.hexdigest().lower() != check['value'].lower():
                raise RuntimeError(f'Official checksum mismatch: {path.name}')
        if expected.get(path.name) and expected[path.name] != spec['sha256']:
            raise RuntimeError(f'Source snapshot mismatch: {path.name}')
        print('VERIFIED INPUT', json.dumps(spec), flush=True)
    write_json(run.root / 'contracts' / f'{source}-inputs.json', specs)
    return specs


def ingest(specs, spark, config, run):
    """Chunked raw conversion preserves logical CSV ordinal; no Spark-generated row IDs."""
    import pandas as pd
    from pyspark.sql import functions as F
    frames = []
    for spec in specs:
        destination = Path(config.get('cache_root', '/kaggle/temp/ddos-public')) / (spec['sha256'] + '-' + run.root.name)
        destination.mkdir(exist_ok=False)
        total = 0
        cap = config.get('smoke_rows_per_file')
        for index, chunk in enumerate(pd.read_csv(spec['path'], dtype=str, keep_default_na=False,
                                                  chunksize=config.get('csv_chunk_rows', 100000), nrows=cap)):
            if len(chunk.columns) != spec['expected_columns']:
                raise RuntimeError(f'Unexpected schema for {spec["path"]}: {chunk.columns.tolist()}')
            chunk['source_ordinal'] = range(total, total + len(chunk))
            chunk['source_file_hash'] = spec['sha256']
            chunk['source'] = spec['source']
            chunk['topology'] = spec['topology']
            chunk.to_parquet(destination / f'part-{index:05d}.parquet', index=False, compression='zstd')
            total += len(chunk)
            print('INGEST', spec['source'], spec['topology'], total, flush=True)
        if total == 0:
            raise RuntimeError('Empty source CSV')
        spec['rows_ingested'] = total
        frame = spark.read.parquet(str(destination)).withColumn('row_id', F.sha2(F.concat_ws(':', 'source_file_hash', F.col('source_ordinal').cast('string')), 256))
        frames.append(frame)
    result = frames[0]
    for frame in frames[1:]:
        result = result.unionByName(frame)
    write_json(run.root / 'contracts' / f'{specs[0]["source"]}-ingestion.json', specs)
    return result
