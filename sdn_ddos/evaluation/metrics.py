import numpy as np
from sklearn.metrics import (confusion_matrix, precision_recall_fscore_support, average_precision_score,
                             roc_auc_score, matthews_corrcoef, balanced_accuracy_score, brier_score_loss)


def evaluate(table, scores, threshold=0.5, calibrated=True, _subgroups=True):
    scores = np.asarray(scores, dtype=float)
    if len(scores) != len(table) or not np.isfinite(scores).all():
        raise ValueError('Scores must align with rows and be finite')
    truth = table['target'].to_numpy(dtype=int)
    prediction = scores >= threshold
    tn, fp, fn, tp = confusion_matrix(truth, prediction, labels=[0, 1]).ravel()
    precision, recall, f1, _ = precision_recall_fscore_support(truth, prediction, average='binary', zero_division=0)
    benign = table['is_benign'].to_numpy(dtype=bool)
    benign_fp = int(prediction[benign].sum())
    result = {'rows': len(table), 'threshold': float(threshold), 'tn': int(tn), 'fp': int(fp), 'fn': int(fn), 'tp': int(tp),
              'precision': float(precision), 'recall': float(recall), 'f1': float(f1),
              'mcc': float(matthews_corrcoef(truth, prediction)), 'balanced_accuracy': float(balanced_accuracy_score(truth, prediction)),
              'average_precision': float(average_precision_score(truth, scores)) if truth.sum() else None,
              'roc_auc': float(roc_auc_score(truth, scores)) if len(np.unique(truth)) == 2 else None,
              'brier': float(brier_score_loss(truth, scores)) if calibrated else None,
              'benign_false_positives': benign_fp, 'benign_rows': int(benign.sum()),
              'benign_fpr': benign_fp / int(benign.sum()) if benign.sum() else None, 'families': {}}
    for family, indices in table.groupby('attack_family').indices.items():
        result['families'][str(family)] = {'rows': len(indices), 'ddos_predictions': int(prediction[indices].sum())}
    if _subgroups:
        for column in ('source', 'topology'):
            if column in table:
                result[column + '_breakdown'] = {str(group): evaluate(table.iloc[indices].reset_index(drop=True), scores[indices], threshold,
                                                                     calibrated=calibrated, _subgroups=False)
                                                 for group, indices in table.groupby(column).indices.items()}
    return result


def choose_threshold(table, scores, fpr_limit=0.01):
    """Threshold learned on its reserved development subset, never final-test observations."""
    benign = table['is_benign'].to_numpy(dtype=bool)
    if benign.sum() < 100:
        raise ValueError('Insufficient benign threshold-development observations; no reliable 1% operating-point estimate')
    groups = [benign]
    if 'source' in table:
        groups = [benign & table['source'].eq(source).to_numpy() for source in table['source'].unique()]
        if any(group.sum() < 100 for group in groups):
            raise ValueError('Each source needs at least100 benign threshold-development observations; increase the recorded development cohort')
    scores = np.asarray(scores)
    order = np.argsort(-scores, kind='stable')
    ordered = scores[order]
    positive = table['target'].to_numpy() == 1
    cumulative_benign = np.cumsum(benign[order])
    cumulative_positive = np.cumsum(positive[order])
    cumulative_groups = [np.cumsum(group[order]) for group in groups]
    ends = np.r_[np.flatnonzero(ordered[:-1] != ordered[1:]), len(ordered) - 1]
    feasible = [i for i in ends if all(cumulative[i] / group.sum() <= fpr_limit for cumulative, group in zip(cumulative_groups,groups))]
    if not feasible:
        return float(np.nextafter(np.max(scores), np.inf))
    best = max(feasible, key=lambda i: (cumulative_positive[i], -cumulative_benign[i], ordered[i]))
    return float(ordered[best])
