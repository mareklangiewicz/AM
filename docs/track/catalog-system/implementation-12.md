# Incremental publication and final health — local acceptance

November 8, 2026. Implements [ticket 12](issues/12-implement-incremental-publication-and-final-health.md).
Main publication code is at `d36b16f7beaa75cd645784e825865ad1ab9535df`.
Marek's accepted literal encoding is at `e6163409e273ddff87beffee20b88f14b341e2a0`;
final rehearsal code is `e77d85f0d0003dd56590284047da96cfbb98b0d9`.
All work and transport tests were local. No source push, dispatch, live acquisition,
enrollment, public channel, installed-host, Pages or yadm change occurred.

## Implemented behavior

The maintained explicit collect/validate/publish interface now streams validation
of exact Git parents, retaining compact source metadata. Selected sources decode
lazily; candidates reuse untouched blobs and their validated metadata under an
in-memory parent/rule identity. Changed bytes and whole-candidate references are
checked. Imported receipts never confer trust; a new process or changed rules
performs full parent validation. There is no persistent trust/recovery store.
Full fallback cost is included in the receipts below.

Publication checks trusted run/attempt, source/input, exact parent, path/type/size,
content hash, domain and enrollment bindings again. Artifact code is never run.
Format 2 publishes first, followed by enabled target publication and independent
best-effort status. Exact-parent conflicts stop later catalog writes, without
merge/retry. Confirmed remote acceptance, refused writes and ambiguous results stay
distinct. Status failure leaves the previous original report untouched; a newer
catalog can legitimately precede status confirmation. Finalization is attempted
on normal candidate/artifact/publication failures, without fake zero counts or pins.

Status implements stage outcomes, source denominators, known/absent/unknown input
catalog states, available selected-unattempted detail, truthful 64-summary / 8-detail /
90-daily retention and unknown source-count attempt coverage. Measured requests,
charged bytes, timing and confirmed local tree/object metrics stay separate from
unavailable received bytes, RSS, packed history or remote storage. No public start
record, current-running claim or guaranteed report delivery is introduced.

The prepared hourly/manual workflow uses a collection-only Action, exact trusted
checkouts with credential persistence disabled, pinned dependencies before
step-scoped tokens, read-only acquisition, one-day inert artifacts and a separate
write-enabled publisher/finalizer. It does not cancel an active run. Profile flags
expose scope/budget settings independently of enrolled count. Target channel
activation remains disabled until the separately reviewed rollout.

## Leading `=` literal media types

Marek chose the existing `media_type` field, with no new literal field. Decode one
leading `=` literally and stop, before alias handling: `=raw` → `raw`, `=zip` →
`zip`, `==raw` → `=raw`. Writers escape bare literals and original leading `=`
values. Unescaped `zip`, ordinary full types, omission and empty values retain
their existing meanings; unknown unescaped bare aliases still refuse.

[The saved-value receipt](mime-roundtrip-12.json) checks all **175,073 assets** in
**500 original sources**, including **76 distinct original values** and **6,691
`raw` values**. Every value round-trips exactly through the encoder/decoder.
The shared wire fixture independently exercises shell/browser/schema behavior,
including alias collisions, repeated `=`, empty literals, default omission, full
media types, Unicode and escaped newlines. Older private v3 candidates built under
the pre-amendment semantics should be regenerated from their normalized inputs;
this amendment precedes public v3 activation. Format 2 is unchanged.

[Loader comparison](loader-comparison-12.json) on the three largest saved documents
shows identical values from safe Python/C loaders, with about 8–10× faster loading
in the compiled implementation. The contract reader now reuses the maintained
safe C loader when available, after unchanged strict original-byte/domain checks;
the safe Python fallback remains. Fixture parity also checks both implementations.

## Focused verification

