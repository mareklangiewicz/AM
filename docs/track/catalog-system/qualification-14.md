# Scale, compatibility and recovery qualification

November 8, 2026. Ticket 13 is resolved with Marek's explicit device/screen-reader/
comprehension deferrals and the recorded timing misses preserved. Ticket 14 is
claimed, not resolved. These checks do not activate collection, enroll sources,
change installed hosts or establish live quotas/throughput.

## Complete synthetic source tree

```
python3 -B tools/catalog-collector/qualify_scale_tree.py \
  --saved-data /tmp/am-browser-review-data-20261108 \
  --work NEW_DIRECTORY
```

[Receipt](scale-tree-14.json). A hash-checked archive supplies 499 distinct saved
source shapes, repeated deterministically to 5,000 synthetic identities and
distinct numeric sources. The original shape range is 1–33 retained releases,
1–1,750 total retained assets/source and 1,109–401,944 bytes/source. Original
release/asset facts and observations are retained as synthetic template content;
repository identities/names are explicitly synthetic. No new observation is
claimed. One source is replaced by a valid 32-prerelease-plus-older-stable boundary
fixture, with synthetic title padding to 2,097,024 bytes (128 bytes below the cap).
An early fixture with 33 prereleases was refused by the maintained retention
validator and corrected before the completed run; it was not accepted as capacity
evidence.

The complete tree has 5,000 apps, 5,000 sources, 5,000 provenance partitions and
two roots: **10,002 documents / 319,417,844 logical YAML bytes**. The maintained
full candidate validator checks every document, source identity and schema/
recipe/rule reference. It passes in 751.1 seconds; preparation takes 61.3 seconds.
Python high-water RSS is 401,544 KiB (392.1 MiB). An inherited 2 GiB address-space
cap bounds the Python process and each child, not their simultaneous RSS sum.
No upstream request, received byte or charged byte occurs in this saved test.

Tree/file counts have more than 25% unused allowance under the existing 1 GiB /
20,000-file v3 safeguards. The boundary source intentionally has almost no unused
document allowance; it is a supported-limit stress case, not an ordinary-source
headroom claim. All-supported-document browser processing is still unqualified.

The first low-level publication **refuses `history_bound` in an empty repository**:
the old guard charges 319,417,844 uncompressed YAML bytes against a 268,435,456-byte
Git-object cap. Its ref remains absent. Passing domain validation is therefore
not recorded as initial publication/capacity acceptance.

## Git-object accounting correction

```
python3 -B tools/catalog-collector/qualify_scale_storage.py \
  --qualified-work QUALIFIED_TREE_DIRECTORY --work NEW_STORAGE_DIRECTORY
python3 -B tools/catalog-collector/qualify_scale_publication.py \
  --qualified-work QUALIFIED_TREE_DIRECTORY \
  --storage-receipt NEW_STORAGE_DIRECTORY/receipt.json \
  --work NEW_PUBLICATION_DIRECTORY
```

[Storage probe](scale-storage-14.json). On exactly that fixture, Git writes
76,373,769 loose-object bytes and packs the reachable graph into 62,144,855 bytes
(plus a 281,240-byte index). The probe creates only an unreferenced measurement
commit, not a ref or a publication. Repeated saved shapes improve packing; this
does not represent 5,000 independently sampled real sources or growing history.

The guard is corrected without raising the 256 MiB cap: count existing physical
objects, compressed changed blobs and conservative tree/commit space. Pin loose
compression to level 6, then check actual stored bytes again before the atomic ref
advance. A failed final check may leave unreachable staging objects, never a
changed last-good ref. Tree/document limits remain independent. A regression
first failed with `history_bound` on compressible logical data larger than its
small test storage cap; it now passes. Incompressible over-cap growth still
refuses and preserves the exact ref, including an injected faulty estimate.

