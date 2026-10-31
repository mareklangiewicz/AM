"""Replay frozen Brave selection pipelines against retained bytes; no network."""
import hashlib
import json
from pathlib import Path
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]

def main():
    body = (OUT / 'body.json').read_bytes()
    report = json.loads((OUT / 'report.json').read_bytes())
    assert report['accepted'] and hashlib.sha256(body).hexdigest() == report['body_sha256']
    frozen = json.loads((OUT.parent / 'brave-enrollment-preparation.json').read_bytes())
    assets = {a['browser_download_url'] for release in json.loads(body) for a in release['assets']}
    results = []
    for row in frozen['recipes']:
        raw = (ROOT / row['path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == row['sha256'], row['path']
        lines = [line for line in raw.decode().splitlines() if line.startswith('version=$(curl ')]
        assert len(lines) == 2 and all(line == row['original_selector'] for line in lines)
        prefix = 'version=$(curl -Ls ' + frozen['alias'] + ' | '
        for phase, line in zip(('install', 'update'), lines):
            assert line.startswith(prefix) and line.endswith(')')
            pipeline = line[len(prefix):-1]
            # Execute only the exact retained sed/grep/head pipeline with saved stdin.
            assert pipeline.startswith('sed ') and 'curl' not in pipeline and 'wget' not in pipeline
            result = subprocess.run(['sh', '-c', pipeline], input=body, capture_output=True, check=True)
            selected = result.stdout.decode().rstrip('\n')
            results.append(dict(path=row['path'], phase=phase, selected=selected,
                                actual_asset=selected in assets, stderr=result.stderr.decode()))
    summary = dict(body_sha256=report['body_sha256'], live_requests=0,
                   selector_checks=len(results), actual_asset_matches=sum(r['actual_asset'] for r in results),
                   missing=[r for r in results if not r['actual_asset']], results=results)
    (OUT / 'selector-report.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({k:v for k,v in summary.items() if k != 'results'}, indent=2))
    return bool(summary['missing'])

if __name__ == '__main__':
    raise SystemExit(main())
