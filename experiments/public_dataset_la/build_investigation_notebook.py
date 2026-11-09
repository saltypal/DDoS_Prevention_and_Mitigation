"""Build the self-contained, report-only Kaggle dataset investigation notebook."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import textwrap

import nbformat as nbf

HERE = Path(__file__).resolve().parent
DEST = HERE / "notebooks"
DEST.mkdir(exist_ok=True)
RUN_ID = "public-investigation-20261107-v2"

intro = """# Public DDoS/SDN dataset investigation

Project: DDoS_Prevention_and_Mitigation. Purpose: investigate before choosing datasets;
this notebook does not train classifiers, concatenate unrelated schemas, or publish data.
Version2 is a focused LAN/cloud follow-up: fixes identifier exclusions and uses cloud
activity as target. NF pair and IoT-23 findings remain in preserved version1 outputs.
All computation and preprocessing below are inline. Intended target: Kaggle managed CPU
Python, internet enabled, no GPU. Large source data remain remote. Download only the
small report bundle locally. Dependencies: existing Kaggle numpy, pandas, pyarrow,
requests, nbformat and IPython; actual versions are recorded before work.

Sources: [UQ NetFlow V3](https://staff.itee.uq.edu.au/marius/NIDS_datasets/),
[temporal extraction methods](https://arxiv.org/abs/2503.04404),
[LAN-SDN-NIDS](https://doi.org/10.21950/QMAXKP),
[cloud DDoS methods](https://doi.org/10.3390/info15040195),
[IoT-23](https://www.stratosphereips.org/datasets-iot23).
Mirrors are acquisition mechanisms, not independent sources or new captures.

Acceptance: recover a report for each candidate, or an explicit access/failure record;
record source versions, integrity and observed row coverage; audit label/identifier leakage;
distinguish full scans from bounded probes. Publication/redistribution permissions must be
checked independently of the article license. A network-data mixture is not automatically novel.
"""

setup = r'''
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import contextlib, hashlib, importlib.metadata, io, json, math, os, platform
import shutil, sys, time, traceback, zipfile
import numpy as np
import pandas as pd
import requests
import nbformat

RUN_ID = __RUN_ID__
SOURCE_SNAPSHOT = __SOURCE_SNAPSHOT__
ROOT = Path('/kaggle/working/experiments/public_dataset_la/runs') / RUN_ID
ROOT.mkdir(parents=True, exist_ok=False)
REPORTS, LOGS = ROOT / 'reports', ROOT / 'logs'
REPORTS.mkdir(); LOGS.mkdir()
# Bulk downloads are deliberately outside the saved report tree.
CACHE = Path('/kaggle/temp/public_dataset_investigation') / RUN_ID
CACHE.mkdir(parents=True, exist_ok=True)
START = time.monotonic()
SELECTED_CANDIDATES = ['BCCC-cPacket-Cloud-DDoS-2024', 'LAN-SDN-NIDS']
CHUNK_ROWS = 100_000
SAMPLE_ROWS = 20_000
SEED = 20261107
MAX_REMOTE_DOWNLOAD_BYTES = 2_000_000_000
MAX_SECONDS = 4 * 3600
# Main candidates are scanned fully. IoT-23 has >325M rows: inspect at most
# 1M rows per scenario, including every scenario; explicitly report prefix bias.
IOT_LOG_ROW_LIMIT = 1_000_000
STATE = {'run_id': RUN_ID, 'source_snapshot': SOURCE_SNAPSHOT,
         'started_utc': datetime.now(timezone.utc).isoformat(), 'datasets': [], 'failures': []}

def write_json(path, value):
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, default=str, allow_nan=False), encoding='utf-8')
    tmp.replace(path)

def checkpoint():
    write_json(ROOT / 'run_state.json', STATE)

def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''): h.update(block)
    return h.hexdigest()

versions = {}
for package in ['numpy', 'pandas', 'pyarrow', 'requests', 'nbformat', 'ipython', 'kagglehub']:
    try: versions[package] = importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError: versions[package] = None
environment = {'interpreter': sys.executable, 'python': sys.version,
               'platform': platform.platform(), 'cpu_count': os.cpu_count(),
               'packages': versions, 'backend': 'CPU; no model training',
               'working_disk': shutil.disk_usage('/kaggle/working')._asdict(),
               'input_root': str(Path('/kaggle/input').resolve()),
               'source_snapshot': SOURCE_SNAPSHOT, 'config': {
                   'chunk_rows': CHUNK_ROWS, 'sample_rows': SAMPLE_ROWS, 'seed': SEED,
                   'max_seconds': MAX_SECONDS, 'iot_log_row_limit': IOT_LOG_ROW_LIMIT}}
write_json(ROOT / 'environment.json', environment)
(ROOT / 'persistence_marker.txt').write_text(RUN_ID)
assert (ROOT / 'persistence_marker.txt').read_text() == RUN_ID
checkpoint()
print('SETUP COMPLETE', json.dumps(environment, indent=2), flush=True)
print('Report output:', ROOT, '\nRemote-only cache:', CACHE, flush=True)
'''

logging_code = r'''
print('START cell output preservation', flush=True)
from IPython import get_ipython
IP = get_ipython()
CELL_RECORDS = []
CURRENT = {}

class Tee(io.TextIOBase):
    def __init__(self, original, file): self.original, self.file = original, file
    def write(self, text):
        self.original.write(text); self.file.write(text); self.file.flush()
        return len(text)
    def flush(self): self.original.flush(); self.file.flush()

def before_cell(info):
    number = len(CELL_RECORDS) + 1
    path = LOGS / f'cell-{number:03d}.log'
    CURRENT.update(source=info.raw_cell, number=number, started=time.monotonic(),
                   utc=datetime.now(timezone.utc).isoformat(), outputs=[], file=path.open('a'))
    CURRENT['stdout'], CURRENT['stderr'] = sys.stdout, sys.stderr
    sys.stdout = Tee(sys.stdout, CURRENT['file']); sys.stderr = Tee(sys.stderr, CURRENT['file'])
    print(f'START CELL {number:03d} UTC {CURRENT["utc"]}', flush=True)

def after_cell(result):
    if not CURRENT: return
    error = result.error_in_exec or result.error_before_exec
    elapsed = time.monotonic() - CURRENT['started']
    print(f'END CELL {CURRENT["number"]:03d} status={"failed" if error else "complete"} seconds={elapsed:.3f}', flush=True)
    sys.stdout, sys.stderr = CURRENT['stdout'], CURRENT['stderr']
    CURRENT['file'].close()
    output = (LOGS / f'cell-{CURRENT["number"]:03d}.log').read_text(errors='replace')
    node = nbformat.v4.new_code_cell(CURRENT['source'], id=f'executed-{CURRENT["number"]:03d}')
    node.execution_count = result.execution_count
    # Notebook contains full persisted cell stream plus captured display data.
    node.outputs = [nbformat.v4.new_output('stream', name='stdout', text=output)] + CURRENT['outputs']
    if error:
        node.outputs.append(nbformat.v4.new_output('error', ename=type(error).__name__,
                            evalue=str(error), traceback=traceback.format_exception(error)))
    CELL_RECORDS.append(node)
    write_json(LOGS / 'cell_ledger.json', [{'cell_id': c.id, 'execution_count': c.execution_count,
               'has_error': any(o.output_type == 'error' for o in c.outputs)} for c in CELL_RECORDS])
    executed = nbformat.v4.new_notebook(cells=[nbformat.v4.new_markdown_cell(
        '# Captured Kaggle execution\nSource snapshot: ' + SOURCE_SNAPSHOT +
        '\nSetup environment is in environment.json. Setup/hook cells precede capture; '+
        'use the canonical source notebook to rerun. Native process output may escape this hook.')]+CELL_RECORDS)
    nbformat.write(executed, ROOT / 'executed_cells.ipynb')
    CURRENT.clear()

ORIGINAL_PUBLISH = IP.display_pub.publish
def capture_display(data, metadata=None, **kwargs):
    if CURRENT:
        CURRENT['outputs'].append(nbformat.v4.new_output('display_data', data=data, metadata=metadata or {}))
    return ORIGINAL_PUBLISH(data, metadata=metadata, **kwargs)
IP.display_pub.publish = capture_display
IP.events.register('pre_run_cell', before_cell)
IP.events.register('post_run_cell', after_cell)
print('COMPLETE hooks active for subsequent cells; each writes logs and execution evidence incrementally.', flush=True)
'''

acquire = r'''
print('START discover attached inputs and official LAN-SDN-NIDS files', flush=True)
INPUT_MANIFEST = __INPUT_MANIFEST__
write_json(ROOT / 'input_manifest.json', INPUT_MANIFEST)
FILES = []
inventory = []

def candidate_for(path):
    s = str(path).lower()
    if 'nf-ton' in s or 'nf_ton' in s: return 'NF-ToN-IoT-v3'
    if 'nf-bot' in s or 'nf_bot' in s: return 'NF-BoT-IoT-v3'
    if 'bccc' in s or 'cpacket' in s: return 'BCCC-cPacket-Cloud-DDoS-2024'
    if 'iot-23' in s or 'iot23' in s: return 'IoT-23'
    return None

for path in sorted(Path('/kaggle/input').rglob('*')):
    if not path.is_file(): continue
    candidate = candidate_for(path)
    inventory.append({'path': str(path), 'bytes': path.stat().st_size, 'candidate': candidate})
    if candidate == 'IoT-23' and ('.metadata.' in path.name or path.name == 'scenario-summary.parquet'):
        continue
    # Only parse data tables; never load/execute bundled source or malware binaries.
    if candidate in SELECTED_CANDIDATES and (path.suffix.lower() in {'.csv', '.parquet'} or path.name == 'conn.log.labeled'):
        FILES.append({'candidate': candidate, 'path': str(path), 'topology': None, 'acquisition': 'attached-readonly'})
write_json(REPORTS / 'attached_inventory.json', inventory)
print('Attached files:', len(inventory), 'tables:', len(FILES), flush=True)
input_checks = []
for source in INPUT_MANIFEST.get('kaggle_dataset_sources', []):
    if source.get('purpose') not in SELECTED_CANDIDATES: continue
    for expected in source.get('files', []):
        matches = [f for f in inventory if Path(f['path']).name==Path(expected['name']).name]
        check = {'ref':source['ref'],'version_observed':source.get('version_observed'),
                 'name':expected['name'],'expected_bytes':expected['bytes'],
                 'mounted_matches':matches,
                 'size_match':len(matches)==1 and matches[0]['bytes']==expected['bytes']}
        input_checks.append(check)
        if not check['size_match']:
            STATE['failures'].append({'candidate':source['ref'],'error':'Input inventory mismatch',
                                      'file':expected['name']})
write_json(REPORTS/'input_size_reconciliation.json',input_checks)
for candidate in ['NF-ToN-IoT-v3','NF-BoT-IoT-v3']:
    if candidate not in SELECTED_CANDIDATES: continue
    present = [r for r in FILES if r['candidate']==candidate]
    if len(present)!=1:
        STATE['failures'].append({'candidate':candidate,'error':f'Expected one CSV, found {len(present)}'})
checkpoint()

DV = 'https://edatos.consorciomadrono.es'
response = requests.get(DV + '/api/datasets/:persistentId/',
                        params={'persistentId': 'doi:10.21950/QMAXKP'}, timeout=(20, 90))
response.raise_for_status()
metadata = response.json()
write_json(REPORTS / 'lan_dataverse_metadata.json', metadata)
version = metadata['data']['latestVersion']
assert version['versionState'] == 'RELEASED'
print('LAN official dataset version:', version['versionNumber'], version['versionMinorNumber'],
      'license:', version.get('license'), flush=True)
selected = {'linear.csv', 'tree.csv', 'star.csv', 'mesh.csv', 'subnets.csv',
            'FULL_SDN_NIDS.parquet', 'data_dictionary.csv', 'readme_en.txt'}
downloaded = 0
for item in version['files']:
    info = item['dataFile']; name = info['filename']
    if name not in selected: continue
    if item.get('restricted'): raise RuntimeError('Restricted LAN file: ' + name)
    size = info.get('filesize', 0)
    if downloaded + size > MAX_REMOTE_DOWNLOAD_BYTES: raise RuntimeError('Download budget exceeded')
    if shutil.disk_usage(str(CACHE)).free < size * 2 + 1_000_000_000: raise RuntimeError('Remote free disk insufficient')
    target = CACHE / name
    print('Downloading official LAN file:', name, 'expected bytes:', size, flush=True)
    md5, digest = hashlib.md5(), hashlib.sha256()
    count = 0; mark = time.monotonic()
    with requests.get(DV + f'/api/access/datafile/{info["id"]}', stream=True, timeout=(20, 120)) as r:
        r.raise_for_status()
        with target.open('wb') as out:
            for block in r.iter_content(4 * 1024 * 1024):
                if not block: continue
                count += len(block)
                if count > size + 1_000_000 or downloaded + count > MAX_REMOTE_DOWNLOAD_BYTES:
                    raise RuntimeError('Unexpected download size')
                out.write(block); md5.update(block); digest.update(block)
                if time.monotonic() - mark > 20:
                    print(name, 'download bytes:', count, flush=True); mark = time.monotonic()
    assert count == size, (name, count, size)
    checksum = info.get('checksum', {})
    if checksum.get('type') == 'MD5': assert md5.hexdigest() == checksum['value']
    downloaded += count
    record = {'candidate': 'LAN-SDN-NIDS', 'path': str(target), 'bytes': count,
              'sha256': digest.hexdigest(), 'official_checksum': checksum,
              'topology': name.split('.')[0] if name in {'linear.csv','tree.csv','star.csv','mesh.csv','subnets.csv'} else None,
              'acquisition': 'official-dataverse', 'file_id': info['id']}
    if target.suffix in {'.csv', '.parquet'} and name != 'data_dictionary.csv': FILES.append(record)
    else: shutil.copy2(target, REPORTS / name)
    STATE.setdefault('downloads', []).append(record); checkpoint()
print('COMPLETE input acquisition:', len(FILES), 'tables; LAN downloaded bytes:', downloaded, flush=True)
if not FILES: raise RuntimeError('No dataset tables found')
'''

profiler = r'''
print('START define bounded-memory full-table profiler', flush=True)
import pyarrow.parquet as pq

def excluded_identifier(column):
    c = column.lower().strip()
    return (c in {'label','attack','attack_type','attack_cat','category','subcategory','class',
                  'topology','dataset','source_dataset','uid','flow_id','id','timestamp','ts',
                  'ip.src','ip.dst','eth.src','eth.dst','src_ip','dst_ip','src_port','dst_port',
                  'sport','dport','id.orig_h','id.resp_h','id.orig_p','id.resp_p',
                  'source_row','scenario','capture','capture_id','activity',
                  'src_mac','dst_mac','subflow_id'}
            or any(t in c for t in ['ipv4_src','ipv4_dst','l4_src_port','l4_dst_port',
                                    'flow_start','flow_end','timestamp_', 'mac_a','mac_b',
                                    'label','unnamed:']))

def readers(path):
    if path.suffix.lower() == '.parquet':
        consumed = 0
        for batch in pq.ParquetFile(path).iter_batches(batch_size=CHUNK_ROWS):
            take = min(len(batch), IOT_LOG_ROW_LIMIT-consumed) if '.features.' in path.name else len(batch)
            if take <= 0: break
            yield batch.slice(0,take).to_pandas()
            consumed += take
    elif path.name == 'conn.log.labeled':
        names = None
        with path.open(errors='replace') as stream:
            for line in stream:
                if line.startswith('#fields'): names = line.strip().split()[1:]; break
        if not names: raise ValueError('Missing Zeek #fields header')
        consumed = 0
        for chunk in pd.read_csv(path, sep=r'\s+', comment='#', names=names, dtype=str,
                                 chunksize=50_000, engine='python'):
            take = min(len(chunk), IOT_LOG_ROW_LIMIT - consumed)
            if take <= 0: break
            yield chunk.iloc[:take]; consumed += take
    else:
        yield from pd.read_csv(path, chunksize=CHUNK_ROWS, low_memory=False)

class UniqueSketch:
    """HyperLogLog, p=14. Relative standard error about 0.81%; not exact duplicate counts."""
    def __init__(self): self.registers = np.zeros(16384, dtype=np.uint8)
    def add(self, hashes):
        x = np.asarray(hashes, dtype=np.uint64)
        index = (x & np.uint64(16383)).astype(np.int64)
        w = x >> np.uint64(14)
        rank = np.full(len(x), 51, dtype=np.uint8)
        nonzero = w != 0
        rank[nonzero] = (50 - np.floor(np.log2(w[nonzero].astype(float)))).astype(np.uint8)
        np.maximum.at(self.registers, index, rank)
    def estimate(self):
        m = len(self.registers)
        e = (0.7213 / (1 + 1.079/m)) * m*m / np.exp2(-self.registers.astype(float)).sum()
        zeros = np.count_nonzero(self.registers == 0)
        return float(m * np.log(m/zeros)) if e < 2.5*m and zeros else float(e)

def profile(record, number):
    path = Path(record['path'])
    key = f'{number:02d}-' + ''.join(c if c.isalnum() or c in '-_.' else '_' for c in path.name)
    folder = REPORTS / key; folder.mkdir()
    print('START PROFILE', record['candidate'], path.name, 'bytes', path.stat().st_size, flush=True)
    stats, labels, groups, day_labels = {}, Counter(), Counter(), Counter()
    rows = 0; sample = None; rng = np.random.default_rng(SEED + number)
    sketch = UniqueSketch(); schema = None; target = None; chunk_duplicates = 0
    began = time.monotonic(); last = began
    for chunk_no, chunk in enumerate(readers(path), 1):
        if time.monotonic() - START > MAX_SECONDS: raise TimeoutError('Total investigation time budget exceeded')
        chunk.columns = [str(c).strip() for c in chunk.columns]
        if chunk.columns.duplicated().any(): raise ValueError('Duplicate column names after trimming')
        if schema is None:
            schema = list(chunk.columns)
            priority = (['detailed-label','label'] if record['candidate']=='IoT-23' else
                        ['activity','attack','attack_type','attack_cat','category','class','label'])
            lookup = {c.lower(): c for c in schema}
            target = next((lookup[c] for c in priority if c in lookup), None)
            print('Schema:', len(schema), 'columns; target:', target, flush=True)
        if list(chunk.columns) != schema: raise ValueError('Schema changed during scan')
        n = len(chunk); rows += n
        y = chunk[target].fillna('<missing>').astype(str).str.strip() if target else pd.Series(['<unlabeled>']*n, index=chunk.index)
        labels.update(y.value_counts().to_dict())
        if 'topology' in chunk:
            groups.update({str(k): int(v) for k,v in chunk.groupby(['topology',target], dropna=False).size().items()} if target else {})
        for column in schema:
            s = chunk[column]
            missing = s.isna()
            if not pd.api.types.is_numeric_dtype(s):
                missing = missing | s.astype(str).str.strip().isin(['','-','(empty)'])
            numeric = pd.to_numeric(s.mask(missing), errors='coerce')
            finite = numeric.notna() & np.isfinite(numeric)
            values = numeric[finite].to_numpy(dtype=float)
            item = stats.setdefault(column, {'missing':0,'numeric_parse_count':0,'nonfinite':0,
                     'finite_count':0,'min':None,'max':None, 'sum':0.0, 'sum_squares':0.0,'observed_dtypes':set()})
            item['observed_dtypes'].add(str(s.dtype)); item['missing'] += int(missing.sum())
            item['numeric_parse_count'] += int(numeric.notna().sum())
            item['nonfinite'] += int((numeric.notna() & ~np.isfinite(numeric)).sum())
            item['finite_count'] += len(values)
            if len(values):
                lo,hi = float(values.min()),float(values.max())
                item['min'] = lo if item['min'] is None else min(item['min'],lo)
                item['max'] = hi if item['max'] is None else max(item['max'],hi)
                item['sum'] += float(values.sum()); item['sum_squares'] += float(np.square(values).sum())
            if column.lower() in {'flow_start_milliseconds', 'flow_start_ms'}:
                dates = pd.to_datetime(numeric, unit='ms', utc=True, errors='coerce').dt.strftime('%Y-%m-%d').fillna('<invalid>')
                table = pd.DataFrame({'day': dates, 'label': y}).value_counts()
                day_labels.update({str(k): int(v) for k,v in table.items()})
        predictors = [c for c in schema if not excluded_identifier(c)]
        hashed = pd.util.hash_pandas_object(chunk[predictors], index=False).to_numpy()
        sketch.add(hashed)
        chunk_duplicates += int(pd.Series(hashed).duplicated().sum())
        # Uniform priority reservoir across the ENTIRE file, not its first rows.
        priorities = rng.random(n)
        keep = np.argpartition(priorities, min(SAMPLE_ROWS,n)-1)[:min(SAMPLE_ROWS,n)]
        part = chunk.iloc[keep].copy(); part['__priority'] = priorities[keep]
        sample = part if sample is None else pd.concat([sample,part],ignore_index=True)
        if len(sample) > SAMPLE_ROWS: sample = sample.nsmallest(SAMPLE_ROWS,'__priority')
        if time.monotonic()-last > 20 or chunk_no == 1:
            print(path.name, 'chunks',chunk_no,'rows',rows,'seconds',round(time.monotonic()-began,1),flush=True)
            write_json(folder / 'progress.json', {'rows_scanned':rows, 'chunk':chunk_no,'complete':False})
            last = time.monotonic()
    if rows == 0: raise ValueError('Empty table')
    sample = sample.drop(columns='__priority').reset_index(drop=True)
    numeric_sample = sample.apply(pd.to_numeric, errors='coerce').replace([np.inf,-np.inf],np.nan)
    numeric_sample.corr(method='spearman').to_csv(folder / 'sample_spearman.csv')
    column_rows = []
    for c,item in stats.items():
        count = item['finite_count']
        item['observed_dtypes'] = sorted(item['observed_dtypes'])
        item['mean'] = item['sum']/count if count else None
        item['std'] = math.sqrt(max(0,item['sum_squares']/count-item['mean']**2)) if count else None
        item['numeric_parse_fraction_nonmissing'] = item['numeric_parse_count']/max(1,rows-item['missing'])
        item['sample_unique'] = int(sample[c].nunique(dropna=False))
        # Do not expose raw IP addresses/identifiers in downloaded evidence.
        if not excluded_identifier(c): item['sample_top_values'] = {str(k):int(v) for k,v in sample[c].fillna('<missing>').value_counts().head(8).items()}
        column_rows.append({'column':c, **{k:v for k,v in item.items() if k not in {'sample_top_values','observed_dtypes'}}})
    pd.DataFrame(column_rows).to_csv(folder / 'column_quality.csv',index=False)
    pd.DataFrame(sorted(labels.items()),columns=['label','rows']).to_csv(folder / 'label_counts.csv',index=False)
    write_json(folder / 'column_details.json',stats)
    write_json(folder / 'day_label_counts.json',day_labels)
    write_json(folder / 'topology_label_counts.json',groups)
    sample_predictors = [c for c in schema if not excluded_identifier(c)]
    sample_safe = sample[sample_predictors].copy()
    if target: sample_safe['audit_label'] = sample[target].astype(str)
    # A compact anonymized numeric/categorical sample allows follow-up checks,
    # but it is an audit sample, not an approved published or training dataset.
    sample_safe.head(1000).to_csv(folder / 'audit_sample.csv',index=False)
    conflicts = None
    if target:
        h = pd.util.hash_pandas_object(sample[sample_predictors].astype(str),index=False)
        conflicts = int(pd.DataFrame({'h':h,'y':sample[target]}).groupby('h').y.nunique().gt(1).sum())
    assoc = []
    if target:
        for c in sample_predictors:
            vals = sample[c].fillna('<missing>').astype(str)
            if vals.nunique() <= 80:
                tab = pd.crosstab(vals,sample[target])
                assoc.append({'column':c,'sample_cardinality':int(vals.nunique()),
                              'majority_label_purity':float(tab.max(axis=1).sum()/tab.to_numpy().sum())})
    write_json(folder / 'sample_categorical_purity.json',assoc)
    bounded = path.name=='conn.log.labeled' or '.features.' in path.name
    summary = {**record, 'rows_scanned':rows,'schema':schema,'target':target,
               'labels':dict(labels),'scan_scope':'bounded scenario prefix' if bounded else 'full table',
               'possible_truncation':bounded and rows>=IOT_LOG_ROW_LIMIT,
               'excluded_predictors':[c for c in schema if excluded_identifier(c)],
               'feature_vector_unique_estimate':sketch.estimate(),
               'unique_estimator':'HLL p=14; RSE approximately0.81%; dtype-dependent hashes, not exact canonical duplicates',
               'within_chunk_hash_duplicate_lower_bound':chunk_duplicates,
               'sample_rows':len(sample),'sample_conflicting_feature_hash_groups':conflicts,
               'seconds':time.monotonic()-began,'report_directory':str(folder),
               'source_sha256':sha256(path)}
    if path.suffix == '.parquet':
        summary['parquet_total_rows'] = pq.ParquetFile(path).metadata.num_rows
        metadata_path = path.with_name(path.name.replace('.features.', '.metadata.'))
        if metadata_path != path and metadata_path.exists():
            meta = pq.ParquetFile(metadata_path)
            summary['paired_metadata_schema'] = meta.schema_arrow.names
            summary['paired_metadata_rows'] = meta.metadata.num_rows
            summary['paired_metadata_join_contract'] = 'scenario filename + source_row; NOT implicit row order'
            assert meta.metadata.num_rows == summary['parquet_total_rows']
    write_json(folder/'summary.json',summary)
    STATE['datasets'].append(summary); checkpoint()
    print('COMPLETE PROFILE',path.name,'rows',rows,'labels',dict(labels),'seconds',round(summary['seconds'],1),flush=True)
    return summary

print('COMPLETE profiler definitions', flush=True)
'''

scan = r'''
print('START full data audit; each table checkpoints independently', flush=True)
for number, record in enumerate(FILES, 1):
    try: profile(record,number)
    except Exception as exc:
        failure = {'candidate':record['candidate'],'path':record['path'],
                   'error':repr(exc),'traceback':traceback.format_exc()}
        STATE['failures'].append(failure); checkpoint()
        print('FAILED table; preserved evidence:',failure,flush=True)
for candidate in ['NF-ToN-IoT-v3','NF-BoT-IoT-v3','BCCC-cPacket-Cloud-DDoS-2024','IoT-23','LAN-SDN-NIDS']:
    if candidate not in SELECTED_CANDIDATES: continue
    if not any(r['candidate']==candidate for r in STATE['datasets']):
        STATE['failures'].append({'candidate':candidate,'error':'No successfully scanned table; see inventory/access evidence'})
checkpoint()
print('COMPLETE table audit:',len(STATE['datasets']),'successful tables;',len(STATE['failures']),'failures',flush=True)
'''

lan_exact = r'''
print('START LAN consolidated exact duplicate and topology coverage audit',flush=True)
lan = next((r for r in FILES if Path(r['path']).name=='FULL_SDN_NIDS.parquet'),None)
if lan:
    frame = pd.read_parquet(lan['path']); frame.columns = frame.columns.str.strip()
    columns = [c for c in frame if not excluded_identifier(c)]
    feature_hash = pd.util.hash_pandas_object(frame[columns],index=False)
    label = next((c for c in frame if c.lower()=='label'),None)
    exact = {'rows':len(frame),'columns':list(frame),
             'exact_full_row_duplicates':int(frame.duplicated().sum()),
             'exact_predictor_duplicates':int(frame.duplicated(subset=columns).sum()),
             'predictor_columns':columns,'topology_is_audit_group_not_predictor':True,
             'raw_timestamps_available':any('timestamp' in c.lower() or c.lower()=='ts' for c in frame)}
    if label:
        conflict = pd.DataFrame({'h':feature_hash,'label':frame[label]}).groupby('h').label.nunique()
        exact['candidate_conflicting_predictor_hash_groups'] = int(conflict.gt(1).sum())
    if 'topology' in frame and label:
        pd.crosstab(frame['topology'],frame[label]).to_csv(REPORTS/'lan_topology_label_coverage.csv')
        grouped = pd.DataFrame({'h':feature_hash,'topology':frame['topology']}).groupby('h').topology.nunique()
        exact['predictor_hash_groups_crossing_topologies'] = int(grouped.gt(1).sum())
    # Exact vector-level matching of hashes is only a candidate lineage test:
    # dtype / float serialization can differ between raw CSV and consolidated Parquet.
    projected = Counter()
    lineage = []
    reference = Counter(pd.util.hash_pandas_object(frame[columns+[label]],index=False).tolist())
    for record in FILES:
        if record['candidate']!='LAN-SDN-NIDS' or not record.get('topology'): continue
        seen = 0
        for chunk in pd.read_csv(record['path'],chunksize=CHUNK_ROWS,float_precision='round_trip'):
            chunk.columns = chunk.columns.str.strip()
            assert set(columns+[label]).issubset(chunk.columns)
            projected.update(pd.util.hash_pandas_object(chunk[columns+[label]],index=False).tolist())
            seen += len(chunk)
        lineage.append({'topology':record['topology'],'rows':seen})
    exact['raw_csv_projection_rows'] = lineage
    exact['raw_projection_hash_multiset_matches_parquet'] = projected==reference
    exact['raw_projection_hash_multiset_mismatch_excess_rows'] = sum((projected-reference).values())
    exact['lineage_note'] = 'Hash comparison, not proof of equality; false mismatch possible from dtype/float serialization.'
    write_json(REPORTS/'lan_exact_audit.json',exact)
    print(json.dumps(exact,indent=2),flush=True)
    del frame,feature_hash
else: print('Unavailable consolidated LAN file; audit explicitly skipped',flush=True)
print('COMPLETE LAN exact audit',flush=True)
'''

compare = r"""
print('START feature compatibility and decision report',flush=True)
summaries = STATE['datasets']
compatibility = []
for i,a in enumerate(summaries):
    for b in summaries[i+1:]:
        if a['candidate']==b['candidate']: continue
        ca,cb=set(a['schema']),set(b['schema'])
        compatibility.append({'a':a['candidate'],'a_file':Path(a['path']).name,
             'b':b['candidate'],'b_file':Path(b['path']).name,
             'common_column_names':sorted(ca&cb),
             'common_label_strings':sorted(set(a['labels'])&set(b['labels'])),
             'warning':'Name overlap does not establish matching units, flow keys or observation intervals'})
write_json(REPORTS/'pairwise_schema_overlap.json',compatibility)
rows=[]
for r in summaries:
    rows.append({'candidate':r['candidate'],'file':Path(r['path']).name,
                 'rows_scanned':r['rows_scanned'],'columns':len(r['schema']),
                 'labels':len(r['labels']),'scope':r['scan_scope'],'seconds':r['seconds']})
table=pd.DataFrame(rows); table.to_csv(REPORTS/'dataset_comparison.csv',index=False)
print(table.to_string(index=False),flush=True)
decision = '''# Dataset decision evidence

This is an investigation, not evidence that pooling improves performance.

- LAN-SDN-NIDS is the provisional primary choice for SDN-specific analysis.
  Five topology files and their consolidated Parquet are alternate representations,
  not independent extra observations. Never concatenate all six as training rows.
  Verify topology holdout class coverage, cross-topology duplicates, feature conflicts,
  and traffic-only versus OpenFlow-feature ablation before classifier claims.
- NF-ToN-IoT-v3 plus NF-BoT-IoT-v3 is the compatible-pooling candidate.
  Verify identical schemas/units, then compare source-only, pooled and held-out-source
  tests with fixed source-specific test sets. Preserve original attack families.
  Start a clean shared-label task with Benign/DoS/DDoS. Do not map Scanning to
  Reconnaissance automatically, and do not relabel unrelated attacks as benign.
- BCCC NTLFlowLyzer and IoT-23 Zeek records are independent robustness candidates,
  not automatic additions to the NetFlow schema. Frame byte counts and IP byte
  counts, timeout rules and directional keys can differ despite similar names.
- Missing OpenFlow fields cannot be replaced by zero and treated as observations.
  A union of these schemas risks letting missingness/source identity reveal labels.
- Investigate feature duplicates and contradictory labels before splitting. Raw IPs,
  capture dates, topology labels and source names are audit metadata, not predictors.
  Chronological splitting requires class coverage checks: attacks can occur on separate days.
- Published sources have inconsistent totals; trust measured rows with explicit scope.
  HLL estimates and random-sample correlations are not exact full-data measurements.
- IoT-23 content probes are bounded prefixes per scenario, not representative samples
  of all 325M+ records. Metadata row counts establish total size without a full content scan.
  Mirror licensing and original licensing differ; resolve permissions before republishing.
- A cleaned combined Kaggle dataset can be prepared remotely after selecting the
  schema, label mapping, split rules and redistribution permissions. No publication
  or credentials are embedded in this notebook.

Consult dataset_comparison.csv, per-file summary/quality/labels, official metadata,
lan_exact_audit.json and run_state.json. A missing candidate is a coverage gap.
'''
(REPORTS/'decision.md').write_text(decision,encoding='utf-8')
(REPORTS/'index.html').write_text('<html><head><meta charset="utf-8"></head><body><h1>Dataset audit</h1>'+
     table.to_html(index=False)+'<pre>'+__import__('html').escape(decision)+'</pre></body></html>',encoding='utf-8')
STATE['completed_utc']=datetime.now(timezone.utc).isoformat()
STATE['status']='complete_with_gaps' if STATE['failures'] else 'complete'
STATE['elapsed_seconds']=time.monotonic()-START
checkpoint()
print('COMPLETE compatibility report',STATE['status'],'elapsed seconds',STATE['elapsed_seconds'],flush=True)
"""

export = r'''
print('START export compact evidence bundle; no large dataset files included',flush=True)
# The bundle contains all data reports and logs flushed so far. The saved output
# directory also retains this final cell's ending log/executed export after its hook runs.
manifest={str(p.relative_to(ROOT)):{'bytes':p.stat().st_size,'sha256':sha256(p)}
          for p in ROOT.rglob('*') if p.is_file() and p.suffix not in {'.zip','.tmp'}}
write_json(ROOT/'SHA256_MANIFEST.json',manifest)
bundle=ROOT.parent/(RUN_ID+'-reports.zip')
with zipfile.ZipFile(bundle,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for p in ROOT.rglob('*'):
        if p.is_file() and p.suffix!='.tmp': z.write(p,str(Path(RUN_ID)/p.relative_to(ROOT)))
print('COMPLETE report bundle',bundle,'bytes',bundle.stat().st_size,flush=True)
print('Retrieve only the report zip and notebook/kernel logs locally; bulk input/cache files remain remote.',flush=True)
print('Final live log/executed notebook are saved separately; archive/checksums precede final-cell completion.',flush=True)
'''


def build(input_manifest: dict | None = None) -> None:
    snapshot = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    cells = [nbf.v4.new_markdown_cell(intro, id="objective")]
    stages = [
        ("environment", setup.replace("__RUN_ID__", repr(RUN_ID)).replace("__SOURCE_SNAPSHOT__", repr(snapshot))),
        ("observability", logging_code),
        ("acquisition", acquire.replace("__INPUT_MANIFEST__", repr(input_manifest or {}))),
        ("profiling-contract", profiler),
        ("full-audit", scan),
        ("lan-exact-audit", lan_exact),
        ("compatibility", compare),
        ("export", export),
    ]
    for name, source in stages:
        code = textwrap.dedent(source).strip()
        compile(code, f"cell-{name}", "exec")
        cells.append(nbf.v4.new_code_cell(code, id=name))
    notebook = nbf.v4.new_notebook(cells=cells, metadata={
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
        "project": "DDoS_Prevention_and_Mitigation", "source_snapshot": snapshot,
    })
    nbf.validate(notebook)
    dest = DEST / "01_public_dataset_investigation.ipynb"
    nbf.write(notebook, dest)
    print(dest)
    print("Notebook SHA256:", hashlib.sha256(dest.read_bytes()).hexdigest())


if __name__ == "__main__":
    manifest_path = HERE / "input_manifest.json"
    build(json.loads(manifest_path.read_text()) if manifest_path.exists() else None)
