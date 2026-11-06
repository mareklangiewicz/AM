"""Static discovery candidates only; never execute recipe shell or enroll sources."""
import collections
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

root = Path(__file__).resolve().parents[4]
pattern = re.compile(r'https://(?:api\.github\.com/repos/|github\.com/)'
                     r'([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)(?=[/\s\x22\x27?#]|$)')
counts = collections.Counter()
repositories = set()
rows = []
for arch in ('x86_64', 'aarch64', 'i686', 'armv7l'):
    for path in sorted((root/'programs'/arch).glob('*')):
        if not path.is_file():
            continue
        body = path.read_bytes()
        candidates = sorted({m.group(1).removesuffix('.git').lower()
                             for m in pattern.finditer(body.decode())})
        category = ('no_literal_github_repository' if not candidates else
                    'one_literal_github_repository' if len(candidates) == 1 else
                    'multiple_literal_github_repositories')
        counts[category] += 1
        repositories.update(candidates)
        rows.append(dict(recipe=str(path.relative_to(root)),
            sha256=hashlib.sha256(body).hexdigest(), category=category,
            repository_candidates=candidates))
result = dict(source=subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'],
    text=True).strip(), counts=dict(counts), distinct_literal_candidates=len(repositories),
    limitation='Text mentions only: not verified download sources, numeric identities or release availability.')
if '--summary' not in sys.argv:
    result['recipes'] = rows
print(json.dumps(result, indent=2))
