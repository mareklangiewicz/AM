#!/bin/sh
# PROTOTYPE, throwaway: see docs/design/version-catalog.md.
# Resolve recipe rows to the newest few matching release assets via GraphQL.
# Usage: resolve.sh <recipes.tsv> <arch> <cache dir> > catalog.tsv
# Needs gh (authenticated) and jq, both preinstalled on GitHub runners.
# Raw responses are cached per batch in <cache dir>, so reruns cost nothing.
set -u
recipes="$1" arch="$2" cache="$3"
here=$(dirname "$0")
tab=$(printf '\t')
mkdir -p "$cache" || exit 1

# fetch NREL REPO...: print the path of the cached GraphQL response for one batch.
fetch() {
	nrel="$1"
	shift
	f="$cache/$(printf '%s %s' "$nrel" "$*" | sha1sum | cut -c1-16).json"
	if [ ! -s "$f" ]; then
		q="query { rateLimit { cost remaining }"
		i=0
		for r in "$@"; do
			q="$q r$i: repository(owner: \"${r%%/*}\", name: \"${r#*/}\") { nameWithOwner
  releases(first: $nrel, orderBy: {field: CREATED_AT, direction: DESC}) {
    nodes { tagName createdAt publishedAt isPrerelease isLatest
      releaseAssets(first: 50) { nodes { name size digest } } } } }"
			i=$((i + 1))
		done
		gh api graphql -f query="$q }" > "$f"
		jq -r '"batch cost \(.data.rateLimit.cost) remaining \(.data.rateLimit.remaining)"' "$f" >&2
	fi
	echo "$f"
}

# flatten NREL BATCHSIZE < repo list: fetch in batches, print assets.tsv rows (see pick.awk).
# Rows are keyed by the repo as the recipe spells it, lowercased, since GraphQL
# answers with the current name of a renamed repo.
flatten() {
	xargs -n "$2" echo | while read -r batch; do
		# shellcheck disable=SC2086 # one word per repo
		f=$(fetch "$1" $batch)
		jq -r '.errors[]? | "error: \(.type) \(.message)"' "$f" >&2
		jq -r --arg repos "$batch" '($repos | ascii_downcase | split(" ")) as $names
			| .data // {} | to_entries[] | select(.key | test("^r[0-9]+$")) | select(.value)
			| $names[.key[1:] | tonumber] as $repo
			| .value.releases.nodes as $rels
			| ([$rels[].isLatest] | index(true) // -1) as $latest
			| [$repo, -1] , ($rels | to_entries[] | .key as $d | .value as $r | $r.releaseAssets.nodes[]
				| [$repo, $d, $latest, $r.isPrerelease, $r.tagName, $r.publishedAt, .name, .size,
					(.digest // "" | sub("^sha256:"; ""))])
			| @tsv' "$f"
	done
}

pick() {
	LC_ALL=C sort -t "$tab" -k1,1 -k2,2n -k7,7 "$1" | awk -v arch="$arch" -v nomatch="$2" -f "$here/pick.awk" "$recipes" -
}

work=$(mktemp -d) || exit 1
trap 'rm -rf "$work"' EXIT
cut -f2 "$recipes" | LC_ALL=C sort -u > "$work/repos"
flatten 5 25 < "$work/repos" > "$work/assets"
: > "$work/deep"
pick "$work/assets" "$work/deep" > /dev/null 2>&1
# Second pass, deeper, only for repos where some recipe matched nothing:
# today's /releases scan falls through up to 30 releases.
LC_ALL=C sort -o "$work/deep" "$work/deep"
echo "deep pass: $(wc -l < "$work/deep") repos" >&2
flatten 30 5 < "$work/deep" > "$work/deepassets"
tr '[:upper:]' '[:lower:]' < "$work/deep" | awk -F "$tab" 'FNR == NR { deep[$1] = 1; next } !($1 in deep)' - "$work/assets" > "$work/merged"
cat "$work/deepassets" >> "$work/merged"
pick "$work/merged" /dev/null