[Affected-publication receipt](scale-publication-14.json). Every fixture byte is
rehashed against the storage manifest, then the actual low-level publisher writes
the same tree to a new disposable repository. It uses 63,040,276 object bytes;
the conservative guard charges 63,273,798 bytes, leaving **76.4% unused allowance**.
The check takes 80.2 seconds with 342,184 KiB Python high-water RSS. This reruns
the affected guard/write path, not the unchanged 751-second parser suite or a
fresh-process end-to-end CLI. The receipt identifies the exact publisher file
hash measured before the subsequent unchanged-blob optimization.

The same-process `Candidate` now exposes validated blob IDs/sizes only while its
validation rules and exact parent still match. Publication skips unchanged body
reads, rather than materializing and hashing the entire parent again. A focused
regression reproduced reads of apps/provenance/source bodies on a root-only
update; the corrected path reads none. Changed-rule and wrong-parent reuse
refuse. Imported validation receipts still cannot establish production trust.
Publisher schema authority similarly reads only the bounded descriptor at the
exact trusted expected parent; the candidate artifact still receives full domain
validation. Reading one authority field does not import trust in parent blobs.

## Maintained selection compatibility

```
python3 -B tools/catalog-collector/qualify_selections.py \
  --saved-data /tmp/am-browser-review-data-20261108 \
  --legacy-repo SAVED_EVIDENCE_REPO --output OUTPUT_JSON
```

[Receipt](selection-parity-14.json). All 57 currently enrolled installation
declarations, covering 55 numeric sources, produce successful identical policy
results. The maintained v2 shell reader supplies original `asset_facts`; expanded
v3 facts are fed into the same actual maintained awk policy. Every shared release
record also matches its original full facts, including effective observations and
reconstructed asset values. Thirty-two recipe comparisons involve removal of
legacy release records under the accepted v3 retention/tag rules; their selected
results nevertheless match. This compares the actual maintained policy choices,
not invented filename selectors or executed recipes.

The clock is each source's original successful collection time, deliberately not
current installation freshness acceptance. The v2 baseline remains
`cbda9fb78ce4a6f29bdabd63d57f3c0085e8744f`; all saved content hashes are checked.
This does not migrate or qualify installed v3 transport. The existing inventory
of 529 format-2 source recipes (57 declarations / 472 transitional) still describes
source files, not installed hosts or unknown external readers. Format-2 delivery
and retirement remain separately scoped.

## Exact retained site-artifact recovery

```
python3 -B tools/catalog-browser/qualify_restore.py \
  --archive RETAINED_ZIP --sha256 ARCHIVE_SHA256 \
  --source 2d2f7fbeceaef17a48a47bd203677aeb4ebdd231 \
  --work NEW_RESTORE_DIRECTORY
```

[Receipt and file hashes](site-restore-14.json). Read-only GitHub access retrieved
artifact 13625182558 from deployment run 42501013188. The downloaded 5,842,503-byte
ZIP exactly matches GitHub's recorded SHA-256
`83db503db35e55eac2ec8e32c754daaec9c9e0cb24167b1866bc27305124e887`.
Tar member types/paths and the exact source allowlist are checked before writing
files. Seven source files match the deployed Git revision; generated delivery
binds the saved review. Its complete 508-app/499-source YAML payload passes the
current full validator. The optional staging `.nojekyll` marker is absent from
the exact retained deployment tar; the nine actual website files are present.

A synthetic later artifact directory is preserved alongside the before-image.
Restoring to a new directory reproduces all **1,009 files / 31,747,694 bytes**
exactly. Six actual browser checks on the restored loopback site pass in 16.7 s:
desktop/narrow Chromium and desktop Firefox, native fetch, search/source filters,
release assets, A/B/C navigation, help/focus, history, theme and viewport fit.
The narrow B screenshot was visually inspected. An initial sandbox startup refusal
was followed by an approved successful run; the loopback server is stopped.
No Pages redeployment, workflow dispatch or catalog ref write occurred.

GitHub's artifact expires November 9 at 16:41:36 UTC. The exact archive is retained
locally at `/home/marek/Documents/Codex/am-last-good-pages-42501013188.zip`; this is
not a promise of availability on another host. The rollout package must identify
its retained archive location/owner before relying on recovery after expiry.

