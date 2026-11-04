#!/usr/bin/env python3
"""Pinned YAML -> saved JSON -> retained merge -> local Git -> shell consumer."""
import sys
from pathlib import Path
# Legacy experiment entry point; runtime code lives in catalog-collector.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'catalog-collector'))
import copy
import datetime
import json
import os
import pathlib
import subprocess
import tempfile
from unittest.mock import patch

from bounded_experiment import release
from experiment import repository, SCHEMA
from yaml_publication import git, load_local, publish_local, refresh_local, REF

HERE = pathlib.Path(__file__).resolve().parent
REAL_DATETIME = datetime.datetime


class Clock(REAL_DATETIME):
    minute = 0

    @classmethod
    def now(cls, tz=None):
        return REAL_DATETIME(2026,11,4,12,cls.minute,1,tzinfo=datetime.timezone.utc)


def trial(root, tool):
    root.mkdir()
    shim = root/'bin'
    shim.mkdir()
    (shim/'awk').write_text('#!/bin/sh\nexec '+tool+(' awk' if tool=='busybox' else '')+' "$@"\n')
    (shim/'awk').chmod(0o755)
    old_path = os.environ['PATH']
    os.environ['PATH'] = str(shim)+':'+old_path
    try:
        repo = root/'git'
        repo.mkdir()
        git(repo,'init','--bare')
        initial = {str(rid):dict(copy.deepcopy(repository()),repository_id=rid,
                               repository='example/source'+str(rid)) for rid in (123,124,125)}
        apps = {'example':123,'other':124,'untouched':125}
        options = dict(schema=SCHEMA,max_file_bytes=2*1024*1024)
        before = publish_local(repo,apps,initial,expected_parent=None,**options)
        source = root/'response.json'
        source.write_text(json.dumps([release()],ensure_ascii=False))
        bad = root/'bad.json'
        bad.write_text('{')
        good_page = dict(path=source,has_next=True)
        bad_page = dict(path=bad,has_next=False)
        Clock.minute = 0
        def refresh(commit,pages,**extra):
            Clock.minute += 1
            with patch('bounded.datetime.datetime',Clock):
                return refresh_local(repo,commit,pages,attempted_at=f'2026-11-04T12:{Clock.minute:02d}:00Z',
                                     **options,**extra)
        after = refresh(before,{'123':[good_page],'124':[bad_page]})
        loaded_apps, loaded = load_local(repo,after,max_file_bytes=options['max_file_bytes'])
        assert loaded_apps == apps
        assert list(loaded['123']['releases']) == ['456','457']
        assert loaded['123']['releases']['456'] == initial['123']['releases']['456']
        assert loaded['123']['observed_at'] == '2026-11-04T12:01:01Z'
        assert loaded['123']['releases']['457'].get('observed_at') is None
        assert loaded['123']['releases']['457']['title'] == 'café\n\u2028'
        assert loaded['124']['collection']['reason'] == 'invalid_response'
        for key in ('releases','last_success','observed_at'):
            assert loaded['124'][key] == initial['124'][key]
        for path in ('apps.yaml','repositories/125.yaml'):
            assert git(repo,'show',before+':'+path) == git(repo,'show',after+':'+path)
        retry = refresh(after,{'124':[dict(path=source,has_next=False)]})
        _, retried = load_local(repo,retry,max_file_bytes=options['max_file_bytes'])
        assert retried['124']['collection']['status']=='ok'
        assert list(retried['124']['releases']) == ['456','457']
        assert git(repo,'show',retry+':repositories/123.yaml') == git(repo,'show',after+':repositories/123.yaml')
        source.write_text(json.dumps([release(458)],ensure_ascii=False))
        failed = refresh(retry,{'123':[good_page,bad_page]},page_limit='all')
        _, final = load_local(repo,failed,max_file_bytes=options['max_file_bytes'])
        assert final['123']['collection']['status']=='failed'
        assert '458' not in final['123']['releases']
        for key in ('releases','last_success','observed_at'):
            assert final['123'][key] == retried['123'][key]
        # Loading old commit after later ref advances must still return old state.
        assert load_local(repo,before,max_file_bytes=options['max_file_bytes']) == (apps,initial)
        for commit, count in ((before,1),(after,2),(retry,2),(failed,2)):
            snapshot = root/commit
            snapshot.mkdir()
            for name in ('apps.yaml','repositories/123.yaml'):
                target = snapshot/name
                target.parent.mkdir(exist_ok=True)
                target.write_bytes(git(repo,'show',commit+':'+name))
            run = subprocess.run(['/bin/dash',str(HERE/'browse.sh'),str(snapshot),'example'],
                                 capture_output=True,timeout=10)
            assert run.returncode==0,run.stderr
            assert run.stdout.count(b'\n')==count
        refused = 0
        for action in (lambda:refresh(before,{}),
                       lambda:refresh(failed,{'999':[]}),
                       lambda:load_local(repo,'catalog',max_file_bytes=options['max_file_bytes'])):
            try:
                action()
            except ValueError:
                refused += 1
            else:
                raise AssertionError('invalid operation accepted')
            assert git(repo,'rev-parse',REF).decode().strip()==failed
        # Handcraft an invalid historical blob: duplicate map keys must be rejected
        # on load, rather than silently repaired by the general YAML decoder.
        raw = git(repo,'show',before+':apps.yaml')
        raw += b'  "example": 124\n'
        index = root/'invalid-index'
        git(repo,'read-tree',before,index=index)
        oid = git(repo,'hash-object','-w','--stdin',data=raw).decode().strip()
        git(repo,'update-index','--cacheinfo','100644',oid,'apps.yaml',index=index)
        tree = git(repo,'write-tree',index=index).decode().strip()
        invalid = git(repo,'commit-tree',tree,data=b'Invalid input fixture\n').decode().strip()
        try:
            load_local(repo,invalid,max_file_bytes=options['max_file_bytes'])
        except ValueError:
            refused += 1
        else:
            raise AssertionError('duplicate key accepted')
        assert git(repo,'rev-parse',REF).decode().strip()==failed
        return dict(awk=tool,status='passed',snapshots=4,pinned_consumer_reads=4,
                    refused_operations=refused,unselected_bytes_unchanged=True,
                    failed_scope_preserved=True,retry_loaded_previous_state=True)
    finally:
        os.environ['PATH'] = old_path


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='yaml-refresh-') as directory:
        results = [trial(pathlib.Path(directory)/tool,tool) for tool in ('mawk','gawk','busybox')]
    (HERE/'refresh-results.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results,indent=2))
