#!/bin/sh
# PROTOTYPE, throwaway: see docs/design/version-catalog.md.
# Compare the resolver's first pick with what each script's own version= line picks.
# Usage: shadow.sh <programs/arch dir> <sample recipes.tsv> <catalog.tsv> <cache dir>
# The script's pipeline runs with curl replaced by `cat` of a REST response
# fetched once (authenticated, via gh) and cached: one REST call per repo.
set -u
progdir="$1" sample="$2" catalog="$3" cache="$4"
tab=$(printf '\t')
mkdir -p "$cache" || exit 1

while IFS="$tab" read -r app _ conv; do
	line=$(grep -m1 '^[[:space:]]*version=' "$progdir/$app" | sed 's/^[[:space:]]*//')
	endpoint=$(printf '%s\n' "$line" | grep -o "https://api\.github\.com/repos/[^' ]*" | head -1 | sed 's|https://api.github.com/||')
	body="$cache/$(printf '%s' "$endpoint" | tr / _).json"
	[ -s "$body" ] || gh api "$endpoint" > "$body"
	url=$(APP="$app" BODY="$body" sh -c 'curl() { cat "$BODY"; }; eval "$1"; printf %s "$version"' sh "$line")
	first=$(awk -F "$tab" -v a="$app" '$1 == a { print $2 "/" $4; exit }' "$catalog")
	# Decode what GitHub escapes in tags: @ and + (and spaces in asset names).
	picked=$(printf '%s' "${url#https://github.com/*/releases/download/}" | sed 's/%40/@/g; s/%2[Bb]/+/g; s/%20/ /g')
	if [ -z "$url" ] && [ -z "$first" ]; then v="both empty"
	elif [ -z "$url" ]; then v="script empty"
	elif [ -z "$first" ]; then v="catalog empty"
	elif [ "${url#https://github.com/*/releases/download/}" = "$url" ]; then v="script url not a release download"
	elif [ "$picked" = "$first" ]; then v="same"
	elif [ "${picked%%/*}" = "${first%%/*}" ]; then v="same tag, other asset"
	else v="other tag"
	fi
	echo "$conv $v" >&2
	[ "$v" = same ] || printf '%s\t%s\t%s\tscript=%s\tcatalog=%s\n' "$v" "$app" "$conv" "$url" "$first"
done < "$sample" 2>&1 >&3 | sort | uniq -c >&2
