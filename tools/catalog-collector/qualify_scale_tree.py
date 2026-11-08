"""Complete synthetic source-tree qualification from hash-checked saved shapes.

Offline only. Never changes enrollment or the saved input. All writes go to a new
disposable work directory. A refusal is evidence, not permission to raise a cap.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import platform
import re
import resource
import time

import contracts as c
import incremental as inc
from publication import git,publish_tree,REF,HISTORY_CAP


def digest(raw): return hashlib.sha256(raw).hexdigest()


def boundary_source(template,revision,rid):
    """One near-limit document; padding titles is explicitly synthetic stress."""
    obj=c.decode(template)
    record=next(iter(obj['releases'].values()))
    obj.update(c.header('repository',revision),repository_id=rid,repository='synthetic/scale-boundary')
    obj['releases']={str(index):dict(copy.deepcopy(record),tag='synthetic-'+str(index),
                                    prerelease=True,title='') for index in range(1,34)}
    # The stable record is older than all 32 prereleases at the same timestamp.
    obj['releases']['1']['prerelease']=False
    remaining=c.FILE_CAP-128-len(c.encode(obj))
    for record in obj['releases'].values():
        amount=min(64000,remaining)
        record['title']='x'*amount;remaining-=amount
    if remaining: raise ValueError('boundary title capacity')
    raw=c.encode(obj)
    if len(raw)!=c.FILE_CAP-128: raise AssertionError('boundary byte calculation')
    c.decode(raw)
    return raw


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--saved-data',type=Path,required=True)
    parser.add_argument('--work',type=Path,required=True,help='New directory only')
    parser.add_argument('--count',type=int,default=5000)
    args=parser.parse_args()
    if not 1<=args.count<=10000:parser.error('--count must be 1..10000')
    # Cap this Python process and inherited children; this is not a cgroup/RSS sum.
    resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
    args.work.mkdir(parents=True,exist_ok=False)
    started=time.monotonic()
    revision=git(c.ROOT,'rev-parse','HEAD').decode().strip()
    result=dict(synthetic=True,live_acquisition=False,app_count=args.count,source_count=args.count,
                source_revision=revision,python=platform.python_version(),
                harness_sha256=digest(Path(__file__).read_bytes()),
                address_space_cap_bytes=2*1024**3,
                rss_scope='Python process and largest child high-waters, not simultaneous aggregate',
                received_upstream_bytes=0,charged_upstream_bytes=0,
                seed_sha256={},stages={})
    try:
        metadata=json.loads((args.saved_data/'review.json').read_text())
        result.update(saved_pin=metadata['pin'],saved_baseline=metadata['baseline'])
        templates=[];shape_counts=[]
        for name,expected in sorted(metadata['document_sha256'].items()):
            if not name.startswith('repositories/'):continue
            raw=(args.saved_data/metadata['pin']/name).read_bytes()
            if digest(raw)!=expected: raise ValueError('saved source digest mismatch')
            obj=c.decode(raw)
            shape_counts.append(dict(bytes=len(raw),releases=len(obj['releases']),
                                     assets=sum(len(row['assets']) for row in obj['releases'].values())))
            templates.append(raw);result['seed_sha256'][name]=expected
        if not templates:raise ValueError('no source templates')
        result['saved_shapes']=dict(count=len(templates),
            ranges={key:dict(min=min(row[key] for row in shape_counts),max=max(row[key] for row in shape_counts),
                            total=sum(row[key] for row in shape_counts)) for key in ('bytes','releases','assets')})
        tree={};apps={};bindings={}
        for index in range(args.count):
            name=f'scale-{index:05d}';rid=1000000000000+index
            raw=templates[index%len(templates)]
            raw=re.sub(rb'^schema: .*$',('schema: '+json.dumps(c.header('repository',revision)['schema'])).encode(),raw,count=1,flags=re.M)
            raw=re.sub(rb'^repository_id: .*$',f'repository_id: {rid}'.encode(),raw,count=1,flags=re.M)
            raw=re.sub(rb'^repository: .*$',('repository: '+json.dumps('synthetic/'+name)).encode(),raw,count=1,flags=re.M)
            if index==args.count-1:
                raw=boundary_source(next(raw for raw in templates if b'    tag:' in raw),revision,rid)
            path='repositories/'+name+'.yaml';tree[path]=raw;apps[name]=path
            bindings[name]={arch:dict(repository_id=rid,availability='unknown',classification='unknown')
                            for arch in ('x86_64','aarch64','i686','armv7l')}
        inputs={key:revision for key in ('source','policy','recipes','rules','schemas')}
        tree['catalog.yaml']=c.encode(dict(c.header('catalog',revision),inputs=inputs,
            producer=dict(id=1,attempt=1),retention='32-plus-stable-exact-tag-v1'))
        tree['apps.yaml']=c.encode(dict(c.header('apps',revision),apps=apps))
        tree.update(c.partition_provenance(apps,bindings,revision))
        result['stages']['prepare_seconds']=time.monotonic()-started
        result.update(tree_bytes=sum(map(len,tree.values())),documents=len(tree),
            largest_document_bytes=max(map(len,tree.values())),configured_tree_cap=c.TREE_CAP,
            configured_document_cap=c.FILE_CAP,configured_history_cap=HISTORY_CAP,
            boundary_document='repositories/'+f'scale-{args.count-1:05d}'+'.yaml',
            boundary_note='32 prereleases plus older stable, with synthetic title padding to document cap minus 128 bytes')
        print(json.dumps(dict(stage='prepared',tree_bytes=result['tree_bytes'],documents=len(tree))),flush=True)
        # Preserve exact generated bytes so later affected checks can reuse them.
        folder=args.work/'tree';folder.mkdir()
        for path,raw in tree.items():
            target=folder/path;target.parent.mkdir(exist_ok=True);target.write_bytes(raw)
        original=inc.decode;decoded=0
        def progress(*values):
            nonlocal decoded
            value=original(*values);decoded+=1
            if decoded%500==0: print(json.dumps(dict(stage='full_validation',documents=decoded)),flush=True)
            return value
        inc.decode=progress
        check_started=time.monotonic()
        try: candidate=inc.Candidate(None,tree)
        finally:inc.decode=original
        result['stages']['full_validation_seconds']=time.monotonic()-check_started
        result['validation']=candidate.validation
        repo=args.work/'catalog.git';git(args.work,'init','--bare','--quiet','--template=',str(repo))
        metrics={};publish_started=time.monotonic()
        try:
            result['commit']=publish_tree(repo,candidate,None,metrics=metrics)
            result['publication']='accepted'
        except ValueError as error:
            result.update(publication='refused',reason=str(error))
        result['stages']['publication_seconds']=time.monotonic()-publish_started
        result['publication_metrics']=metrics
        result['final_ref']=git(repo,'for-each-ref','--format=%(objectname)',REF).decode().strip() or None
    except Exception as error:
        result.update(error_type=type(error).__name__,error=str(error))
        raise
    finally:
        result.update(seconds=time.monotonic()-started,
            peak_self_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            peak_largest_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)
        (args.work/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({key:value for key,value in result.items() if key!='seed_sha256'}),flush=True)


if __name__=='__main__':main()
