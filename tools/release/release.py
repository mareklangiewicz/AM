"""Move main-marek: refuse an untested commit, push, repin and dispatch when needed, watch (ticket 38).

    python3 -B tools/release/release.py ship [--ci NAME] [--watch MINUTES]

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


class Refused(Exception):
    pass


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


def ship(run, ci=None, out=print, sleep=time.sleep):
    """Returns the run ids to watch: always 'fast', 'catalog' when dispatched."""
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
    output(run, ['git', 'push', 'origin', 'HEAD:refs/heads/'+BRANCH])
    out('pushed '+head+' to '+BRANCH)
    result = {}
    pin = gh(run, 'variable', 'get', PIN).strip()
    changed = output(run, ['git', 'diff', '--name-only', pin, head, '--', *schedule_gate_paths()]).splitlines()
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


def watch(run, ids, minutes, out=print, sleep=time.sleep, clock=time.monotonic):
    """True when every run completed successfully before the deadline."""
    deadline = clock()+minutes*60
    pending = dict(ids)
    good = True
    while True:
        for name, run_id in list(pending.items()):
            state = json.loads(gh(run, 'run', 'view', str(run_id), '--json', 'status,conclusion'))
            if state['status'] == 'completed':
                out(name+' run '+str(run_id)+': '+state['conclusion'])
                good = good and state['conclusion'] == 'success'
                del pending[name]
        if not pending:
            return good
        if clock() >= deadline:
            out('still running at the deadline: '+', '.join(name+' '+str(i) for name, i in pending.items()))
            return False
        sleep(POLL_SECONDS)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='operation', required=True)
    command = sub.add_parser('ship')
    command.add_argument('--ci', metavar='NAME', help='the tested branch ci/NAME')
    command.add_argument('--watch', type=float, metavar='MINUTES', help='then wait for the runs, at most this long')
    args = parser.parse_args(argv)
    try:
        ids = ship(system, ci=args.ci)
    except Refused as refusal:
        raise SystemExit('refused: '+str(refusal))
    if args.watch is not None and not watch(system, ids, args.watch):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
