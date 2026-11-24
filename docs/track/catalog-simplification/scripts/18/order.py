#!/usr/bin/env python3
"""Ticket 18: is GitHub's releases list strictly newest-first by created_at or published_at?

For each repository named, fetch page 1 of its releases (per_page=100, via `gh api`) and count
adjacent non-draft pairs where the later entry has a newer created_at, or a newer published_at,
than the one before it. Any such pair means a partial page cannot prove a missing release gone
by comparing its time with the oldest release returned.

Usage: order.py OWNER/REPO...   (ticket 18 ran it on the 14 repositories that failed with
same_tag_conflict on catalog 3fd57907b; scripts/07/twins.py lists them)
"""

import json
import subprocess
import sys

totals = dict(pairs=0, created=0, published=0)
for repo in sys.argv[1:]:
    releases = [r for r in json.loads(subprocess.check_output(
        ['gh', 'api', f'repos/{repo}/releases?per_page=100&page=1'], text=True)) if not r['draft']]
    for before, after in zip(releases, releases[1:]):
        totals['pairs'] += 1
        totals['created'] += before['created_at'] < after['created_at']
        totals['published'] += before['published_at'] < after['published_at']
print('adjacent pairs out of newest-first order:', totals)
