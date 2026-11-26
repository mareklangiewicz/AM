"""One collector run: read GitHub, then commit catalog/ to main-marek.

    catalog_run.py collect --checkout DIR --output CANDIDATE --run-id N --attempt N [--evidence DIR]
    catalog_run.py publish --candidate CANDIDATE --remote URL --scratch DIR --run-id N --attempt N

collect runs without write access. It reads catalog/ from a checkout of
main-marek: the apps in apps.yaml are enrolled, each through the repository
file it points to. It reads the repositories whose data is oldest (never-read
and newest-failure counted by the newer of observed_at and failed_at), and
writes a candidate: the documents it changed under catalog/ (apps.yaml with
fresh labels, never another set of apps), removed.json (repository files no
app points to) and run.json (this run's summary).

publish checks every candidate document with the host's reader
(modules/catalog-parser.am), then commits catalog/ on top of main-marek's tip
and pushes. A push rejected by a newer commit is redone on the new tip, at
most PUSH_ATTEMPTS times. Marek's commits touch catalog/ only to enroll or
drop apps (an apps.yaml entry, a never-read repository file): when the tip's
apps differ from those collect read, the tip's apps.yaml stays and nothing is
removed. A candidate that fails validation commits only
its run summary, with stop_reason internal, and leaves the facts as they were.
"""
import argparse
import json
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

import documents
import host_catalog

ROOT = Path(__file__).resolve().parents[2]
BRANCH = 'main-marek'
PUSH_ATTEMPTS = 5
BATCH_SIZE = 500
LOADER = getattr(yaml, 'CSafeLoader', yaml.SafeLoader)
# host_catalog's stop reasons, when they stopped a run before every selected repository was read.
STOPS = {'request_limit': 'request_budget', 'byte_limit': 'byte_budget', 'time_limit': 'time_budget',
         'primary_rate_reserve': 'quota', 'http_401': 'authentication', 'http_403': 'quota', 'http_429': 'quota'}


def utc():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def attempted_at(top):
    """When this repository was last tried: the newer of its last read and its latest failure."""
    return max(top.get('observed_at', ''), top.get('failed_at', ''))


def load(path):
    document = yaml.load(path.read_text(encoding='utf-8'), Loader=LOADER)
    document.pop('$schema')
    return document


def collect(args):
    started = time.monotonic()
    checkout = Path(args.checkout)
    catalog = checkout/'catalog'
    rows, sources, names = host_catalog.enrollment(root=checkout)
    paths = {rid: catalog/'repositories'/f'{names[rid]}.yaml' for rid in sources}
    tops = {rid: documents.top(path.read_bytes()) for rid, path in paths.items() if path.exists()}
    retained = {rid: dict(repository_id=top['repository_id'], repository=top['repository'],
                          attempted_at=attempted_at(top))
                for rid, top in tops.items()}
    metrics, acquisitions = {}, {}
    report = host_catalog.collect(retained, args.evidence, batch_size=min(args.batch_size, len(sources)),
                                  metrics=metrics, acquisitions=acquisitions, root=checkout)
    output = Path(args.output)
    changed = {}
    for row in report:
        rid = str(row['repository_id'])
        previous = load(paths[rid]) if rid in tops else None
        if row['status'] == 'ok':
            document = documents.repository(previous, acquisitions[rid], repository_id=int(rid), repository=sources[rid])
        elif 'failed_with' in row:
            document = documents.failed(previous, failed_at=row['failed_at'], failed_with=row['failed_with'],
                                        repository_id=int(rid), repository=sources[rid])
        else:
            continue  # a run-wide stop: this repository was not read
        changed[f'repositories/{names[rid]}.yaml'] = documents.encode('repository', document)
    changed['apps.yaml'] = documents.encode('apps', documents.apps(rows, names, root=checkout))
    for rid in sources:
        if f'repositories/{names[rid]}.yaml' in changed:
            tops[rid] = documents.top(changed[f'repositories/{names[rid]}.yaml'])
    now = args.now or utc()
    observed = [tops.get(rid, {}) for rid in sources]
    changed['status/statistics.yaml'] = documents.encode('statistics', documents.statistics(observed, measured_at=now))
    enrolled = {f'repositories/{names[rid]}.yaml' for rid in sources}
    present = {f'repositories/{p.name}' for p in (catalog/'repositories').glob('*.yaml')} if (catalog/'repositories').exists() else set()
    removed = sorted(present-enrolled)
    for relative, raw in changed.items():
        target = output/'catalog'/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    (output/'removed.json').write_text(json.dumps(removed)+'\n')
    selected = metrics['selected_sources']
    summary = dict(reported_at=now, enrolled=len(sources), selected=selected,
                   succeeded=sum(row['status'] == 'ok' for row in report),
                   failed=sum(row['status'] != 'ok' for row in report),
                   http_attempts=metrics['requests'], charged_bytes=metrics['response_bytes'],
                   acquisition_milliseconds=int(metrics['acquisition_seconds']*1000),
                   command_milliseconds=int((time.monotonic()-started)*1000))
    if len(report) < selected and metrics['stop_reason'] in STOPS:
        summary['stop_reason'] = STOPS[metrics['stop_reason']]
    (output/'run.json').write_text(json.dumps(summary)+'\n')