## Completed qualification and remaining gates — November 9, 2026

The long-running checks have completed; no qualification process remains pending.
The current-layout [incremental receipt](incremental-scale-14.json) measures a
400.992 s fresh-parent fallback, 90.107 s projection, 32.110 s changed-document
validation and 3.623 s publication. It changes 501 documents, reuses 9,501 and
reads zero unchanged parent bodies during publication. Packed history grows by
200,525 bytes; old pins remain readable. This is synthetic timestamp refresh,
not fresh upstream acquisition.

The [status receipt](status-scale-14.json) validates 64 summaries, eight complete
500-source detail sets and 90 daily records: 4,066 documents. Snapshot validation
is 43.53 s, retention 15.78 s and total execution 115.84 s. Packed growth is
29,003 bytes. Its constant synthetic catalog pin and short run IDs understate
real variable-field history growth, so this is retention evidence rather than a
complete annual growth model.

The [dual-format receipt](dual-scale-14.json) validates 632,178,575 format-2 bytes
and 319,417,844 format-3 bytes concurrently in 899.731 s. The measured process
high-water RSS is 1,022,764 KiB; this is not aggregate cgroup memory. A local ZIP
proxy is 163,552,760 bytes; it does not measure Actions network transfer. The
normal request/response/acquisition allowances and their historical measurement
scope are recorded in [budget integration](budget-integration-14.json).

[Observed churn](observed-churn-14.json) compares 320 common successful sources
over roughly 3.65 hours: eight changed sources and eleven new release IDs. Newly
enrolled sources are excluded. This short observation is not a stationary annual
rate. [Preliminary annual scenarios](history-projection-preliminary-14.json)
remain historical-layout evidence. The current timestamp sample alone projects
200,525 × 8,760 = 1,756,599,000 added packed v3 bytes/year, before its seed,
status, format-2 or new release payloads. Shallow staging bounds local fetched
history; it does not bound remote reachable history. A complete annual dual-output
profile and explicit capacity review points remain required before acceptance.

### Browser timing decision

Marek explicitly accepted the synthetic 2 MiB stress-case timing exception on
November 9. The [boundary receipt](browser-boundaries-14.json) retains all samples:
title-heavy desktop 268.4–309.5 ms and narrow/4× CPU 813.7–1,081.6 ms;
asset-dense desktop 396.2–814.0 ms and narrow/4× CPU 1,477.3–1,613.6 ms.
Both documents are 2,097,024 bytes. All checks fit the viewport and report no
browser errors; the dense case progressively renders 60 of 18,914 assets.
The 500 ms ordinary-detail target and previously measured misses remain explicit.
This decision does not turn these samples into a timing pass.

### Recovery and published-source follow-up

The exact last-good ZIP is also retained in this repository at
[recovery/site-42501013188.zip](recovery/site-42501013188.zip), independent of
GitHub artifact expiry. A repeat restore derives its allowlist from the exact
pinned deployed staging source and reproduces the same 1,009 files and hashes.
The six successful browser checks above apply to those identical bytes.
Prepared Pages source stages live-channel delivery on main and saved observations
only on browser-review; future Pages artifacts request 30-day retention.

Read-only follow-up at published format-2 ref
`f98e2285e9348541cd00df74eb9ab570aa96b11e` confirms source 1245849062 still has
two conflicting release IDs for tag v0.41.1; conversion still correctly refuses
`same_tag_conflict`. [Exact evidence](latest-tied-source-14.json). Full 500-source
conversion therefore still needs new valid evidence or an explicit exclusion;
the saved 499-source result must not be described as full coverage.

Ticket 14 remains claimed for the annual capacity/operating-profile decision and
remaining rollout evidence. Ticket 15 is not claimed. No live collection, ref
publication, workflow activation, enrollment, installed-host change or push was
performed. Expensive completed checks should not be repeated unless affected by
a subsequent change.
