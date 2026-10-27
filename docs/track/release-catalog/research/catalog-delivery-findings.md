# Persistent catalog publication and exact-prior repeat

2026-10-27, ticket 18. Marek instructed continuation with approval to push and run
workflows. Implemented the next delivery boundary, pushed source revision
`86354b78b0ec00331ce43dfdef354349890e7e49`, and ran exactly two bounded validations:
bootstrap and an exact-prior repeat. No retry, schedule, source expansion or
installed-app change. The first dispatch was at 16:41:58 Europe/Warsaw.

## Published catalog

The new [release-catalog branch](https://github.com/mareklangiewicz/AM/tree/release-catalog)
contains only index.json and six exact body files. It has two ordinary append-only
commits, separate from main-marek source and its historical evidence archives.

| Run | Publication commit | Parent | HTTP outcomes | Collection seconds |
| --- | --- | --- | --- | ---: |
| [40533557297](https://github.com/mareklangiewicz/AM/actions/runs/40533557297) | `efcaeb2f31a62dbae56d8f5be50cce76b2cfb4ef` | none | six 200 | 6.437 |
| [40533858562](https://github.com/mareklangiewicz/AM/actions/runs/40533858562) | `d612ff34b492b337fe51128f769ec9d262d0ee86` | `efcaeb2f31a62dbae56d8f5be50cce76b2cfb4ef` | six 200 | 4.811 |

Both jobs succeeded in both runs. Each collection completed exactly six serial
requests without skips/stops and received 4,877,759 entity bytes. Python 3.12.3/Linux
was recorded. Manifest SHA256 remained
`1c550b882e9855a7a652e44516d88db95046641da92f4b6e34fd65b9a6da87b9`.

The repeat loaded the first published commit and supplied all six exact prior
validator tuples; original sent-condition evidence was independently matched to
the previous index. All responses were 200 and 4 body digests changed.
This establishes persistent prior loading and conditional request wiring, **not a
live 304 outcome**. Synthetic 304 receipt preservation/validation refresh remains
covered offline. No additional collection was made to seek a 304 or wait an hour.

## Independent validation and public reading

Fetched the public catalog branch into a separate bare repository, compared both
commit trees to their respective artifact candidates and reran full storage plus
artifact recomputation. Verified exact parent linkage, source/run/manifest and
per-file hashes. All 12 aliases were read pinned to each full commit, checked for
current freshness and byte integrity. After the second commit, the first pinned
generation still read consistently. The current tree is 4,893,981 bytes.
Current index SHA256: `ecfcb74f40ef064d6766ac54756ff6a246ef515c535399a02b64cfecb446671a`.

Also performed exactly two unauthenticated catalog reads with clean curl config,
no redirects/retries: the index and the selected Obsidian latest body, both at
`d612ff34b492b337fe51128f769ec9d262d0ee86` on raw.githubusercontent.com. They matched the published index
hash and observation length/SHA256. These were catalog reads, not extra upstream
release collection. [Pinned public index](https://raw.githubusercontent.com/mareklangiewicz/AM/d612ff34b492b337fe51128f769ec9d262d0ee86/index.json).

## Privilege and publication checks

GitHub setup logs independently reported contents:read/metadata:read for collection
and contents:write/actions:read/metadata:read for publication in both runs. The
publisher used same-run immutable artifact ID/digest, API run/repository/source
metadata, bounded safe ZIP parsing and complete reconstruction from prior plus
inert evidence before a normal fast-forward push to the fixed ref. No artifact
code was executed; no writer credential reached upstream transport. The write
token is repository-scoped; fixed-ref restriction is enforced by reviewed code.

[Delivery design](../design/catalog-delivery.md) records exact-prior/absence guards,
shallow tree validation, bounded commands, local CAS, the final remote-parent read,
normal push conflict behavior and limits. After both runs, only this manual workflow
remained active; six unrelated/historical workflows remained disabled_manually.
No source push started an experiment.

## Offline checks and post-run archive hardening

66 offline tests passed before the live runs, including local bare-remote bootstrap/
conditional repeat, stale-parent refusal, exact prior planning, artifact mutations,
unsafe ZIP paths/modes and pinned reads. The prior real GitHub artifact ZIP also
passed digest/strict-member parsing and full candidate recomputation.

During final review, added a central-directory count/size check before ZipFile
allocates its member objects; ZIP64/multidisk are deliberately refused in this small
profile. This post-run hardening is verified by a focused early-refusal test,
**67 passing offline tests**, and both actual live artifact ZIPs. It was not exercised
by another live workflow; the two runs above used the exact source revision stated.
No extra source calls were needed to test that parser-only change.

## Persistent evidence and remaining work

[Evidence archive](catalog-delivery-40533557297-40533858562-evidence.tar.gz),
1,614,964 bytes, SHA256 `f73c29f75e667b8ba1de0f6affdf1d539c13b9f5c6661adf291ac4263aeabf22`, contains exact artifact ZIPs,
publication JSON, run metadata, permission summaries, checks, workflow/manifest
snapshots, isolation/public-read evidence and a catalog Git bundle preserving both
published commits. Cloned the bundle offline and verified both trees; verified ZIP
digests again from the archive. [Machine checks](catalog-delivery-checks.json) retain
the full revision/commit/artifact relationships and local Git object measurements.

This is bounded manual remote delivery for six sources, not a fleet scheduler,
long-term retention study, adversarial audit or installer/client migration. The
publication gate currently requires all six successful 200/304 transfers; a failed
collection retains the previous branch rather than publishing a partial update.
Future manual runs must pin the current publication commit explicitly; no fallback,
force push, automatic retry or history rewrite exists. History/storage budgets
remain provisional as documented; live 304, full remote history retention, broader
compatibility and consumer integration remain unverified or separate work.

Next useful step is a small read-only consumer that resolves a publication ref once,
fetches its pinned index plus requested body, enforces freshness/integrity and returns
exact bytes to existing filters. App selection stays in those filters. No schedule
or installed updater should be added merely because this delivery sample succeeded.
