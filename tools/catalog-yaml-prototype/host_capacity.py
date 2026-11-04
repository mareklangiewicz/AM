#!/usr/bin/env python3
"""Measured saved-list coverage for the host candidate; no HTTP or new caps."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'catalog-collector'))
import hashlib
import json
import os
import re
import resource
import shutil
import subprocess
import tarfile
import tempfile
import time

from attempt_adapter import merge_attempts,utc
from yaml_adapter import schema_url
from yaml_enrollment import enroll,shared_recipes
from yaml_publication import candidate_tree,tree_documents
from yaml_staging import policy

ROOT=Path(__file__).resolve().parents[2]
RESEARCH=ROOT/'docs/track/release-catalog/research'


def saved_lists(wanted):
    """Prefer saved page-100 responses, then fill from historical list archives."""
    found={}
    def accept(report,body,location):
        url=report.get('url',report.get('descriptor',{}).get('url',''))
        match=re.fullmatch(r'https://api.github.com/repositories/([1-9][0-9]*)/releases(?:\?per_page=100)?',url)
        if not match or match[1] not in wanted or report.get('status')!=200:return
        size=100 if '?per_page=100' in url else 30
        if match[1] in found and found[match[1]]['page_size']>=size:return
        if len(body)!=report['body_bytes'] or hashlib.sha256(body).hexdigest()!=report['body_sha256']:
            raise ValueError('saved response hash mismatch: '+location)
        found[match[1]]=dict(report=report,body=body,evidence=location,page_size=size,url=url)
    paths=sorted(RESEARCH.glob('*/release-*/report.json'))+[
        RESEARCH/'brave-release-20261031/report.json',RESEARCH/'am-utils-release-20261028/report.json']
    for path in paths:
        if path.exists():accept(json.loads(path.read_text()),path.with_name('body.json').read_bytes(),str(path.relative_to(ROOT)))
    archive=RESEARCH/'supervised-baseline-40529551070-evidence.tar.gz'
    with tarfile.open(archive) as saved:
        prefix='supervised-baseline-40529551070/'
        for report in json.load(saved.extractfile(prefix+'report.json'))['attempts']:
            rid=str(report['repository_id'])
            if rid in wanted and rid not in found:
                accept(report,saved.extractfile(prefix+report['request_id']+'.body').read(),
                       str(archive.relative_to(ROOT))+':'+report['request_id'])
    archive=RESEARCH/'appimage-next-large-batch-20261102/evidence.tar.gz'
    with tarfile.open(archive) as saved:
        for member in saved:
            if not member.name.startswith('./release-') or not member.name.endswith('/report.json'):continue
            report=json.load(saved.extractfile(member))
            match=re.fullmatch(r'https://api.github.com/repositories/([1-9][0-9]*)/releases',report.get('url',''))
            if match and match[1] in wanted and match[1] not in found:
                accept(report,saved.extractfile(member.name.replace('report.json','body.json')).read(),
                       str(archive.relative_to(ROOT))+':'+member.name)
    return found


def measure(revision):
    started=time.monotonic()
    manifest=(ROOT/'docs/track/release-catalog/design/yaml-manifest.json').read_bytes()
    limits=policy((ROOT/'tools/catalog-collector/yaml-policy.json').read_bytes())
    apps,identities,enrollment=enroll(manifest,1,shared_recipes(ROOT),source_revision=revision)
    saved=saved_lists(set(identities));repositories={};records=[]
    for rid,item in sorted(saved.items()):
        r=item['report']
        start=r.get('started_at',r.get('request_started_at'))
        end=r.get('completed_at',r.get('response_completed_at'))
        headers=r.get('public_headers',r.get('headers',{}))
        attempt=dict(repository_id=int(rid),descriptor=dict(url=item['url']),body=item['body'],
                     outcome='response',status=200,request_started_at=start,response_completed_at=end)
        previous=dict(identities[rid])
        obj=merge_attempts(previous,[(attempt,'rel="next"' in headers.get('link',''))],
            attempted_at=utc(start).strftime('%Y-%m-%dT%H:%M:%SZ'),
            page_size=item['page_size'],max_catalog_bytes=limits['max_file_bytes'])
        if obj['collection']['status']!='ok':raise ValueError(('saved source refused',rid,obj['collection']))
        repositories[rid]=obj
        records.append(dict(repository_id=rid,evidence=item['evidence'],page_size=item['page_size'],
            raw_bytes=len(item['body']),body_sha256=r['body_sha256'],observed_at=obj['observed_at'],
            releases=len(obj['releases']),assets=sum(len(v['assets']) for v in obj['releases'].values())))
    covered_apps={name:rid for name,rid in apps.items() if str(rid) in repositories}
    tree=candidate_tree(covered_apps,repositories,schema=schema_url(revision),max_file_bytes=limits['max_file_bytes'])
    tree_documents(tree,limits)
    sizes={p:len(b) for p,b in tree.items()}
    largest=max((p for p in tree if p!='apps.yaml'),key=lambda p:sizes[p])
    measurements=[]
    with tempfile.TemporaryDirectory(prefix='yaml-saved-capacity-') as directory:
        root=Path(directory)
        for name in (largest,'repositories/438803890.yaml'):
            doc=root/'repository.yaml';doc.write_bytes(tree[name]);expected=None
            for tool in ('mawk','gawk','busybox'):
                bindir=root/tool;bindir.mkdir(exist_ok=True)
                awk=bindir/'awk'
                if not awk.exists():
                    if tool=='busybox':
                        awk.write_text('#!/bin/sh\nexec '+shutil.which(tool)+' awk "$@"\n');awk.chmod(0o755)
                    else:awk.symlink_to(shutil.which(tool))
                env=dict(os.environ,PATH=str(bindir)+':/usr/bin:/bin',
                         AM_YAML_MAX_INPUT_BYTES=str(limits['max_file_bytes']),
                         AM_YAML_MAX_OUTPUT_BYTES=str(limits['max_file_bytes']))
                stats=root/'time'
                result=subprocess.run(['/usr/bin/time','-f','%e %M','-o',str(stats),
                    'sh',str(ROOT/'modules/catalog-yaml-reader.am'),'asset_facts',str(doc)],
                    env=env,check=True,capture_output=True,timeout=90)
                hashed=hashlib.sha256(result.stdout).hexdigest()
                if expected is not None and expected!=hashed:raise ValueError('awk projection mismatch')
                expected=hashed
                seconds,rss=stats.read_text().split()
                measurements.append(dict(document=name,awk=tool,wall_seconds=float(seconds),
                    max_rss_kib=int(rss),output_bytes=len(result.stdout),sha256=hashed))
    return dict(source_revision=revision,live=False,complete_bootstrap=False,
        policy_sha256=hashlib.sha256((ROOT/'tools/catalog-collector/yaml-policy.json').read_bytes()).hexdigest(),
        enrolled_sources=len(identities),saved_list_sources=len(saved),
        missing_list_sources={rid:identities[rid]['repository'] for rid in sorted(set(identities)-set(saved))},
        enrolled_paths=len(enrollment['recipes']),covered_apps=len(covered_apps),
        raw_bytes=sum(r['raw_bytes'] for r in records),yaml_tree_bytes=sum(sizes.values()),
        largest_document=largest,largest_yaml_bytes=sizes[largest],
        releases=sum(r['releases'] for r in records),assets=sum(r['assets'] for r in records),
        records=records,consumer_measurements=measurements,
        local_wall_seconds=round(time.monotonic()-started,3),
        parent_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        limitation='Saved observations at their original page sizes/times; not live page-100/default collection, transport timing or operational cap acceptance.')


if __name__=='__main__':
    resource.setrlimit(resource.RLIMIT_AS,(768*1024*1024,768*1024*1024))
    resource.setrlimit(resource.RLIMIT_CPU,(180,180))
    revision=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD']).decode().strip()
    result=measure(revision)
    print(json.dumps(result,sort_keys=True,indent=2))
