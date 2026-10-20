#!/usr/bin/env python3
# PROTOTYPE, throwaway: see docs/design/version-catalog.md.
# Classify programs/<arch>/* scripts into recipe rows by their first version= line.
# Usage: classify.py <programs/arch dir> <arch>  > recipes.tsv   (report on stderr)
import os, re, sys
from collections import Counter

ARCHES = {"i386", "i686", "armhf", "aarch64", "arm64", "armv7l", "x86_64", "amd64", "x64", "x86"}
# Words that, when present in the URL, mean "this arch" for each target.
SELF = {"x86_64": {"x86_64", "amd64", "x64", "x86"}, "aarch64": {"aarch64", "arm64"}}
ENDPOINT = re.compile(r"""^version=\$\(curl -Ls '?https://api\.github\.com/repos/([^/'\s]+/[^/'\s]+)/releases(/latest)?'?$""")
SED = "sed 's/[()\",{} ]/\\n/g'"
STAGE_KIND = {
    'grep -oi "https.*mage$"': "appimage_url",
    'grep -oi "https.*download.*mage$"': "appimage_url",
    'grep -oi "https.*download.*"': "any_url",
    'grep -i "appimage$"': "appimage_filter",
}
ARCH_EXCL = re.compile(r'^grep -vi "([^"]+)"$')
ARCH_INCL = re.compile(r'^grep -i "([^"]+)"$')


def classify(line, arch):
    stages = [s.strip() for s in line.split(" | ")]  # never bare "|": patterns contain \|
    m = ENDPOINT.match(stages[0])
    if not m:
        return None, "endpoint:other"
    repo, latest = m.group(1), bool(m.group(2))
    if len(stages) < 3 or stages[1] != SED or stages[-1] != "head -1)":
        return None, "shape:other"
    kinds = []
    for s in stages[2:-1]:
        if s in STAGE_KIND:
            kinds.append(STAGE_KIND[s])
            continue
        e = ARCH_EXCL.match(s)
        if e:
            words = set(e.group(1).lower().split("\\|"))
            if words <= ARCHES and not words & SELF[arch]:
                kinds.append("arch_excl")
                continue
        i = ARCH_INCL.match(s)
        if i and set(i.group(1).lower().split("\\|")) <= SELF[arch]:
            kinds.append("arch_incl")
            continue
        return None, "pattern"
    # Arch policy: "excl" = names this arch or none (x86_64 style), "incl" = must name it.
    policy = "incl" if "arch_incl" in kinds else "excl"
    k = sorted("arch_excl" if x == "arch_incl" else x for x in kinds)
    if k in (["appimage_url", "arch_excl"], ["any_url", "appimage_filter", "arch_excl"]):
        asset = "appimage"
    elif k == ["any_url", "arch_excl"]:
        asset = "any"
    else:
        return None, "stages:" + ",".join(k)
    return (repo, ("latest" if latest else "newest") + ":" + asset + ":" + policy), None


def main():
    d, arch = sys.argv[1], sys.argv[2]
    why, conv = Counter(), Counter()
    for app in sorted(os.listdir(d)):
        try:
            with open(os.path.join(d, app), errors="replace") as f:
                lines = [l.strip() for l in f if l.lstrip().startswith("version=")]
        except IsADirectoryError:
            continue
        if not lines:
            why["no version= line"] += 1
            continue
        if "api.github.com" not in lines[0]:
            why["not github"] += 1
            continue
        if len(set(lines)) > 1:
            why["version= lines differ"] += 1  # installer and AM-updater disagree
            continue
        row, reason = classify(lines[0], arch)
        if row:
            conv[row[1]] += 1
            print(f"{app}\t{row[0]}\t{row[1]}")
        else:
            why[reason] += 1
    for k, n in conv.most_common():
        print(f"{n:6} {k}", file=sys.stderr)
    for k, n in why.most_common():
        print(f"{n:6} skip: {k}", file=sys.stderr)


main()
