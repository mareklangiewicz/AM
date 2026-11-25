"""Saved upstream fixture loader; not an operational command."""
import hashlib
import json
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[2]
from fixture_facts import utc

ARCHIVE = ROOT/'docs/track/release-catalog/research/supervised-baseline-40529551070-evidence.tar.gz'

PREFIX = 'supervised-baseline-40529551070/'

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
