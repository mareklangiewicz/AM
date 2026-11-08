"""Offline saved retained seed + three labelled updates, in an isolated Git repo.

No HTTP, source enrollment, ref push or mutation of the supplied evidence repo.
Each phase is a separate process so reported RSS is a phase process high-water.
"""
import argparse
import copy
from datetime import datetime,timedelta,timezone
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import sys
import tempfile
import time

import contracts as c
from incremental import Snapshot,Candidate,decode as decode_fact,rules
from publication import git,publish_tree,REF
from retention import observation
from retention_v3 import merge


def seed_source(old,revision):
    records={};tags={}
    for rid,record in old['releases'].items():
        at=observation(record,old['observed_at']);tag=record['tag']
        if tag in tags:
            previous=tags[tag]
            old_at=observation(records[previous],old['observed_at'])
            if at==old_at: raise ValueError('same_tag_conflict')
            if at<old_at:continue
            records.pop(previous)
        tags[tag]=rid;records[rid]=dict(copy.deepcopy(record),observed_at=at)
    at=old['last_success']['completed_at']
    retained=merge(dict(releases=records,observed_at=old['observed_at']),{},completed_at=at)
    return c.decode(c.encode(dict(c.header('repository',revision),repository_id=old['repository_id'],repository=old['repository'],
        collected_at=at,scope=dict(page_size=old['last_success']['page_size'],pages_fetched=old['last_success']['pages_fetched'],history_complete=old['last_success']['history_complete']),
        observed_at=at,releases={rid:c.compact_release(record) for rid,record in retained.items()})))


