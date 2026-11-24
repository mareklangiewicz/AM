#!/usr/bin/env python3
"""Ticket 07: what GitHub returns for the sources failing with same_tag_conflict.

For each repository file on CATALOG_REF with `failed_with: same_tag_conflict`, fetch page 1 of
its releases (per_page=100, via `gh api`) and print every tag shared by several non-draft
releases: IDs, publication times, asset counts, shared asset names, Linux-looking assets per
twin, and whether the tag is the newest.

Usage: twins.py [CATALOG_REF]   (default origin/release-catalog-v3; run inside the AM checkout)
"""

import collections
import json
import re
import subprocess
import sys

ref = sys.argv[1] if len(sys.argv) > 1 else 'origin/release-catalog-v3'
LINUX = re.compile(r'(?i)appimage|linux|\.deb$|\.rpm$')


def git(*args):
    return subprocess.check_output(['git', *args], text=True)


files = git('grep', '-l', '-E', 'failed_with: "?same_tag_conflict', ref, '--', 'repositories').split()
print(f'{len(files)} sources failing with same_tag_conflict on {ref}')
for f in files:
    path = f.split(':', 1)[1]
    repo = re.search(r'^repository: "(.*)"$', git('show', f'{ref}:{path}'), re.M).group(1)
    releases = json.loads(subprocess.check_output(
        ['gh', 'api', f'repos/{repo}/releases?per_page=100&page=1'], text=True))
    by_tag = collections.defaultdict(list)
    for r in releases:
        if not r['draft']:
            by_tag[r['tag_name']].append(r)
    newest = releases[0]['tag_name'] if releases else None
    for tag, twins in by_tag.items():
        if len(twins) < 2:
            continue
        names = [{a['name'] for a in r['assets']} for r in twins]
        print(repo, tag, 'newest' if tag == newest else 'not-newest',
              'ids', [r['id'] for r in twins], 'published', sorted({r['published_at'] for r in twins}),
              'assets', [len(n) for n in names], 'shared', len(set.intersection(*names)),
              'linux', [sum(bool(LINUX.search(x)) for x in n) for n in names])
