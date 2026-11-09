from __future__ import annotations

import contextlib
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, default=str, allow_nan=False), encoding='utf-8')
    temporary.replace(path)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


class Tee:
    def __init__(self, stream, log):
        self.stream, self.log = stream, log

    def write(self, text):
        self.stream.write(text)
        self.log.write(text)
        self.log.flush()

    def flush(self):
        self.stream.flush()
        self.log.flush()


class Run:
    def __init__(self, root, config):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=False)
        self.ledger = []
        self.config = config
        for name in ('logs', 'reports', 'figures', 'contracts', 'models', 'scores', 'manifests'):
            (self.root / name).mkdir()
        write_json(self.root / 'resolved_config.json', config)
        revision = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True)
        environment = {'python': sys.version, 'executable': sys.executable, 'platform': platform.platform(),
                       'cpu_count': os.cpu_count(), 'revision': revision.stdout.strip() or 'uncommitted-snapshot',
                       'cwd': str(Path.cwd()), 'utc': datetime.now(timezone.utc).isoformat(), 'packages': {}}
        import shutil
        if shutil.which('java'):
            java = subprocess.run(['java','-version'],capture_output=True,text=True)
            environment['java_version'] = (java.stderr + java.stdout).strip()
        environment['gpu_runtime_requested'] = False
        for package in ('numpy', 'pandas', 'pyarrow', 'scikit-learn', 'pyspark', 'xgboost', 'lightgbm', 'catboost'):
            try:
                environment['packages'][package] = importlib.metadata.version(package)
            except importlib.metadata.PackageNotFoundError:
                environment['packages'][package] = None
        write_json(self.root / 'environment.json', environment)
        freeze = subprocess.run([sys.executable, '-m', 'pip', 'freeze'], capture_output=True, text=True)
        (self.root / 'resolved-packages.txt').write_text(freeze.stdout, encoding='utf-8')
        print('RUN', self.root, environment, flush=True)

    @contextlib.contextmanager
    def stage(self, name):
        entry = {'stage': name, 'start_utc': datetime.now(timezone.utc).isoformat(), 'status': 'running'}
        self.ledger.append(entry)
        write_json(self.root / 'cell_ledger.json', self.ledger)
        started = time.monotonic()
        with (self.root / 'logs' / (name + '.log')).open('a', encoding='utf-8') as log:
            with contextlib.redirect_stdout(Tee(sys.stdout, log)), contextlib.redirect_stderr(Tee(sys.stderr, log)):
                print('START', name, flush=True)
                try:
                    yield
                    entry['status'] = 'complete'
                except BaseException:
                    entry['status'] = 'failed'
                    traceback.print_exc()
                    raise
                finally:
                    entry['seconds'] = time.monotonic() - started
                    write_json(self.root / 'cell_ledger.json', self.ledger)
                    print('END', name, entry, flush=True)

    def finalize(self):
        # The ledger is finalized before hashing; never hash a log while it is open.
        files = {str(p.relative_to(self.root)): {'bytes': p.stat().st_size, 'sha256': sha256(p)}
                 for p in sorted(self.root.rglob('*')) if p.is_file() and p.name != 'SHA256_MANIFEST.json'}
        write_json(self.root / 'SHA256_MANIFEST.json', files)


def spark_session(config):
    import shutil
    if not shutil.which('java'):
        raise RuntimeError('Java 17+ is required by the pinned Spark runtime. Install it in the Kaggle runtime before processing.')
    from pyspark.sql import SparkSession
    return (SparkSession.builder.master('local[2]').appName('sdn-ddos-research')
            .config('spark.driver.memory', config.get('spark_driver_memory', '8g'))
            .config('spark.sql.shuffle.partitions', str(config.get('shuffle_partitions', 32)))
            .config('spark.sql.ansi.enabled', 'false')
            .config('spark.local.dir', config.get('spark_temp', '/kaggle/temp/ddos-spark'))
            .getOrCreate())
