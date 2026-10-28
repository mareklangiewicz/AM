"""Offline audit of the frozen paths after the reviewed c++filt correction; executes only fixed sed/grep pipelines."""
import collections
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]
QUEUE = ROOT / 'docs/track/release-catalog/design/migration-enrollment-queue.json'
BODY = OUT / 'body.json'


def main():
    queue = json.loads(QUEUE.read_bytes())
    raw = BODY.read_bytes()
    body_report = json.loads((OUT / 'report.json').read_bytes())
    assert hashlib.sha256(raw).hexdigest() == body_report['body_sha256']
    assets = {a['browser_download_url'] for r in json.loads(raw) for a in r['assets']}
    env = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'}
    # This is exactly the recipes' tokenization. No installer or updater executes.
    tokens = subprocess.run(['sed', r's/[()",{} ]/\n/g'], input=raw, env=env,
                            check=True, stdout=subprocess.PIPE).stdout
    rows = []
    for name in queue['first_stage']['recipes']:
        path = ROOT / name
        source = path.read_text()
        apps = re.findall(r'^APP=(.*)$', source, re.M)
        assert len(apps) == 2 and apps[0] == apps[1], name
        app = apps[0]
        assert re.fullmatch(r'[a-z0-9.+-]+', app), name
        arch = name.split('/')[1]
        assert arch in ('aarch64', 'x86_64'), name
        component = 'c%2B%2Bfilt' if app == 'c++filt' else '${APP}'
        expr = f'https.*download.*/{arch}-[0-9]{{8}}/{component}_.*-{arch}-static$'
        lines = [line for line in source.splitlines() if line.startswith('version=')]
        expected = ('version=$(curl -Ls https://api.github.com/repos/ivan-hc/am-utils/releases '
                    '| sed \'s/[()",{} ]/\\n/g\' | grep -Eoi "' + expr + '" | head -1)')
        assert lines == [expected, expected], name
        pattern = expr.replace('${APP}', app)
        matches = subprocess.run(['grep', '-Eoi', pattern], input=tokens, env=env,
                                 stdout=subprocess.PIPE)
        assert matches.returncode in (0, 1), name
        urls = matches.stdout.decode().splitlines()
        # Differential execution of the original fixed selector suffix, with APP
        # passed as data, never interpolated into shell source.
        suffix = expected.split('| sed ', 1)[1][:-1]
        original = subprocess.run(['sh', '-c', 'sed ' + suffix], input=raw,
                                  env=dict(env, APP=app), check=True,
                                  stdout=subprocess.PIPE).stdout.decode().rstrip('\n')
        selected = urls[0] if urls else ''
        assert selected == original, name
        rows.append(dict(path=name, app=app, arch=arch,
                         recipe_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                         match_count=len(urls), unique_match_count=len(set(urls)),
                         selected=selected, selected_is_asset=selected in assets,
                         differential_equal=True))
    report = dict(body_sha256=body_report['body_sha256'],
                  queue_sha256=hashlib.sha256(QUEUE.read_bytes()).hexdigest(),
                  recipes=len(rows), by_arch=dict(collections.Counter(r['arch'] for r in rows)),
                  missing=sum(not r['selected'] for r in rows),
                  multiple=sum(r['match_count'] > 1 for r in rows),
                  non_asset=sum(bool(r['selected']) and not r['selected_is_asset'] for r in rows),
                  differential_equal=sum(r['differential_equal'] for r in rows), rows=rows)
    (OUT / 'selector-report-fixed.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'rows'}, indent=2))
    return bool(report['missing'] or report['non_asset'])


if __name__ == '__main__':
    raise SystemExit(main())
