"""Persist compact diagnostic curves independently of notebook rendering."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, precision_recall_curve, confusion_matrix
from sklearn.calibration import calibration_curve


def diagnostics(table, scores, directory, threshold=0.5, calibrated=False):
    directory=Path(directory)
    directory.mkdir(parents=True,exist_ok=True)
    truth=table['target'].to_numpy(dtype=int)
    def save(name):
        plt.tight_layout(); plt.savefig(directory/(name+'.png'),dpi=130); plt.close()
    plt.figure()
    matrix=confusion_matrix(truth,scores>=threshold,labels=[0,1])
    plt.imshow(matrix,cmap='Blues')
    for (row,column),value in np.ndenumerate(matrix):
        plt.text(column,row,str(value),ha='center',va='center')
    plt.xlabel('Predicted: non-DDoS / DDoS'); plt.ylabel('Observed'); plt.title('Development confusion counts')
    save('confusion')
    if len(np.unique(truth))==2:
        fpr,tpr,thresholds=roc_curve(truth,scores)
        pd.DataFrame({'fpr':fpr,'tpr':tpr,'threshold':thresholds}).to_csv(directory/'roc.csv',index=False)
        plt.figure(); plt.plot(fpr,tpr); plt.plot([0,1],[0,1],'--'); plt.xlabel('All-negative FPR (includes other attacks)'); plt.ylabel('DDoS recall'); save('roc')
        precision,recall,_=precision_recall_curve(truth,scores)
        pd.DataFrame({'precision':precision,'recall':recall}).to_csv(directory/'precision-recall.csv',index=False)
        plt.figure(); plt.plot(recall,precision); plt.xlabel('DDoS recall'); plt.ylabel('Precision'); save('precision-recall')
        fraction,mean=calibration_curve(truth,scores,n_bins=10,strategy='quantile')
        pd.DataFrame({'mean_score':mean,'observed_positive_fraction':fraction}).to_csv(directory/'reliability.csv',index=False)
        plt.figure(); plt.plot(mean,fraction,'o-'); plt.plot([0,1],[0,1],'--'); plt.xlabel('Mean score'); plt.ylabel('Observed DDoS fraction'); plt.title('Calibrated' if calibrated else 'Raw score reliability diagnostic'); save('reliability')
