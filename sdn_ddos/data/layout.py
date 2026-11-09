"""Reconstruct read-only Parquet layouts from flat Kaggle Dataset assets."""
from pathlib import Path
import json
import os
from sdn_ddos.runtime.run import sha256


def materialize_layouts(input_root, cache_root='/kaggle/temp/ddos-prepared-layouts'):
    roots=[]
    for manifest in Path(input_root).rglob('prepared-layout.json'):
        layout=json.loads(manifest.read_text())
        destination=Path(cache_root)/sha256(manifest)
        destination.mkdir(parents=True,exist_ok=True)
        for relative, info in layout['files'].items():
            path=Path(relative)
            asset=Path(info['asset'])
            if path.is_absolute() or '..' in path.parts or len(asset.parts)!=1:
                raise ValueError('Unsafe prepared dataset layout')
            source=manifest.parent/asset
            if source.stat().st_size!=info['bytes'] or sha256(source)!=info['sha256']:
                raise RuntimeError(f'Prepared Dataset asset differs from its manifest: {asset}')
            target=destination/path
            target.parent.mkdir(parents=True,exist_ok=True)
            if not target.exists():
                os.symlink(source.resolve(),target)
        roots.append(destination)
    return roots
