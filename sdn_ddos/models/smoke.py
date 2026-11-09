"""Generated software-contract fixtures; NEVER evidence of real detection accuracy."""
import numpy as np
import pandas as pd
from sdn_ddos.models.classifiers import FAMILIES
from sdn_ddos.models.benchmark import execute_fit
from sdn_ddos.runtime.run import write_json


def model_smoke(config, run):
    rng=np.random.default_rng(42)
    n=600
    x=rng.normal(size=n)
    table=pd.DataFrame({'row_id':[f'fixture-{i}' for i in range(n)],'x':x,'z':rng.normal(size=n),
                        'empty':np.full(n,np.nan),'protocol':np.where(x>0,'tcp','udp'),
                        'target':(x+rng.normal(scale=0.3,size=n)>0).astype(float)})
    table.loc[::11,'z']=np.nan
    train=run.root/'fixture-train.parquet'
    heldout=run.root/'fixture-heldout.parquet'
    table.iloc[:400].to_parquet(train,index=False)
    table.iloc[400:].to_parquet(heldout,index=False)
    contract={'numeric':['x','z','empty'],'categorical':['protocol'],'scope':'generated contract fixture only'}
    status=[]
    for family in FAMILIES:
        with run.stage(f'contract-{family}'):
            request={'family':family,'train':str(train),'predict':{'heldout':str(heldout)},'contract':contract,
                     'output':str(run.root/'models'/family),'verify_reload':True,'spark_driver_memory':'4g'}
            result=execute_fit(request,config.get('fit_timeout_seconds',180))
            status.append(dict(family=family,**result))
            write_json(run.root/'reports'/'model-contracts.json',status)
            print(family,result,flush=True)
    if any(r['status']!='complete' for r in status):
        raise RuntimeError('One or more generated model contract checks failed; inspect persisted fit logs')
    return status
