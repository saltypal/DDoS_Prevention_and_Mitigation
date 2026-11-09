"""One bounded fit per child process, with complete model persistence and diagnostics."""
import argparse
import json
import os
from pathlib import Path
import time
import joblib
import numpy as np
import pandas as pd
from sdn_ddos.models.classifiers import SPARK_FAMILIES, python_pipeline, fit_spark, predict_spark
from sdn_ddos.runtime.run import spark_session, write_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--request', required=True)
    args = parser.parse_args()
    request = json.loads(Path(args.request).read_text())
    root = Path(request['output'])
    root.mkdir(parents=True, exist_ok=False)
    train = pd.read_parquet(request['train'])
    contract = dict(request['contract'])
    # Training-only empty-column decision; persist it and apply unchanged to all score inputs.
    contract['numeric'] = [c for c in contract['numeric'] if train[c].notna().any()]
    if train['target'].nunique() != 2:
        raise ValueError('Training partition lacks a class')
    family = request['family']
    print('FIT START', family, 'rows', len(train), flush=True)
    start = time.monotonic()
    spark = None
    try:
        if family in SPARK_FAMILIES:
            spark = spark_session(request)
            model = fit_spark(family, train, contract, spark)
            model.write().save(str(root / 'spark_model'))
        else:
            model = python_pipeline(family, contract)
            model.fit(train, train['target'])
            joblib.dump(model, root / 'python_model.joblib')
        seconds = time.monotonic() - start
        write_json(root / 'bundle.json', dict(request, contract=contract, fit_seconds=seconds,
                                             raw_score_semantics='sigmoid-margin' if family == 'linear_svm' else 'uncalibrated_probability'))
        for name, path in request['predict'].items():
            table = pd.read_parquet(path)
            start = time.monotonic()
            if family in SPARK_FAMILIES:
                scores = predict_spark(model, table, contract, spark)
            else:
                scores = model.predict_proba(table)[:, 1]
            if not np.isfinite(scores).all():
                raise RuntimeError(f'Nonfinite scores: {name}')
            table[['row_id']].assign(score=scores).to_parquet(root / f'{name}-scores.parquet', index=False)
            print('SCORED', name, len(table), 'seconds', time.monotonic() - start, flush=True)
        print('FIT COMPLETE', family, seconds, flush=True)
    finally:
        if spark:
            spark.stop()


if __name__ == '__main__':
    main()