| Check | Result |
| --- | --- |
| `python3 -B -m unittest discover -s tools/catalog-collector -p test_contracts.py -v` | 11 tests pass in 12.421 seconds, including exact writer/shell/browser/schema media-type expectations and safe-loader parity. |
| `python3 -B -m unittest discover -s tools/catalog-collector -p test_pipeline_publication.py -v` | 9 tests pass in 55.689 seconds: disposable transport success, v2 success/v3 conflict, ambiguous writes, final-summary failure, newer C/older S, bad hashes/run/missing artifacts, selected-unattempted detail, retention/unknown coverage, incremental trust invalidation and tied-tag refusal. |
| Affected legacy collection/normalization/canonical checks | 30 test invocations pass in 46.293 seconds; reused unchanged-input evidence from the preceding ticket-12 implementation. |
| Shared wire fixtures on mawk/gawk/BusyBox; shellcheck; whitespace | Pass. All generated files reproduce exactly. |
| Prepared workflow/action checks | Explicit read/write permission split, pinned Actions, disabled checkout persistence, non-cancelling concurrency and embedded bash syntax pass. Artifact Action v4 pins were verified through the official repositories' Git refs. No workflow execution occurred. |
| Committed CLI smoke at `d36b16f7b` | Actual credential-free saved collect → publish against three disposable local channels succeeds; zero HTTP, E=500/Q=1, absent target parent, all local channel publications confirmed, collection parent ref unchanged and temporary files cleaned. This unaffected protocol evidence is reused. |

## One saved seed plus three updates

[Complete receipt](rehearsal-12.json) binds source/rule revisions, all 500 original
source-document SHA-256 values and the exact saved baseline
`cbda9fb78ce4a6f29bdabd63d57f3c0085e8744f`. The preserved evidence repository was
read-only. Each phase ran in its own Python process in an isolated publication
repository, retaining baseline history. Temporary repositories were removed on
normal exit. No HTTP/acquisition or remote publication occurred.

The seed contains **499 valid sources**, with **one explicit source refusal**:
source **1245849062** has different IDs for an exact tag at the same saved
observation time. The already accepted conflict rule requires refusal, so no ID
was chosen and no target app-map entry was fabricated. Its format-2 baseline data
and history remain untouched. This is a partial target seed from 500 input sources,
not a claim that all 500 successfully converted.

| Phase | Seconds | Tree bytes | Changed/reused blobs | Python peak RSS KiB | Largest child peak KiB | Reachable pack bytes |
| --- | ---: | ---: | --- | ---: | ---: | ---: |
| Saved retained seed | 453.393 | 31,594,820 | 502 / 0 | 75,344 | 75,344 | 68,218,055 |
| Identical retained-observation replay | 64.622 | 31,594,820 | 1 / 501 | 66,816 | 73,300 | 68,218,418 |
| Three-source synthetic update | 52.535 | 31,597,439 | 4 / 498 | 67,100 | 75,832 | 68,219,467 |
| All-499-source synthetic refresh | 221.707 | 31,610,674 | 500 / 2 | 70,292 | 79,596 | 68,448,271 |

RSS is the separate phase process high-water. Child RSS is the largest child
high-water, not simultaneous aggregate memory. Packing consistently used one
thread, compression 6, window 10 and depth 50 in the isolated repo. These local
reachable pack bytes are not remote GitHub storage or a long-term projection.
The original format-2 tree is 63,690,470 bytes; size differences include compact
encoding, accepted retention and the one refused source, rather than encoding alone.
Largest target document is 401,975 bytes after the final update.

The replay reused every source blob, plus apps/provenance; only the producer
root changed. The named subset is `0x808`, `0xchat-app-main`, `0xfx`, respectively
new version, same-ID edit and exact-tag replacement. Only those source blobs and
the descriptor changed; every other source blob/observation remained exact.
The wider synthetic update changed all 499 valid sources, preserving both
non-producer roots. Source retention, timestamp, conflict and overflow refusals
also have focused tests. Synthetic timestamps/edits are explicitly labelled and
do not count as fresh upstream observations or acquisition capacity.

Full parent fallback measured 114.899 seconds for the saved 63.7 MB v2 parent,
then 62.444 / 48.257 / 47.504 seconds for the v3 phases. The full check happens
once per process and remains a measurable cost, rather than accepting arbitrary
receipt claims. Temporary candidate tree and local history guard remain below
current limits in this cohort.

## Reuse and remaining gates

Ticket 14 should reuse this exact rehearsal unless changed inputs/behavior
invalidate it. It still owns thousands-of-app/source qualification, temporary
shared-acquisition dual-output cost, quota/refresh/headroom, the 12-month history
projection, consumer selection differences and rollback. Existing numerical
safeguards remain baselines to reassess; these 499-source results do not qualify
5,000 sources. The tied-tag source refusal remains explicit for rollout review.
Ticket 13 owns real browser integration/fetch/DOM/mobile/accessibility checks.
No public activation or installed-host delivery is authorized by this receipt.
