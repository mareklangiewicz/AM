"""Inactive workflow proposal support. No command-line entry point or token lookup.

Only the separately reviewed workflow artifact calls run(), supplying its step token.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import time

from collector import Descriptor, Source, collect, plan, require
from supervised_transport import SupervisedTransport, Token


def load_manifest(raw, workflow_identity):
    require(type(raw) is bytes and len(raw) <= 64_000, 'invalid_manifest')
    obj = json.loads(raw)
    require(type(obj) is dict and obj.get('schema') == 1 and
            type(obj.get('sources')) is list and len(obj['sources']) == 6, 'invalid_manifest')
    sources = []
    for row in obj['sources']:
        require(type(row) is dict and type(row.get('repository_id')) is int and
                row['repository_id'] > 0 and type(row.get('url')) is str and
                type(row.get('identity_evidence')) is str, 'unenrolled_source')
        desc = Descriptor(row['url'])
        require(row.get('request_id') == desc.request_id, 'manifest_request_id_mismatch')
        require(type(row.get('aliases')) is list, 'invalid_aliases')
        sources.append(Source(desc, row['repository_id'], row['identity_evidence'],
                              tuple(row['aliases'])))
    return plan(tuple(sources), workflow_identity)


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
    return load_manifest(raw, int(context['repository_id']))


class Clock:
    utcnow = staticmethod(lambda: datetime.now(timezone.utc))
    monotonic = staticmethod(time.monotonic)


def run(context, raw, actual_revision, token, output):
    value = preflight(context, raw, actual_revision)
    transport = SupervisedTransport(value, workflow_identity=int(context['repository_id']),
                                    source_revision=actual_revision,
                                    approved_revision=context['approved_revision'])
    credential = Token(token)
    attempts, report = collect(value, transport, Clock(), credential,
                               workflow_identity=int(context['repository_id']))
    directory = Path(output)
    directory.mkdir(parents=True, exist_ok=False)
    for attempt in attempts:
        body = attempt.pop('body')
        attempt['body_bytes'] = len(body)
        attempt['body_sha256'] = hashlib.sha256(body).hexdigest()
        if attempt['outcome'] == 'response':
            (directory / (attempt['request_id'] + '.body')).write_bytes(body)
    (directory / 'report.json').write_text(json.dumps({
        'context': context, 'run': report, 'attempts': attempts,
        'interpretation': 'Complete transfer is not release validation or publication approval.'
    }, indent=2) + '\n')
    return report['complete'] and all(a['status'] == 200 for a in attempts)
