"""Verify frozen selectors against exact acquired assets and prepare bounded shards."""
import difflib
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import tempfile

from collector import Descriptor, require
from identity_batch import ROOT
from large_evidence import DIRECTORY, OUTPUT, PAYLOAD_HASH, saved
from migration_batch import compact_recipe, pipeline
from storage import canonical, content, digest


def prepare():
    raw = (DIRECTORY/'payload.json').read_bytes()
    require(digest(raw) == PAYLOAD_HASH, 'payload_changed')
    payload = json.loads(raw)
    batch = json.loads((OUTPUT/'batch.json').read_bytes())
    require(batch['payload_sha256'] == PAYLOAD_HASH and not batch['stopped'], 'incomplete_evidence')
    responses = {r['alias']: r for r in batch['releases']}
    result = dict(migrated=[], exceptions=[], sources=[], metadata_verified=True,
                  production_applied=False, payload_sha256=PAYLOAD_HASH)
    patch = []
    for row in payload['rows']:
        response = responses.get(row['alias'])
        if not response or not response['accepted']:
            result['exceptions'].extend(dict(path=r['path'], alias=row['alias'],
                reason='identity_or_release_refused') for r in row['recipes'])
            continue
        known = batch['identities'][row['identity_request']]
        identity = saved(ROOT/known['evidence'], row['identity_request'])
        require(identity['accepted'] and identity['identity']['id'] == response['repository_id'], 'identity_evidence')
        directory = ROOT/response['evidence']
        report = saved(directory, response['fetch_url'])
        require(report['accepted'], 'release_evidence')
        body = (directory/'body.json').read_bytes()
        releases = content(body, dict(url=response['fetch_url']))
        if isinstance(releases, dict):
            releases = [releases]
        assets = {a['browser_download_url'] for release in releases for a in release['assets']}
        accepted = []
        for recipe in row['recipes']:
            path = ROOT/recipe['path']
            original = path.read_bytes()
            require(digest(original) == recipe['sha256'], 'recipe_changed')
            selections = []
            for key in ('install_selector', 'update_selector'):
                selector = pipeline(row, recipe[key])
                # This frozen family contains only text-filter pipelines. Refuse
                # command substitution/control operators before executing filters.
                require(not any(x in selector for x in ('`', '$(', ';', '&&', '\n')), 'unsafe_selector')
                run = subprocess.run(['sh', '-c', 'APP='+shlex.quote(path.name)+'\n'+selector],
                    input=body, capture_output=True, timeout=10)
                require(run.returncode == 0, 'selector_failed')
                selections.append(run.stdout.decode().strip())
            if selections[0] != selections[1] or selections[0] not in assets:
                result['exceptions'].append(dict(path=recipe['path'], alias=row['alias'],
                    reason='original_selector_missing_actual_asset', selected=selections))
                continue
            # An ARM-labelled path selecting an explicitly x86-only filename is
            # not established ARM compatibility merely because the old filter did it.
            if recipe['arch'] in ('aarch64', 'armv7l') and re.search(
                    r'(?:x86[_-]?64|amd64|x64|i[3-6]86)', selections[0].rsplit('/', 1)[-1], re.I):
                result['exceptions'].append(dict(path=recipe['path'], alias=row['alias'],
                    reason='arm_compatibility_unproven', selected=selections))
                continue
            source = compact_recipe(recipe, row)
            with tempfile.NamedTemporaryFile() as check:
                check.write(source.encode()); check.flush()
                subprocess.run(['sh', '-n', check.name], check=True)
            patch.extend(difflib.unified_diff(original.decode().splitlines(True), source.splitlines(True),
                fromfile='a/'+recipe['path'], tofile='b/'+recipe['path']))
            accepted.append(recipe['path'])
            result['migrated'].append(dict(path=recipe['path'], alias=row['alias'],
                source_sha256=recipe['sha256'], candidate_sha256=digest(source.encode()),
                selected=selections[0], evidence=response['evidence'],
                lines_removed=recipe['lines']-len(source.splitlines()),
                bytes_removed=len(original)-len(source.encode())))
        if accepted:
            result['sources'].append(dict(url=response['fetch_url'], repository_id=response['repository_id'],
                request_id=Descriptor(response['fetch_url']).request_id, aliases=[row['alias']],
                identity_evidence='docs/track/release-catalog/issues/67-expand-appimage-migration-throughput.md#verified-identities',
                body_bytes=len(body), evidence=response['evidence']))
    # Merge exact numeric descriptor duplicates only after both original identities
    # have been independently verified; never normalize consumer aliases.
    unique = {}
    for source in result['sources']:
        rid = source['request_id']
        if rid in unique:
            unique[rid]['aliases'].extend(source['aliases'])
        else:
            unique[rid] = source
    result['sources'] = list(unique.values())
    prepared = DIRECTORY/'prepared'
    prepared.mkdir(exist_ok=True)
    legacy = (ROOT/'docs/track/release-catalog/design/staged-manifest.json').read_bytes()
    manifests = {'00': json.loads(legacy)}
    current, body_bytes = [], 0
    for source in result['sources']:
        if len(current) == 52 or body_bytes+source['body_bytes'] > 32_000_000:
            manifests[f'{len(manifests):02d}'] = dict(schema=2, sources=current)
            current, body_bytes = [], 0
        current.append({k: v for k, v in source.items() if k not in ('body_bytes', 'evidence')})
        body_bytes += source['body_bytes']
    if current:
        manifests[f'{len(manifests):02d}'] = dict(schema=2, sources=current)
    require(len(manifests) <= 32, 'shard_count')
    inventory = dict(schema=1, shards={})
    for name, manifest in manifests.items():
        data = legacy if name == '00' else canonical(manifest)+b'\n'
        path = prepared/f'manifest-{name}.json'
        path.write_bytes(data)
        inventory['shards'][name] = dict(path=str(path.relative_to(ROOT)), sha256=digest(data))
    (prepared/'inventory.json').write_bytes(canonical(inventory)+b'\n')
    (prepared/'recipes.patch').write_text(''.join(line if line.endswith('\n') else
        line+'\n\\ No newline at end of file\n' for line in patch))
    subprocess.run(['git', 'apply', '--check', str(prepared/'recipes.patch')], cwd=ROOT, check=True)
    (prepared/'migration.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(recipes=len(result['migrated']), exceptions=len(result['exceptions']),
        sources=len(result['sources']), shards=len(manifests),
        body_bytes=sum(s['body_bytes'] for s in result['sources']),
        lines_removed=sum(r['lines_removed'] for r in result['migrated'])), indent=2))
    return result


if __name__ == '__main__':
    prepare()
