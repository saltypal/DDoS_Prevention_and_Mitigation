"""Versioned Kaggle staging, bounded submission and filtered evidence retrieval.

No credentials are read by this script; authenticated Kaggle CLI owns authentication.
"""
import argparse
import json
from pathlib import Path
import subprocess
import time
import os
import re
import importlib
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import nbformat
from sdn_ddos.runtime.run import write_json, sha256

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent.parent


def command(arguments, log, timeout=900):
    environment=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8')
    result=subprocess.run(arguments,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout,env=environment)
    log.parent.mkdir(parents=True,exist_ok=True)
    log.write_text(result.stdout+'\nSTDERR\n'+result.stderr,encoding='utf-8')
    print(result.stdout,result.stderr,flush=True)
    if result.returncode:
        raise RuntimeError(f'CLI failed with exit {result.returncode}; see {log}')
    return result.stdout


def submit(args):
    run=ROOT/'runs'/args.run_id
    stage=run/'source_snapshot'
    stage.mkdir(parents=True,exist_ok=False)
    notebook=nbformat.read(ROOT/'notebooks'/args.notebook,as_version=4)
    for cell in notebook.cells:
        if cell.cell_type=='code' and 'REVISION = None' in cell.source:
            cell.source=cell.source.replace('REVISION = None',f'REVISION = {args.commit!r}')
        if args.overrides and cell.cell_type=='code' and 'config = json.loads' in cell.source:
            overrides=json.loads(Path(args.overrides).read_text())
            cell.source+='\nconfig.update('+repr(overrides)+')\nprint("RESOLVED OVERRIDES",config,flush=True)\n'
    nbformat.validate(notebook)
    nbformat.write(notebook,stage/args.notebook)
    metadata={'id':'satyapaladugu/'+args.slug,'title':args.title,'code_file':args.notebook,
              'language':'python','kernel_type':'notebook','is_private':True,'enable_gpu':False,'enable_internet':True,
              'dataset_sources':args.dataset,'kernel_sources':args.upstream,'competition_sources':[]}
    write_json(stage/'kernel-metadata.json',metadata)
    provenance={'run_id':args.run_id,'notebook_identity':metadata['id'],'source_commit':args.commit,
                'utc':datetime.now(timezone.utc).isoformat(),'source_sha256':sha256(stage/args.notebook),
                'inputs':args.dataset,'upstream':args.upstream,'status':'staged',
                'expected_remote_root':'/kaggle/working/experiments/public_dataset_la/runs/<timestamped-run-id>/',
                'expected_local_evidence':str(run/'retrieved')}
    if args.overrides:
        provenance['config_overrides']=json.loads(Path(args.overrides).read_text())
    write_json(run/'submission.json',provenance)
    with (PROJECT/'KAGGLE_RUNS.md').open('a',encoding='utf-8') as mapping:
        mapping.write('\n\n## Staged '+args.run_id+'\n\n'+json.dumps(provenance,indent=2)+'\n')
    owned=command(['kaggle','kernels','list','--mine','--search',args.slug,'--format','json'],run/'logs'/'owned-before.json')
    # Never push a revision over a healthy active run.
    if args.slug in owned:
        status=command(['kaggle','kernels','status',metadata['id']],run/'logs'/'status-before.log')
        if 'RUNNING' in status or 'QUEUED' in status:
            raise RuntimeError('Existing notebook is active; do not interrupt it')
    output=command(['kaggle','kernels','push','-p',str(stage)],run/'logs'/'submission.log')
    provenance['status']='submission_accepted'
    provenance['response']=output.strip()
    write_json(run/'submission.json',provenance)
    return provenance


def retrieve(args):
    run=ROOT/'runs'/args.run_id
    pattern = r'.*' if args.smoke else r'.*(\.json|\.log|\.ipynb|\.png|\.csv|resolved-packages\.txt)$'
    # The installed CLI writes native logs with the Windows default code page and
    # ignores parsed output versions. Use the same public SDK with explicit UTF8/version.
    import requests
    api=importlib.import_module('kaggle.api.kaggle_api_extended').KaggleApi()
    api.authenticate()
    request_type=importlib.import_module('kagglesdk.kernels.types.kernels_api_service').ApiListKernelSessionOutputRequest
    components=args.identity.split('/')
    owner,slug=components[:2]
    output=(run/'retrieved').resolve()
    output.mkdir(parents=True,exist_ok=True)
    items=[]; token=None; native_log=''
    with api.build_kaggle_client() as client:
        while True:
            request=request_type()
            request.user_name=owner; request.kernel_slug=slug; request.page_size=200
            if len(components)>2: request.version_label=components[2]
            if token: request.page_token=token
            response=client.kernels.kernels_api_client.list_kernel_session_output(request)
            items.extend((item.file_name,item.url) for item in response.files or [] if re.search(pattern,item.file_name))
            native_log=response.log or native_log
            token=response.next_page_token
            if not token: break
    def download(item):
        name,url=item
        destination=(output/name).resolve()
        if not destination.is_relative_to(output):
            raise ValueError('Unsafe remote output path')
        destination.parent.mkdir(parents=True,exist_ok=True)
        partial=destination.with_name(destination.name+'.partial')
        try:
            with requests.get(url,stream=True,timeout=120) as response:
                if response.status_code!=200:
                    raise RuntimeError(f'Output HTTP {response.status_code}: {name}')
                with partial.open('wb') as handle:
                    for block in response.iter_content(2*1024*1024): handle.write(block)
            partial.replace(destination)
        except requests.RequestException as error:
            raise RuntimeError(f'Output retrieval {type(error).__name__}: {name}') from None
        return name
    print('RETRIEVING',len(items),'filtered outputs; signed URLs are not logged',flush=True)
    with ThreadPoolExecutor(max_workers=6) as pool:
        for count,_ in enumerate(pool.map(download,items),1):
            if count%25==0: print('RETRIEVAL PROGRESS',count,len(items),flush=True)
    (output/(slug+'.log')).write_text(native_log or '',encoding='utf-8')
    if args.expected_commit:
        environments=[json.loads(p.read_text(encoding='utf-8')) for p in output.rglob('environment.json')]
        if not environments or any(e['revision']!=args.expected_commit for e in environments):
            raise RuntimeError('Retrieved source revision does not match the expected pinned commit')
    files=[p for p in (run/'retrieved').rglob('*') if p.is_file()]
    write_json(run/'retrieval_manifest.json',{str(p.relative_to(run/'retrieved')):{'bytes':p.stat().st_size,'sha256':sha256(p)} for p in files})
    print('RETRIEVED',len(files),'files',sum(p.stat().st_size for p in files),'bytes',flush=True)


