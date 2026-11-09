"""Load trusted, version-pinned bundles and perform real conditional expert dispatch."""
from pathlib import Path
import json
import joblib
import numpy as np
from scipy.special import logit
from sdn_ddos.models.classifiers import SPARK_FAMILIES, predict_spark


class ClassifierBundle:
    def __init__(self, directory, spark=None):
        self.root = Path(directory)
        self.info = json.loads((self.root / 'bundle.json').read_text())
        self.spark = spark
        if self.info['family'] in SPARK_FAMILIES:
            if spark is None:
                raise ValueError('A Spark session is required for this saved classifier')
            from pyspark.ml import PipelineModel
            self.model = PipelineModel.load(str(self.root / 'spark_model'))
        else:
            self.model = joblib.load(self.root / 'python_model.joblib')

    def predict(self, table):
        contract = self.info['contract']
        missing = set(contract['numeric'] + contract['categorical']) - set(table.columns)
        if missing:
            raise ValueError(f'Input feature contract is incomplete: {missing}')
        if self.info['family'] in SPARK_FAMILIES:
            return predict_spark(self.model, table, contract, self.spark)
        return self.model.predict_proba(table)[:, 1]


class DomainMixtureBundle:
    def __init__(self, directory, experts_root=None, spark=None):
        self.root = Path(directory)
        self.info = json.loads((self.root / 'bundle.json').read_text())
        self.gate = joblib.load(self.root / 'gate.joblib')
        self.calibrator = joblib.load(self.root / 'calibrator.joblib')
        experts_root = Path(experts_root) if experts_root else self.root.parent
        self.experts = [ClassifierBundle(experts_root / f'domain-expert-{index}', spark)
                        for index in range(len(self.info['experts']))]

    def predict(self, table):
        weights = self.gate.route(table[self.info['gate_features']], self.info['top_k'])
        positive = np.zeros(len(table))
        calls = []
        for index, expert in enumerate(self.experts):
            rows = np.flatnonzero(weights[:, index] > 0)
            if len(rows):
                values = expert.predict(table.iloc[rows])
                positive[rows] += weights[rows, index] * values
            calls.append(len(rows))
        scores = self.calibrator.predict_proba(logit(np.clip(positive, 1e-6, 1 - 1e-6))[:, None])[:, 1]
        return {'score': scores, 'ddos': scores >= self.info['threshold'], 'expert_rows_scored': calls}


class EnsembleBundle:
    def __init__(self, directory, benchmark_root, spark=None):
        self.root = Path(directory)
        self.info = json.loads((self.root / 'bundle.json').read_text())
        self.combiner = joblib.load(self.root / 'combiner.joblib')
        self.calibrator = joblib.load(self.root / 'calibrator.joblib')
        self.members = [ClassifierBundle(Path(benchmark_root) / 'models' / f'{self.info["condition"]}-{family}', spark)
                        for family in self.info['members']]

    def predict(self, table):
        raw = np.column_stack([member.predict(table) for member in self.members])
        mixed = self.combiner.predict_proba(raw)[:, 1]
        scores = self.calibrator.predict_proba(logit(np.clip(mixed, 1e-6, 1 - 1e-6))[:, None])[:, 1]
        return {'score': scores, 'ddos': scores >= self.info['threshold']}
