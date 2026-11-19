#!/usr/bin/env python3
"""Per-version split of exact instances by (arch, our form). Usage: queries.py versions.json matches.json"""
import json, sys
from collections import Counter, defaultdict
V = json.load(open(sys.argv[1])); M = json.load(open(sys.argv[2]))
c = defaultdict(Counter)
for r in M['rows']:
    for x in r['exact']:
        v = V[x['version']]; c[(v['template'][10:], v['commit'][:9], v['date'])][(r['arch'], r['ours'])] += 1
for k, v in sorted(c.items()): print(k, dict(v))
