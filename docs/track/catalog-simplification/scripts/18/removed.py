#!/usr/bin/env python3
"""Ticket 18: between two catalog commits, which releases did collection remove, and was each
removal proven by a complete history?

For every repository file whose observed_at changed (collected in between), classify each release
ID present in BEFORE and absent in AFTER: dropped by the 32-release retention cap (AFTER holds 32
or more and the release is no newer than the 32nd newest kept), removed by a complete history, or
removed without proof (printed). Also counts files that
now hold two release IDs under one tag (twins), and per-release observed_at overrides in each.

Usage: removed.py BEFORE AFTER   (catalog commits on release-catalog-v3; run inside the AM checkout)
"""

import collections
import subprocess
import sys

import yaml

Loader = getattr(yaml, 'CSafeLoader', yaml.SafeLoader)
before_ref, after_ref = sys.argv[1], sys.argv[2]


def documents(ref):
    names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', ref, '--', 'repositories'])
    batch = subprocess.run(['git', 'cat-file', '--batch'], input=b''.join(
        f'{ref}:'.encode() + n + b'\n' for n in names.splitlines()), capture_output=True, check=True).stdout
    docs, i = {}, 0
    for name in names.splitlines():
        nl = batch.index(b'\n', i)
        size = int(batch[i:nl].split()[2])
        docs[name.decode()] = yaml.load(batch[nl + 1:nl + 1 + size], Loader=Loader)
        i = nl + 2 + size
    return docs


def published(release):
    return release.get('published_at', release.get('created_at'))


def overrides(docs):
    return sum('observed_at' in r for d in docs.values() for r in (d.get('releases') or {}).values())


before, after = documents(before_ref), documents(after_ref)
counts = collections.Counter()
for path, new in after.items():
    old = before.get(path)
    if not old or old.get('observed_at') == new.get('observed_at') or 'observed_at' not in new:
        continue
    counts['collected'] += 1
    gone = set(old.get('releases') or {}) - set(new['releases'])
    complete = new['scope']['history_complete']
    kept = new['releases']
    # The 32nd newest kept release; a 33rd (the newest stable, kept on purpose) can be older.
    newest = sorted((published(r) for r in kept.values()), reverse=True)
    oldest_kept = newest[min(len(newest), 32) - 1] if newest else None
    for rid in sorted(gone, key=int):
        record = old['releases'][rid]
        if len(kept) >= 32 and oldest_kept is not None and published(record) <= oldest_kept:
            counts['dropped by 32-release retention'] += 1
        elif complete:
            counts['removed by complete history'] += 1
        else:
            counts['removed WITHOUT proof'] += 1
            print('unproven removal:', new['repository'], rid, record['tag'])
twins = [d['repository'] for d in after.values()
         if len({r['tag'] for r in (d.get('releases') or {}).values()}) < len(d.get('releases') or {})]
print(dict(counts), 'files with twins:', twins,
      'overrides:', overrides(before), '->', overrides(after))
