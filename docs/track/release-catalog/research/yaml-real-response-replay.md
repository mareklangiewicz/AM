# Real saved-response replay and collector adapter — November 4, 2026

[87](../issues/87-replay-real-responses-and-prepare-adapter.md), prototype
`125a2ff9d` on `prep/yaml-offline-publication`. This is offline evidence and a
source adapter candidate, not an operational format switch.

## Saved-data result

The tracked `appimage-batch-20261102/release-*/{report,body}.json` evidence contains
44 successful response bodies: 41 numeric release-list endpoints and three
latest-only endpoints. Initial inspection counted all 44 together; replay excludes
the three latest-only bodies explicitly rather than relabeling them as list pages.
Forty list requests used default 30-release pages; one requested per_page=100.
Their body lengths and SHA-256 hashes match the retained acquisition reports.

The 41 list responses contain 914 releases and 14,242 assets in 27,821,797 raw
bytes. Published repository YAML totals 5,259,677 bytes; largest source
`16089035` is 1,251,974 bytes. All source documents fit the proposed 2 MiB cap in
this replay; that does not accept the cap or establish a worst-case bound.
Individual sizes/hashes/evidence paths are in `real-replay-results.json`.

The replay bootstraps a complete local snapshot, loads it, replays the original
attempts in their two explicit page-size groups and loads the resulting pinned
snapshot. Release facts, shared observation times and last-success metadata match
across replay. Original receipt times are preserved at schema whole-second
precision; replay time is not substituted. An independent saved-object comparison
checks release IDs/tag/title/URL/publication/prerelease and asset IDs/names/URLs/
sizes/content types for every release/asset. That fact comparison was run separately
after adding it to the replay harness; the complete publication run preceded that
oracle addition. Saved identities supply readable names when available; otherwise
the saved release URL supplies the readable owner/name. Numeric identities come
from the recorded numeric descriptors. Generated `source-ID` aliases and example
schema URLs are fixtures, not actual AM enrollment or production schema pins.

The largest source's complete `browse.sh` command returns identical 30-row hashes:
mawk 1.454 s, GNU awk 2.577 s, BusyBox 8.495 s. These include the example's two
repository parses. Total full offline replay took 175.136 s, including repeated
whole-tree validation, PyYAML, Git and local host load. This is neither live
collection timing nor a 100-release-default capacity result. BusyBox compatibility
works, but mawk/GNU awk remain preferable for larger ordinary queries.

## Small adapter candidate

`attempt_adapter.py` maps existing collector attempt body/outcome/status, numeric
identity/list descriptor and recorded receipt time into existing retained merges.
The caller supplies explicit validated `has_next` metadata. It connects pinned
loading and local publication without changing transport or consumer machinery.
The retained model now imports the reusable writer directly, avoiding test-fixture
imports. No caching, daemon, raw-body archive or watchdog was added.

Six focused tests pass: original receipt/partial retention, later-page rollback,
lazy finite scope, wrong identity/latest/304/duplicate-JSON refusal, transport/rate
outcomes and invalid receipt handling. The existing three-tool closed-loop refresh
experiment also passes after the import change: twelve snapshots/reads and twelve
rejected operations. Compilation and whitespace checks pass. Other historical
matrices retain their recorded revisions.

## Production integration review

The remaining adapter diff has concrete seams:

- Configure unconditional numeric **list** requests at the chosen page size/scope;
  latest-only routes cannot implement this catalog model.
- Supply validated pagination metadata and retain existing collector transport
  limits. This candidate neither parses arbitrary Link headers nor fetches pages.
- Feed completed attempts and the previous pinned format-2 source set into this
  adapter; carry the real app map and unselected repositories forward.
- Stage the validated YAML tree through the publication workflow using an actual
  reviewed source/schema revision. Existing format-1 validators/workflows are not
  compatible by merely changing filenames.

A 304 response is deliberately unsupported: retained facts do not record which
releases belonged to the prior partial page. Reobserving every retained release
would change freshness incorrectly. Unconditional list bodies keep the first
integration simple; adding membership/cache machinery is not proposed here.

Production file caps and initial enrollment/bootstrap still need an explicit
choice. No live request, workflow edit/dispatch, remote catalog publication,
daily repin, installed consumer change or production-format migration occurred.
Source pushes remain separately authorized from operational publication.
