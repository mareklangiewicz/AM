"""Move main-marek: refuse an untested commit, push, watch (ticket 38).

    python3 -B tools/release/release.py ship [--ci NAME] [--watch MINUTES]
    python3 -B tools/release/release.py plan [--ci NAME]     what ship would do; writes nothing
    python3 -B tools/release/release.py watch [RUN_ID ... | --ci NAME] [--minutes N]

Exit codes of a watch: 0 all green, 1 a run failed, 3 still running at the
deadline (it prints the watch command that continues).

Run from a main-marek checkout whose HEAD is the commit to ship. A commit that
changes anything outside docs/ and catalog/ needs `--ci NAME`: `ci/NAME` on
origin must be HEAD, or an ancestor that HEAD changes only under docs/ and
catalog/, and its latest Long tests run on that commit must have succeeded.
A push that changes only catalog/ starts no Fast tests run (tests.yml ignores it).

When HEAD changes catalog/ or the catalog contract (CONTRACT), every catalog/
file at HEAD must pass HEAD's own readers, the host's awk and the page's JS,
or ship refuses: hosts and the page read main-marek's catalog/ directly
(ticket 24). Every plan and ship also compares the deployed page's schema.mjs
with HEAD's.
"""
import argparse
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import time

REPO = 'mareklangiewicz/AM'
BRANCH = 'main-marek'
UNTESTED = ('docs/', 'catalog/')  # changes that need no Long tests
CONTRACT = {'schemas/catalog.schema.yaml', 'modules/catalog-tables.am', 'modules/catalog-parser.am',
            'tools/catalog-contract/parse.mjs', 'tools/catalog-contract/schema.mjs'}
READERS = ('modules/catalog-tables.am', 'modules/catalog-parser.am',
           'tools/catalog-contract/parse.mjs', 'tools/catalog-contract/schema.mjs')
SCHEMA = 'tools/catalog-contract/schema.mjs'
DEPLOYED_SCHEMA = 'https://mareklangiewicz.pl/AM/'+SCHEMA
REDEPLOY = 'gh workflow run catalog-pages.yml --ref '+BRANCH+' -f deploy=true'
POLL_SECONDS = 20
APPEAR_SECONDS = 120
RETRY_SECONDS = 10
ATTEMPTS = 3
SHOWN = 10  # problems a refusal lists before it only counts the rest
# The page's reader, over every file named on stdin (one per line).
NODE_VALIDATE = (
    "import {parseDocument} from './tools/catalog-contract/parse.mjs';"
    "import {readFileSync} from 'node:fs';"
    "let s='';for await(const b of process.stdin)s+=b;"
    "for(const path of s.split('\\n').filter(Boolean)){"
    "try{parseDocument(readFileSync(path,'utf8'))}catch(e){console.log(path+': '+e.message)}}")


class Refused(Exception):
    pass


def say(line):
    """Print now, also when stdout is a pipe or file (a backgrounded run)."""
    print(line, flush=True)


