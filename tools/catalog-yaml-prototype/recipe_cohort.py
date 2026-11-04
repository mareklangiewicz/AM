#!/usr/bin/env python3
"""Compare named policies with actual recipes on saved bytes; never uses network."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/catalog-collector'))
from attempt_adapter import merge_attempts, utc
from experiment import SCHEMA
from yaml_publication import candidate_tree
from yaml_recipe_cohort import COHORT, select_cohort

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


def legacy(recipe, raw):
    source = (ROOT/'programs'/recipe).read_text()
    # Trusted recipe declarations only: never source the installer entry point.
    declarations = source.split('# shellcheck source=modules/appimage.am')[0]
    helper = (ROOT/'modules/appimage.am').read_text().split('# Preserve the installed')[0]
    run = subprocess.run(['/bin/dash', '-c', declarations+'\n'+helper+'\nam_appimage_select_asset'],
        input=raw, capture_output=True, check=True, env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'})
    return run.stdout.decode().strip()


def main():
    saved = fixtures()
    rows = []
    for recipe in COHORT:
        raw, record, repository = saved[262342594 if recipe.endswith('/obsidian') else 16408992]
        selected = select_cohort(recipe, repository, 'b'*40,
            now=utc(repository['observed_at']))
        old = legacy(recipe, raw)
        assert old == selected['asset']['url'], (recipe, old, selected)
        rows.append(dict(recipe=recipe, recipe_sha256=hashlib.sha256((ROOT/'programs'/recipe).read_bytes()).hexdigest(),
            body_sha256=record['body_sha256'], body_bytes=len(raw),
            request_id=record['request_id'], observed_at=repository['observed_at'],
            legacy_url=old, proposed=selected, equal=True,
            release_page_ids=[str(r['id']) for r in json.loads(raw)],
            release_published_ids=sorted(repository['releases'],
                key=lambda rid: (repository['releases'][rid]['published_at'], int(rid)), reverse=True)))
    result = dict(archive=str(ARCHIVE.relative_to(ROOT)),
        archive_sha256=hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
        scope='saved default-size 30 list pages, not current/default-capacity evidence', cases=rows)
    (Path(__file__).with_name('recipe-cohort-results.json')).write_text(json.dumps(result, indent=2)+'\n')
    print('Five recipe comparisons pass on two hash-checked saved list bodies.')


if __name__ == '__main__':
    main()
