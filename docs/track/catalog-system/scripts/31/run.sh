#!/bin/sh
# Ticket 31's counts, at the commits it measured. Reads Git objects only.
# Usage: run.sh OUT_DIR   (match.py takes about a minute)
set -eu
out=${1:?usage: run.sh OUT_DIR}
here=$(cd "$(dirname "$0")" && pwd)
repo=$(git -C "$here" rev-parse --show-toplevel)
upstream=ba061a639a50260b6be405b15b22be10be328264
ours=36c087049957734cd10b0aa4c509e5520b46d93b
mkdir -p "$out"
python3 -I "$here/versions.py" "$repo" "$upstream" "$out/versions.json"
python3 -I -B "$here/match.py" "$repo" "$upstream" "$ours" "$out/versions.json" "$out/matches.json"
python3 -I "$here/table.py" "$out/versions.json" "$out/matches.json" > "$out/table.md"
python3 -I "$here/queries.py" "$out/versions.json" "$out/matches.json" > "$out/versions-split.txt"
echo "wrote $out/table.md and $out/versions-split.txt"
