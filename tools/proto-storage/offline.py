#!/usr/bin/env python3
"""THROWAWAY ticket 08 experiment. No HTTP or remote Git operations.
Run: python tools/proto-storage/offline.py [--output /tmp/PROTOTYPE-storage]
"""
import argparse
import copy
import hashlib
import json
import re
import subprocess
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

MAX_BODY = 8_000_000
HEADERS = {'etag', 'last-modified', 'link', 'date', 'location', 'retry-after',
           'content-type', 'x-ratelimit-limit', 'x-ratelimit-remaining',
           'x-ratelimit-reset', 'x-ratelimit-used', 'x-ratelimit-resource'}

def require(ok, message):
    if not ok:
        raise ValueError(message)

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()

def digest(value):
    return hashlib.sha256(value).hexdigest()

def pairs(items):
    result = {}
    for key, value in items:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result

def decode(raw):
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite JSON')))

def time(value):
    parsed = datetime.fromisoformat(value)
    require(parsed.utcoffset() is not None, 'timestamp must include timezone')
    return parsed

def descriptor(value):
    require(set(value) == {'url', 'api_version', 'accept'}, 'descriptor fields')
    require(value['api_version'] == '2022-11-28' and
            value['accept'] == 'application/vnd.github+json', 'representation not reviewed')
    u = urlsplit(value['url'])
    require(u.scheme == 'https' and u.netloc == 'api.github.com' and not u.fragment,
            'public GitHub host required')
    require(re.fullmatch(r'/(?:repos/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+|repositories/[0-9]+)/releases(?:/latest|/tags/[^/?#]+)?', u.path),
            'release path required')
    require(not u.query or re.fullmatch(r'(?:per_page|page)=[1-9][0-9]*(?:&(?:per_page|page)=[1-9][0-9]*)*', u.query),
            'unreviewed query')
    return digest(canonical(value))

def manifest_check(manifest):
    require(set(manifest) == {'sources', 'aliases'}, 'manifest fields')
    for rid, source in manifest['sources'].items():
        require(set(source) == {'descriptor', 'public_enrollment'}, 'source fields')
        require(descriptor(source['descriptor']) == rid, 'descriptor identity mismatch')
        require(source['public_enrollment'] == {
            'basis': 'reviewed-public-source', 'privileged_visibility': False},
            'public enrollment missing or privileged')
    for alias, rid in manifest['aliases'].items():
        descriptor({'url': alias, 'api_version': '2022-11-28', 'accept': 'application/vnd.github+json'})
        require(rid in manifest['sources'], 'alias target absent')


def content(raw, desc):
    require(isinstance(raw, bytes) and len(raw) <= MAX_BODY, 'missing or oversized body')
    value = decode(raw)
    is_list = urlsplit(desc['url']).path.endswith('/releases')
    require(isinstance(value, list) if is_list else isinstance(value, dict), 'wrong response shape')
    for release in value if is_list else [value]:
        require(isinstance(release, dict) and isinstance(release.get('id'), int)
                and isinstance(release.get('tag_name'), str)
                and release.get('draft') is False
                and isinstance(release.get('assets'), list), 'invalid or draft release')
    return value


