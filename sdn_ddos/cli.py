import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from sdn_ddos.runtime.run import Run, spark_session


def execute(config, output=None):
    if not Path('/kaggle/working').exists() and not config.get('allow_local_fixture', False):
        raise RuntimeError('Scientific processing is Kaggle-only. Local execution is limited to explicit contract fixtures.')
    name = config.get('name', 'run') + '-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    root = output or str(Path('/kaggle/working/experiments/public_dataset_la/runs') / name)
    run = Run(root, config)
    spark = None
    try:
        spark = spark_session(config)
        with run.stage('runtime-preflight'):
            print('Spark version', spark.version, 'master', spark.sparkContext.master, flush=True)
            assert spark.range(10).count() == 10
        if config['stage'] == 'audit':
            from sdn_ddos.data.sources import acquire, ingest
            from sdn_ddos.data.prepare import sanitize, partition
            from sdn_ddos.analysis.eda import profile
            for source in config.get('sources', ['ton', 'bot', 'lan']):
                with run.stage(f'{source}-engineering-audit'):
                    raw = ingest(acquire(source, config, run), spark, config, run)
                    data, contract = sanitize(raw, source, run)
                    data = partition(data, source, config, run)
                    profile(data, source, contract, config, run)
        elif config['stage'] == 'prepare':
            from sdn_ddos.data.prepare import prepare_source
            for source in config.get('sources', ['ton', 'bot', 'lan']):
                prepare_source(source, spark, config, run)
        elif config['stage'] == 'benchmark':
            from sdn_ddos.models.benchmark import benchmark
            benchmark(spark, config, run)
        else:
            raise ValueError(f'Unknown stage {config["stage"]}')
    finally:
        if spark:
            spark.stop()
        run.finalize()
    return run.root


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--output')
    args = parser.parse_args()
    execute(json.loads(Path(args.config).read_text()), args.output)


if __name__ == '__main__':
    main()
