"""Saved upstream fixture loader; not an operational command."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
from fixture_facts import merge_attempts, utc
from test_yaml_reader import SCHEMA
from yaml_publication import candidate_tree
from reference_policies import AM_UTILS, select_cohort

RID = 1225768109

EVIDENCE = ROOT/'docs/track/release-catalog/research/am-utils-release-20261028'

def fixture():
    raw = (EVIDENCE/'body.json').read_bytes()
    report = json.loads((EVIDENCE/'report.json').read_bytes())
    if len(raw) != report['body_bytes'] or hashlib.sha256(raw).hexdigest() != report['body_sha256']:
        raise ValueError('saved body identity')
    attempt = dict(repository_id=RID, descriptor=report['descriptor'], body=raw,
                   outcome='response', status=report['status'],
                   request_started_at=report['started_at'], response_completed_at=report['completed_at'])
    repository = merge_attempts(dict(format=2, schema=SCHEMA, repository_id=RID,
                                    repository='ivan-hc/am-utils'), [(attempt, False)],
        attempted_at=utc(report['started_at']).strftime('%Y-%m-%dT%H:%M:%SZ'),
        page_size=30, max_catalog_bytes=2097152)
    if repository['collection']['status'] != 'ok':
        raise ValueError('saved normalization refused')
    apps = {recipe.split('/')[1]:RID for recipe in AM_UTILS}
    tree = candidate_tree(apps, {str(RID):repository}, schema=SCHEMA, max_file_bytes=2097152)
    return raw, report, repository, tree