def monitor(args):
    run=ROOT/'runs'/args.run_id
    run.mkdir(parents=True,exist_ok=True)
    previous={}
    for round_number in range(args.rounds):
        terminal=False
        for identity in args.identity:
            result=subprocess.run(['kaggle','kernels','status',identity],capture_output=True,text=True,timeout=90)
            output=result.stdout.strip()
            if output!=previous.get(identity):
                print(datetime.now(timezone.utc).isoformat(),identity,output,flush=True)
                previous[identity]=output
            terminal=terminal or any(word in output for word in ('COMPLETE','ERROR','CANCEL','FAILED'))
        write_json(run/'monitor-state.json',{'utc':datetime.now(timezone.utc).isoformat(),'round':round_number,'states':previous})
        if terminal: return
        time.sleep(args.interval)
    print('Bounded monitoring interval ended; persisted state is available',flush=True)


def publish_prepared(args):
    source=Path(args.prepared_run).resolve()
    artifact=json.loads((source/'SHA256_MANIFEST.json').read_text())
    total=sum(item['bytes'] for item in artifact.values())
    import shutil
    if total > 2*1024**3 or shutil.disk_usage(source).free < 5*1024**3:
        raise RuntimeError('Local publication exceeds the approved storage envelope')
    directory=ROOT/'runs'/args.run_id/'dataset_payload'
    directory.mkdir(parents=True,exist_ok=False)
    layout={'source_run':source.name,'source_manifest_sha256':sha256(source/'SHA256_MANIFEST.json'),'files':{}}
    for index,(relative,info) in enumerate(artifact.items()):
        path=source/relative
        if not path.exists() or path.stat().st_size!=info['bytes'] or sha256(path)!=info['sha256']:
            raise RuntimeError(f'Cannot publish unverified/incomplete artifact {relative}')
        name=f'asset-{index:05d}'+path.suffix
        os.link(path,directory/name)  # Same-volume read-only payload; no second bulk copy.
        layout['files'][relative]=dict(asset=name,**info)
    write_json(directory/'prepared-layout.json',layout)
    write_json(directory/'dataset-metadata.json',{'id':'satyapaladugu/'+args.slug,'title':args.title,
        'licenses':[{'name':args.license}],
        'description':'Private prepared research data. Original source: '+args.attribution+
        '. Source measurements sanitized with protected split/quarantine metadata; DDoS versus non-DDoS target. '
        'No detector accuracy or new traffic collection claim. Assets preserve Parquet and reconstruct their '
        'directory layout through prepared-layout.json and the versioned sdn_ddos.data.layout module. '
        'Original dataset license/attribution and restrictions apply.'})
    command(['kaggle','datasets','create','-p',str(directory),'--keep-tabular','--quiet'],directory.parent/'logs'/'dataset-create.log',timeout=1800)
    write_json(directory.parent/'publication.json',{'dataset':'satyapaladugu/'+args.slug,'private':True,
             'source_run':source.name,'bytes':total,'layout_sha256':sha256(directory/'prepared-layout.json')})


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    commands=parser.add_subparsers(dest='operation',required=True)
    sub=commands.add_parser('submit')
    for name in ('run-id','notebook','slug','title','commit'):
        sub.add_argument('--'+name,required=True)
    sub.add_argument('--dataset',action='append',default=[])
    sub.add_argument('--upstream',action='append',default=[])
    sub.add_argument('--overrides')
    sub=commands.add_parser('retrieve')
    sub.add_argument('--run-id',required=True)
    sub.add_argument('--identity',required=True)
    sub.add_argument('--smoke',action='store_true')
    sub.add_argument('--expected-commit')
    sub=commands.add_parser('monitor')
    sub.add_argument('--run-id',required=True)
    sub.add_argument('--identity',action='append',required=True)
    sub.add_argument('--rounds',type=int,default=20)
    sub.add_argument('--interval',type=int,default=45)
    sub=commands.add_parser('publish-prepared')
    for name in ('run-id','prepared-run','slug','title','license','attribution'):
        sub.add_argument('--'+name,required=True)
    arguments=parser.parse_args()
    if arguments.operation=='submit': submit(arguments)
    elif arguments.operation=='retrieve': retrieve(arguments)
    elif arguments.operation=='monitor': monitor(arguments)
    else: publish_prepared(arguments)
