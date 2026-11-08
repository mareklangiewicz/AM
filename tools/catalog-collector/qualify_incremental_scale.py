"""Fresh-process full-parent validation and one synthetic 500-source refresh.

Only the supplied disposable qualification repository is modified. Preserves the
old pin, unchanged blobs and observations; no upstream transport or enrollment.
"""
import argparse
from datetime import datetime,timedelta,timezone
import json
import hashlib
from pathlib import Path
import resource
import time

import contracts as c
import incremental as inc
from publication import git,publish_tree,REF


def pack(repo):
    started=time.monotonic()
    git(repo,'-c','pack.threads=1','-c','pack.compression=6','repack','-ad','--window=10','--depth=50')
    return dict(bytes=sum(path.stat().st_size for path in (repo/'objects/pack').glob('*.pack')),
                seconds=time.monotonic()-started)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',type=Path,required=True)
    parser.add_argument('--parent',type=c.pin,required=True)
    parser.add_argument('--batch-size',type=int,default=500)
    parser.add_argument('--run-id',type=int,default=2)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('output must not exist')
    if not 1<=args.batch_size<=5000 or args.run_id<1:raise ValueError('batch size/run id')
    if git(args.repo,'remote').strip():raise ValueError('disposable local repository only')
    if git(args.repo,'rev-parse',REF).decode().strip()!=args.parent:raise ValueError('expected qualification parent')
    resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
    result=dict(synthetic=True,live_acquisition=False,batch_size=args.batch_size,parent=args.parent,
        source_head=git(c.ROOT,'rev-parse','HEAD').decode().strip(),
        implementation_files_sha256={name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in ('publication.py','incremental.py','contracts.py','wire_validation.py','yaml_publication.py')},
        packing='git repack -ad --window=10 --depth=50; threads=1; compression=6',
        rss_scope='separate Python process high-water and largest child, not simultaneous aggregate')
    started=time.monotonic()
    try:
        result['packed_before']=pack(args.repo)
        original=inc.decode;count=0
        def progress(*values):
            nonlocal count
            value=original(*values);count+=1
            if count%500==0:print(json.dumps(dict(stage='full_parent_fallback',documents=count)),flush=True)
            return value
        inc.decode=progress
        try:snapshot=inc.Snapshot(args.repo,args.parent)
        finally:inc.decode=original
        result['parent_validation']=snapshot.validation
        descriptor=c.decode(snapshot['catalog.yaml']);descriptor['producer']=dict(id=args.run_id,attempt=1)
        beginning=time.monotonic()
        noop=inc.Candidate(snapshot,{'catalog.yaml':c.encode(descriptor)})
        result['metadata_only_candidate']=dict(seconds=time.monotonic()-beginning,**noop.validation)
        changed={};selected=sorted(path for path in snapshot if path.startswith('repositories/'))[:args.batch_size]
        if len(selected)!=args.batch_size:raise ValueError('insufficient source population')
        beginning=time.monotonic()
        for index,path in enumerate(selected):
            old=c.decode(snapshot[path])
            at=(datetime.fromisoformat(old['collected_at'].replace('Z','+00:00'))+timedelta(days=2)).strftime('%Y-%m-%dT%H:%M:%SZ')
            releases={rid:{key:value for key,value in c.expand_release(record,old['observed_at']).items() if key!='observed_at'}
                      for rid,record in old['releases'].items()}
            # Reobserve exactly these retained records; no fabricated network call.
            updated=c.source(old,dict(received_at=at,releases=releases,history_complete=old['scope']['history_complete']),
                rid=old['repository_id'],repository=old['repository'],revision=descriptor['inputs']['schemas'])
            changed[path]=c.encode(updated)
            if (index+1)%100==0:print(json.dumps(dict(stage='synthetic_timestamp_refresh',sources=index+1)),flush=True)
        result['projection_seconds']=time.monotonic()-beginning
        changed['catalog.yaml']=c.encode(descriptor)
        beginning=time.monotonic();candidate=inc.Candidate(snapshot,changed)
        result['incremental_validation_seconds']=time.monotonic()-beginning
        result['candidate']=candidate.validation
        untouched=set(snapshot)-set(changed)
        if any(candidate.entries[path]!=snapshot.entries[path] for path in untouched):raise AssertionError('unchanged blob identity')
        # Measure real snapshot reads during publication; unchanged bodies must
        # remain unmaterialized, independently of timing/host-load variation.
        reads=[];read=inc.Snapshot.__getitem__
        def count_read(instance,path):reads.append(path);return read(instance,path)
        inc.Snapshot.__getitem__=count_read
        metrics={};beginning=time.monotonic()
        try:commit=publish_tree(args.repo,candidate,args.parent,metrics=metrics)
        finally:inc.Snapshot.__getitem__=read
        result.update(commit=commit,publication_seconds=time.monotonic()-beginning,
                      publication_metrics=metrics,publication_parent_blob_reads=len(reads))
        if reads:raise AssertionError('publication read unchanged source bodies')
        if git(args.repo,'rev-parse',commit+'^').decode().strip()!=args.parent:raise AssertionError('direct child')
        old_source=selected[0]
        if git(args.repo,'show',args.parent+':'+old_source)!=snapshot[old_source]:raise AssertionError('old pin changed')
        result['packed_after']=pack(args.repo)
        result['packed_added_bytes']=result['packed_after']['bytes']-result['packed_before']['bytes']
        result.update(unchanged_documents=len(untouched),old_pin_preserved=True,
            refresh_note='Timestamp-only synthetic successful refresh of all retained records in each selected source; no recipe/fact changes or live quota claim.')
    except Exception as error:
        result.update(error_type=type(error).__name__,error=str(error));raise
    finally:
        result.update(seconds=time.monotonic()-started,
            peak_self_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            peak_largest_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
