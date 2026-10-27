"""Manual workflow collection and validated candidate staging. No command-line entry point or token lookup.

The reviewed manual workflow calls run(), supplying only its step token.
"""
from datetime import datetime, timezone
import hashlib
import json
import platform
from pathlib import Path
import re
import time

from collector import collect, require, plan, Prior, timestamp
from manifest import load_manifest
from supervised_transport import SupervisedTransport, Token


def preflight(context, raw, actual_revision):
    require(context.get('repository') == 'mareklangiewicz/AM' and
            context.get('event') == 'workflow_dispatch' and
            context.get('ref') == 'refs/heads/main-marek', 'unapproved_context')
    for key in ('repository_id', 'run_id', 'run_attempt'):
        require(type(context.get(key)) is str and
                re.fullmatch(r'[1-9][0-9]*', context[key]), 'invalid_context')
    for key in ('sha', 'workflow_sha', 'approved_revision'):
        require(type(context.get(key)) is str and
                re.fullmatch(r'[0-9a-f]{40}', context[key]), 'invalid_revision')
    require(actual_revision == context['sha'] == context['workflow_sha'] ==
            context['approved_revision'], 'unapproved_revision')
    require(type(context.get('manifest_sha256')) is str and
            re.fullmatch(r'[0-9a-f]{64}', context['manifest_sha256']) and
            hashlib.sha256(raw).hexdigest() == context['manifest_sha256'], 'unapproved_manifest')
    pin = context.get('previous_publication', '')
    require(type(pin) is str and (pin == '' or re.fullmatch('[0-9a-f]{40}', pin)), 'invalid_prior_pin')
    return load_manifest(raw, int(context['repository_id']))


class Clock:
    utcnow = staticmethod(lambda: datetime.now(timezone.utc))
    monotonic = staticmethod(time.monotonic)


def prepare(context, raw, actual_revision, previous_tree=None):
    value = preflight(context, raw, actual_revision)
    from storage import validate
    previous = validate(previous_tree) if previous_tree is not None else None
    if not previous:
        require(context.get('previous_publication', '') == '', 'missing_pinned_prior')
        return value
    require(type(context.get('previous_publication')) is str and
            re.fullmatch('[0-9a-f]{40}', context['previous_publication']), 'missing_prior_pin')
    require(previous['workflow_repository_id'] == int(context['repository_id']) and
            timestamp(previous['generated_at']) <= Clock.utcnow(), 'invalid_prior_context')
    priors = {}
    for request in value.requests:
        source = request.source; rid = source.descriptor.request_id
        entry = previous['entries'].get(rid)
        if entry and entry['availability'] == 'available':
            obs = entry['observation']
            require(timestamp(obs['validated_at']) <= Clock.utcnow(), 'future_prior')
            priors[rid] = Prior(source.descriptor, previous_tree[obs['path']], obs['sha256'],
                                obs['validated_at'], tuple(entry['validators'].items()))
    return plan(tuple(r.source for r in value.requests), int(context['repository_id']), priors)


def run(context, raw, actual_revision, token, output, *, previous_tree=None):
    value = prepare(context, raw, actual_revision, previous_tree)
    transport = SupervisedTransport(value, workflow_identity=int(context['repository_id']),
                                    source_revision=actual_revision,
                                    approved_revision=context['approved_revision'])
    credential = Token(token)
    attempts, report = collect(value, transport, Clock(), credential,
                               workflow_identity=int(context['repository_id']))
    directory = Path(output)
    directory.mkdir(parents=True, exist_ok=False)
    evidence = []
    for attempt in attempts:
        body = attempt['body']
        evidence.append({**{k: v for k, v in attempt.items() if k != 'body'},
                         'body_bytes': len(body), 'body_sha256': hashlib.sha256(body).hexdigest()})
        if attempt['outcome'] == 'response':
            (directory / (attempt['request_id'] + '.body')).write_bytes(body)
    (directory / 'report.json').write_text(json.dumps({
        'context': context, 'run': report, 'attempts': evidence,
        'runtime': {'python': platform.python_version(), 'system': platform.system()},
        'interpretation': 'Complete transfer is not release validation or publication approval.'
    }, indent=2) + '\n')
    from storage import apply
    try:
        tree, transitions = apply(previous_tree, raw, attempts, workflow_identity=int(context['repository_id']),
            generated_at=Clock.utcnow().isoformat(), revision=actual_revision,
            run={'id': context['run_id'], 'attempt': context['run_attempt']})
    except (ValueError, TypeError, KeyError):
        (directory / 'storage-report.json').write_text('{"outcome":"storage_refusal"}\n')
        return False
    candidate = directory / 'candidate'
    candidate.mkdir()
    for path, data in tree.items():
        target = candidate / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    (directory / 'storage-report.json').write_text(json.dumps({
        'outcome': 'validated_candidate', 'transitions': transitions,
        'files': {p: {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
                  for p, data in tree.items()}
    }, indent=2) + '\n')
    return (report['complete'] and all(a['status'] in {200, 304} for a in attempts)
            and all(t['outcome'] in {'observed', 'validated'} for t in transitions))
