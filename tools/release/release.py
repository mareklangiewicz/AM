"""Move main-marek: refuse an untested commit, push, repin and dispatch when needed, watch (ticket 38).

    python3 -B tools/release/release.py ship [--ci NAME] [--watch MINUTES]
    python3 -B tools/release/release.py plan [--ci NAME]     what ship would do; writes nothing
    python3 -B tools/release/release.py watch [RUN_ID ...] [--minutes N]

Exit codes of a watch: 0 all green, 1 a run failed, 3 still running at the
deadline (it prints the watch command that continues).

Run from a main-marek checkout whose HEAD is the commit to ship. A commit that
changes anything outside docs/ needs `--ci NAME`: `ci/NAME` on origin must be
HEAD and its latest Long tests run on HEAD must have succeeded. The schedule
pin moves, and a catalog run is dispatched, only when the collection inputs
differ from the pin (the gate's own list, ticket 22).
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'catalog-collector'))
from collection_interface import schedule_gate_paths  # noqa: E402  one list for the gate and this

REPO = 'mareklangiewicz/AM'
BRANCH = 'main-marek'
PIN = 'CATALOG_SCHEDULE_REVISION'
POLL_SECONDS = 20
APPEAR_SECONDS = 120
SHOWN = 20  # changed inputs plan lists before it only counts the rest


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


def decide(run, ci=None, out=say):
    """Everything ship checks before it writes: raises Refused, or returns the
    commit to push, the current pin and the collection inputs changed since it."""
    if output(run, ['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip() != BRANCH:
        raise Refused('check out '+BRANCH+' first')
    output(run, ['git', 'fetch', '--quiet', 'origin', BRANCH])
    head = output(run, ['git', 'rev-parse', 'HEAD']).strip()
    base = output(run, ['git', 'rev-parse', 'origin/'+BRANCH]).strip()
    if head == base:
        raise Refused('nothing to ship: HEAD is origin/'+BRANCH)
    if run(['git', 'merge-base', '--is-ancestor', base, head])[0]:
        raise Refused('HEAD is not a fast-forward of origin/'+BRANCH)
    if ci:
        branch = 'ci/'+ci
        remote = output(run, ['git', 'ls-remote', 'origin', 'refs/heads/'+branch]).split()
        if remote[:1] != [head]:
            raise Refused('origin '+branch+' is not HEAD; push HEAD there and wait for Long tests')
        latest = runs(run, '--workflow', 'long-tests.yml', '--branch', branch, '--commit', head,
                      '--limit', '1', '--json', 'databaseId,status,conclusion')
        if not latest or (latest[0]['status'], latest[0]['conclusion']) != ('completed', 'success'):
            raise Refused('Long tests on '+branch+' are not green for HEAD: '+json.dumps(latest))
        out('Long tests '+str(latest[0]['databaseId'])+' green on '+branch)
    else:
        code = [path for path in output(run, ['git', 'diff', '--name-only', base, head]).splitlines()
                if not path.startswith('docs/')]
        if code:
            raise Refused('changes outside docs/ need --ci NAME (a green Long tests run): '+', '.join(code[:10]))
    pin = gh(run, 'variable', 'get', PIN).strip()
    changed = output(run, ['git', 'diff', '--name-only', pin, head, '--', *schedule_gate_paths()]).splitlines()
    return dict(head=head, pin=pin, changed=changed)


def plan(run, ci=None, out=say):
    """Print what ship would do now, writing nothing (ticket 40)."""
    try:
        found = decide(run, ci, out)
    except Refused as refusal:
        out('would refuse: '+str(refusal))
        return False
    out('would push '+found['head']+' to '+BRANCH)
    if found['changed']:
        out('would repin '+PIN+' '+found['pin']+' -> '+found['head']+' and dispatch catalog.yml; '
            + str(len(found['changed']))+' collection inputs changed:')
        for path in found['changed'][:SHOWN]:
            out('  '+path)
        if len(found['changed']) > SHOWN:
            out('  ... and '+str(len(found['changed'])-SHOWN)+' more')
    else:
        out(PIN+' stays '+found['pin']+': collection inputs unchanged')
    return True


def ship(run, ci=None, out=say, sleep=time.sleep):
    """Returns the run ids to watch: always 'fast', 'catalog' when dispatched."""
    found = decide(run, ci, out)
    head, pin, changed = found['head'], found['pin'], found['changed']
    output(run, ['git', 'push', 'origin', 'HEAD:refs/heads/'+BRANCH])
    out('pushed '+head+' to '+BRANCH)
    result = {}
    if changed:
        gh(run, 'variable', 'set', PIN, '--body', head)
        out(PIN+' '+pin+' -> '+head+' ('+str(len(changed))+' collection inputs changed)')
        dispatched = ('--workflow', 'catalog.yml', '--event', 'workflow_dispatch', '--commit', head, '--json', 'databaseId')
        before = {row['databaseId'] for row in runs(run, *dispatched)}
        gh(run, 'workflow', 'run', 'catalog.yml', '--ref', BRANCH)
        result['catalog'] = appeared(run, lambda: next((row['databaseId'] for row in runs(run, *dispatched)
                                                        if row['databaseId'] not in before), None),
                                     sleep, 'dispatched catalog run')
    else:
        out(PIN+' stays '+pin+': collection inputs unchanged')
    result = dict(fast=appeared(run, lambda: next((row['databaseId'] for row in runs(
        run, '--workflow', 'tests.yml', '--event', 'push', '--commit', head, '--limit', '1', '--json', 'databaseId')), None),
        sleep, 'Fast tests run'), **result)
    for name, run_id in result.items():
        out(name+' run '+str(run_id)+': https://github.com/'+REPO+'/actions/runs/'+str(run_id))
    return result


GREEN, RED, RUNNING = 'green', 'red', 'running'
EXIT = {GREEN: 0, RED: 1, RUNNING: 3}


def watch(run, ids, minutes, out=say, sleep=time.sleep, clock=time.monotonic):
    """GREEN when every run succeeded, RED as soon as one did not (once the
    deadline or the others end), RUNNING when the deadline came first: then
    the last line is the command that continues the watch (ticket 41)."""
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
                + ' '.join(str(i) for i in pending.values())+' --minutes 30')
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
    command.add_argument('--ci', metavar='NAME', help='the tested branch ci/NAME')
    command.add_argument('--watch', type=float, metavar='MINUTES', help='then wait for the runs, at most this long')
    sub.add_parser('plan', help='print what ship would do; writes nothing').add_argument(
        '--ci', metavar='NAME', help='the tested branch ci/NAME')
    resume = sub.add_parser('watch', help='watch runs (default: every run on origin/main-marek) until done')
    resume.add_argument('ids', nargs='*', metavar='RUN_ID')
    resume.add_argument('--minutes', type=float, default=30)
    args = parser.parse_args(argv)
    if args.operation == 'watch':
        ids = named(args.ids) if args.ids else pushed_runs(system)
        if not ids:
            raise SystemExit('no runs to watch')
        raise SystemExit(EXIT[watch(system, ids, args.minutes)])
    if args.operation == 'plan':
        raise SystemExit(0 if plan(system, ci=args.ci) else 1)
    try:
        ids = ship(system, ci=args.ci)
    except Refused as refusal:
        raise SystemExit('refused: '+str(refusal))
    if args.watch is not None:
        raise SystemExit(EXIT[watch(system, ids, args.watch)])


if __name__ == '__main__':
    main()
