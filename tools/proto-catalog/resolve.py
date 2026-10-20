#!/usr/bin/env python3
# PROTOTYPE, throwaway: see docs/design/version-catalog.md.
# Resolve recipe rows to the newest few matching release assets via GraphQL.
# Usage: resolve.py <recipes.tsv> <arch> <cache dir> [releases=5] > catalog.tsv
# Raw responses are cached per batch in <cache dir>, so reruns cost nothing.
import hashlib, json, os, re, subprocess, sys

BATCH, DEEP_BATCH, KEEP = 25, 5, 3
OTHER = {
    "x86_64": ["i386", "i686", "armhf", "aarch64", "arm64", "armv7l"],
    "aarch64": ["x86_64", "amd64", "armv7l", "i386", "i686", "armhf"],
}
SELF = {"x86_64": ["x86_64", "amd64"], "aarch64": ["aarch64", "arm64"]}
SIDECAR = re.compile(r"\.(zsync|sha256|sha512|sha1|md5|sig|asc|minisig|sum|txt|json|yml|yaml)$|sums?$", re.I)

QUERY_REPO = """
r%d: repository(owner: %s, name: %s) {
  nameWithOwner
  releases(first: %d, orderBy: {field: CREATED_AT, direction: DESC}) {
    nodes { tagName createdAt publishedAt isPrerelease isLatest
      releaseAssets(first: 50) { nodes { name size digest } } }
  }
}"""


def fetch(repos, cache, nrel):
    key = hashlib.sha1(("%d " % nrel + " ".join(repos)).encode()).hexdigest()[:16]
    path = os.path.join(cache, key + ".json")
    if not os.path.exists(path):
        parts = []
        for i, r in enumerate(repos):
            o, n = r.split("/", 1)
            parts.append(QUERY_REPO % (i, json.dumps(o), json.dumps(n), nrel))
        q = "query { rateLimit { cost remaining } %s }" % "".join(parts)
        out = subprocess.run(["gh", "api", "graphql", "-f", "query=" + q], capture_output=True, text=True).stdout
        with open(path, "w") as f:
            f.write(out)
    with open(path) as f:
        resp = json.load(f)
    data = resp.get("data") or {}
    if "rateLimit" in data and data["rateLimit"]:
        print("batch cost %(cost)s remaining %(remaining)s" % data["rateLimit"], file=sys.stderr)
    for e in resp.get("errors", []):
        print("error:", e.get("type"), e.get("message"), file=sys.stderr)
    return {r: data.get("r%d" % i) for i, r in enumerate(repos)}


def arch_ok(name, arch, policy):
    n = name.lower()
    if any(w in n for w in OTHER[arch]):
        return False
    return policy == "excl" or any(w in n for w in SELF[arch])


def pick(repo_data, conv, arch):
    order, asset, policy = conv.split(":")
    rels = repo_data["releases"]["nodes"]
    if order == "latest":
        i = next((i for i, r in enumerate(rels) if r["isLatest"]), None)
        if i is None:
            return []
        rels = [rels[i]] + [r for r in rels[i + 1:] if not r["isPrerelease"]]
    rows = []
    for depth, r in enumerate(rels):
        # REST lists assets sorted by name (bytewise); today's head -1 depends on it.
        for a in sorted(r["releaseAssets"]["nodes"], key=lambda a: a["name"]):
            name = a["name"]
            if SIDECAR.search(name) or not arch_ok(name, arch, policy):
                continue
            if asset == "appimage" and not name.lower().endswith(".appimage"):
                continue
            rows.append((r["tagName"], r["publishedAt"], name, a["size"], (a["digest"] or "").removeprefix("sha256:"), depth))
            break
        if len(rows) == KEEP:
            break
    return rows


def main():
    recipes, arch, cache = sys.argv[1], sys.argv[2], sys.argv[3]
    nrel = int(sys.argv[4]) if len(sys.argv) > 4 else 5
    os.makedirs(cache, exist_ok=True)
    rows = [l.rstrip("\n").split("\t") for l in open(recipes)]
    repos = sorted({r[1] for r in rows})
    data = {}
    for i in range(0, len(repos), BATCH):
        data.update(fetch(repos[i:i + BATCH], cache, nrel))
    # Second pass, deeper, only for repos where some recipe matched nothing:
    # today's /releases scan falls through up to 30 releases.
    deep = sorted({repo for app, repo, conv in rows if data.get(repo) and not pick(data[repo], conv, arch)})
    print(f"deep pass: {len(deep)} repos", file=sys.stderr)
    for i in range(0, len(deep), DEEP_BATCH):
        data.update(fetch(deep[i:i + DEEP_BATCH], cache, 30))
    missing = empty = 0
    for app, repo, conv in rows:
        d = data.get(repo)
        if not d:
            missing += 1
            continue
        got = pick(d, conv, arch)
        if not got:
            empty += 1
        for tag, pub, name, size, sha, depth in got:
            print(f"{app}\t{tag}\t{pub}\t{name}\t{size}\t{sha}\t{depth}")
    print(f"repos {len(repos)}, apps {len(rows)}, repo missing {missing}, no match {empty}", file=sys.stderr)


main()
