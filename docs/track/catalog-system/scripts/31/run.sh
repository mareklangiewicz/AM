#!/bin/sh
# Ticket 31's numbers, at the commits it measured. Reads Git objects only.
# Usage: run.sh OUT_DIR   (match.py takes about a minute)
set -eu
out=${1:?usage: run.sh OUT_DIR}
here=$(cd "$(dirname "$0")" && pwd)
repo=$(git -C "$here" rev-parse --show-toplevel)
upstream=ba061a639a50260b6be405b15b22be10be328264
ours=36c087049957734cd10b0aa4c509e5520b46d93b
resolved=539ccac8d9   # ticket 31 resolved: its layouts.json had the two reviewed layouts
base=7b4f831e6        # the bulk conversion's merge base
mkdir -p "$out"
git -C "$repo" show "$resolved:tools/recipe-conversion/layouts.json" > "$out/layouts.json"
git -C "$repo" ls-tree -r --name-only "$base" -- programs/x86_64 programs/aarch64 programs/i686 programs/armv7l \
	> "$out/base_paths.txt"
git -C "$repo" grep -l -e 'Which version you choose' "$upstream" -- \
	'programs/x86_64/*' 'programs/aarch64/*' 'programs/i686/*' 'programs/armv7l/*' | sed "s|^$upstream:||" > "$out/choice.txt"
python3 -I "$here/versions.py" "$repo" "$upstream" "$out/versions.json"
python3 -I -B "$here/match.py" "$repo" "$upstream" "$ours" "$out/versions.json" "$out/matches.json"
python3 -I "$here/table.py" "$out/versions.json" "$out/matches.json" > "$out/table.md"
python3 -I "$here/queries.py" "$out/versions.json" "$out/matches.json" > "$out/versions-split.txt"
python3 -I "$here/report.py" "$out/versions.json" "$out/matches.json" "$out/layouts.json" > "$out/report.txt"
python3 -I "$here/origins.py" "$out/versions.json" "$out/matches.json" "$out/base_paths.txt" "$repo" "$upstream" \
	"$out/layouts.json" > "$out/origins.txt"
python3 -I "$here/loose.py" "$out/versions.json" "$out/matches.json" "$out/choice.txt" > "$out/loose.txt"
echo "wrote $out: table.md versions-split.txt report.txt table.json origins.txt loose.txt"