def system(argv):
    done = subprocess.run(argv, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    if done.returncode and argv[:2] != ['git', 'merge-base']:
        sys.stderr.write(done.stderr)
    return done.returncode, done.stdout


def retrying(run, sleep=time.sleep):
    """`run`, with a failing gh call tried again (ticket 48). Not git, whose
    exit codes are answers."""
    def attempt(argv):
        if argv[:1] != ['gh']:
            return run(argv)
        for tried in range(1, ATTEMPTS+1):
            code, text = run(argv)
            if not code:
                return code, text
            if tried < ATTEMPTS:
                sleep(RETRY_SECONDS)
        raise RuntimeError('failed ('+str(code)+') after '+str(ATTEMPTS)+' attempts: '+' '.join(argv))
    return attempt


def output(run, argv):
    code, text = run(argv)
    if code:
        raise RuntimeError('failed ('+str(code)+'): '+' '.join(argv))
    return text


def gh(run, *args):
    return output(run, ['gh', *args, '-R', REPO])


def runs(run, *args):
    return json.loads(gh(run, 'run', 'list', *args))


def appeared(run, find, sleep, what):
    for _ in range(APPEAR_SECONDS//POLL_SECONDS+1):
        found = find()
        if found is not None:
            return found
        sleep(POLL_SECONDS)
    raise RuntimeError(what+' did not appear within '+str(APPEAR_SECONDS)+' s')


def needing_tests(paths):
    return [path for path in paths if not path.startswith(UNTESTED)]


def long_tests(run, branch, commit, fields):
    """The latest Long tests run of `commit` on `branch` (by sha: the latest
    on the branch can be the previous commit's), as a list of 0 or 1 rows."""
    return runs(run, '--workflow', 'long-tests.yml', '--branch', branch, '--commit', commit,
                '--limit', '1', '--json', fields)


def long_tests_run(run, ci, sleep=time.sleep):
    """{'Long tests': id} of HEAD on ci/NAME, waiting for a just-pushed run to appear."""
    head = output(run, ['git', 'rev-parse', 'HEAD']).strip()
    branch = 'ci/'+ci
    found = appeared(run, lambda: next((row['databaseId'] for row in long_tests(run, branch, head, 'databaseId')), None),
                     sleep, 'Long tests run on '+branch+' for '+head)
    return {'Long tests': found}


def validate_catalog(head, repo='.'):
    """Problems of HEAD's catalog/ files under HEAD's own readers; empty when valid."""
    if subprocess.run(['git', '-C', repo, 'cat-file', '-e', head+':catalog'], capture_output=True).returncode:
        return ['HEAD has no catalog/ files']
    archive = subprocess.run(['git', '-C', repo, 'archive', head, '--', 'catalog', *READERS],
                             capture_output=True, check=True).stdout
    problems = []
    with tempfile.TemporaryDirectory() as directory:
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            tar.extractall(directory, filter='data')
        files = sorted(path.relative_to(directory).as_posix() for path in (Path(directory)/'catalog').rglob('*')
                       if path.is_file())
        awk = ['awk', '-f', 'modules/catalog-tables.am', '-f', 'modules/catalog-parser.am']
        for path in files:
            with open(Path(directory)/path, 'rb') as stream:
                done = subprocess.run(awk, stdin=stream, capture_output=True, cwd=directory)
            if done.returncode:
                problems.append(path+' (awk): '+done.stderr.decode(errors='replace').strip())
        node = subprocess.run(['node', '--input-type=module', '-e', NODE_VALIDATE], input=''.join(f+'\n' for f in files),
                              capture_output=True, text=True, cwd=directory)
        if node.returncode:
            problems.append('node reader failed: '+node.stderr.strip())
        for line in node.stdout.splitlines():
            path, _, message = line.partition(': ')
            problems.append(path+' (node): '+message)
    return sorted(problems)


def decide(run, ci=None, out=say, validate=None):
    """Everything ship checks before it writes: raises Refused, or returns the
    commit to push and whether its push starts a Fast tests run."""
    if output(run, ['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip() != BRANCH:
        raise Refused('check out '+BRANCH+' first')
    output(run, ['git', 'fetch', '--quiet', 'origin', BRANCH])
    head = output(run, ['git', 'rev-parse', 'HEAD']).strip()
    base = output(run, ['git', 'rev-parse', 'origin/'+BRANCH]).strip()
    if head == base:
        raise Refused('nothing to ship: HEAD is origin/'+BRANCH)
    if run(['git', 'merge-base', '--is-ancestor', base, head])[0]:
        raise Refused('HEAD is not a fast-forward of origin/'+BRANCH)
    changed = output(run, ['git', 'diff', '--name-only', base, head]).splitlines()
    if ci:
        branch = 'ci/'+ci
        tip = output(run, ['git', 'ls-remote', 'origin', 'refs/heads/'+branch]).split()[:1]
        if not tip:
            raise Refused('origin has no '+branch+'; push HEAD there and wait for Long tests')
        tip = tip[0]
        if tip != head:
            if run(['git', 'merge-base', '--is-ancestor', tip, head])[0]:
                raise Refused('origin '+branch+' is not HEAD or an ancestor of it; push HEAD there and wait for'
                              ' Long tests')
            code = needing_tests(output(run, ['git', 'diff', '--name-only', tip, head]).splitlines())
            if code:
                raise Refused('HEAD changes more than docs/ and catalog/ since '+branch+': '+', '.join(code[:10]))
        latest = long_tests(run, branch, tip, 'databaseId,status,conclusion')
        if not latest or (latest[0]['status'], latest[0]['conclusion']) != ('completed', 'success'):
            raise Refused('Long tests on '+branch+' are not green for '+tip+': '+json.dumps(latest))
        out('Long tests '+str(latest[0]['databaseId'])+' green on '+branch
            + ('' if tip == head else ' at '+tip+'; HEAD adds only docs/ and catalog/'))
    else:
        code = needing_tests(changed)
        if code:
            raise Refused('changes outside docs/ and catalog/ need --ci NAME (a green Long tests run): '
                          + ', '.join(code[:10]))
    if any(path in CONTRACT or path.startswith('catalog/') for path in changed):
        out("validating catalog/ under HEAD's readers (awk and node, one process per file for awk)")
        problems = (validate or validate_catalog)(head)
        if problems:
            more = ' and '+str(len(problems)-SHOWN)+' more' if len(problems) > SHOWN else ''
            raise Refused("catalog/ fails HEAD's readers: "+'; '.join(problems[:SHOWN])+more)
        out("catalog/ valid under HEAD's readers")
    code, deployed = run(['curl', '-fsS', '--max-time', '20', DEPLOYED_SCHEMA])
    if code:
        out('deployed page schema unreadable (curl exit '+str(code)+')')
    elif deployed == output(run, ['git', 'show', head+':'+SCHEMA]):
        out('deployed page schema matches HEAD')
    else:
        out('deployed page schema differs from HEAD; redeploy when ready: '+REDEPLOY)
    return dict(head=head, fast=not all(path.startswith('catalog/') for path in changed))


def plan(run, ci=None, out=say, validate=None):
    """Print what ship would do now, writing nothing (ticket 40)."""
    try:
        found = decide(run, ci, out, validate)
    except Refused as refusal:
        out('would refuse: '+str(refusal))
        return False
    out('would push '+found['head']+' to '+BRANCH)
    out('Fast tests would run on it' if found['fast'] else 'no Fast tests run: HEAD changes only catalog/')
    return True


def ship(run, ci=None, out=say, sleep=time.sleep, validate=None):
    """Returns the run ids to watch: 'fast' unless the push changes only catalog/."""
    found = decide(run, ci, out, validate)
    head = found['head']
    output(run, ['git', 'push', 'origin', 'HEAD:refs/heads/'+BRANCH])
    out('pushed '+head+' to '+BRANCH)
    if not found['fast']:
        out('no Fast tests run: HEAD changes only catalog/')
        return {}
    result = dict(fast=appeared(run, lambda: next((row['databaseId'] for row in runs(
        run, '--workflow', 'tests.yml', '--event', 'push', '--commit', head, '--limit', '1', '--json', 'databaseId')), None),
        sleep, 'Fast tests run'))
    for name, run_id in result.items():
        out(name+' run '+str(run_id)+': https://github.com/'+REPO+'/actions/runs/'+str(run_id))
    return result


GREEN, RED, RUNNING = 'green', 'red', 'running'
EXIT = {GREEN: 0, RED: 1, RUNNING: 3}


def watch(run, ids, minutes, out=say, sleep=time.sleep, clock=time.monotonic):
    """GREEN when every run succeeded. RED when one did not, returned once the
    others end or the deadline comes. RUNNING when the deadline came with
    nothing failed: then the last line is the command that continues the
    watch for the same number of minutes (ticket 41)."""
    deadline = clock()+minutes*60
    pending = dict(ids)
    good = True
    while True:
        for name, run_id in list(pending.items()):
            state = json.loads(gh(run, 'run', 'view', str(run_id), '--json', 'status,conclusion'))
            if state['status'] == 'completed':
                out(label(name, run_id)+': '+state['conclusion'])
                good = good and state['conclusion'] == 'success'
                del pending[name]
        if not pending:
            return GREEN if good else RED
        if clock() >= deadline:
            out('still running at the deadline: '+', '.join(label(name, i) for name, i in pending.items()))
            if not good:
                return RED
            out('not failed; continue with: python3 -B tools/release/release.py watch '
                + ' '.join(str(i) for i in pending.values())+f' --minutes {minutes:g}')
            return RUNNING
        sleep(POLL_SECONDS)


def pushed_runs(run):
    """Every recent run on the commit origin/main-marek points at, by workflow name."""
    output(run, ['git', 'fetch', '--quiet', 'origin', BRANCH])
    head = output(run, ['git', 'rev-parse', 'origin/'+BRANCH]).strip()
    found = {}
    for row in runs(run, '--commit', head, '--limit', '20', '--json', 'databaseId,workflowName'):
        found.setdefault(row['workflowName'], row['databaseId'])
    return found


def named(ids):
    """Runs given by id; label() prints them as plain 'run ID'."""
    return {i: int(i) for i in ids}


def label(name, run_id):
    return ('' if name == str(run_id) else name+' ')+'run '+str(run_id)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='operation', required=True)
    command = sub.add_parser('ship')
    preview = sub.add_parser('plan', help='print what ship would do; writes nothing')
    for each in (command, preview):
        each.add_argument('--ci', metavar='NAME', help='the tested branch ci/NAME')
    command.add_argument('--watch', type=float, metavar='MINUTES', help='then wait for the runs, at most this long')
    resume = sub.add_parser('watch', help='watch runs (default: every run on origin/main-marek) until done')
    resume.add_argument('ids', nargs='*', metavar='RUN_ID')
    resume.add_argument('--ci', metavar='NAME', help='watch the Long tests run of HEAD on ci/NAME')
    resume.add_argument('--minutes', type=float, default=30)
    args = parser.parse_args(argv)
    run = retrying(system)  # every command's gh calls (ticket 48)
    if args.operation == 'watch':
        if args.ci and args.ids:
            parser.error('watch takes RUN_IDs or --ci, not both')
        ids = long_tests_run(run, args.ci) if args.ci else named(args.ids) if args.ids else pushed_runs(run)
        if not ids:
            raise SystemExit('no runs to watch')
        raise SystemExit(EXIT[watch(run, ids, args.minutes)])
    if args.operation == 'plan':
        raise SystemExit(0 if plan(run, ci=args.ci) else 1)
    try:
        ids = ship(run, ci=args.ci)
    except Refused as refusal:
        raise SystemExit('refused: '+str(refusal))
    if args.watch is not None and ids:
        raise SystemExit(EXIT[watch(run, ids, args.watch)])


if __name__ == '__main__':
    main()
