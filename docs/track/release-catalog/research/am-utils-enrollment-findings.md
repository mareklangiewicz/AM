# am-utils identity enrollment evidence

2026-10-28. Ticket [47](../issues/47-enroll-scoped-migration-sources.md).
The user approved the review package's one bounded unauthenticated repository
identity GET. Exactly one request was performed; no source push, release request,
collection, publication, workflow change or installed operation occurred.

## Reviewed identity

`GET https://api.github.com/repos/ivan-hc/am-utils` returned HTTP 200 at
2026-10-28T19:16:18.342103+00:00. The exact response establishes:

- Repository ID: **1225768109**, a positive integer distinct from this fork's
  workflow repository ID 1291019762.
- full_name: **ivan-hc/am-utils**, matching the expected name.
- private: **false**; visibility: **public**.

[Body](am-utils-enrollment-20261028/body.json): 4965 bytes, SHA256
`d52aff9b6e7e7ea1772320847f1d879dd9c33a9930ad5f582cef9dfe29587e19`.
[Headers](am-utils-enrollment-20261028/headers.txt): 1323 bytes, SHA256
`3041a080f2b671c9127e678cd72865a11312f012c149c4378221f9447310bc76`.
[Report](am-utils-enrollment-20261028/report.json) records exact start/completion,
public headers, status, identity checks and elapsed monotonic time 0.556822 seconds.
Curl exited 0, parent termination is absent and Content-Length matches body length.

The [saved runner](am-utils-enrollment-20261028/request.py) uses curl -q first,
an allowlisted environment, direct verified HTTPS, HTTP/1.1, pinned API version
2022-11-28/Accept headers and identity encoding. No authentication, ambient proxy,
netrc/config, redirects, retries or follow-ups. Connect timeout is 10 seconds;
parent and curl enforce a 30-second overall deadline. The parent bounds both
streams at 64,000 bytes with one overflow sentinel and kills/reaps on overflow or
deadline. Retained header values are checked at 8192 bytes. Existing report evidence
prevents accidental repeat execution. The successful response fits every bound;
this run alone does not test all failure paths or establish release transport cost.

## Next stage remains separate

After committing this evidence, the candidate numeric fetch descriptor can be
`https://api.github.com/repositories/1225768109/releases`, with the exact alias
`https://api.github.com/repos/ivan-hc/am-utils/releases`. Compute the request ID
from that numeric descriptor and retain this reviewed identity anchor. Begin with
no conditional validators; repository metadata ETag is not a release validator.

The numeric release route remains unrequested and unverified. This identity read
neither enrolls a seventh operational source nor establishes selectors for the
356 recipes, release-body size or publication capacity. Tickets 48/49 stay blocked;
ticket 47 stays claimed/partial. The next live release read requires its own exact
bounded proposal and authorization. Existing six-source manifest, approved pilot
source pin, schedule and publication are unchanged.
