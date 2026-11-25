"""Saved upstream fixture loader; not an operational command."""
import hashlib
import json
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[2]
from fixture_facts import utc
from fixture_v3 import REVISION, repository

ARCHIVE = ROOT/'docs/track/release-catalog/research/supervised-baseline-40529551070-evidence.tar.gz'

PREFIX = 'supervised-baseline-40529551070/'

def fixtures():
    """Obsidian and Neovim as format-3 source documents, by repository id."""
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
            assert record['outcome'] == 'response' and record['status'] == 200
            name = 'obsidianmd/obsidian-releases' if rid == 262342594 else 'neovim/neovim'
            received = utc(record['response_completed_at']).strftime('%Y-%m-%dT%H:%M:%SZ')
            releases = json.loads(raw)  # saved with per_page=30: a full page is not all history
            result[rid] = repository(rid, name, releases, received, REVISION, complete=len(releases) < 30)
    assert len(result) == 2
    return result


def saved_bodies():
    """GitHub's release-list bodies and receipt times for Neovim and Obsidian,
    saved by run 40529551070 (per_page=30), by repository id."""
    bodies = {}
    with tarfile.open(ARCHIVE) as archive:
        report = json.load(archive.extractfile(PREFIX+'report.json'))
        for record in report['attempts']:
            rid = record['repository_id']
            if rid in (262342594, 16408992) and record['descriptor']['url'].endswith('/releases'):
                raw = archive.extractfile(PREFIX+record['request_id']+'.body').read()
                assert hashlib.sha256(raw).hexdigest() == record['body_sha256']
                bodies[rid] = (raw, utc(record['response_completed_at']).strftime('%Y-%m-%dT%H:%M:%SZ'))
    assert set(bodies) == {262342594, 16408992}
    return bodies
