#!/usr/bin/env python3
"""Ticket 07: are the per-release observed_at overrides releases GitHub deleted?

A release carries its own observed_at only when the latest fetch did not return it. The fetch
proves it gone when the source's history is complete (the fetch reached the end) or when the
release is newer than one the fetch did return (GitHub lists newest first). Prints how many
overrides are proven gone, how many may lie beyond the fetched page, in how many sources, and
their ages relative to the source's observed_at.

Usage: gone.py [CATALOG_REF]   (default origin/release-catalog-v3; run inside the AM checkout)
"""

import collections
import datetime
import subprocess
import sys

import yaml

ref = sys.argv[1] if len(sys.argv) > 1 else 'origin/release-catalog-v3'
Loader = getattr(yaml, 'CSafeLoader', yaml.SafeLoader)
names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', ref, '--', 'repositories'])
batch = subprocess.run(['git', 'cat-file', '--batch'], input=b''.join(
    f'{ref}:'.encode() + n + b'\n' for n in names.splitlines()), capture_output=True, check=True).stdout


def time(s):
    return datetime.datetime.fromisoformat(s.replace('Z', '+00:00'))


counts, sources, ages, i = collections.Counter(), set(), [], 0
while i < len(batch):
    nl = batch.index(b'\n', i)
    size = int(batch[i:nl].split()[2])
    body = batch[nl + 1:nl + 1 + size]
    i = nl + 2 + size
    if b'\n    observed_at:' not in body:
        continue
    doc = yaml.load(body, Loader=Loader)
    releases = doc['releases']
    seen = [r['published_at'] for r in releases.values() if 'observed_at' not in r]
    for r in releases.values():
        if 'observed_at' not in r:
            continue
        gone = doc['scope']['history_complete'] or (seen and r['published_at'] > min(seen))
        counts['proven gone' if gone else 'maybe beyond the page'] += 1
        sources.add(doc['repository'])
        ages.append((time(doc['observed_at']) - time(r['observed_at'])).total_seconds() / 86400)
ages.sort()
print(dict(counts), 'sources', len(sources))
if ages:
    print(f'age in days: min {ages[0]:.1f}, median {ages[len(ages) // 2]:.1f}, max {ages[-1]:.1f}')
