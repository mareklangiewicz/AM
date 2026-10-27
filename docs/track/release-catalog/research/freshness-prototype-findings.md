# Offline client freshness findings

2026-10-27. [Ticket 10](../issues/10-offline-client-freshness.md).
Primary source: commit `694613538` on `proto/offline-freshness-v1`,
`tools/proto-freshness/`. The single HTML walkthrough embeds the same pure core
used by the Node/local Git replay. [Machine report](freshness-prototype-report.json).

## Verdict

The bounded experiment supports the proposed age/availability/consent separation.
The replay recorded 54 outcomes, including 53 successful expected checks/refusals
and one explicitly historical timing demonstration. Six synthetic release-list
sources and synthetic measured timestamps avoid inventing missing completion
times for the real baseline/hour evidence. No collector/client integration,
HTTP request, Actions dispatch or installed-app change occurred.

- Ages 0, 86,399 and exactly 86,400 seconds are fresh. At 86,401 seconds,
  explicit acceptance is required. Acceptance leaves observation times intact.
- Consent binds to full publication commit, descriptor ID and exact body SHA-256.
  Another commit, source or digest cannot reuse it. Unknown/unavailable/retired
  entries and removed aliases refuse even when an old body and acceptance exist.
- A temporary 503 leaves the original validation age intact. A legitimate 304
  updates validation while preserving receipt, with separate timing provenance.
  Historical round-completion receipt or validation bases refuse current lookup.
- Missing/unparseable/invalid calendar timestamps, future validation and future
  publication times refuse. No negative-age clamping or clock tolerance is applied.
- Alias removal is independent of descriptor retirement. Another active alias
  can still reach the same available descriptor under the same freshness rules.
- Re-enrollment resets current observation/validators and availability to unknown,
  retaining historical metadata separately. An old conditional validator cannot
  restore it. The walkthrough also demonstrates a new successful response.
- Reads use the resolved full commit for both index and body. After B appears,
  A remains stale and B can be fresh; missing pinned index/body never falls back.
- Schema/descriptor/alias/manifest identity, body path, hash and length refusals
  precede delivery. The result is a decision; an adapter must expose bytes only
  for fresh or explicitly accepted-stale results.
- Six-source, 8,000,000-byte body, 2,000,000-byte index, 50,000,000-byte tree and
  128,000,000-byte pack limits allow equality and reject plus one. Actual source,
  body and index overflow candidates and an injected pack overflow refuse before
  publication writes. The tree overflow uses the same pure preflight with injected
  measured sizes. All refusals preserve publication B. This does not measure a
  50 MB tree or 128 MB pack. The tiny synthetic pack was 3,150 bytes on this run.

## Review consequences

Commit-bound acceptance is deliberately strict: even identical bytes in a new
publication require fresh acceptance. During an outage this can cause repeated
prompts as unrelated sources publish. The experiment demonstrates that tradeoff;
it does not silently weaken consent to a branch-wide or digest-only policy.

Exactly 24 hours is a proposed inclusive boundary, not an approved installer UX.
No clock skew allowance is a conservative prototype choice and may reject real
clock differences. Operational clock assumptions require review before migration.
Separate receipt_time_basis/validation_time_basis and alias state are modeled in
experimental schema 2; that number is not an adopted production format version.

## Reproduction and limits

Run `node tools/proto-freshness/replay.cjs` from the captured branch (Node 18+ and
Git). It prints a new `PROTOTYPE-freshness-*` directory with local commits and its
report; those disposable commit IDs are not repository source commits and must
be regenerated on another machine. No remotes are configured there.

Open `demo.html` directly. A Node DOM-stub smoke check verified that its embedded
core matches core.js exactly, exercised all 17 guided clicks and checked boundary,
consent and unavailable-state displays. This is not browser visual QA. The HTML
uses local Web Crypto; no packages or server are required. No test suite was added.

The candidate validator and index parser are bounded fixture code, not a hardened
untrusted-publication importer or full GitHub schema validator. The prototype does
not claim arbitrary hostile-input safety. Descriptor classes are intentionally
limited to the synthetic release-list fixture. Concurrent publication races beyond
the bounded local experiment, remote transport, trusted ref resolution, public
visibility, acceptance persistence and installer UX remain outside scope.

[Ticket 11](../issues/11-review-client-and-collection-boundaries.md) records the
review frontier. No production code has been merged from this prototype.
