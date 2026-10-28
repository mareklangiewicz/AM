"""Static preparation for ticket 48. Reads recipes; never executes them."""
import collections
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).with_name('executable-lifecycle-audit.json')


def main():
    inventory = ROOT / 'docs/track/release-catalog/research/recipe-family-inventory.json'
    selectors = ROOT / 'docs/track/release-catalog/research/am-utils-release-20261028/selector-report-fixed.json'
    rows = json.loads(inventory.read_bytes())['plain_utility_batch']
    evidence = {r['path']: r for r in json.loads(selectors.read_bytes())['rows']}
    shapes = collections.defaultdict(list)
    identities = set()
    lines = size = 0
    for row in rows:
        path = ROOT / row['path']
        raw = path.read_bytes()
        source = raw.decode()
        assert hashlib.sha256(raw).hexdigest() == evidence[row['path']]['recipe_sha256'], path
        apps = re.findall(r'^APP=(.*)$', source, re.M)
        versions = re.findall(r'^version=.*$', source, re.M)
        assert len(apps) == 2 and apps[0] == apps[1] == path.name, path
        assert len(versions) == 2 and versions[0] == versions[1], path
        normalized = re.sub(r'^APP=.*$', 'APP=<identity>', source, flags=re.M)
        normalized = re.sub(r'^version=.*$', 'version=<selector>', normalized, flags=re.M)
        shapes[hashlib.sha256(normalized.encode()).hexdigest()].append(row['path'])
        identities.add(apps[0])
        lines += len(source.splitlines())
        size += len(raw)
    assert len(rows) == 356 and len(identities) == 178 and len(shapes) == 1
    report = dict(
        scope='static offline preparation; no operational enrollment or migration',
        inventory_sha256=hashlib.sha256(inventory.read_bytes()).hexdigest(),
        selector_evidence_sha256=hashlib.sha256(selectors.read_bytes()).hexdigest(),
        recipes=len(rows), identities=len(identities), lines=lines, bytes=size,
        by_arch=dict(sorted(collections.Counter(r['arch'] for r in rows).items())),
        identities_rejected_by_current_appimage_validator=sorted(
            app for app in identities if not re.fullmatch(r'[a-z0-9_-]+', app)),
        lifecycle_shapes=dict(sorted(shapes.items())),
    )
    OUT.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'lifecycle_shapes'}, indent=2))


if __name__ == '__main__':
    main()
