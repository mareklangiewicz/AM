#!/bin/sh
# Usage from the AM root: sh tools/catalog-probe/inventory.sh OUTPUT_DIRECTORY
set -eu
out=${1:?usage: inventory.sh OUTPUT_DIRECTORY}
mkdir -p "$out"
git rev-parse HEAD > "$out/source-revision.txt"
LC_ALL=C awk -v scripts="$out/scripts.tsv" -f tools/catalog-probe/inventory.awk \
    programs/x86_64/* programs/aarch64/* > "$out/requests.tsv"
awk -F '\t' 'NR > 1 && $3 == "code" && $5 ~ /^release-/ { print $4 }' "$out/requests.tsv" \
    | LC_ALL=C sort -u > "$out/release-request-candidates.txt"
echo 'Inventory complete. Candidate URLs require review; this is not an approved collection manifest.'
