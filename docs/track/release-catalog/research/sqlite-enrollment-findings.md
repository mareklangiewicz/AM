# SQLite Browser identity enrollment

2026-10-27. The user explicitly authorized pushing f8182c6e9 and exactly one
unauthenticated metadata GET. The push succeeded before the request. No workflow
was activated and no release collection was authorized or performed.

## Reviewed identity

Exactly one GET to https://api.github.com/repos/sqlitebrowser/sqlitebrowser returned
HTTP 200 at 2026-10-27T15:13:12.572062+00:00. Its exact JSON body reports:

- id: **19416551** (positive integer)
- full_name: **sqlitebrowser/sqlitebrowser** (expected name)
- private: **false**
- visibility: **public**

The response satisfies all proposed identity enrollment checks. The
[exact body](sqlite-enrollment-20261027/body.json),
[wire headers](sqlite-enrollment-20261027/headers.txt) and
[machine report](sqlite-enrollment-20261027/report.json) are retained in Git.
Body: 6947 bytes, SHA256 `77afcf9cf7db587b650567cf8e2bfa2566ebe1d03eacc8ddbc975686d2ff524f`.
Headers: 1323 bytes, SHA256 `86e0da79477d3be101feb24bcd7954faf94df76d273f5337d2cf690193c5fd80`.
Elapsed local monotonic time: 0.497 seconds.

The one curl process used -q first, an allowlisted environment, --noproxy '*',
--proto '=https', --http1.1, --max-redirs 0, no --location/retry/auth/netrc flags,
--connect-timeout 10, --max-time 30, --max-filesize 64000, the pinned API/Accept
headers and identity encoding. A parent select loop independently enforced 30
seconds and bounded captured headers/body at 64,000 bytes each; selected retained
header values were checked through the collector's 8,192-byte limit. System TLS
verification stayed enabled. Curl exit 0 and Content-Length 6947 match the saved
body. No redirect, retry, follow-up or actual credential was used. The process was
reaped. This was the separately approved metadata tool, not the supervised release
adapter; it does not establish live behavior of that adapter.

## Enrolled manifest and next approval

The sixth row of staged-manifest.json now uses numeric ID 19416551 and this
reviewed evidence. Its consumer alias is preserved; the new fetch descriptor has
a new request ID. No previous validators are imported. The enrolled manifest SHA256
is `1c550b882e9855a7a652e44516d88db95046641da92f4b6e34fd65b9a6da87b9`. The earlier package's incomplete-manifest hash and refusal
are historical evidence, superseded by this reviewed enrollment.

The exact numeric SQLite release route, like the other candidate numeric routes,
remains unverified. The six-release baseline is still separately authorized work:
serial, at most six GET attempts, no redirects/retries/pagination/fallback, using
the staged manifest. The candidate workflow remains outside .github/workflows.
Activation must be approved before installation; record the resulting pushed
commit and manifest hash and recheck server-side workflow isolation before
requesting dispatch. The approved f8182c6e9 push is complete. The enrollment follow-up is committed
locally; its push, workflow activation and collection are not performed here.

## Offline verification after enrollment

49 tests pass on Python 3.14.4/Linux: 17 collector, 20 transport, four workflow
preflight and eight historical churn tests. The new real-manifest check validates
all six rows without creating a worker. Missing-identity refusal is retained as an
explicit in-memory mutation; synthetic ID 999 remains test-only. git diff --check
passes. The workflow proposal is unchanged and remains inactive.
