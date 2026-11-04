#!/usr/bin/env python3
"""Synthetic retained growth shaped by the real Sunshine page; no HTTP/cap change."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'catalog-collector'))
import copy
from datetime import datetime,timedelta,timezone
import hashlib
import json
import resource
import subprocess
import time

from sunshine_fixture import saved
from bounded import normalize
from retention import refresh
from writer import document
from yaml_adapter import schema_url
from yaml_publication import decode_document
from yaml_staging import policy
from storage import canonical

ROOT=Path(__file__).resolve().parents[2]


def measure(revision):
    started=time.monotonic()
    source,body,report=saved()
    raw=json.loads(body)
    limits=policy((ROOT/'tools/catalog-collector/yaml-policy.json').read_bytes())
    previous=dict(format=2,schema=schema_url(revision),repository_id=source['repository_id'],repository='LizardByte/Sunshine')
    release_step=max(r['id'] for r in raw)+1
    asset_step=max(a['id'] for r in raw for a in r['assets'])+1
    rows=[]
    for cycle in range(1,31):
        batch=copy.deepcopy(raw)
        for release in batch:
            release['id']+=cycle*release_step
            for asset in release['assets']:asset['id']+=cycle*asset_step
        at=(datetime(2026,11,4,tzinfo=timezone.utc)+timedelta(days=cycle)).strftime('%Y-%m-%dT%H:%M:%SZ')
        response=dict(received_at=at,releases=normalize(batch,30),has_next=True,bytes=len(canonical(batch)),seconds=0)
        result=refresh(previous,[response],attempted_at=at,max_catalog_bytes=limits['max_file_bytes'],page_size=30)
        if result['collection']['status']=='failed':
            if result['collection']['reason']!='collection_limit':raise ValueError('unexpected growth refusal')
            if any(result.get(key)!=previous.get(key) for key in ('schema','releases','observed_at','last_success')):
                raise ValueError('retained facts changed on capacity refusal')
            encoded=document(result).encode()
            decode_document(encoded,limits['max_file_bytes'])
            return dict(source_revision=revision,live=False,synthetic=True,
                body_sha256=report['body_sha256'],cycles=rows,refused_cycle=cycle,
                refusal=result['collection']['reason'],preserved_releases=len(previous['releases']),
                preserved_assets=sum(len(r['assets']) for r in previous['releases'].values()),
                preserved_yaml_bytes=len(document(previous).encode()),failed_metadata_yaml_bytes=len(encoded),
                max_file_bytes=limits['max_file_bytes'],local_wall_seconds=round(time.monotonic()-started,3),
                parent_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                limitation='IDs/receipt times are synthetic, asset density/strings derive from saved page; no upstream history, transport timing or operating-cap acceptance.')
        previous=result
        rows.append(dict(cycle=cycle,releases=len(result['releases']),
                         assets=sum(len(r['assets']) for r in result['releases'].values()),yaml_bytes=len(document(result).encode())))
    raise ValueError('growth refusal not reached within bounded experiment')


if __name__=='__main__':
    resource.setrlimit(resource.RLIMIT_AS,(768*1024*1024,768*1024*1024))
    resource.setrlimit(resource.RLIMIT_CPU,(180,180))
    revision=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD']).decode().strip()
    print(json.dumps(measure(revision),indent=2,sort_keys=True))