def validate(tree):
    require(isinstance(tree, dict) and all(isinstance(v, bytes) for v in tree.values()), 'regular byte files only')
    index = decode(tree['index.json'])
    require(set(index) == {'schema_version', 'generated_at', 'manifest_sha256', 'manifest',
                           'collector_revision', 'run', 'aliases', 'entries'}, 'index fields')
    require(index['schema_version'] == 1, 'unknown schema')
    manifest_check(index['manifest'])
    require(index['manifest_sha256'] == digest(canonical(index['manifest'])), 'manifest hash')
    require(re.fullmatch('[0-9a-f]{40}', index['collector_revision']), 'collector revision')
    require(isinstance(index['run'], str) and bool(index['run']), 'run provenance')
    generated = time(index['generated_at'])
    expected = {'index.json'}
    for rid, entry in index['entries'].items():
        require(set(entry) == {'descriptor', 'observation', 'validators', 'latest_attempt', 'availability'}, 'entry fields')
        require(descriptor(entry['descriptor']) == rid, 'entry identity')
        require(entry['availability'] in {'available', 'unavailable', 'unknown', 'retired'}, 'availability')
        active = rid in index['manifest']['sources']
        require(active == (entry['availability'] != 'retired'), 'retirement mismatch')
        if active:
            require(entry['descriptor'] == index['manifest']['sources'][rid]['descriptor'], 'manifest descriptor')
        require(set(entry['validators']) <= {'etag', 'last-modified'}, 'validator fields')
        attempt = entry['latest_attempt']
        if attempt:
            require(set(attempt) == {'at', 'status', 'outcome', 'headers'}, 'attempt fields')
            require(time(attempt['at']) <= generated, 'future attempt')
            require(set(attempt['headers']) <= HEADERS, 'unsafe header')
        obs = entry['observation']
        if obs:
            require(set(obs) == {'path', 'sha256', 'bytes', 'received_at', 'validated_at',
                                 'validation_status', 'link', 'scope', 'timing_basis'}, 'observation fields')
            path = 'bodies/' + rid + '.json'
            require(obs['path'] == path, 'unsafe body path')
            require(obs['scope'] == 'single-response' and obs['validation_status'] in {200, 304}, 'observation status/scope')
            require(obs['timing_basis'] in {'response-completed', 'saved-round-completion-upper-bound'}, 'timing basis')
            require(time(obs['received_at']) <= time(obs['validated_at']) <= generated, 'observation chronology')
            require(attempt is not None and time(obs['validated_at']) <= time(attempt['at']), 'attempt chronology')
            raw = tree[path]
            require(digest(raw) == obs['sha256'] and len(raw) == obs['bytes'], 'body digest/length')
            content(raw, entry['descriptor'])
            expected.add(path)
        require(entry['availability'] != 'available' or obs is not None, 'available without body')
    require(set(index['manifest']['sources']) <= set(index['entries']), 'missing active entries')
    for alias, rid in index['aliases'].items():
        require(rid in index['entries'], 'dangling alias')
        require(index['manifest']['aliases'].get(alias) == rid or index['entries'][rid]['availability'] == 'retired', 'unreviewed alias')
    require(all(index['aliases'].get(a) == r for a, r in index['manifest']['aliases'].items()), 'missing reviewed alias')
    require(set(tree) == expected, 'unexpected files')
    return index


