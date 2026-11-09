"""Small generated contract fixtures, never public-data performance evidence."""
import ast
from pathlib import Path
import unittest
import numpy as np
import pandas as pd
import nbformat
import tempfile
from sdn_ddos.evaluation.alignment import align_scores
from sdn_ddos.models.combine import FeatureGate, WeightedMean, ProbabilityMean, grouped_folds
from sdn_ddos.evaluation.metrics import evaluate, choose_threshold
from sdn_ddos.features.contracts import feature_contract


class ContractChecks(unittest.TestCase):
    def test_score_identity(self):
        root=Path(__file__).resolve().parent/'runs'/'contract-fixtures'
        root.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as directory:
            path=Path(directory)/'scores.parquet'
            rows=pd.DataFrame({'row_id':['a','b']})
            pd.DataFrame({'row_id':['b','a'],'score':[0.8,0.2]}).to_parquet(path,index=False)
            np.testing.assert_allclose(align_scores(path,rows),[0.2,0.8])
            pd.DataFrame({'row_id':['a','b','extra'],'score':[0.2,0.8,0.5]}).to_parquet(path,index=False)
            with self.assertRaises(ValueError): align_scores(path,rows)
            pd.DataFrame({'row_id':['a','wrong'],'score':[0.2,0.8]}).to_parquet(path,index=False)
            with self.assertRaises(ValueError): align_scores(path,rows)
    def test_feature_exclusions(self):
        columns = ['row_id', 'source', 'topology', 'Attack', 'Label', 'DNS_QUERY_ID', 'FLOW_START_MILLISECONDS', 'IN_BYTES', 'PROTOCOL']
        result = feature_contract('ton', columns)
        self.assertEqual(result['numeric'], ['IN_BYTES'])
        self.assertEqual(result['categorical'], ['PROTOCOL'])

    def test_grouped_folds(self):
        table = pd.DataFrame({'feature_group': ['a','a','b','c','d','e','f','g','h'],
                              'session_group': ['u','v','v','w','x','y','z','q','r'],
                              'target': [0,0,1,0,1,0,1,0,1]})
        for train, test in grouped_folds(table):
            for key in ('feature_group', 'session_group'):
                self.assertFalse(set(table.iloc[train][key]) & set(table.iloc[test][key]))

    def test_threshold_ties_and_metrics(self):
        table = pd.DataFrame({'target': [0]*200+[1]*20, 'is_benign': [True]*200+[False]*20,
                              'attack_family': ['benign']*200+['ddos']*20})
        score = np.r_[np.zeros(198), [0.7,0.7], np.ones(20)*0.8]
        threshold = choose_threshold(table, score, 0.01)
        metrics = evaluate(table, score, threshold)
        self.assertEqual(metrics['recall'], 1)
        self.assertLessEqual(metrics['benign_fpr'], 0.01)
        with self.assertRaises(ValueError):
            evaluate(table, score[:-1])

    def test_ensemble_and_gate(self):
        rng=np.random.default_rng(42)
        features=rng.normal(size=(300,3))
        y=(features[:,0]>0).astype(int)
        scores=np.column_stack([np.where(y,0.85,0.15),rng.uniform(0.2,0.8,300),np.where(y,0.65,0.35)])
        for model in [ProbabilityMean(),WeightedMean()]:
            p=model.fit(scores,y).predict_proba(scores)
            self.assertTrue(np.isfinite(p).all())
            np.testing.assert_allclose(p.sum(axis=1),1)
        gate=FeatureGate().fit(features,scores,y)
        np.testing.assert_allclose(gate.route(features).sum(axis=1),1)
        self.assertTrue(np.all(np.count_nonzero(gate.route(features,2),axis=1)==2))
        self.assertTrue(np.isfinite(gate.predict(features,scores)).all())

    def test_generated_notebooks(self):
        root=Path(__file__).resolve().parent
        for path in (root/'notebooks').glob('*.ipynb'):
            if path.name=='01_public_dataset_investigation.ipynb': continue
            book=nbformat.read(path,as_version=4)
            nbformat.validate(book)
            for cell in book.cells:
                if cell.cell_type=='code': ast.parse(cell.source)


if __name__=='__main__':
    unittest.main(verbosity=2)
