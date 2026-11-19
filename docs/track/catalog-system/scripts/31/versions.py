#!/usr/bin/env python3
"""Every distinct version of every upstream template, from Git history.

Usage: versions.py REPO UPSTREAM OUT.json

For each file under templates/ on UPSTREAM, walk `git log --follow` and keep
the blob at each commit, following renames (R) but stopping at the commit
where the file was created as a copy (C): --follow otherwise continues into
the copied file's history (AM-SAMPLE-AppBundle into AM-SAMPLE-AppImage, the
muliple-variants template into programs/x86_64/zapzap, ...).
Templates deleted before UPSTREAM are walked the same way from the parent of
their deleting commit, and flagged deleted=True.
Distinct bodies only (first, i.e. newest, commit that has that body kept, plus
the oldest commit having it).
"""
import json, subprocess, sys

repo, upstream, out = sys.argv[1:4]

def git(*a):
    return subprocess.check_output(['git', '-C', repo, *a], stderr=subprocess.DEVNULL).decode('utf-8', 'replace')

def walk(start, path):
    rows = []
    log = git('log', '--follow', '--name-status', '--format=C %H %ad', '--date=short', start, '--', path)
    commit = date = None
    for line in log.splitlines():
        if line.startswith('C '):
            _, commit, date = line.split(); continue
        if not line.strip(): continue
        parts = line.split('\t')
        status, newpath = parts[0], parts[-1]
        if status.startswith('D'): continue
        if not newpath.startswith('templates/'): break
        rows.append((commit, date, newpath))
        # A copy (C) starts this file: what --follow shows before it is the
        # history of the file it was copied from (another template, or a
        # recipe), not a version of this template. Renames (R) are followed.
        if status.startswith('C'): break
    return rows

current = git('ls-tree', '--name-only', upstream, 'templates/').split()
deleted = []
for line in git('log', '--diff-filter=D', '--name-only', '--format=C %H', upstream, '--', 'templates/').splitlines():
    if line.startswith('C '): commit = line.split()[1]
    elif line.strip() and line.strip() not in current: deleted.append((line.strip(), commit))

versions = []
gens = {}
def generator(commit):
    if commit not in gens:
        try: gens[commit] = git('show', commit + ':modules/template.am')
        except subprocess.CalledProcessError: gens[commit] = ''
    return gens[commit]

seen_names = set()
claimed = set()
for name, start, is_deleted in [(p, upstream, False) for p in current] + [(p, c + '^', True) for p, c in deleted]:
    if (name, is_deleted) in seen_names: continue
    seen_names.add((name, is_deleted))
    bodies = {}
    for commit, date, path in walk(start, name):
        try: body = git('show', commit + ':' + path)
        except subprocess.CalledProcessError: continue
        if body not in bodies:
            bodies[body] = dict(template=name, deleted=is_deleted, commit=commit, date=date, path=path,
                                oldest_commit=commit, oldest_date=date)
        else:
            bodies[body].update(oldest_commit=commit, oldest_date=date)
    for body, row in bodies.items():
        if body in claimed: continue  # a deleted name renamed into a current one
        claimed.add(body)
        row['body'] = body
        row['generator'] = generator(row['commit'])
        row['lines'] = body.count('\n')
        versions.append(row)

for i, v in enumerate(versions): v['id'] = i
json.dump(versions, open(out, 'w'))
from collections import Counter
c = Counter((v['template'], v['deleted']) for v in versions)
for (t, d), n in sorted(c.items()): print(n, t, '(deleted)' if d else '')
print('total distinct versions', len(versions))
