"""Saved upstream fixture loader; not an operational command."""
import hashlib
import json
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[2]
from fixture_facts import merge_attempts, utc
from test_yaml_reader import SCHEMA
from yaml_publication import candidate_tree

ARCHIVE = ROOT/'docs/track/release-catalog/research/supervised-baseline-40529551070-evidence.tar.gz'

PREFIX = 'supervised-baseline-40529551070/'

def fixtures():
    result = {}
    with tarfile.open(ARCHIVE) as archive:
        report = json.load(archive.extractfile(PREFIX+'report.json'))
        for record in report['attempts']:
            rid = record['repository_id']
            if rid not in (262342594, 16408992) or not record['descriptor']['url'].endswith('/releases'):
                continue
            raw = archive.extractfile(PREFIX+record['request_id']+'.body').read()
            assert len(raw) == record['body_bytes']
            assert hashlib.sha256(raw).hexdigest() == record['body_sha256']
            attempt = dict(record, body=raw)
            initial = dict(format=2, schema=SCHEMA, repository_id=rid,
                repository='obsidianmd/obsidian-releases' if rid == 262342594 else 'neovim/neovim')
            normalized = merge_attempts(initial, [(attempt, True)],
                attempted_at=utc(record['request_started_at']).strftime('%Y-%m-%dT%H:%M:%SZ'),
                page_size=30, max_catalog_bytes=2097152)
            assert normalized['collection']['status'] == 'ok'
            candidate_tree({'fixture': rid}, {str(rid): normalized}, schema=SCHEMA, max_file_bytes=2097152)  # Full structural validation.
            result[rid] = (raw, record, normalized)
    assert len(result) == 2
    return result
