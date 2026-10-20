# version-catalog

POSIX sh generator of a TSV catalog of AM app versions (x86_64).

    ./catalog.sh [AM_DIR] [CACHE_DIR] > versions.tsv    # GITHUB_TOKEN optional

Columns (header line `#name repo tag date size url status`, tab-separated, `-` = empty):
status is `ok`, `unknown` (version line is not api.github.com/repos/O/R/releases[/latest]),
`error` (fetch failed) or `archived` (reserved, not yet produced).

- Repos are deduplicated; one `/releases/latest` request per repo.
- Conditional requests: ETag stored in CACHE_DIR, sent as If-None-Match (304 = free).
- Stops fetching when x-ratelimit-remaining hits 0; remaining repos become `error`.
- size/url are the FIRST asset of the latest release, not the script's own grep filter.
- Overrides: VC_CURL (tests stub), VC_API.

Tests: `shellspec -s dash` (also passes under bash). No network.

    awk -F'\t' '$7=="ok"' versions.tsv | sort -t"$(printf '\t')" -k4r | head
