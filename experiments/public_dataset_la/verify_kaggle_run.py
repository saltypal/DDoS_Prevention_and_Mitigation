"""Verify downloaded evidence and Parquet metadata, without local dataset analysis."""
import argparse
import json
from pathlib import Path
import pyarrow.parquet as pq
from sdn_ddos.runtime.run import write_json, sha256


def verify(root, expected_commit):
    root=Path(root)
    manifests=list(root.rglob('SHA256_MANIFEST.json'))
    if len(manifests)!=1:
        raise ValueError(f'Expected exactly one artifact manifest: {manifests}')
    manifest=manifests[0]
    source=json.loads(manifest.read_text(encoding='utf-8'))
    verified=[]; missing=[]; failed=[]
    for relative, info in source.items():
        path=manifest.parent/relative
        if not path.exists(): missing.append(relative)
        elif path.stat().st_size!=info['bytes'] or sha256(path)!=info['sha256']: failed.append(relative)
        else: verified.append(relative)
    environment=json.loads((manifest.parent/'environment.json').read_text())
    if environment['revision']!=expected_commit:
        raise RuntimeError('Unexpected source commit')
    ledger=json.loads((manifest.parent/'cell_ledger.json').read_text())
    if any(item['status']!='complete' for item in ledger):
        raise RuntimeError('Incomplete/failed recorded stages')
    parquets={}
    for path in (manifest.parent/'parquet').glob('*') if (manifest.parent/'parquet').exists() else []:
        files=list(path.rglob('*.parquet'))
        if files:
            parquets[path.name]={'files':len(files),'rows_from_footers':sum(pq.ParquetFile(p).metadata.num_rows for p in files),
                                  'bytes':sum(p.stat().st_size for p in files)}
    result={'expected_commit':expected_commit,'manifest_entries':len(source),'verified':len(verified),
            'not_retrieved':missing,'failed':failed,'completed_stages':len(ledger),'parquet_metadata':parquets}
    write_json(root/'verification_summary.json',result)
    if failed: raise RuntimeError(f'Artifact checksum mismatch: {failed}')
    print(json.dumps(result,indent=2))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',required=True)
    parser.add_argument('--commit',required=True)
    args=parser.parse_args()
    verify(args.root,args.commit)
