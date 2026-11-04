"""Explicit entry point for the inactive manual YAML workflow proposal.

No installed consumer integration; tokens are supplied only by the calling step.
"""
import hashlib
import os
from pathlib import Path
import subprocess
import sys

from collector import require
from storage import canonical, decode
from yaml_adapter import IncompleteBootstrap, list_plan
from yaml_delivery import fetch_prior, publish
from yaml_enrollment import shared_recipes
from yaml_staging import checked, collect_stage
from retention import parameters


def prepare(root, environ):
    context = {k[4:].lower():v for k,v in environ.items() if k.startswith('CTX_')}
    raw = (root/'docs/track/release-catalog/design/staged-manifest.json').read_bytes()
    policy_raw = (root/'tools/catalog-collector/yaml-policy.json').read_bytes()
    revision = subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
    checked(context,raw,revision,policy_raw)
    scope_raw = environ['YAML_SCOPE_JSON'].encode('utf-8')
    require(len(scope_raw) <= 64000, 'yaml_scope_bound')
    scope = decode(scope_raw)
    require(type(scope) is dict and set(scope) == {'sources','page_size','page_limit','reconcile'}
            and hashlib.sha256(canonical(scope)).hexdigest() == context['yaml_scope_sha256'],
            'unapproved_yaml_scope')
    require(scope['sources'] is None or type(scope['sources']) is list and
            all(type(rid) is str for rid in scope['sources']), 'invalid_source_subset')
    parameters(scope['page_size'],scope['page_limit'])
    require(type(scope['reconcile']) is bool and
            (not scope['reconcile'] or scope['page_limit'] == 'all'), 'invalid_yaml_scope')
    list_plan(raw,int(context['repository_id']),sources=scope['sources'],page_size=scope['page_size'])
    return context,raw,revision,policy_raw,scope


def run(mode, root, environ):
    require(mode in {'validate','collect','publish'}, 'invalid_yaml_workflow_mode')
    context,raw,revision,policy_raw,scope = prepare(root,environ)
    if mode == 'validate':
        return 0
    token = environ.pop('YAML_WORKFLOW_TOKEN').encode('ascii')
    scratch = Path(environ['RUNNER_TEMP'])
    if mode == 'publish':
        artifact_id = environ['YAML_ARTIFACT_ID']
        artifact_digest = environ['YAML_ARTIFACT_DIGEST']
        publish(context,raw,revision,policy_raw,shared_recipes(root),artifact_id,
                artifact_digest,token,scratch/'yaml-publication')
        return 0
    from supervised_transport import SupervisedTransport, Token
    from workflow_adapter import Clock
    repo = scratch/'yaml-prior'
    fetch_prior(context,raw,revision,policy_raw,token,repo)
    credential = Token(token)
    def transport(value):
        return SupervisedTransport(value,workflow_identity=int(context['repository_id']),
            source_revision=revision,approved_revision=context['approved_revision'])
    try:
        report = collect_stage(context,raw,revision,policy_raw,shared_recipes(root),
            transport,Clock(),credential,scratch/'yaml-staging',repo=repo,**scope)
    except IncompleteBootstrap as failure:
        print(canonical(failure.report).decode('utf-8'))
        return 1
    print(canonical(report).decode('utf-8'))
    return 0 if not report['not_attempted_repositories'] and all(
        status == 'ok' for status in report['sources'].values()) else 1


if __name__ == '__main__':
    require(len(sys.argv) == 2, 'invalid_yaml_workflow_mode')
    raise SystemExit(run(sys.argv[1],Path.cwd(),os.environ))
