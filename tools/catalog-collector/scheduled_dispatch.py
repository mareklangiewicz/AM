"""Hourly pilot controller; dispatches existing guarded workflow once.

The installed schedule requires an approved source revision and bounded window.
No upstream collection, publication credential or Git checkout occurs here.
"""
from datetime import datetime, timezone
import json
import os
import re
import subprocess
import time

from collector import require

REPOSITORY = 'mareklangiewicz/AM'
WORKFLOW = 'catalog-collector.yml'
MANIFEST = '1c550b882e9855a7a652e44516d88db95046641da92f4b6e34fd65b9a6da87b9'
CRON = '17 * * * *'


def command(args):
    # Control API responses only; never print credentials or subprocess diagnostics.
    result = subprocess.run(['gh', *args], capture_output=True, timeout=30)
    require(result.returncode == 0 and len(result.stdout) <= 1_000_000,
            'schedule_command_refused')
    return result.stdout


def dispatch(context, *, now=None, execute=command):
    require(context.get('repository') == REPOSITORY and
            context.get('event') == 'schedule' and context.get('schedule') == CRON and
            context.get('ref') == 'refs/heads/main-marek' and
            context.get('run_attempt') == '1', 'unapproved_schedule_context')
    revision = context.get('approved_revision', '')
    require(re.fullmatch('[0-9a-f]{40}', revision) is not None and
            context.get('sha') == context.get('workflow_sha') == revision,
            'unapproved_schedule_revision')
    start, end = context.get('start', ''), context.get('until', '')
    require(re.fullmatch('[0-9]{10}', start) is not None and
            re.fullmatch('[0-9]{10}', end) is not None, 'invalid_schedule_window')
    start, end = int(start), int(end)
    require(0 < end-start <= 86400, 'invalid_schedule_window')
    now = time.time() if now is None else now
    require(start <= now < end, 'inactive_schedule_window')

    def api(path):
        route = f'repos/{REPOSITORY}' + ('/'+path if path else '')
        return json.loads(execute(['api', route]))

    # Refuse drift and overlap before resolving a parent or submitting any run.
    repository = api('')
    require(repository['default_branch'] == 'main-marek', 'changed_default_branch')
    source = api('git/ref/heads/main-marek')['object']['sha']
    require(source == revision, 'schedule_source_moved')
    workflows = api('actions/workflows')
    require(workflows['total_count'] == len(workflows['workflows']) and
            {w['path'] for w in workflows['workflows'] if w['state'] == 'active'} ==
            {'.github/workflows/catalog-collector.yml',
             '.github/workflows/catalog-schedule.yml'}, 'unexpected_active_workflow')
    runs = api(f'actions/workflows/{WORKFLOW}/runs?per_page=100')
    # Recent API ordering cannot prove no arbitrarily old active run. The actual
    # collector concurrency and exact-prior checks remain the authoritative guard.
    require(not any(r['status'] != 'completed' for r in runs['workflow_runs']),
            'collector_already_active')
    since = datetime.fromtimestamp(start, timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    window_runs = api(f'actions/workflows/{WORKFLOW}/runs?per_page=1&created=%3E%3D{since}')
    require(type(window_runs['total_count']) is int and
            0 <= window_runs['total_count'] < 24, 'schedule_run_budget_exhausted')
    parent = api('git/ref/heads/release-catalog')['object']['sha']
    require(re.fullmatch('[0-9a-f]{40}', parent) is not None, 'invalid_schedule_prior')
    # Recheck the window immediately before dispatch after bounded API IO.
    current = time.time() if context.get('_live_clock') else now
    require(start <= current < end, 'inactive_schedule_window')
    execute(['workflow', 'run', WORKFLOW, '--repo', REPOSITORY,
             '--ref', 'main-marek', '-f', 'approved_revision='+revision,
             '-f', 'manifest_sha256='+MANIFEST, '-f', 'previous_publication='+parent])
    return {'outcome': 'dispatch_submitted', 'approved_revision': revision,
            'previous_publication': parent, 'window_until': end}


if __name__ == '__main__':
    context = {k[4:].lower(): v for k, v in os.environ.items() if k.startswith('CTX_')}
    context['_live_clock'] = True
    print(json.dumps(dispatch(context)))
