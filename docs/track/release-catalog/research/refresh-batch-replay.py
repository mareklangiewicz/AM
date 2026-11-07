"""Offline batch-sizing experiment; synthetic identities never enroll sources.

Replay measured release bodies through the maintained collector, publisher and
reader. Budget overrides apply only within this process. No network requests.
"""
import argparse, contextlib, hashlib, json, resource, subprocess, sys, time
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[4]; sys.path.insert(0,str(ROOT/'tools/catalog-collector'))
import host_catalog as collector
from yaml_publication import load_local, SAFE_LOADER
from publication import git, publish_tree
import yaml
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('mode',choices=['current-budgets','candidate'])
parser.add_argument('--evidence',required=True,type=Path,help='Directory containing batch-1 through batch-5')
parser.add_argument('--output',required=True,type=Path,help='New experiment directory')
parser.add_argument('--count',type=int,default=500)
parser.add_argument('--transfer-mib',type=int,default=512)
args=parser.parse_args()
mode=args.mode
count=args.count
assert count>0 and args.transfer_mib>0
resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))
OUT=args.output;OUT.mkdir(parents=True,exist_ok=False)
BASE=args.evidence
rows,sources=collector.configuration()
files={}
for batch in range(1,6):
    for path in (BASE/f'batch-{batch}').glob('*-releases.json'):
        files[path.name.split('-')[0]]=path
assert set(files)==set(sources)
ordered=sorted(files,key=int)
fixtures=[]
for number in range(count):
    original=ordered[number%len(ordered)]
    fixtures.append(dict(app='fixture-'+str(number),repository_id=number+1,
        repository='fixture/source-'+str(number),original_repository_id=int(original),path=files[original]))
config_rows=[{k:r[k] for k in ('app','repository_id','repository')} for r in fixtures]
config_sources={str(r['repository_id']):r['repository'] for r in fixtures}
case=OUT
repo=case/'catalog.git'
git(repo.parent,'init','--bare','--quiet',str(repo))
calls=[]
def response(rid,evidence,allowance, *, rate=None):
    row=fixtures[int(rid)-1]
    with row['path'].open('rb') as stream: body=stream.read(allowance+1)
    calls.append(dict(repository_id=int(rid),original_repository_id=row['original_repository_id'],bytes=len(body),sha256=hashlib.sha256(body).hexdigest()))
    return body, '2026-11-07T00:00:00Z'
revision=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
caps=dict(REQUEST_CAP=count)
if mode!='current-budgets':caps.update(TOTAL_CAP=args.transfer_mib*1024**2,ACQUISITION_SECONDS=900)
start=time.monotonic();result={}
try:
    with patch.multiple(collector,**caps),patch.object(collector,'configuration',return_value=(config_rows,config_sources)),patch.object(collector,'_response',side_effect=response), (case/'command.log').open('w') as log,contextlib.redirect_stdout(log):
        tree,report=collector.collect(revision,{},evidence=BASE,batch_size=count)
        collection_seconds=time.monotonic()-start
        first=publish_tree(repo,tree,None)
        publish_seconds=time.monotonic()-start-collection_seconds
        prior_start=time.monotonic()
        apps,prior=load_local(repo,first,max_file_bytes=collector.FILE_CAP)
        read_seconds=time.monotonic()-prior_start
        if mode!='current-budgets':
            calls.clear()
            second_start=time.monotonic()
            tree2,report2=collector.collect(revision,prior,evidence=BASE,batch_size=count)
            second=publish_tree(repo,tree2,first)
            assert len(report2)==count and all(r['status']=='ok' for r in report2)
            assert git(repo,'rev-parse',second+'^').decode().strip()==first
            # A later attempt legitimately changes collection attempt metadata.
            assert yaml.load(tree2['apps.yaml'],Loader=SAFE_LOADER)['apps']==apps
            for rid,old in prior.items():
                new=yaml.load(tree2['repositories/'+rid+'.yaml'],Loader=SAFE_LOADER)
                assert old['releases']==new['releases'] and old.get('observed_at')==new.get('observed_at')
            result.update(retained_refresh_seconds=time.monotonic()-second_start,retained_pin=second,retained_release_ids_and_observations_preserved=True)
        result.update(attempted=len(report),successful=sum(r['status']=='ok' for r in report),response_bytes=sum(r['bytes'] for r in calls),collection_seconds=collection_seconds,publication_seconds=publish_seconds,prior_read_seconds=read_seconds,pin=first,yaml_bytes=sum(map(len,tree.values())),largest_yaml_bytes=max(map(len,tree.values())),published_apps=len(apps),published_sources=len(prior),local_git_bytes=sum(p.stat().st_size for p in (repo/'objects').rglob('*') if p.is_file()))
except Exception as error:
    result.update(error=type(error).__name__+': '+str(error),attempted=len(calls),response_bytes=sum(r['bytes'] for r in calls))
result.update(source_revision=revision,source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'tools/catalog-collector/host_catalog.py',ROOT/'tools/catalog-collector/yaml_publication.py',ROOT/'tools/catalog-collector/publication.py']},corpus=[dict(repository_id=int(rid),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for rid,p in sorted(files.items(),key=lambda row:int(row[0]))],mode=mode,seconds=time.monotonic()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,address_space_bytes=1024**3,request_cap=count,total_response_cap=caps.get('TOTAL_CAP',collector.TOTAL_CAP),acquisition_seconds=caps.get('ACQUISITION_SECONDS',collector.ACQUISITION_SECONDS),fixture_sources=count,distinct_real_response_sources=len(files),synthetic_identity_note='Synthetic distinct identities cycle saved real release responses; no new upstream identity or live API capacity claim.',fixture_response_bytes=sum(r['path'].stat().st_size for r in fixtures),fixtures=[{k:v for k,v in r.items() if k!='path'} for r in fixtures])
(case/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('fixtures','corpus','source_hashes')}),flush=True)
