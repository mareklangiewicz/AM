"""Pure observation storage. No network, Git, filesystem or credential access."""
import copy
from dataclasses import asdict
import hashlib
import json
import re

from collector import BODY_CAP, Descriptor, selected_headers, timestamp, require
from manifest import load_manifest

INDEX_CAP = 2_000_000
TREE_CAP = 50_000_000
SCHEMA = 1


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode('utf-8')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def decode(raw):
    def pairs(items):
        obj = {}
        for key, value in items:
            require(key not in obj, 'duplicate_json_key')
            obj[key] = value
        return obj
    def constant(_):
        raise ValueError('nonfinite_json')
    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
    except (ValueError, TypeError, UnicodeError, RecursionError):
        raise ValueError('invalid_json') from None


def content(raw, descriptor):
    require(type(raw) is bytes and len(raw) <= BODY_CAP, 'invalid_body')
    value = decode(raw)
    is_list = descriptor['url'].split('?', 1)[0].endswith('/releases')
    require(type(value) is (list if is_list else dict), 'invalid_release_shape')
    for release in value if is_list else [value]:
        require(type(release) is dict and type(release.get('id')) is int and
                release['id'] > 0 and type(release.get('tag_name')) is str and
                release['draft'] is False and type(release.get('assets')) is list and
                type(release.get('published_at')) is str, 'nonpublic_or_invalid_release')
        timestamp(release['published_at'])
        for asset in release['assets']:
            require(type(asset) is dict and type(asset.get('id')) is int and asset['id'] > 0
                    and type(asset.get('name')) is str, 'invalid_asset')
    return value


def public_headers(values):
    require(type(values) is dict, 'invalid_headers')
    selected = selected_headers(tuple(values.items()))
    require(selected == values, 'unselected_header')
    return selected


def validators(values):
    require(type(values) is dict and set(values) <= {'etag', 'last-modified'},
            'invalid_validators')
    public_headers(values)
    require(all(0 < len(v.encode()) <= 8192 for v in values.values()), 'invalid_validators')


