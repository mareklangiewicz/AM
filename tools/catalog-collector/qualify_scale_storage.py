"""Measure disposable Git objects for an already-qualified synthetic source tree.

No publication, ref updates or cap overrides. Plumbing creates an unreferenced
commit solely to measure one consistently packed reachable object graph.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time

from publication import git,HISTORY_CAP


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qualified-work',type=Path,required=True)
    parser.add_argument('--work',type=Path,required=True)
    args=parser.parse_args();args.work.mkdir(parents=True,exist_ok=False)
    resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
    evidence=json.loads((args.qualified_work/'receipt.json').read_text())
    if 'error' in evidence or evidence['validation']['documents']!=evidence['documents']:
        raise ValueError('complete validation evidence required')
    repo=args.work/'objects.git';git(args.work,'init','--bare','--quiet','--template=',str(repo))
    index=args.work/'index';git(repo,'read-tree','--empty',index=index)
    started=time.monotonic();updates=bytearray();manifest={};total=0
    for path in sorted((args.qualified_work/'tree').rglob('*')):
        if path.is_symlink():raise ValueError('tree symlink')
        if not path.is_file():continue
        name=path.relative_to(args.qualified_work/'tree').as_posix();raw=path.read_bytes()
        total+=len(raw);manifest[name]=hashlib.sha256(raw).hexdigest()
        blob=git(repo,'hash-object','-w','--stdin',data=raw).strip()
        updates.extend(b'100644 '+blob+b'\t'+name.encode()+b'\0')
        if len(manifest)%1000==0:print(json.dumps(dict(stage='object_write',documents=len(manifest))),flush=True)
    if total!=evidence['tree_bytes'] or len(manifest)!=evidence['documents']:raise ValueError('qualified workload counts changed')
    git(repo,'update-index','-z','--index-info',data=bytes(updates),index=index)
    tree=git(repo,'write-tree',index=index).decode().strip()
    commit=git(repo,'commit-tree',tree,data=b'Synthetic storage measurement; not published\n').decode().strip()
    loose=sum(path.stat().st_size for path in (repo/'objects').rglob('*') if path.is_file())
    object_seconds=time.monotonic()-started;pack_started=time.monotonic()
    git(repo,'pack-objects','--revs','--window=10','--depth=50','--threads=1','--compression=6',
        str(args.work/'reachable'),data=(commit+'\n').encode())
    packs=sum(path.stat().st_size for path in args.work.glob('reachable-*.pack'))
    indexes=sum(path.stat().st_size for path in args.work.glob('reachable-*.idx'))
    refs=git(repo,'for-each-ref','--format=%(refname)').decode().strip()
    if refs:raise AssertionError('measurement unexpectedly created a ref')
    result=dict(synthetic=True,source_revision=evidence['source_revision'],
        qualified_receipt_sha256=hashlib.sha256((args.qualified_work/'receipt.json').read_bytes()).hexdigest(),
        logical_yaml_bytes=total,documents=len(manifest),loose_object_bytes=loose,
        packed_reachable_bytes=packs,pack_index_bytes=indexes,history_cap=HISTORY_CAP,
        loose_unused_fraction=1-loose/HISTORY_CAP,object_write_seconds=object_seconds,
        packing_seconds=time.monotonic()-pack_started,unreferenced_commit=commit,refs_created=False,
        packing='pack-objects --revs --window=10 --depth=50 --threads=1 --compression=6',
        limits='One synthetic seed, no existing history, no updates. Repeated saved shapes share content and improve deltas; not 5000 real independent sources or annual history.',
        peak_self_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        peak_largest_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
        document_sha256=manifest)
    (args.work/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:value for key,value in result.items() if key!='document_sha256'},indent=2))


if __name__=='__main__':main()
