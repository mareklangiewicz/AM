#!/usr/bin/env python3
"""Format-2 writer -> local Git snapshots -> simple shell consumer, offline only."""
import sys
from pathlib import Path
# Legacy experiment entry point; runtime code lives in catalog-collector.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'catalog-collector'))
import copy
import json
import os
import pathlib
import subprocess
import tempfile

import yaml
from experiment import repository, SCHEMA
from retention import refresh
from yaml_publication import git, publish_local, REF

HERE = pathlib.Path(__file__).resolve().parent


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
        git(repo, 'init', '--bare')
        first = repository()
        other = dict(copy.deepcopy(first), repository_id=124, repository='example/other')
        apps = {'example':123, 'example-beta':123, 'other':124}
        options = dict(schema=SCHEMA, max_file_bytes=2*1024*1024)
        before = publish_local(repo, apps, {'123':first,'124':other},expected_parent=None,**options)
        facts = copy.deepcopy(first['releases']['456'])
        facts['tag'] = 'v3.0.0'
        updated = refresh(first, [dict(received_at='2026-11-04T12:00:01Z',
                          releases={'457':facts},has_next=True,bytes=1,seconds=0)],
                          attempted_at='2026-11-04T12:00:00Z')
        failed = refresh(other,[dict(error='transport')],attempted_at='2026-11-04T12:00:00Z')
        assert failed['releases'] == other['releases']
        assert failed['observed_at'] == other['observed_at']
        after = publish_local(repo, apps, {'123':updated,'124':failed},expected_parent=before,**options)
        paths = git(repo,'ls-tree','-r','--name-only',after).decode().splitlines()
        assert paths == ['apps.yaml','repositories/123.yaml','repositories/124.yaml']
        assert git(repo,'rev-parse',after+'^').decode().strip() == before
        old_rows = None
        for commit, expected in ((before,first),(after,updated),(before,first)):
            snapshot = root/commit
            snapshot.mkdir(exist_ok=True)
            for name in paths:
                path = snapshot/name
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(git(repo,'show',commit+':'+name))
            assert yaml.safe_load((snapshot/'repositories/123.yaml').read_bytes()) == expected
            rows = b''
            for rid, record in expected['releases'].items():
                values = (record['tag'],record.get('observed_at',expected['observed_at']),
                          record['published_at'],record['prerelease'],record['title'])
                rows += (rid+''.join('\t'+json.dumps(value,ensure_ascii=False) for value in values)+'\n').encode()
            run = subprocess.run(['/bin/dash',str(HERE/'browse.sh'),str(snapshot),'example-beta'],
                                 capture_output=True,timeout=10)
            assert (run.returncode,run.stdout)==(0,rows),run.stderr
            if commit == before:
                if old_rows is not None:
                    assert run.stdout == old_rows
                old_rows = run.stdout
        saved = yaml.safe_load(git(repo,'show',after+':repositories/124.yaml'))
        assert saved == failed and saved['collection']['status']=='failed'
        # Refusal must not move the already accepted snapshot.
        cases = [({'123':updated,'124':failed},before,options),
                 ({'123':dict(updated,repository_id=999),'124':failed},after,options),
                 ({'123':updated,'124':failed},after,dict(options,max_file_bytes=1))]
        bad = copy.deepcopy(updated)
        bad['releases']['457']['title'] = 'unsupported\x01control'
        cases.append(({'123':bad,'124':failed},after,options))
        cases.append(({'123':updated},after,options))  # app "other" still refers to 124
        refused = 0
        for repositories, parent, limits in cases:
            try:
                publish_local(repo,apps,repositories,expected_parent=parent,**limits)
            except (ValueError,yaml.YAMLError):
                refused += 1
            else:
                raise AssertionError('invalid publication accepted')
            assert git(repo,'rev-parse',REF).decode().strip()==after
        return dict(awk=tool,status='passed',snapshots=2,pinned_reads=3,
                    refused_candidates=refused,tree_files=paths,
                    retained_old_observation=True,failed_source_preserved=True)
    finally:
        os.environ['PATH'] = old_path


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='yaml-publication-') as directory:
        results = [trial(pathlib.Path(directory)/tool,tool) for tool in ('mawk','gawk','busybox')]
    (HERE/'publication-results.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results,indent=2))
