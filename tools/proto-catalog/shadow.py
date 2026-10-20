#!/usr/bin/env python3
# PROTOTYPE, throwaway: see docs/design/version-catalog.md.
# Compare the resolver's first pick with what each script's own version= line picks.
# Usage: shadow.py <programs/arch dir> <sample recipes.tsv> <catalog.tsv> <cache dir>
# The script's pipeline runs in bash with curl replaced by `cat` of a REST response
# fetched once (authenticated) and cached, so it costs one REST call per repo.
import os, re, subprocess, sys, urllib.parse
from collections import Counter

DL = re.compile(r"^https://github\.com/([^/]+/[^/]+)/releases/download/([^/]+)/(.+)$")


def rest(endpoint, cache):
    path = os.path.join(cache, endpoint.replace("/", "_") + ".json")
    if not os.path.exists(path):
        out = subprocess.run(["gh", "api", endpoint], capture_output=True, text=True).stdout
        with open(path, "w") as f:
            f.write(out)
    return path


def script_pick(progdir, app, cache):
    line = next(l.strip() for l in open(os.path.join(progdir, app), errors="replace") if l.lstrip().startswith("version="))
    ep = re.search(r"https://api\.github\.com/(repos/[^'\s]+)", line).group(1)
    body = rest(ep, cache)
    sh = 'APP=%s; curl() { cat %s; }; %s; printf %%s "$version"' % (app, body, line)
    return subprocess.run(["bash", "-c", sh], capture_output=True, text=True).stdout.strip()


def main():
    progdir, sample, catalog, cache = sys.argv[1:5]
    os.makedirs(cache, exist_ok=True)
    first = {}
    for l in open(catalog):
        f = l.rstrip("\n").split("\t")
        first.setdefault(f[0], f)
    verdict = Counter()
    for l in open(sample):
        app, repo, conv = l.rstrip("\n").split("\t")
        url = script_pick(progdir, app, cache)
        cat = first.get(app)
        m = DL.match(url)
        if not url and not cat:
            v = "both empty"
        elif not url:
            v = "script empty"
        elif not cat:
            v = "catalog empty"
        elif not m:
            v = "script url not a release download"
        else:
            tag, name = urllib.parse.unquote(m.group(2)), urllib.parse.unquote(m.group(3))
            if (tag, name) == (cat[1], cat[3]):
                v = "same"
            elif tag == cat[1]:
                v = "same tag, other asset"
            else:
                v = "other tag"
        verdict[(conv, v)] += 1
        if v != "same":
            print(f"{v}\t{app}\t{conv}\tscript={url}\tcatalog={cat[1] + '/' + cat[3] if cat else ''}")
    for (conv, v), n in sorted(verdict.items()):
        print(f"{n:5} {conv:24} {v}", file=sys.stderr)


main()
