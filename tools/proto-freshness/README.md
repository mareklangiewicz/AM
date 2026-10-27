# Throwaway offline freshness prototype

Ticket 10. Run `node tools/proto-freshness/replay.cjs` (Node 18+ and Git).
It prints a new `PROTOTYPE-freshness-*` directory containing a disposable Git
repository and `report.json`. Delete only that directory to clean up.
No network calls, remote writes, installed apps or package dependencies.

Open `demo.html` directly for free play and guided walkthroughs. Its first script
is an embedded copy of `core.js`; the same pure lookup, 304 and re-enrollment
functions drive both the page and the local Git replay. The browser shell uses
local Web Crypto. The branch movement controls are illustrative, whereas the
runner creates actual commits and reads pinned paths through Git.

All response bytes and measured timestamps are explicitly synthetic. They model
the needed future collector contract, not missing timestamps from the old archive.
The experiment uses six descriptors. Experimental schema 2 adds separate receipt
and validation time bases and alias states; it is not an adopted production schema.
Descriptor matching is intentionally limited to the synthetic release-list URLs.

The runner executes acceptance scenarios, not a production test suite. It checks
freshness and consent boundaries, unknown/unavailable/retired/removed refusals,
separate timing provenance, re-enrollment, exact body integrity and missing pinned
files. It checks caps at exact boundaries and plus one; source/body/index caps
also run through publication. Tree/pack overflow uses injected measured sizes.
No 50 MB tree or 128 MB history is allocated for a boundary check. Tree validation
and cap checks happen before publication writes; ref update compares the expected
parent. Concurrent writer races beyond this bounded runner are not modeled here.

Missing pinned files never fall back to a branch tip or upstream. Acceptance is an
in-memory value bound to full commit, request ID and body SHA-256. It cannot bypass
availability, identity, timing or integrity checks. A new publication requires new
acceptance even if body bytes match. The lookup result is metadata; the adapter
must expose body bytes only for fresh or explicitly accepted-stale results.

This remains a prototype: no whole GitHub schema, hostile index parser, archive
transport, trusted-ref resolver, credential policy, retention service, acceptance
persistence or installer UX. Candidate measurement assumes regular byte maps;
no arbitrary artifact import is added. Remote public visibility remains unproven.