def validate_index(index_raw):
    """Validate all metadata without fetching bodies; lengths bound the closed tree."""
    require(type(index_raw) is bytes and len(index_raw) <= INDEX_CAP, 'index_bound')
    index = decode(index_raw)
    require(type(index) is dict and set(index) == {
        'schema_version', 'generated_at', 'manifest_json', 'manifest_sha256',
        'collector_revision', 'run', 'workflow_repository_id', 'aliases', 'entries'}, 'index_fields')
    require(type(index['schema_version']) is int and index['schema_version'] == SCHEMA, 'schema')
    require(type(index['manifest_json']) is str, 'invalid_manifest')
    raw = index['manifest_json'].encode('utf-8')
    require(digest(raw) == index['manifest_sha256'], 'manifest_digest')
    plan = load_manifest(raw, index['workflow_repository_id'])
    generated = timestamp(index['generated_at'])
    require(type(index['collector_revision']) is str and
            re.fullmatch('[0-9a-f]{40}', index['collector_revision']), 'invalid_revision')
    require(type(index['run']) is dict and set(index['run']) == {'id', 'attempt'} and
            all(type(v) is str and re.fullmatch('[1-9][0-9]*', v)
                for v in index['run'].values()), 'invalid_run')
    require(type(index['entries']) is dict and type(index['aliases']) is dict, 'index_fields')
    active = {r.source.descriptor.request_id: r.source for r in plan.requests}
    declared_bytes = len(index_raw)
    for rid, entry in index['entries'].items():
        require(type(entry) is dict and set(entry) == {
            'descriptor', 'repository_id', 'availability', 'observation', 'validators', 'latest_attempt'},
            'entry_fields')
        require(type(entry['descriptor']) is dict and set(entry['descriptor']) ==
                {'url', 'api_version', 'accept'}, 'invalid_descriptor')
        descriptor = Descriptor(**entry['descriptor'])
        require(type(entry['repository_id']) is int and entry['repository_id'] > 0 and
                entry['repository_id'] != index['workflow_repository_id'], 'invalid_repository_id')
        descriptor.validate(entry['repository_id'])
        require(descriptor.url.startswith(f'https://api.github.com/repositories/{entry["repository_id"]}/releases')
                and descriptor.request_id == rid, 'entry_identity')
        require(entry['availability'] in {'available', 'unavailable', 'unknown', 'retired'}, 'availability')
        require((rid in active) == (entry['availability'] != 'retired'), 'retirement_mismatch')
        if rid in active:
            require(descriptor == active[rid].descriptor and entry['repository_id'] ==
                    active[rid].repository_id, 'manifest_descriptor')
        validators(entry['validators'])
        latest = entry['latest_attempt']
        if latest is not None:
            require(type(latest) is dict and set(latest) == {
                'request_started_at', 'response_completed_at', 'attempt_finished_at',
                'status', 'outcome', 'headers'}, 'attempt_fields')
            require(type(latest['outcome']) is str and latest['outcome'] in {
                'observed', 'validated', 'temporary_error', 'refused', 'invalid_body'}, 'attempt_outcome')
            start, finish = timestamp(latest['request_started_at']), timestamp(latest['attempt_finished_at'])
            require(start <= finish <= generated, 'attempt_chronology')
            if latest['response_completed_at'] is not None:
                require(start <= timestamp(latest['response_completed_at']) <= finish, 'completion_chronology')
            require(latest['status'] is None or type(latest['status']) is int and
                    200 <= latest['status'] <= 599, 'invalid_status')
            public_headers(latest['headers'])
            if latest['outcome'] in {'observed', 'validated'}:
                require(latest['status'] == (200 if latest['outcome'] == 'observed' else 304) and
                        latest['response_completed_at'] is not None, 'attempt_outcome_conflict')
        obs = entry['observation']
        if obs is not None:
            require(type(obs) is dict and set(obs) == {
                'path', 'sha256', 'bytes', 'received_at', 'validated_at', 'validation_status',
                'received_time_basis', 'validation_time_basis', 'scope', 'link'}, 'observation_fields')
            path = f'bodies/{rid}.json'
            require(obs['path'] == path and obs['scope'] == 'single-response' and
                    type(obs['validation_status']) is int and obs['validation_status'] in {200, 304}
                    and obs['received_time_basis'] == obs['validation_time_basis'] == 'response-completed',
                    'observation_provenance')
            require(timestamp(obs['received_at']) <= timestamp(obs['validated_at']) <= generated,
                    'observation_chronology')
            require(latest is not None and timestamp(obs['validated_at']) <=
                    timestamp(latest['attempt_finished_at']), 'observation_attempt_chronology')
            require(type(obs['bytes']) is int and 0 <= obs['bytes'] <= BODY_CAP and
                    type(obs['sha256']) is str and re.fullmatch('[0-9a-f]{64}', obs['sha256']),
                    'body_metadata')
            declared_bytes += obs['bytes']
            require(declared_bytes <= TREE_CAP, 'tree_bound')
            require(obs['link'] is None or type(obs['link']) is str and len(obs['link'].encode()) <= 8192,
                    'invalid_link')
            if latest['outcome'] in {'observed', 'validated'}:
                require(obs['validated_at'] == latest['response_completed_at'] and
                        obs['validation_status'] == latest['status'], 'validation_provenance_conflict')
        require(entry['availability'] != 'available' or obs is not None, 'missing_observation')
        require(obs is not None or entry['validators'] == {}, 'validator_without_body')
    require(set(active) <= set(index['entries']), 'missing_entry')
    wanted = {}
    for rid, source in active.items():
        for alias in (source.descriptor.url, *source.aliases):
            wanted[alias] = rid
    for alias, target in index['aliases'].items():
        require(type(target) is dict and set(target) == {'request_id', 'active'} and
                type(target['active']) is bool and target['request_id'] in index['entries'], 'invalid_alias')
        Descriptor(alias).validate(index['entries'][target['request_id']]['repository_id'])
        require(target['active'] == (alias in wanted) and
                (alias not in wanted or wanted[alias] == target['request_id']), 'alias_state')
    require(all(index['aliases'].get(a) == {'request_id': rid, 'active': True}
                for a, rid in wanted.items()), 'missing_alias')
    return index


def validate(tree):
    """Validate a closed immutable-byte tree, including every retained body."""
    require(type(tree) is dict and all(type(k) is str and type(v) is bytes
                                      for k, v in tree.items()), 'invalid_tree')
    require('index.json' in tree and sum(map(len, tree.values())) <= TREE_CAP, 'tree_bound')
    index = validate_index(tree['index.json'])
    expected = {'index.json'}
    for entry in index['entries'].values():
        obs = entry['observation']
        if obs is not None:
            path = obs['path']
            require(path in tree and len(tree[path]) == obs['bytes'] and
                    digest(tree[path]) == obs['sha256'], 'body_integrity')
            content(tree[path], entry['descriptor'])
            expected.add(path)
    require(set(tree) == expected, 'unexpected_file')
    return index


