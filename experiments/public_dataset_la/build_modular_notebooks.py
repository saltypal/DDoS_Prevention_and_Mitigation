"""Generate thin GitHub-backed Kaggle notebooks; no local scientific processing."""
from pathlib import Path
import ast
import json
import shutil
import nbformat as nbf

ROOT = Path(__file__).resolve().parent
DEST = ROOT / 'notebooks'
URL = 'https://github.com/saltypal/DDoS_Prevention_and_Mitigation.git'
bootstrap = '''import sys, subprocess, shutil, uuid, time
from pathlib import Path
print('START repository bootstrap', flush=True)
started = time.monotonic()
assert Path('/kaggle/working').exists(), 'Execute scientific notebooks on Kaggle'
REPOSITORY = %r
REVISION = None  # None resolves latest main ONCE. Set a recorded SHA to reproduce a run.
checkout = Path('/kaggle/temp') / ('ddos-source-' + uuid.uuid4().hex)
subprocess.run(['git','clone','--depth','1',REPOSITORY,str(checkout)],check=True,timeout=180)
if REVISION:
    subprocess.run(['git','fetch','--depth','1','origin',REVISION],cwd=checkout,check=True,timeout=180)
    subprocess.run(['git','checkout','--detach','FETCH_HEAD'],cwd=checkout,check=True)
SOURCE_COMMIT = subprocess.check_output(['git','rev-parse','HEAD'],cwd=checkout,text=True).strip()
print('PINNED SOURCE',SOURCE_COMMIT,checkout,flush=True)
if not shutil.which('java'):
    subprocess.run(['apt-get','update','-qq'],check=True,timeout=300)
    subprocess.run(['apt-get','install','-y','openjdk-17-jre-headless'],check=True,timeout=600)
subprocess.run(['java','-version'],check=True)
subprocess.run([sys.executable,'-m','pip','install','--disable-pip-version-check','-e',str(checkout)+'[spark,boost,notebooks]'],check=True,timeout=900)
sys.path.insert(0,str(checkout))
import os
os.chdir(checkout)
print('END repository bootstrap',time.monotonic()-started,'seconds',flush=True)
from sdn_ddos.runtime.notebook import install_capture
capture_root=Path('/kaggle/working/experiments/public_dataset_la/cell_capture') / uuid.uuid4().hex
install_capture(capture_root)
''' % URL


def cell(source):
    ast.parse(source)
    return nbf.v4.new_code_cell(source)


def build(filename, title, config, description):
    config_code = f"""import json
from sdn_ddos.cli import execute
print('START configuration', flush=True)
config = json.loads((checkout / 'experiments/public_dataset_la/configs/{config}').read_text())
print(json.dumps(config,indent=2), 'SOURCE', SOURCE_COMMIT, flush=True)
print('END configuration', flush=True)
"""
    if filename == '02_engineering_eda.ipynb':
        config_code += "config['stage']='audit'\nconfig['name']='engineering-eda'\n"
    nb = nbf.v4.new_notebook(cells=[nbf.v4.new_markdown_cell(f'''# {title}
Project: DDoS_Prevention_and_Mitigation. Kaggle CPU; internet enabled. Source: {URL}
{description}
Dependency specification: pyproject.toml in the exact source commit. Bootstrap prints the actual
Python, Java and installed dependencies. No local environment transfers to Kaggle.
Attach seyhed/nf-ton-iot-v3 and seyhed/nf-bot-iot-v3. Official LAN v3.0 is downloaded remotely.
Modules run stage by stage and write incremental logs, Parquet, figures and provenance under
/kaggle/working/experiments/public_dataset_la/. Saved-version persistence/readback must be verified.
Bootstrap output is available in the Kaggle kernel log; subsequent cells are also captured incrementally.
'''), cell(bootstrap), cell(config_code), cell("print('START pipeline', flush=True)\noutput = execute(config)\nprint('END pipeline; artifacts:',output,flush=True)"),
        nbf.v4.new_markdown_cell('''## Interpretation and limitations
Inspect reports and source-specific class counts before accepting artifacts. Prefix smoke outputs
are not training data or performance evidence. Do not claim universal detection or distributed
Spark scaling from a local Kaggle executor. Final tests must remain outside model selection.
''')])
    nb.metadata.kernelspec={'name':'python3','language':'python','display_name':'Python 3'}
    nbf.validate(nb)
    path = DEST / filename
    if path.exists() and filename == '02_engineering_eda.ipynb':
        snapshot = ROOT / 'runs' / 'inline-prototype-20261109'
        snapshot.mkdir(parents=True,exist_ok=True)
        if not (snapshot / filename).exists(): shutil.copy2(path,snapshot / filename)
    nbf.write(nb,path)
    print('Generated',path)


if __name__ == '__main__':
    build('00_modular_preflight.ipynb','Modular source and data preflight','preflight.json','Prefix-only smoke; no classifier training or usable final splits.')
    build('02_engineering_eda.ipynb','Engineering EDA','prepare.json','Descriptive audits with provisional protected partitions; no model fitting.')
    build('03_engineering_preprocessing.ipynb','Source sanitation and protected partitions','prepare.json','Full observational data preparation. Learned preprocessing is fitted within training/model folds.')
    build('04_classifier_benchmark.ipynb','Matched classifier resource pilot','benchmark.json','Attach the completed full-preparation notebook outputs. Fits 12 families on matched bounded cohorts; no final tests.')