def apply(previous_tree, reviewed_manifest, attempts, generated_at, revision, run):
    """Pure apply: returns a new closed byte tree plus transition report."""
    manifest_check(reviewed_manifest)
    old = validate(previous_tree) if previous_tree else {'entries': {}, 'aliases': {}}
    tree = dict(previous_tree or {})
    entries = copy.deepcopy(old['entries'])
    aliases = dict(old['aliases'])
    # Alias remaps explicitly present in the new manifest override old tombstones.
    aliases.update(reviewed_manifest['aliases'])
    for rid, entry in entries.items():
        if rid not in reviewed_manifest['sources']:
            entry['availability'] = 'retired'
    for rid, source in reviewed_manifest['sources'].items():
        if rid not in entries:
            entries[rid] = {'descriptor': source['descriptor'], 'observation': None,
                            'validators': {}, 'latest_attempt': None, 'availability': 'unknown'}
        require(entries[rid]['availability'] != 'retired', 'explicit re-enrollment policy required')
    seen, report = set(), []
    for attempt in attempts:
        rid = attempt['request_id']
        require(rid in reviewed_manifest['sources'] and rid not in seen, 'unknown or duplicate attempt')
        seen.add(rid)
        entry = entries[rid]
        require(attempt['descriptor'] == entry['descriptor'], 'attempt descriptor mismatch')
        require(attempt['timing_basis'] in {'response-completed', 'saved-round-completion-upper-bound'}, 'attempt timing basis')
        at = attempt['at']
        require(time(at) <= time(generated_at), 'future attempt')
        if entry['latest_attempt']:
            require(time(at) >= time(entry['latest_attempt']['at']), 'out-of-order attempt')
        status = attempt['status']
        require(status is None or type(status) is int and 100 <= status <= 599, 'invalid status')
        headers = {k: v for k, v in attempt.get('headers', {}).items() if k in HEADERS}
        require(all(isinstance(v, str) and len(v) <= 8192 for v in headers.values()), 'header bounds')
        outcome = 'temporary-error'
        if status == 200:
            try:
                content(attempt.get('body'), entry['descriptor'])
            except (ValueError, TypeError, UnicodeError):
                entry['availability'], outcome = 'unavailable', 'invalid-body'
            else:
                raw = attempt['body']
                path = 'bodies/' + rid + '.json'
                tree[path] = raw
                entry['observation'] = {'path': path, 'sha256': digest(raw), 'bytes': len(raw),
                    'received_at': at, 'validated_at': at, 'validation_status': 200,
                    'link': headers.get('link'), 'scope': 'single-response',
                    'timing_basis': attempt['timing_basis']}
                entry['validators'] = {k: v for k, v in headers.items() if k in {'etag', 'last-modified'}}
                entry['availability'], outcome = 'available', 'observed'
        elif status == 304:
            obs = entry['observation']
            condition = attempt.get('condition', {})
            require(obs and condition and set(condition) <= {'etag', 'last-modified'}
                    and all(entry['validators'].get(k) == v for k, v in condition.items()),
                    '304 requires exact prior condition and body')
            # Prior whole-tree validation above already checked retained bytes.
            obs['validated_at'], obs['validation_status'] = at, 304
            # timing_basis describes receipt; a 304 must not relabel saved receipt evidence.
            entry['validators'].update({k: v for k, v in headers.items() if k in {'etag', 'last-modified'}})
            entry['availability'], outcome = 'available', 'validated'
        elif status is None or status == 429 or status >= 500 or (
                status == 403 and (headers.get('x-ratelimit-remaining') == '0' or 'retry-after' in headers)):
            pass
        else:
            entry['availability'], outcome = 'unavailable', 'refused'
        entry['latest_attempt'] = {'at': at, 'status': status, 'outcome': outcome, 'headers': headers}
        report.append({'request_id': rid, 'outcome': outcome, 'availability': entry['availability']})
    index = {'schema_version': 1, 'generated_at': generated_at,
             'manifest_sha256': digest(canonical(reviewed_manifest)), 'manifest': reviewed_manifest,
             'collector_revision': revision, 'run': run, 'aliases': aliases, 'entries': entries}
    tree['index.json'] = canonical(index) + b'\n'
    validate(tree)
    return tree, report


