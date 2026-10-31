# Brave eight-source offline contract and rollout review

Ticket [47](../issues/47-enroll-scoped-migration-sources.md), 2026-10-31.
This preparation does not activate enrollment or unblock ticket 49.

## Candidate

[Manifest](staged-manifest-brave.json), SHA256
`dfca1d3e7504e4c6fa83ae6260ba1bb6e2db4cca736fb3693db9ec4aeea1a8bf`,
preserves the exact seven accepted source rows and adds only public repository
`ivan-hc/Brave-appimage`, ID 947512058:

- Fetch `https://api.github.com/repositories/947512058/releases`.
- Alias `https://api.github.com/repos/ivan-hc/Brave-appimage/releases`.
- Request ID `cc6d925dcd7e84d969cfdd6b8f3413a13855b37dca9fc6e569b38a36a967fff8`.
- Pinned API version 2022-11-28 and Accept application/vnd.github+json.
- No initial validators; no pagination, redirect, retry or endpoint substitution.

[Observed identity/release evidence](../research/brave-enrollment-findings.md)
contains the two authorized reads and all twelve unchanged original selector
results for six recipes. It establishes current metadata compatibility, not
AppImage runtime behavior or scheduled enrollment.

The implementation raises only the planner source cap from seven to eight and
allows manifest profiles six, seven and eight. Storage, artifact reconstruction,
publication and supervised transport already use the approved plan; their runtime
code is unchanged. Ninth-source refusal is verified before transport or credentials.
The operational manifest, workflow bytes and dispatcher manifest hash remain
unchanged. An exact manifest hash in the approved context still gates collection.

## Verification and measured resources

The focused enrollment tests cover preserved seven-source descriptors/validators,
unconditional first Brave read, first-304 refusal, missing/invalid/oversized/failed
eighth results, exact ZIP recomputation, all Python reader aliases, unchanged
byte bounds, synthetic conditional repeat and failure age preservation, wrong
conditions, exact-parent local publication and moved-parent refusal. Pinned shell
reads verify the inclusive 48-hour edge, exact stale consent and corrupt-body
refusal. Supervised transport now verifies eight planned workers exactly once and
refuses the ninth. Historical six/seven tests remain in the full suite.

[Reproducible resource replay](../research/replay-brave-enrollment.py) reads the
hash-bound accepted seven-source publication evidence and the actual retained
Brave response, using explicitly synthetic seven 304 events and temporary local
Git. [Measured output](../research/brave-eight-source-replay.json):

| Resource | Measured | Existing cap |
| --- | ---: | ---: |
| Current tree | 8,263,578 bytes | 50,000,000 |
| Index | 18,251 bytes | 2,000,000 |
| Lookup | 6,081 bytes | 2,000,000 |
| Brave body | 639,169 bytes | 8,000,000 per body |
| ZIP artifact | 508,768 bytes | 105,000,000 |
| Temporary Git objects after child | 617,705 bytes | 128,000,000 history |
| Temporary object growth | 45,147 bytes | no growth promise |

Eight nominal 30-second requests consume 240 of the 300-second batch deadline;
actual collection/serialization/job overhead remains unmeasured. Connect stays
10 seconds and existing job timeouts remain five minutes. The caps may refuse a
future larger response/tree; this sample is not a worst-case capacity guarantee.
Temporary object growth does not measure production reachable history or daily
churn. Natural seven-source repeat remains independent and unobserved.

No app/runtime/module/recipe changes require another container matrix here;
whole-command compatibility evidence from ticket 48 is unchanged. [Final validation](../research/brave-eight-source-checks.json) records 212 passing
catalog tests and 22 passing activation checks in the temporary copy. Preparation
and activation revisions are supplied separately at completion.

## Operational review payload — not executed

The prepared [activation patch](brave-eight-source-activation.patch) switches the
operational manifest to these exact candidate bytes, binds its hash in
scheduled_dispatch.py and updates workflow labels plus both operational-binding
regressions together. It is checked in a temporary copy and is not applied to main-marek. After the
preparation checks pass, a separate local `prep/brave-eight-source` commit is
created from this patch for review at its exact SHA, supplied in the completion
message. That branch is an offline activation candidate; creating it changes no
remote source, daily pin or operational worktree configuration.
The main-marek preparation commit alone is not the activation revision; the
separate local activation branch supplies it. Never dispatch
this candidate with the currently pinned source, which still supports only seven.

Before requesting execution approval, read-only recheck remote source and daily
pin (last verified `7b31340a818a226c399130a776c5b03e78241438`), default branch,
workflow isolation, all unfinished runs and publication parent (last observed
`a113cd0aca3247111b6ba231f6a30b6477ac2c75`). These are historical observations,
not authority to overwrite changes. Supply the exact activation SHA and parent
with the approval request; if a natural run advanced the parent, review that actual
parent and its evidence. Do not silently reuse the old parent.

Approval must separately cover pushing the exact activation source, one bounded
manual eight-source collection/publication, acceptance checks and daily repin:

1. Push the approved fast-forward source, leaving the old daily pin during the
   short acceptance window. The source-equality guard skips intervening schedule
   events. Do not dispatch a synthetic daily event.
2. Dispatch catalog-collector.yml once at main-marek with approved_revision equal
   to the full activation SHA, manifest_sha256 equal to the candidate hash above
   and previous_publication equal to the freshly reviewed exact parent.
3. Verify eight exact descriptors attempted once, prior seven conditional requests
   and unconditional Brave, all-source successful validation, actual body/headers,
   deadlines/caps and complete retained artifact/provenance. Ambiguous submission
   requires read-only inspection, never a blind retry.
4. Recompute artifact from exact prior and transfers, verify full published Git
   tree/modes/blobs and single exact parent. Replay the original six recipe
   fingerprints/twelve selectors against the newly returned Brave body; verify
   actual pinned Python/shell readers, alias preservation and freshness. Missing
   assets or any refusal prevents acceptance; no selector substitution.
5. Record actual ZIP/tree/history growth and timing; only after acceptance set
   the daily source pin to the exact activation SHA and verify equality/isolation.
   No host synchronization or recipe migration is included. Only this six-recipe
   subset of 49 may become unblocked; other 49 endpoints remain deferred.

A concrete bounded rollback must accompany activation approval: prepare a
fast-forward revert restoring the exact preactivation accepted seven-source tree,
verify its full tree equality before pushing, then repin to that verified revert.
Never force-push or rewrite catalog history; retain any succeeded eight-source
publication. If there is intervening source work or the rollback tree differs,
stop for review. No second manual collection is included in rollback.
