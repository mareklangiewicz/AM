#!/usr/bin/env python3
"""Why do template instances stay originals/long? Usage: origins.py versions.json matches.json base_paths.txt REPO UPSTREAM"""
import json, sys, subprocess, re
from collections import Counter
V = json.load(open(sys.argv[1])); M = json.load(open(sys.argv[2])); base = set(open(sys.argv[3]).read().split())
repo, up = sys.argv[4], sys.argv[5]
fam = lambda r: V[r['exact'][0]['version']]['template'][10:] if r['exact'] else None
rows = [r for r in M['rows'] if r['exact']]
print('exact instances by (family, ours form, present at merge base 7b4f831e6):')
c = Counter((fam(r), r['ours'], r['recipe'] in base) for r in rows)
for k, n in sorted(c.items(), key=str): print(n, k)
# selection host of originals that are reviewed-layout instances
lay = {7, 10}
orig = [r for r in rows if r['ours'] == 'original' and r['exact'][0]['version'] in lay]
hosts = Counter()
for r in orig:
    src = subprocess.check_output(['git', '-C', repo, 'show', up + ':' + r['recipe']]).decode('utf-8', 'replace')
    m = re.search(r'^SITE="?([^"\n]*)', src, re.M)
    s = m[1] if m else ''
    hosts['github-like OWNER/REPO' if re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', s) else 'other: ' + s.split('/')[0][:30]] += 1
print('reviewed-layout originals by SITE shape:', hosts.most_common(12))