def phase(args):
    started=time.monotonic();repo=args.repo;revision=args.source
    before_objects=sum(p.stat().st_size for p in (repo/'objects').rglob('*') if p.is_file())
    parent=git(repo,'rev-parse',REF).decode().strip()
    names=json.loads((c.ROOT/'tools/catalog-collector/source-names.json').read_text())['active']
    changed={};touched=[];source_hashes={};refused=[]
    if args.phase=='seed':
        old=Snapshot(repo,args.baseline,'format-2')
        apps=old.metadata['apps.yaml']['apps']
        for path,meta in old.metadata.items():
            if not path.startswith('repositories/'):continue
            raw=old[path];source_hashes[path]=hashlib.sha256(raw).hexdigest()
            try:
                obj=seed_source(decode_fact(path,raw,'format-2')[0],revision)
            except ValueError as error:
                if str(error)!='same_tag_conflict':raise
                refused.append(dict(path=path,repository_id=meta['repository_id'],reason='same_tag_conflict'))
                continue
            changed['repositories/'+names[str(obj['repository_id'])]+'.yaml']=c.encode(obj)
        app_paths={app:'repositories/'+names[str(rid)]+'.yaml' for app,rid in apps.items() if 'repositories/'+names[str(rid)]+'.yaml' in changed}
        changed['apps.yaml']=c.encode(dict(c.header('apps',revision),apps=app_paths))
        changed['provenance.yaml']=c.encode(dict(c.header('provenance',revision),apps={app:{arch:dict(repository_id=apps[app],availability='unknown',classification='unknown') for arch in ('x86_64','aarch64','i686','armv7l')} for app in app_paths}))
        snapshot=None;baseline_validation=old.validation
    else:
        snapshot=Snapshot(repo,parent)
        baseline_validation=snapshot.validation
        paths=sorted(path for path in snapshot if path.startswith('repositories/'))
        if args.phase=='replay':
            # Exact saved retained observations are the input; do not turn them
            # into a fabricated new one-page HTTP receipt.
            changed={path:snapshot[path] for path in paths}
        else:
            selected=paths[:3] if args.phase=='subset' else paths
            for index,path in enumerate(selected):
                previous=c.decode(snapshot[path])
                if not previous['releases']: continue
                records={rid:c.expand_release(value,previous['observed_at']) for rid,value in previous['releases'].items()}
                first=min(records,key=int);record=copy.deepcopy(records[first]);record.pop('observed_at',None)
                receipt=(datetime.fromisoformat(previous['collected_at'].replace('Z','+00:00'))+timedelta(days=2)).strftime('%Y-%m-%dT%H:%M:%SZ')
                if args.phase=='subset':
                    if index==0:
                        rid=str(max(map(int,records))+1000000000);record['tag']+='-synthetic-new'
                        record['published_at']=receipt
                    elif index==1:
                        rid=first;record['title']=record.get('title','')+' synthetic same-ID edit'
                    else:
                        rid=str(max(map(int,records))+1000000000) # exact rolling-tag replacement
                    fetched={rid:record}
                else:
                    fetched={rid:{k:v for k,v in value.items() if k!='observed_at'} for rid,value in records.items()}
                    fetched[first]['title']=fetched[first].get('title','')+' synthetic wide edit'
                    assets=fetched[first]['assets']
                    if assets:assets[min(assets,key=int)]['name']+='-synthetic'
                updated=c.source(previous,dict(received_at=receipt,releases=fetched,history_complete=False),
                                 rid=previous['repository_id'],repository=previous['repository'],revision=revision)
                changed[path]=c.encode(updated);touched.append(path)
    inputs={key:revision for key in ('source','policy','recipes','rules','schemas')}
    number={'seed':1,'replay':2,'subset':3,'full':4}[args.phase]
    changed['catalog.yaml']=c.encode(dict(c.header('catalog',revision),inputs=inputs,producer=dict(id=number,attempt=1),retention='32-plus-stable-exact-tag-v1'))
    candidate=Candidate(snapshot,changed)
    # Exact unchanged source blobs are a checked invariant, not inferred from size.
    if snapshot:
        for path,entry in snapshot.entries.items():
            if path.startswith('repositories/') and path not in touched and candidate.entries[path]!=entry:
                raise AssertionError('untouched source changed')
        if args.phase=='replay' and any(candidate.entries[p]!=snapshot.entries[p] for p in snapshot if p.startswith('repositories/')):
            raise AssertionError('saved replay changed source blobs')
    metrics={};commit=publish_tree(repo,candidate,parent,metrics=metrics)
    # One consistently configured reachable pack after each phase; only this
    # isolated repository is repacked. Preserved evidence/history stays untouched.
    git(repo,'-c','pack.threads=1','-c','pack.compression=6','repack','-ad','--window=10','--depth=50')
    packed=sum(path.stat().st_size for path in (repo/'objects/pack').glob('*.pack'))
    result=dict(phase=args.phase,source=revision,rules=rules(),baseline=args.baseline,parent=parent,commit=commit,
                provenance='saved retained observations' if args.phase in ('seed','replay') else 'deterministic synthetic local changes; not upstream observations',
                seconds=time.monotonic()-started,peak_self_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                peak_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
                rss_scope='separate phase Python process high-water; child high-water is the largest child, not simultaneous aggregate',
                documents=len(candidate),sources=sum(p.startswith('repositories/') for p in candidate),
                largest_document_bytes=max(size for _,size in candidate.entries.values()),tree_bytes=candidate.validation['tree_bytes'],
                changed_blobs=candidate.validation['changed_documents'],reused_blobs=candidate.validation['reused_documents'],
                touched=touched,parent_validation=baseline_validation,publication_metrics=metrics,
                object_bytes_before=before_objects,packed_reachable_bytes=packed,
                packing='git repack -ad --window=10 --depth=50; pack.threads=1; pack.compression=6',
                seed_document_sha256=source_hashes,refused_sources=refused)
    args.receipt.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('seed_document_sha256','touched','parent_validation','publication_metrics')}),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-repo',type=Path)
    parser.add_argument('--baseline',type=c.pin,default='cbda9fb78ce4a6f29bdabd63d57f3c0085e8744f')
    parser.add_argument('--output',type=Path)
    parser.add_argument('--source',type=c.pin)
    parser.add_argument('--phase',choices=('seed','replay','subset','full'))
    parser.add_argument('--repo',type=Path)
    parser.add_argument('--receipt',type=Path)
    args=parser.parse_args()
    if args.phase:return phase(args)
    if not args.evidence_repo or not args.output:parser.error('--evidence-repo and --output are required')
    revision=args.source or git(c.ROOT,'rev-parse','HEAD').decode().strip()
    with tempfile.TemporaryDirectory(prefix='am-saved-rehearsal-') as temp:
        root=Path(temp);repo=root/'catalog.git';git(root,'init','--bare','--quiet','--template=',str(repo))
        git(repo,'fetch','--no-tags',str(args.evidence_repo),args.baseline)
        git(repo,'update-ref',REF,args.baseline)
        receipts=[]
        for name in ('seed','replay','subset','full'):
            receipt=root/(name+'.json')
            subprocess.run([sys.executable,'-B',str(Path(__file__).resolve()),'--phase',name,'--repo',str(repo),
                            '--baseline',args.baseline,'--source',revision,'--receipt',str(receipt)],check=True)
            receipts.append(json.loads(receipt.read_text()))
        args.output.write_text(json.dumps(dict(real_source_count=500,synthetic_scale=False,live_acquisition=False,
            preserved_evidence_repo=str(args.evidence_repo),baseline=args.baseline,source=revision,phases=receipts),indent=2)+'\n')


if __name__=='__main__':main()