def apply(previous_tree, manifest_raw, attempts, *, workflow_identity, generated_at, revision, run):
    """Apply inert collector results atomically; do not mutate any caller input."""
    plan = load_manifest(manifest_raw, workflow_identity)
    generated = timestamp(generated_at)
    old = validate(previous_tree) if previous_tree is not None else None
    if old:
        require(old['workflow_repository_id'] == workflow_identity and
                timestamp(old['generated_at']) <= generated, 'previous_provenance')
    tree = dict(previous_tree or {})
    entries = copy.deepcopy(old['entries']) if old else {}
    aliases = copy.deepcopy(old['aliases']) if old else {}
    active = {r.source.descriptor.request_id: r.source for r in plan.requests}
    for target in aliases.values():
        target['active'] = False
    for rid, entry in entries.items():
        if rid not in active:
            entry['availability'] = 'retired'
    for rid, source in active.items():
        require(rid not in entries or entries[rid]['availability'] != 'retired', 'reenrollment_review_required')
        entries.setdefault(rid, dict(descriptor=asdict(source.descriptor), repository_id=source.repository_id,
                                     observation=None, validators={}, latest_attempt=None, availability='unknown'))
        for alias in (source.descriptor.url, *source.aliases):
            aliases[alias] = {'request_id': rid, 'active': True}
    require(type(attempts) is list and len(attempts) <= 6, 'invalid_batch')
    seen, report = set(), []
    for attempt in attempts:
        require(type(attempt) is dict and set(attempt) == {
            'request_id', 'descriptor', 'repository_id', 'request_started_at', 'response_completed_at',
            'attempt_finished_at', 'status', 'headers', 'body', 'condition', 'outcome'}, 'attempt_fields')
        rid = attempt['request_id']
        require(rid in active and rid not in seen, 'unknown_or_duplicate_attempt')
        seen.add(rid)
        entry = entries[rid]
        require(attempt['descriptor'] == entry['descriptor'] and type(attempt['repository_id']) is int
                and attempt['repository_id'] == entry['repository_id'], 'attempt_identity')
        start = timestamp(attempt['request_started_at'])
        finish = timestamp(attempt['attempt_finished_at'])
        require(start <= finish <= generated, 'attempt_chronology')
        if entry['latest_attempt']:
            require(timestamp(entry['latest_attempt']['attempt_finished_at']) <= start, 'out_of_order_attempt')
        headers = public_headers(attempt['headers'])
        status = attempt['status']
        require(status is None or type(status) is int and 200 <= status <= 599, 'invalid_status')
        require(type(attempt['body']) is bytes and len(attempt['body']) <= BODY_CAP, 'invalid_body')
        condition = attempt['condition']; validators(condition)
        require(type(attempt['outcome']) is str and attempt['outcome'] in {
            'response', 'transport_error', 'timeout', 'protocol_refusal', 'clock_refusal', 'truncated_response'},
            'invalid_outcome')
        complete = attempt['outcome'] == 'response'
        completed_at = attempt['response_completed_at']
        require(complete == (completed_at is not None), 'completion_provenance')
        if complete:
            require(status is not None and start <= timestamp(completed_at) <= finish, 'completion_chronology')
            require('content-length' not in headers or status == 304 or
                    headers['content-length'] == str(len(attempt['body'])), 'body_length')
        else:
            require(not attempt['body'], 'partial_body_not_discarded')
        outcome = 'temporary_error'
        if not complete:
            if attempt['outcome'] in {'protocol_refusal', 'clock_refusal'}:
                entry['availability'], outcome = 'unavailable', 'refused'
        elif status == 200:
            require(not condition or entry['observation'] is not None and condition == entry['validators'],
                    'condition_prior_mismatch')
            try:
                content(attempt['body'], entry['descriptor'])
            except (ValueError, KeyError, TypeError):
                entry['availability'], outcome = 'unavailable', 'invalid_body'
            else:
                path = f'bodies/{rid}.json'
                tree[path] = attempt['body']
                entry['observation'] = dict(path=path, sha256=digest(attempt['body']), bytes=len(attempt['body']),
                    received_at=completed_at, validated_at=completed_at, validation_status=200,
                    received_time_basis='response-completed', validation_time_basis='response-completed',
                    scope='single-response', link=headers.get('link'))
                entry['validators'] = {k: v for k, v in headers.items() if k in {'etag', 'last-modified'}}
                entry['availability'], outcome = 'available', 'observed'
        elif status == 304:
            require(entry['availability'] == 'available' and entry['observation'] is not None and
                    condition and condition == entry['validators'] and not attempt['body'], 'invalid_304')
            entry['observation']['validated_at'] = completed_at
            entry['observation']['validation_status'] = 304
            entry['validators'].update({k: v for k, v in headers.items() if k in {'etag', 'last-modified'}})
            outcome = 'validated'
        elif status == 429 or status >= 500 or status == 403 and (
                headers.get('x-ratelimit-remaining') == '0' or 'retry-after' in headers):
            pass
        else:
            entry['availability'], outcome = 'unavailable', 'refused'
        entry['latest_attempt'] = {k: attempt[k] for k in (
            'request_started_at', 'response_completed_at', 'attempt_finished_at', 'status', 'headers')}
        entry['latest_attempt']['outcome'] = outcome
        report.append(dict(request_id=rid, outcome=outcome, availability=entry['availability']))
    tree['index.json'] = canonical(dict(schema_version=SCHEMA, generated_at=generated_at,
        manifest_json=manifest_raw.decode('utf-8'), manifest_sha256=digest(manifest_raw),
        collector_revision=revision, run=run, workflow_repository_id=workflow_identity,
        aliases=aliases, entries=entries)) + b'\n'
    validate(tree)
    return tree, report