def valid(path):
    """The host's own reader accepts this document."""
    with path.open('rb') as stream:
        run = subprocess.run(['awk', '-f', str(ROOT/'modules/catalog-tables.am'), '-f', str(ROOT/'modules/catalog-parser.am')],
                             stdin=stream, capture_output=True)
    if run.returncode:
        print(f'{path}: {run.stderr.decode(errors="replace").strip()}', flush=True)
    return run.returncode == 0


def git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args], check=True, capture_output=True, text=True).stdout.strip()


def enrolled(path):
    """Each app's repository file in an apps.yaml: the enrollment, without its labels."""
    return {app: entry['repository'] for app, entry in load(path)['apps'].items()} if path.exists() else None


def publish(args):
    candidate = Path(args.candidate)
    summary = json.loads((candidate/'run.json').read_text())
    removed = json.loads((candidate/'removed.json').read_text())
    files = sorted(p for p in (candidate/'catalog').rglob('*') if p.is_file())
    ok = all([valid(path) for path in files])
    if not ok:
        summary['stop_reason'] = 'internal'
    scratch = Path(args.scratch)
    git(scratch.parent, 'init', '-q', str(scratch))
    git(scratch, 'remote', 'add', 'origin', args.remote)
    for attempt in range(1, PUSH_ATTEMPTS+1):
        git(scratch, 'fetch', '-q', '--depth=1', 'origin', BRANCH)
        git(scratch, 'checkout', '-q', '--force', '-B', BRANCH, 'FETCH_HEAD')
        catalog = scratch/'catalog'
        # Marek's enrollment edit landed after collect read apps.yaml: the tip's
        # enrollment stands, unpointed files stay, and the next run catches up.
        raced = ok and enrolled(catalog/'apps.yaml') != enrolled(candidate/'catalog/apps.yaml')
        if raced:
            print('apps.yaml changed since collect; keeping the tip\'s and removing nothing', flush=True)
        if ok:
            for path in files:
                if raced and path == candidate/'catalog/apps.yaml':
                    continue
                target = catalog/path.relative_to(candidate/'catalog')
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, target)
            for relative in [] if raced else removed:
                (catalog/relative).unlink(missing_ok=True)
        runs_path = catalog/'status/runs.yaml'
        previous = load(runs_path) if runs_path.exists() else None
        runs_path.parent.mkdir(parents=True, exist_ok=True)
        runs_path.write_bytes(documents.encode('runs', documents.runs(previous, run_id=args.run_id, attempt=args.attempt,
                                                                       summary=summary)))
        git(scratch, 'add', '-A', '--', 'catalog')
        git(scratch, '-c', 'user.name=AM catalog', '-c', 'user.email=41898282+github-actions[bot]@users.noreply.github.com',
            'commit', '-q', '-m', f'catalog: run {args.run_id}-{args.attempt}')
        pushed = subprocess.run(['git', '-C', str(scratch), 'push', '-q', 'origin', f'HEAD:{BRANCH}'], capture_output=True, text=True)
        if pushed.returncode == 0:
            print(f'pushed catalog: run {args.run_id}-{args.attempt} (push attempt {attempt})', flush=True)
            return
        print(f'push attempt {attempt} rejected; retrying on the new tip', flush=True)
    raise SystemExit(f'push rejected {PUSH_ATTEMPTS} times')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = parser.add_subparsers(dest='command', required=True)
    c = sub.add_parser('collect')
    c.add_argument('--checkout', required=True)
    c.add_argument('--output', required=True)
    c.add_argument('--evidence', help='saved GitHub answers instead of the network (tests)')
    c.add_argument('--batch-size', type=int, default=BATCH_SIZE)
    c.add_argument('--now', help='the run time (tests)')
    p = sub.add_parser('publish')
    p.add_argument('--candidate', required=True)
    p.add_argument('--remote', required=True)
    p.add_argument('--scratch', required=True)
    for command in (c, p):
        command.add_argument('--run-id', type=int, required=True)
        command.add_argument('--attempt', type=int, required=True)
    args = parser.parse_args(argv)
    (collect if args.command == 'collect' else publish)(args)


if __name__ == '__main__':
    main()