def git(repo, *args, data=None):
    return subprocess.run(['git', '-C', str(repo), *args], input=data, check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().strip()


def publish(repo, tree, expected_parent):
    """Only a disposable local repository. CAS ref update prevents stale-parent writes."""
    validate(tree)
    require(not git(repo, 'remote'), 'prototype repository must have no remotes')
    try:
        parent = git(repo, 'rev-parse', '--verify', 'refs/heads/publication')
    except subprocess.CalledProcessError:
        parent = None
    require(parent == expected_parent, 'stale expected parent')
    # Private index avoids worktree races. Hash only explicit regular byte files.
    import os
    with tempfile.TemporaryDirectory(prefix='PROTOTYPE-index-') as scratch:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(scratch) / 'index'))
        def run(*args, data=None):
            return subprocess.run(['git', '-C', str(repo), *args], input=data, env=env,
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().strip()
        run('read-tree', '--empty')
        for path, raw in tree.items():
            oid = run('hash-object', '-w', '--stdin', data=raw)
            run('update-index', '--add', '--cacheinfo', '100644', oid, path)
        root = run('write-tree')
        args = ['commit-tree', root]
        if parent:
            args += ['-p', parent]
        commit = run(*args, data=b'PROTOTYPE offline observation publication\n')
        # Git compares the ref atomically, including if it moved after the first check.
        run('update-ref', 'refs/heads/publication', commit, parent or '0' * 40)
        return commit


def lookup(repo, alias, commit):
    require(re.fullmatch('[0-9a-f]{40}', commit), 'pin must be a full commit')
    index = decode(subprocess.check_output(['git', '-C', str(repo), 'show', commit + ':index.json']))
    rid = index['aliases'][alias]
    entry = index['entries'][rid]
    require(entry['availability'] == 'available', 'observation unavailable')
    obs = entry['observation']
    require(obs and obs['path'] == 'bodies/' + rid + '.json', 'unsafe lookup path')
    raw = subprocess.check_output(['git', '-C', str(repo), 'show', commit + ':' + obs['path']])
    require(digest(raw) == obs['sha256'] and len(raw) == obs['bytes'], 'lookup digest/length')
    return raw, entry


def read_tree(root):
    tree = {}
    for path in root.rglob('*'):
        require(not path.is_symlink(), 'symlink refused')
        if path.is_dir():
            require(path.relative_to(root).as_posix() == 'bodies', 'unexpected directory')
        else:
            require(path.is_file() and not path.stat().st_mode & 0o111, 'regular nonexecutable files only')
            tree[path.relative_to(root).as_posix()] = path.read_bytes()
    validate(tree)
    return tree


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    out = args.output or Path(tempfile.mkdtemp(prefix='PROTOTYPE-storage-'))
    if args.output:
        out.mkdir(parents=True, exist_ok=False)
    repo_root = Path(__file__).resolve().parents[2]
    archive = repo_root / 'docs/track/release-catalog/research/churn-hour-40508899451-evidence.tar.gz'
    # Read only named regular archive members, never extract archive paths.
    with tarfile.open(archive) as tar:
        def saved(round_name, name):
            name = f'churn-hour-40508899451/observations/{round_name}/{name}'
            member = tar.getmember(name)
            require(member.isfile() and member.size <= MAX_BODY, 'unsafe evidence member')
            return tar.extractfile(member).read()
        evidence = {r: decode(saved(r, 'observation.json')) for r in ('baseline', 'hour')}
        base = evidence['baseline']
        require(all(e['complete'] and len(e['responses']) == 6 and
                    all(r['status'] == 200 for r in e['responses'].values()) for e in evidence.values()), 'incomplete evidence')
        sources, aliases, ids = {}, {}, {}
        for name, endpoint in base['endpoints'].items():
            desc = {'url': 'https://api.github.com/' + endpoint,
                    'api_version': base['api_version'], 'accept': 'application/vnd.github+json'}
            rid = descriptor(desc)
            ids[name] = rid
            sources[rid] = {'descriptor': desc, 'public_enrollment': {
                'basis': 'reviewed-public-source', 'privileged_visibility': False}}
            aliases[desc['url']] = rid
        aliases['https://api.github.com/repos/wez/wezterm/releases?per_page=100'] = ids['wezterm-list']
        manifest = {'sources': sources, 'aliases': aliases}
        rounds = {}
        for name, ev in evidence.items():
            require(ev['endpoints'] == base['endpoints'], 'evidence endpoint mismatch')
            attempts = []
            for endpoint, response in ev['responses'].items():
                raw = saved(name, endpoint + '.json')
                require(digest(raw) == response['sha256'] and len(raw) == response['body_bytes'], 'evidence integrity')
                rid = ids[endpoint]
                attempts.append({'request_id': rid, 'descriptor': sources[rid]['descriptor'],
                    'status': 200, 'body': raw, 'headers': response['headers'],
                    'at': ev['finished_at'], 'timing_basis': 'saved-round-completion-upper-bound'})
            rounds[name] = attempts
    results = []
    def check(name, condition):
        require(condition, 'scenario failed: ' + name)
        results.append({'scenario': name, 'result': 'passed'})
    def refuses(name, operation):
        try:
            operation()
        except (ValueError, KeyError, TypeError, subprocess.CalledProcessError):
            results.append({'scenario': name, 'result': 'refused as expected'})
        else:
            raise ValueError('scenario did not refuse: ' + name)
    revision = base['source_revision']
    a, _ = apply(None, manifest, rounds['baseline'], base['finished_at'], revision, '40500475496')
    b, _ = apply(a, manifest, rounds['hour'], evidence['hour']['finished_at'], revision, '40508899451')
    for name, tree in [('baseline', a), ('hour', b)]:
        for attempt in rounds[name]:
            check(name + ' exact bytes ' + attempt['request_id'][:8],
                  tree['bodies/' + attempt['request_id'] + '.json'] == attempt['body'])
    rid = ids['obsidian-list']
    desc = sources[rid]['descriptor']
    later = '2026-10-27T14:00:00+00:00'
    def attempt(status, **kwargs):
        return {'request_id': rid, 'descriptor': desc, 'status': status, 'at': later,
                'timing_basis': 'response-completed', 'headers': {}, **kwargs}
    def advance(previous=b, manifest_value=manifest, batch=None):
        return apply(previous, manifest_value, batch or [], later, revision, 'synthetic-offline')[0]
    before = validate(b)['entries'][rid]
    conditional = attempt(304, condition={'etag': before['validators']['etag']})
    c = advance(batch=[conditional])
    observed = validate(c)['entries'][rid]
    check('304 preserves body and received time, advances validation',
          c['bodies/' + rid + '.json'] == b['bodies/' + rid + '.json'] and
          observed['observation']['received_at'] == before['observation']['received_at'] and
          observed['observation']['validated_at'] == later and observed['validators'] == before['validators'])
    check('304 headers do not inherit old quota/date', observed['latest_attempt']['headers'] == {})
    refuses('304 without condition', lambda: advance(batch=[attempt(304)]))
    refuses('304 wrong condition', lambda: advance(batch=[attempt(304, condition={'etag': 'wrong'})]))
    refuses('304 no prior observation', lambda: advance(previous=None, batch=[conditional]))
    missing = dict(b); del missing['bodies/' + rid + '.json']
    refuses('304 missing bytes', lambda: advance(previous=missing, batch=[conditional]))
    wrong = copy.deepcopy(conditional); wrong['descriptor'] = {**desc, 'url': desc['url'] + '?page=2'}
    refuses('304 mismatched descriptor', lambda: advance(batch=[wrong]))
    for status, headers in [(None, {}), (429, {}), (503, {}), (403, {'x-ratelimit-remaining': '0'}), (403, {'retry-after': '60'})]:
        entry = validate(advance(batch=[attempt(status, headers=headers)]))['entries'][rid]
        check('temporary ' + str(status) + str(headers), entry['observation'] == before['observation'] and entry['availability'] == 'available')
    for status in (404, 410, 301, 401, 403):
        tree = advance(batch=[attempt(status, headers={'location': 'https://example.invalid/'})])
        entry = validate(tree)['entries'][rid]
        check('refusal ' + str(status), entry['availability'] == 'unavailable' and entry['observation'] == before['observation'])
        check('temporary failure does not clear refusal ' + str(status),
              validate(advance(previous=tree, batch=[attempt(503)]))['entries'][rid]['availability'] == 'unavailable')
    for name, raw in [('invalid JSON', b'{'), ('wrong shape', b'{}'), ('draft', b'[{"id":1,"tag_name":"v1","assets":[],"draft":true}]'),
                      ('oversized', b' ' * (MAX_BODY + 1)), ('duplicate key', b'{"id":1,"id":2}')]:
        entry = validate(advance(batch=[attempt(200, body=raw)]))['entries'][rid]
        check(name, entry['availability'] == 'unavailable' and entry['observation'] == before['observation'])
    empty = advance(batch=[attempt(200, body=b'[]\n', headers={'authorization': 'MUST-NOT-PERSIST', 'set-cookie': 'secret'})])
    check('empty list replaces old body', empty['bodies/' + rid + '.json'] == b'[]\n')
    check('sensitive headers discarded', b'MUST-NOT-PERSIST' not in empty['index.json'] and b'secret' not in empty['index.json'])
    check('not attempted stays unchanged', validate(advance())['entries'] == validate(b)['entries'])
    unknown = advance(previous=None, batch=[attempt(503)])
    check('new failed source stays unknown', validate(unknown)['entries'][rid]['availability'] == 'unknown')
    retired_manifest = copy.deepcopy(manifest)
    del retired_manifest['sources'][rid]
    retired_manifest['aliases'] = {a: r for a, r in aliases.items() if r != rid}
    retired = advance(manifest_value=retired_manifest)
    check('retirement retains alias tombstone', validate(retired)['entries'][rid]['availability'] == 'retired' and validate(retired)['aliases'][desc['url']] == rid)
    changed = copy.deepcopy(manifest)
    changed_desc = {**desc, 'url': desc['url'] + '?page=2'}
    changed_id = descriptor(changed_desc)
    del changed['sources'][rid]
    changed['sources'][changed_id] = {**sources[rid], 'descriptor': changed_desc}
    changed['aliases'] = {a: (changed_id if r == rid else r) for a, r in aliases.items()}
    replaced = advance(manifest_value=changed)
    check('changed target gets no validators', validate(replaced)['entries'][changed_id]['validators'] == {})
    refuses('changed target cannot reuse 304', lambda: advance(previous=replaced, manifest_value=changed, batch=[
        {**conditional, 'request_id': changed_id, 'descriptor': changed_desc}]))
    for name, mutate in [
        ('bad manifest hash', lambda i: i.update(manifest_sha256='0' * 64)),
        ('unknown schema', lambda i: i.update(schema_version=2)),
        ('unsafe body path', lambda i: i['entries'][rid]['observation'].update(path='../outside')),
        ('wrong body hash', lambda i: i['entries'][rid]['observation'].update(sha256='0' * 64)),
        ('contradictory times', lambda i: i['entries'][rid]['observation'].update(received_at='2099-01-01T00:00:00+00:00')),
        ('alias identity', lambda i: i['aliases'].update({'https://api.github.com/repos/a/b/releases': '0'*64}))]:
        bad = dict(b); index = decode(bad['index.json']); mutate(index); bad['index.json'] = canonical(index)
        refuses(name, lambda bad=bad: validate(bad))
    for name, mutation in [('unenrolled', lambda m: m['sources'][rid].pop('public_enrollment')),
                           ('privileged visibility', lambda m: m['sources'][rid]['public_enrollment'].update(privileged_visibility=True)),
                           ('unreviewed host', lambda m: m['sources'][rid]['descriptor'].update(url='https://example.org/releases'))]:
        bad = copy.deepcopy(manifest); mutation(bad)
        refuses(name, lambda bad=bad: advance(manifest_value=bad))
    refuses('duplicate manifest keys', lambda: decode(b'{"aliases":{},"aliases":{}}'))
    refuses('unexpected file', lambda: validate({**b, 'extra': b'x'}))
    root = out / 'candidate'
    for path, raw in b.items():
        target = root / path; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(raw)
    check('disk round trip', read_tree(root) == b)
    (root / 'link').symlink_to('/dev/null')
    refuses('symlink', lambda: read_tree(root)); (root / 'link').unlink()
    (root / 'index.json').chmod(0o755)
    refuses('executable mode', lambda: read_tree(root)); (root / 'index.json').chmod(0o644)
    repo = out / 'PROTOTYPE-publication'; repo.mkdir()
    git(repo, 'init', '--quiet', '--template=')
    git(repo, 'config', 'gc.auto', '0')
    git(repo, 'config', 'user.name', 'Offline storage prototype')
    git(repo, 'config', 'user.email', 'prototype@invalid')
    def pack_bytes():
        return sum(p.stat().st_size for p in (repo / '.git/objects/pack').iterdir() if p.is_file())
    def sizes(tree):
        return {'body_bytes': sum(len(v) for k, v in tree.items() if k.startswith('bodies/')),
                'index_bytes': len(tree['index.json']),
                'loose_object_file_bytes': sum(p.stat().st_size for d in (repo / '.git/objects').iterdir()
                    if d.is_dir() and re.fullmatch('[0-9a-f]{2}', d.name) for p in d.iterdir() if p.is_file()),
                'git_objects': git(repo, 'count-objects', '-v')}
    ca = publish(repo, a, None); sa = sizes(a)
    git(repo, 'repack', '-adf', '--window=10', '--depth=50'); git(repo, 'prune-packed'); pa = git(repo, 'count-objects', '-v'); pa_bytes = pack_bytes()
    cb = publish(repo, b, ca); sb = sizes(b)
    git(repo, 'gc', '--prune=now'); incremental_gc_bytes = pack_bytes()
    git(repo, 'repack', '-adf', '--window=10', '--depth=50'); git(repo, 'prune-packed'); pb = git(repo, 'count-objects', '-v'); pb_bytes = pack_bytes()
    old_bytes, _ = lookup(repo, desc['url'], ca)
    new_bytes, _ = lookup(repo, desc['url'], cb)
    check('commit A remains consistent after B', old_bytes == a['bodies/' + rid + '.json'] and old_bytes != new_bytes)
    refuses('stale parent publication', lambda: publish(repo, c, ca))
    check('stale parent leaves B intact', git(repo, 'rev-parse', 'refs/heads/publication') == cb)
    cr = publish(repo, retired, cb)
    refuses('retired lookup', lambda: lookup(repo, desc['url'], cr))
    git(repo, 'repack', '-adf', '--window=10', '--depth=50'); git(repo, 'prune-packed'); packed = git(repo, 'count-objects', '-v')
    report = {'question': 'Exact storage transitions and commit-pinned reads, offline only',
              'evidence_archive_sha256': digest(archive.read_bytes()),
              'timing_limit': 'saved-round-completion-upper-bound; never measured per-response completion',
              'enrollment_limit': 'explicit six-source offline fixture assertion, not automated public-visibility proof',
              'manifest': manifest, 'scenarios': results,
              'commits': {'baseline': ca, 'hour': cb, 'retired': cr},
              'sizes': {'baseline_before_gc': sa, 'baseline_packed': pa, 'baseline_pack_bytes': pa_bytes, 'hour_before_gc': sb,
                        'two_publications_packed': pb, 'hour_pack_bytes': pb_bytes,
                        'baseline_to_hour_pack_growth_bytes': pb_bytes - pa_bytes,
                        'two_publications_incremental_gc_pack_bytes': incremental_gc_bytes,
                        'three_publications_packed': packed},
              'limits': ['No freshness expiry policy in lookup', 'No remote/hosting/privilege-isolation claims',
                         'No fleet retention inference', 'Shape validation is deliberately minimal for six fixtures']}
    (out / 'report.json').write_bytes(canonical(report) + b'\n')
    (out / 'reviewed-manifest.json').write_bytes(canonical(manifest) + b'\n')
    print(json.dumps({'output': str(out), 'scenarios': len(results), 'sizes': report['sizes']}, indent=2))

if __name__ == '__main__':
    main()
