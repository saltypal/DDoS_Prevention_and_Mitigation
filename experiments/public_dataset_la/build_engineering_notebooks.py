"""Generate standalone Kaggle notebooks. No dataset computation runs locally."""
from pathlib import Path
import ast
import hashlib
import textwrap
import nbformat as nbf

ROOT = Path(__file__).resolve().parent
DEST = ROOT / 'notebooks'
REVISION = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()

setup = r'''
import sys, json, time, hashlib, shutil, platform, importlib.metadata as metadata
from pathlib import Path
from datetime import datetime, timezone
from contextlib import contextmanager, redirect_stdout, redirect_stderr
print('START runtime setup', flush=True)
assert Path('/kaggle/working').exists(), 'Run on Kaggle; local data processing is disabled'
RUN_ID = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
OUT = Path('/kaggle/working/experiments/public_dataset_la/runs') / (STAGE + '-' + RUN_ID)
OUT.mkdir(parents=True, exist_ok=False)
for name in ['logs','reports','figures','parquet','contracts']:
    (OUT/name).mkdir()
from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.master('local[*]').appName('ddos-engineering').config('spark.sql.shuffle.partitions','32').getOrCreate()
environment = {'python':sys.version,'executable':sys.executable,'platform':platform.platform(),
               'source_snapshot':SOURCE_SNAPSHOT,'spark':spark.version,
               'versions':{p:metadata.version(p) for p in ['pandas','pyarrow','pyspark','matplotlib','nbformat']},
               'free_bytes':shutil.disk_usage(OUT).free}
(OUT/'environment.json').write_text(json.dumps(environment,indent=2))
assert environment['free_bytes'] > 5*1024**3, 'Insufficient working disk headroom'
print(environment, 'OUTPUT', OUT, flush=True)
ledger = []
class Tee:
    def __init__(self, console, file): self.console, self.file = console, file
    def write(self, text): self.console.write(text); self.file.write(text); self.file.flush()
    def flush(self): self.console.flush(); self.file.flush()
@contextmanager
def stage(name):
    start=time.time(); entry={'stage':name,'start':start,'status':'running'}; ledger.append(entry)
    def persist(): (OUT/'cell_ledger.json').write_text(json.dumps(ledger,indent=2))
    persist()
    with (OUT/'logs'/f'{name}.log').open('w') as log:
        with redirect_stdout(Tee(sys.stdout,log)), redirect_stderr(Tee(sys.stderr,log)):
            print('START',name,flush=True)
            try:
                yield
                entry['status']='complete'
            except BaseException:
                import traceback
                entry['status']='failed'; traceback.print_exc(); raise
            finally:
                entry['seconds']=time.time()-start; persist()
                print('END',name,entry['status'],entry['seconds'],flush=True)
print('END runtime setup', flush=True)
'''

acquire = r'''
with stage('inputs'):
    import requests
    specs=[]
    for name, filename in [('ton','NF-ToN-IoT-v3.csv'),('bot','NF-BoT-IoT-v3.csv')]:
        hits=list(Path('/kaggle/input').rglob(filename))
        assert len(hits)==1, (filename,hits)
        specs.append({'source':name,'path':str(hits[0]),'expected_columns':55,'version_observed':1})
    api='https://edatos.consorciomadrono.es/api'
    release=requests.get(api+'/datasets/:persistentId/',params={'persistentId':'doi:10.21950/QMAXKP'},timeout=90)
    release.raise_for_status(); release=release.json()['data']['latestVersion']
    (OUT/'contracts'/'lan_release.json').write_text(json.dumps(release,indent=2))
    files={x['dataFile']['id']:x['dataFile'] for x in release['files']}
    cache=Path('/kaggle/temp/ddos-public'); cache.mkdir(parents=True,exist_ok=True)
    for topology,fid in [('Linear',55750),('Mesh',55751),('Star',55752),('Subnets',55753),('Tree',55754)]:
        p=cache/f'{topology}.csv'; expected=files[fid]['checksum']
        if not p.exists():
            print('Downloading',topology,flush=True)
            with requests.get(api+f'/access/datafile/{fid}',stream=True,timeout=120) as r:
                r.raise_for_status()
                with p.open('wb') as handle:
                    for chunk in r.iter_content(4*1024*1024): handle.write(chunk)
        specs.append({'source':'lan','topology':topology,'path':str(p),'expected_columns':47,'official_checksum':expected})
    tables={}
    for spec in specs:
        p=Path(spec['path']); sha=hashlib.sha256()
        official=spec.get('official_checksum'); verify=hashlib.new(official['type'].lower().replace('-','')) if official else None
        with p.open('rb') as handle:
            while block:=handle.read(8*1024*1024):
                sha.update(block)
                if verify: verify.update(block)
        if verify: assert verify.hexdigest().lower()==official['value'].lower(), 'Source checksum mismatch'
        spec.update(sha256=sha.hexdigest(),bytes=p.stat().st_size)
        key=spec['source']+'_'+spec.get('topology','flows')
        frame=spark.read.option('header',True).option('mode','FAILFAST').csv(str(p))
        assert len(frame.columns)==spec['expected_columns'], (key,frame.columns)
        tables[key]=frame
        print('Verified',key,spec['bytes'],spec['sha256'],flush=True)
    (OUT/'contracts'/'inputs.json').write_text(json.dumps(specs,indent=2))
'''

