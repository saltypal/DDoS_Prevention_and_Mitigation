"""OOF ensembles and a feature-driven mixture gate on the same expert probabilities."""
import numpy as np
from scipy.optimize import minimize
from scipy.special import softmax
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline


class ProbabilityMean:
    def fit(self, scores, y):
        self.weights_ = np.ones(scores.shape[1]) / scores.shape[1]
        return self

    def predict_proba(self, scores):
        positive = np.asarray(scores) @ self.weights_
        return np.column_stack([1 - positive, positive])


class WeightedMean(ProbabilityMean):
    def fit(self, scores, y):
        def objective(weights):
            p = np.clip(scores @ weights, 1e-8, 1 - 1e-8)
            return -np.mean(y * np.log(p) + (1 - y) * np.log1p(-p))
        result = minimize(objective, np.ones(scores.shape[1]) / scores.shape[1], method='SLSQP',
                          bounds=[(0, 1)] * scores.shape[1], constraints={'type': 'eq', 'fun': lambda w: w.sum() - 1})
        if not result.success:
            raise RuntimeError(f'Weight optimization failed: {result.message}')
        self.weights_ = result.x
        return self


class FeatureGate:
    """Frozen-expert MoE: gate sees measured numeric features, never a source/label ID."""
    def fit(self, features, expert_scores, y, regularization=0.01):
        self.preprocessing_ = Pipeline([('impute', SimpleImputer(strategy='median', keep_empty_features=True)), ('scale', StandardScaler())])
        x = self.preprocessing_.fit_transform(features)
        x = np.column_stack([x, np.ones(len(x))])
        e = expert_scores.shape[1]
        def objective(flat):
            w = flat.reshape(x.shape[1], e)
            gates = softmax(x @ w, axis=1)
            p = np.clip(np.sum(gates * expert_scores, axis=1), 1e-8, 1 - 1e-8)
            loss = -np.mean(y * np.log(p) + (1 - y) * np.log1p(-p)) + regularization * np.mean(w * w)
            dp = ((p - y) / (p * (1 - p)))[:, None]
            gradient = x.T @ (dp * gates * (expert_scores - p[:, None])) / len(x)
            gradient += 2 * regularization * w / w.size
            return loss, gradient.ravel()
        result = minimize(objective, np.zeros(x.shape[1] * e), jac=True, method='L-BFGS-B', options={'maxiter': 150})
        if not result.success:
            raise RuntimeError(f'Gate optimization did not converge: {result.message}')
        self.weights_ = result.x.reshape(x.shape[1], e)
        return self

    def route(self, features, top_k=None):
        x = self.preprocessing_.transform(features)
        weights = softmax(np.column_stack([x, np.ones(len(x))]) @ self.weights_, axis=1)
        if top_k:
            selected = np.argpartition(weights, -top_k, axis=1)[:, -top_k:]
            mask = np.zeros_like(weights)
            np.put_along_axis(mask, selected, 1, axis=1)
            weights *= mask
            weights /= weights.sum(axis=1, keepdims=True)
        return weights

    def predict(self, features, expert_scores, top_k=None):
        return np.sum(self.route(features, top_k) * expert_scores, axis=1)


def connected_groups(table):
    """Connected components ensure BOTH identical features and flow groups stay together."""
    parent = np.arange(len(table))
    def find(index):
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index
    for column in ('feature_group', 'session_group'):
        first = {}
        for index, value in enumerate(table[column]):
            if value in first:
                parent[find(index)] = find(first[value])
            else:
                first[value] = index
    groups = np.array([find(i) for i in range(len(table))])
    return groups


def grouped_folds(table, folds=3):
    from sklearn.model_selection import GroupKFold
    groups=connected_groups(table)
    if len(np.unique(groups)) < folds:
        raise ValueError('Too few independent connected groups for OOF')
    splits = list(GroupKFold(n_splits=folds).split(table, table['target'], groups))
    for train, heldout in splits:
        if table.iloc[train]['target'].nunique() != 2:
            raise ValueError('OOF training fold lacks a class')
    return splits


def development_partitions(table, seed=42):
    """Stratify only WITHIN already protected development sources, never final tests."""
    from sklearn.model_selection import StratifiedGroupKFold
    import pandas as pd
    output={name:[] for name in ('selection','calibration','threshold')}
    for source,group in table.groupby('source',sort=True):
        group=group.reset_index(drop=True)
        components=connected_groups(group)
        splitter=StratifiedGroupKFold(n_splits=3,shuffle=True,random_state=seed)
        seen=[]
        for name,(_,indices) in zip(output,splitter.split(group,group['target'],groups=components)):
            subset=group.iloc[indices]
            if subset['target'].nunique()!=2:
                raise RuntimeError(f'{source}/{name}: connected development groups cannot provide binary coverage; review protocol')
            used=set(components[indices])
            if any(used & previous for previous in seen):
                raise RuntimeError('Development group overlap')
            seen.append(used)
            output[name].append(subset)
    return {name:pd.concat(pieces,ignore_index=True) for name,pieces in output.items()}
