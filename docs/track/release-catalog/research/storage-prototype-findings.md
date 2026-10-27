# Offline storage/publication prototype findings

2026-10-27. Ticket [08](../issues/08-offline-storage-prototype.md).
Primary source: commit `bff0d5bf2` on `proto/offline-storage-v1`, `tools/proto-storage/offline.py`,
`demo.html` and README. No production module or remote publication was created.
The [machine report](storage-prototype-report.json) preserves the exact replay
results, input archive hash, local publication commits and fixture manifest.
Local publication commit objects are disposable; rerun the captured source to
regenerate them. Commit IDs and compressed commit-object sizes vary with time.

## Answer

The bounded offline experiment supports the proposed separation of exact response
bytes, freshness/availability and atomic commit-pinned publication. All 64 replay
checks passed using the complete baseline/hour archive plus synthetic failures.
The question is answered for these fixtures, not all possible upstream content.

- All twelve saved response bodies remain byte-for-byte identical after apply.
- A conditional 304 retains bytes/receipt time/validators, advances validation,
  and does not inherit old attempt quota/date headers. Missing bodies, missing or
  wrong conditions and mismatched descriptors refuse the entire candidate.
- Empty lists replace older nonempty data. Timeout, 429, 5xx and evidenced rate-limit
  403 retain freshness and availability. Absence, redirects, auth refusals and
  invalid/oversized/draft bodies retain evidence but make current reads unavailable.
  Later temporary failures do not clear a refusal. New failed sources stay unknown.
- Retirement retains alias tombstones. Changed targets get new identities and
  cannot reuse validators. Alias target, descriptor, manifest hash, schema,
  timestamps, body hash/path, duplicate keys, public enrollment, sensitive headers,
  unexpected files, symlinks and executable modes were exercised.
- A reader pinned to A reads the original body after B appears. A stale-parent
  publication refuses and leaves B intact. Publication uses Git's atomic
  expected-old-value ref update as well as a preliminary parent check.
- Retired-source lookup refuses. App-specific release/asset selection is absent.

## Schema refinements exposed by replay

The prototype embeds the reviewed manifest beside its digest, allowing validation
of membership and retired entries without a separate hidden input. This is a
candidate refinement, not acceptance of a production schema.

The saved probe records request-start times and round completion, not individual
receipt/validation completion. The fixture uses round completion as a labelled
upper bound (`timing_basis=saved-round-completion-upper-bound`). This does not
establish exact historical freshness. A later 304 does not relabel original
receipt timing. A future collector must measure actual response completion;
these fixture times must not enter a production publication as measured times.

The fixture manifest explicitly asserts reviewed public enrollment for the six
already approved sample sources, with no privileged visibility. This is not an
automated proof from authenticated response content. Actual public enrollment
and exclusion of privileged visibility still require an operational method.

Removal of an alias alone, re-enrollment of retired IDs and future representation
versions are deliberately not generalized. Re-enrollment refuses until policy is
explicit. A reviewed target remap gets a new ID while retaining the old entry.

## Storage measurements

Git 2.53.0; bytes unless stated otherwise. Raw `count-objects -v` fields use Git's
KiB accounting; filesystem measurements below use exact bytes.

| Measurement | Baseline | Hour |
| --- | ---: | ---: |
| Exact response bodies | 4,877,752 | 4,877,754 |
| Index including manifest/provenance | 11,868 | 11,868 |
| Loose object file bytes newly present at that stage | 428,594 | 428,486 |
| Full repack, pack plus index | 335,312 | 340,383 |

Full-repack growth is 5,071 bytes with `repack -adf --window=10 --depth=50`.
Incremental `git gc` instead produced 368,753 bytes after the hour publication,
33,441 more than the baseline pack. Repacking existing deltas can retain a larger
layout; this experiment records the difference without choosing a retention or
maintenance policy. No force push/history rewriting is involved.

The earlier probe's 4,324-byte growth used a smaller diagnostic index and different
paths/tree metadata. This publication index adds descriptors, manifest, aliases,
body hashes, validators, availability and timing/provenance. The measurements
therefore need not match. Tiny commit-object differences also depend on run time.
Six endpoints over one hour still cannot establish fleet/annual storage bounds.

## Validation and limits

Run `python tools/proto-storage/offline.py` from the captured branch; it creates a
new temporary directory and prints its location. No network or remote path exists
in the runner, and the temporary repository has no remotes. No new test suite was
added: the runner is itself the bounded acceptance experiment. HTML script syntax
was checked with Node; its UI has not been browser-tested. The walkthrough is an
explicitly illustrative in-memory reducer, separate from the Python replay.

The shape validator checks six-source release structure and draft exclusion,
not the entire GitHub API schema. The client helper proves selective commit-pinned
consistency; it deliberately does not implement stale acceptance, freshness expiry,
ref transport or hosting. Symlink/executable checks apply to disk import; the pure
apply input is a closed map of path-to-bytes, never an executable artifact.

Remote delivery, real public-source enrollment, privilege isolation, scheduling,
retention thresholds and client migration remain unimplemented. Review the schema
and these limits before any operational implementation. No push, HTTP request,
Actions dispatch, installed-app change or new authorization is implied.
