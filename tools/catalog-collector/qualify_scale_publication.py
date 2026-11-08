"""Rerun only changed low-level publication against an exact qualified fixture.

This is an offline affected-check harness, not production validation receipt
import. Production Candidate/Snapshot trust rules are unchanged. Every fixture
byte is rehashed; unchanged full parser validation is deliberately not repeated.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time

from publication import git,publish_tree,REF,HISTORY_CAP


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qualified-work',type=Path,required=True)
    parser.add_argument('--storage-receipt',type=Path,required=True)
    parser.add_argument('--work',type=Path,required=True)
    args=parser.parse_args();args.work.mkdir(parents=True,exist_ok=False)
    resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
    started=time.monotonic();storage=json.loads(args.storage_receipt.read_text())
    receipt=args.qualified_work/'receipt.json'
    if hashlib.sha256(receipt.read_bytes()).hexdigest()!=storage['qualified_receipt_sha256']:
        raise ValueError('qualified fixture receipt changed')
    tree={}
    for path,expected in storage['document_sha256'].items():
        raw=(args.qualified_work/'tree'/path).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('fixture bytes changed')
        tree[path]=raw
    repo=args.work/'published.git';git(args.work,'init','--bare','--quiet','--template=',str(repo))
    metrics={};pin=publish_tree(repo,tree,None,metrics=metrics)
    if git(repo,'rev-parse',REF).decode().strip()!=pin:raise AssertionError('local publication pin')
    result=dict(commit=pin,synthetic=True,remote_publication=False,history_cap=HISTORY_CAP,
        metrics=metrics,seconds=time.monotonic()-started,
        peak_self_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        peak_largest_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
        guard_unused_fraction=1-metrics['history_guard_bytes']/HISTORY_CAP,
        scope='Affected low-level publisher on the exact previously fully validated synthetic tree; every byte rehashed. Full parser validation not repeated; not a fresh-process end-to-end CLI receipt.',
        publication_module_sha256=hashlib.sha256(Path(__file__).with_name('publication.py').read_bytes()).hexdigest())
    (args.work/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