eda = r'''
import matplotlib.pyplot as plt
import numpy as np
for key,frame in tables.items():
    with stage('eda-'+key):
        label='Attack' if 'Attack' in frame.columns else 'label'
        count=frame.count()
        labels=frame.groupBy(label).count().toPandas()
        labels.to_csv(OUT/'reports'/f'{key}-labels.csv',index=False)
        nulls=frame.agg(*[F.sum(F.when(F.col(c).isNull() | (F.trim(F.col(c))==''),1).otherwise(0)).alias(c) for c in frame.columns]).first().asDict()
        (OUT/'reports'/f'{key}-quality.json').write_text(json.dumps({'rows':count,'columns':frame.columns,'null_or_empty':nulls},indent=2))
        # Bounded sample: uniform sampling followed by a hard cap, explicitly not full-population quantiles.
        sample=frame.sample(False,min(1.,20000/max(count,1)),seed=42).limit(20000).toPandas()
        numeric=sample.drop(columns=[label],errors='ignore').apply(__import__('pandas').to_numeric,errors='coerce')
        numeric=numeric.replace([np.inf,-np.inf],np.nan).dropna(axis=1,how='all')
        numeric=numeric[[c for c in numeric if not any(t in c.lower() for t in ['addr','mac','timestamp','port','label'])]]
        fig,ax=plt.subplots(figsize=(9,4)); ax.bar(labels[label],labels['count']); ax.tick_params(axis='x',rotation=45); ax.set_title(key+' full-table class counts'); fig.tight_layout(); fig.savefig(OUT/'figures'/f'{key}-01-labels.png'); plt.show(); plt.close(fig)
        fig,ax=plt.subplots(figsize=(10,4)); missing=sorted(nulls,key=nulls.get,reverse=True)[:15]; ax.barh(missing,[nulls[c] for c in missing]); ax.set_title(key+' full-table null/empty counts'); fig.tight_layout(); fig.savefig(OUT/'figures'/f'{key}-02-missing.png'); plt.show(); plt.close(fig)
        if numeric.shape[1]:
            col=numeric.columns[0]
            fig,ax=plt.subplots(); numeric[col].hist(ax=ax,bins=50); ax.set_title(key+' sampled '+col); fig.savefig(OUT/'figures'/f'{key}-03-distribution.png'); plt.show(); plt.close(fig)
            fig,ax=plt.subplots(figsize=(8,6)); corr=numeric.iloc[:,:12].corr(); image=ax.imshow(corr,vmin=-1,vmax=1,cmap='coolwarm'); ax.set_xticks(range(len(corr)),corr.columns,rotation=90); ax.set_yticks(range(len(corr)),corr.columns); fig.colorbar(image,ax=ax); ax.set_title(key+' sampled correlations'); fig.tight_layout(); fig.savefig(OUT/'figures'/f'{key}-04-correlations.png'); plt.show(); plt.close(fig)
            fig,ax=plt.subplots(); x=np.sort(numeric[col].dropna()); ax.plot(x,np.arange(1,len(x)+1)/max(len(x),1)); ax.set_title(key+' sampled empirical CDF: '+col); fig.savefig(OUT/'figures'/f'{key}-05-cdf.png'); plt.show(); plt.close(fig)
        print('PROFILE COMPLETE',key,count,'sample rows',len(sample),flush=True)
'''

def code(source):
    source=textwrap.dedent(source).strip()
    ast.parse(source)
    return nbf.v4.new_code_cell(source)

intro='''# Engineering EDA — Kaggle CPU
Project: DDoS_Prevention_and_Mitigation. Source snapshot is printed at runtime.
Dependencies: Kaggle Python with pyspark, pandas, numpy, pyarrow, requests, matplotlib, nbformat.
Attach seyhed/nf-ton-iot-v3 and seyhed/nf-bot-iot-v3; enable internet for the official LAN release.
Prithvi: ToN; Roydon: BoT; Satya: LAN. Outputs are version-specific run artifacts.
This initial EDA increment does not finalize preprocessing or splits. Sample plots are descriptive.
Raw NF timestamps, IPs, ports, LAN topology and labels are audit metadata, not approved predictors.
DDoS is positive; other attacks are non-DDoS, not benign. NetFlow and LAN OpenFlow observations
need semantic verification before crossover. Full-dataset quality summaries cannot establish model generalization.
'''
nb=nbf.v4.new_notebook(cells=[nbf.v4.new_markdown_cell(intro),code("STAGE='engineering-eda'\nSOURCE_SNAPSHOT="+repr(REVISION)),code(setup),code(acquire),code(eda),nbf.v4.new_markdown_cell('''## Pending acceptance gates
This is an initial implementation: full numeric nonfinite auditing, event chronology, duplicate-group
analysis and protected split design must be added before preprocessing/model selection. No model
scores or prepared training dataset are produced here. Review sample feature selection before presentation.
Saved output persistence requires a completed Kaggle version and downstream readback verification.
''')])
nb.metadata.kernelspec={'display_name':'Python 3','language':'python','name':'python3'}
nbf.validate(nb)
DEST.mkdir(exist_ok=True)
path=DEST/'02_engineering_eda.ipynb'
nbf.write(nb,path)
print('Created and structurally validated',path)
