#!/usr/bin/env python3
"""Serial offline capacity cases over maintained runtime; no HTTP/token lookup.

Run each case under /usr/bin/time externally. Logical transport clock is simulated;
wall/CPU/RSS measurements are local processing evidence, not live API latency.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'catalog-collector'))
from datetime import datetime, timedelta, timezone
import hashlib
import json
import resource
import tempfile
import time

from collector import Chunk, Connected, End, Headers
from storage import canonical
from yaml_adapter import IncompleteBootstrap, schema_url
from yaml_enrollment import enroll, shared_recipes
from yaml_staging import collect_stage, policy, read_staged
from yaml_publication import candidate_tree, decode_document, tree_documents
from bounded import normalize
from retention import refresh
from writer import document

ROOT = Path(__file__).resolve().parents[2]
RAW = (ROOT/'docs/track/release-catalog/design/staged-manifest.json').read_bytes()
POLICY = (ROOT/'tools/catalog-collector/yaml-policy.json').read_bytes()


class Clock:
    def __init__(self): self.seconds = 0
    def monotonic(self): return self.seconds
    def utcnow(self): return datetime(2026,11,4,16,tzinfo=timezone.utc)+timedelta(seconds=self.seconds)


def releases(repository, count=100, assets=8, first=1):
    return [dict(id=n,draft=False,tag_name='v'+str(n),name='Synthetic release '+str(n),
        html_url=f'https://github.com/{repository}/releases/tag/v{n}',
        published_at='2026-11-03T00:00:00Z',prerelease=False,
        assets=[dict(id=n*1000+a,name=f'app-{a}-x86_64.AppImage',size=123456,
            browser_download_url=f'https://github.com/{repository}/releases/download/v{n}/app-{a}-x86_64.AppImage',
            content_type='application/octet-stream',digest='sha256:'+'a'*64)
            for a in range(1,assets+1)]) for n in range(first,first+count)]


def context(revision, raw=RAW):
    scope = dict(sources=None,page_size=100,page_limit=1,reconcile=False)
    return dict(repository='mareklangiewicz/AM',repository_id='1',event='workflow_dispatch',
        ref='refs/heads/main-marek',sha=revision,workflow_sha=revision,approved_revision=revision,
        run_id='10',run_attempt='1',previous_publication='',
        manifest_sha256=hashlib.sha256(raw).hexdigest(),
        yaml_policy_sha256=hashlib.sha256(POLICY).hexdigest(),
        yaml_scope_sha256=hashlib.sha256(canonical(scope)).hexdigest())


def synthetic(revision, assets, *, single_source=False):
    raw = RAW
    if single_source:
        manifest = json.loads(RAW)
        manifest['schema'] = 2
        first_id = manifest['sources'][0]['repository_id']
        manifest['sources'] = [s for s in manifest['sources'] if s['repository_id'] == first_id]
        raw = canonical(manifest)
    recipes = list(shared_recipes(ROOT))
    apps,identities,_ = enroll(raw,1,recipes,source_revision=revision)
    clock = Clock()
    calls = []
    class Transport:
        def execute(self,request,credential,limits):
            rid = str(request.source.repository_id)
            body = canonical(releases(identities[rid]['repository'],assets=assets))
            calls.append(dict(repository_id=rid,bytes=len(body)))
            yield Connected()
            yield Headers(200,(('x-ratelimit-limit','1000'),('x-ratelimit-remaining','900'),
                               ('x-ratelimit-reset','1793894400')))
            clock.seconds += 1
            for offset in range(0,len(body),8192): yield Chunk(body[offset:offset+8192])
            yield End()
    with tempfile.TemporaryDirectory(prefix='yaml-capacity-') as directory:
        output = Path(directory)/'artifact'
        try:
            report = collect_stage(context(revision,raw),raw,revision,POLICY,recipes,
                lambda value:Transport(),clock,object(),output,repo=None)
        except IncompleteBootstrap as failure:
            assert not output.exists()
            return dict(status='refused',report=failure.report,sources=len(identities),assets_per_release=assets,
                        body_bytes_generated=sum(c['bytes'] for c in calls),requests=len(calls))
        tree,receipt = read_staged(output,policy(POLICY))
        counts = [len(decode_document(b,policy(POLICY)['max_file_bytes']).get('releases',{}))
                  for p,b in tree.items() if p != 'apps.yaml']
        assert len(counts) == len(identities)
        failed = {rid:decode_document(tree['repositories/'+rid+'.yaml'],policy(POLICY)['max_file_bytes'])['collection']['reason']
                  for rid,status in report['sources'].items() if status != 'ok'}
        assert counts == ([0] if single_source else [100]*49)
        assert bool(failed) == single_source
        assert not report['not_attempted_repositories']
        return dict(status='staged_failed_metadata' if failed else 'staged',sources=len(identities),apps=len(apps),failures=failed,releases=sum(counts),
            assets=sum(counts)*assets,assets_per_release=assets,requests=len(calls),
            body_bytes=report['received_bytes'],yaml_tree_bytes=sum(map(len,tree.values())),
            largest_yaml_bytes=max(map(len,tree.values())),receipt_bytes=len(receipt),
            simulated_transport_seconds=report['elapsed_seconds'],
            tree_sha256=hashlib.sha256(canonical({p:hashlib.sha256(b).hexdigest()
                                               for p,b in sorted(tree.items())})).hexdigest())


def growth(revision):
    limits = policy(POLICY)
    previous = dict(format=2,schema=schema_url(revision),repository_id=123,repository='example/app')
    records = []
    for day in range(1,41):
        at = (datetime(2026,11,4,tzinfo=timezone.utc)+timedelta(days=day)).strftime('%Y-%m-%dT%H:%M:%SZ')
        facts = normalize(releases('example/app',first=(day-1)*100+1),100)
        response = dict(received_at=at,releases=facts,has_next=True,bytes=100,seconds=0)
        result = refresh(previous,[response],attempted_at=at,max_catalog_bytes=limits['max_file_bytes'])
        size = len(document(result).encode())
        if result['collection']['status'] == 'failed':
            assert result['collection']['reason'] == 'collection_limit'
            assert all(result.get(k) == previous.get(k) for k in ('schema','releases','last_success','observed_at'))
            assert set(result['releases']) == set(previous['releases'])
            return dict(status='growth_refused_atomically',days=records,refused_day=day,
                retained_releases=len(previous['releases']),retained_yaml_bytes=len(document(previous).encode()),
                failed_metadata_yaml_bytes=size,cap=limits['max_file_bytes'],
                note='synthetic bytes/time inputs are not API resource measurements')
        decode_document(document(result).encode(),limits['max_file_bytes'])
        if day > 1:
            assert result['releases']['1']['observed_at'] == previous.get('releases',{}).get('1',{}).get(
                'observed_at',previous['observed_at'])
        records.append(dict(day=day,releases=len(result['releases']),yaml_bytes=size))
        previous = result
    raise AssertionError('fixture did not reach current per-file cap')


def saved(revision):
    from real_replay import saved_inputs
    repositories,pages,records,excluded = saved_inputs()
    apps = {'source-'+rid:int(rid) for rid in repositories}
    tree = candidate_tree(apps,repositories,schema=next(iter(repositories.values()))['schema'],
                          max_file_bytes=policy(POLICY)['max_file_bytes'])
    tree_documents(tree,policy(POLICY))
    from collections import Counter
    return dict(status='saved_normalization_validated',sources=len(records),
        releases=sum(r['releases'] for r in records),assets=sum(r['assets'] for r in records),
        raw_bytes=sum(r['raw_bytes'] for r in records),yaml_tree_bytes=sum(map(len,tree.values())),
        largest_yaml_bytes=max(map(len,tree.values())),
        page_size_counts=dict(Counter(str(r['page_size']) for r in records)),
        excluded_latest=len(excluded),
        evidence='hash-checked saved responses and original receipt times, not current collection',
        tree_sha256=hashlib.sha256(canonical({p:hashlib.sha256(b).hexdigest()
                                            for p,b in sorted(tree.items())})).hexdigest())


if __name__ == '__main__':
    import subprocess
    if len(sys.argv) != 2 or sys.argv[1] not in {'ordinary','dense','growth','saved'}:
        raise SystemExit('usage: capacity.py ordinary|dense|growth|saved')
    resource.setrlimit(resource.RLIMIT_AS,(768*1024*1024,768*1024*1024))
    resource.setrlimit(resource.RLIMIT_CPU,(180,180))
    revision = subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
    started = time.monotonic()
    case = sys.argv[1]
    result = (saved(revision) if case == 'saved' else growth(revision) if case == 'growth'
              else synthetic(revision,80 if case == 'dense' else 8,single_source=case == 'dense'))
    result.update(case=case,source_revision=revision,policy_sha256=hashlib.sha256(POLICY).hexdigest(),
                  local_wall_seconds=round(time.monotonic()-started,3),live=False)
    print(json.dumps(result,sort_keys=True),flush=True)
