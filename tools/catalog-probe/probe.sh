#!/bin/sh
# Bounded read-only probe. Run in Actions with GH_TOKEN and an output directory.
set -eu

out=${1:?usage: probe.sh OUTPUT_DIRECTORY}
: "${GH_TOKEN:?GH_TOKEN must be the workflow token}"
mkdir -p "$out"

request() {
    name=$1
    endpoint=$2
    shift 2
    : > "$out/$name.json" # A 304 response may not create an output file.
    status=$(curl --silent --show-error --max-time 60 \
        --header "Authorization: Bearer $GH_TOKEN" \
        --header 'Accept: application/vnd.github+json' \
        --header 'X-GitHub-Api-Version: 2022-11-28' \
        --header 'User-Agent: AM-catalog-probe' \
        --dump-header "$out/$name.headers" \
        --output "$out/$name.json" --write-out '%{http_code}' \
        "$@" "https://api.github.com/$endpoint")
    printf '%s\n' "$status" > "$out/$name.status"
    printf '\n%s: HTTP %s; bytes %s\n' "$name" "$status" "$(wc -c < "$out/$name.json" | tr -d ' ')"
    awk 'tolower($0) ~ /^(etag|x-ratelimit-[^:]*|retry-after|date):/ { sub(/\r$/, ""); print }' "$out/$name.headers"
    case "$status" in
        200|304) ;;
        *) echo 'Request failed; stopping without retry.' >&2; exit 1 ;;
    esac
}

# Capture baseline independently for REST and GraphQL; these are separate budgets.
request rate-before rate_limit
jq -e '.resources.core and .resources.graphql' "$out/rate-before.json" >/dev/null
jq '{core: .resources.core, graphql: .resources.graphql}' "$out/rate-before.json"

request rest-first repos/obsidianmd/obsidian-releases/releases
jq -e 'type == "array"' "$out/rest-first.json" >/dev/null
etag=$(awk 'tolower($0) ~ /^etag:/ { sub(/^[^:]*:[[:space:]]*/, ""); sub(/\r$/, ""); value=$0 } END { print value }' "$out/rest-first.headers")
if [ -n "$etag" ]; then
    request rest-conditional repos/obsidianmd/obsidian-releases/releases --header "If-None-Match: $etag"
    if [ "$status" = 200 ]; then
        jq -e 'type == "array"' "$out/rest-conditional.json" >/dev/null
        echo 'Conditional read returned 200; compare observations before inferring cache behavior.'
    fi
else
    echo 'No ETag returned; conditional request not performed.'
fi

# Fixed, deliberately small query. No scripts, version ranking, or asset selection.
cat > "$out/query.graphql" <<'QUERY'
query {
  rateLimit { cost remaining resetAt }
  obsidian: repository(owner: "obsidianmd", name: "obsidian-releases") {
    nameWithOwner
    releases(first: 5, orderBy: {field: CREATED_AT, direction: DESC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        tagName name createdAt publishedAt isPrerelease isLatest
        releaseAssets(first: 50) {
          pageInfo { hasNextPage endCursor }
          nodes { name size digest downloadUrl }
        }
      }
    }
  }
  neovim: repository(owner: "neovim", name: "neovim") {
    nameWithOwner
    releases(first: 5, orderBy: {field: CREATED_AT, direction: DESC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        tagName name createdAt publishedAt isPrerelease isLatest
        releaseAssets(first: 50) {
          pageInfo { hasNextPage endCursor }
          nodes { name size digest downloadUrl }
        }
      }
    }
  }
}
QUERY
jq -n --rawfile query "$out/query.graphql" '{query: $query}' > "$out/query.json"
request graphql graphql --header 'Content-Type: application/json' --data-binary "@$out/query.json"
jq -e '((.errors // []) | length == 0) and (.data.obsidian != null) and (.data.neovim != null) and (.data.rateLimit != null)' "$out/graphql.json" >/dev/null
jq '.data | {rateLimit, repositories: [(.obsidian, .neovim) | {nameWithOwner, releases: (.releases.nodes | length), moreReleases: .releases.pageInfo.hasNextPage, truncatedAssets: [.releases.nodes[] | select(.releaseAssets.pageInfo.hasNextPage) | .tagName]}]}' "$out/graphql.json"

request rate-after rate_limit
jq '{core: .resources.core, graphql: .resources.graphql}' "$out/rate-after.json"
echo 'Probe finished. This is one small observation, not a capacity or long-term cache benchmark.'
