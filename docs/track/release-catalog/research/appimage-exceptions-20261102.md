# Four redirect identities and eight recipe candidates — November 2, 2026

Continuation of tickets 47/49 after the accepted 52-source rollout. User requested
continuation; four explicitly recorded numeric identity targets and their exact
release lists were read as public metadata. Eight HTTP 200 responses, anonymous,
no retries or redirect following. Original headers/bodies are retained under
[the evidence directory](appimage-exceptions-20261102/).

## Explicit identity review

Only the original exact recipe aliases are proposed; no canonical-name aliases
are added. Numeric fetch endpoints stay bound to verified public repository IDs.
These owner/name changes are made visible for the next enrollment approval:

| Original spelling | Current public full_name | Numeric ID | Recipes proposed |
| --- | --- | --- | --- |
| mysteryx93/NaturalGroundingPlayer | mysteryx93/HanumanInstituteApps | 37950127 | 3 x86_64 |
| DavidVentura/offline-translator-linux | DavidVentura/offline-translator-qt | 1069135746 | x86_64, aarch64 |
| Jermolene/TiddlyDesktop | TiddlyWiki/TiddlyDesktop | 15743523 | x86_64 only |
| LifetimeLabsDev/privacynotes.app | LifetimeLabsHQ/PrivacyNotes.app | 1227817920 | x86_64, aarch64 |

### identity-1

[Exact identity/body/report](appimage-exceptions-20261102/identity-1/report.json).
### identity-2

[Exact identity/body/report](appimage-exceptions-20261102/identity-2/report.json).
### identity-3

[Exact identity/body/report](appimage-exceptions-20261102/identity-3/report.json).
### identity-4

[Exact identity/body/report](appimage-exceptions-20261102/identity-4/report.json).

## Candidate implementation and exclusions

[Eight recipe replacements](appimage-exceptions-20261102/recipes.patch) use the
existing shared AppImage lifecycle and preserve both original selectors and
exact original aliases. Original frozen recipe hashes match current legacy files;
all sixteen selectors select actual returned assets and agree with candidate
selectors. Recipe reduction: 544 lines / 25,702 bytes. No production recipe is
changed in the active worktree by this preparation.

The original aarch64/tiddlydesktop selector selects the same linux64 asset as
x86_64. Asset URL membership alone does not prove ARM compatibility; leave this
legacy recipe unchanged pending explicit architecture/selector scope. Its x86_64
candidate preserves the original preview-channel choice. The powerliminals-player
selector retains its existing Player432Hz choice. Both payloader paths remain
unchanged under the retained 404; no replacement repository is inferred.
If accepted/published, these eight candidates bring the scoped implementation
count to 121/124; the three paths above stay outside delivery.

## Bounded enrollment candidate

[Enrollment patch](appimage-exceptions-20261102/enrollment.patch) preserves all 52
accepted descriptors and aliases, adds four numeric /releases endpoints, updates the daily manifest hash, raises
only source/artifact-count limits to 56/116, and retains the historical 52-source
profile. Request, byte, time, storage and publication rules remain unchanged.
Old manifest hashes cannot authorize this new manifest. Proposed manifest SHA256:
`e4cfa58e2262b07e1bc7e06cd09edbf19e573d40211b5d1fd2fa6a6ae1d5a788`.

[Replay metrics](appimage-exceptions-20261102/capacity.json): 37,838,243-byte tree
and 2,886,734-byte ZIP fit existing caps. All 52 existing 304 events are explicitly
synthetic; the four new bodies are genuine saved responses. Full artifact
recomputation, every reference reader, ZIP roundtrip and exact local Git parent/tree
pass. First-new 304 and incomplete publication refuse. These are offline capacity
figures, not live 56-request timing or live conditional-response evidence.

[Candidate checks](appimage-exceptions-20261102/candidate-checks.log) cover eight
inert installs and generated updates, both candidate architectures' transfer
failure/retry, checksum repair, integrity refusal, stale refusal/exact consent,
and invalid app identities before mutation. No app binaries were executed.
[Verification harness](appimage-exceptions-20261102/verify.py) runs in an isolated
snapshot with enrollment and recipe patches applied; pass the collection ZIP
13139128488 from the retained accepted-52 evidence archive as its first argument.
The harness reuses the existing lifecycle cases with this batch's two architectures
and a synthetic clock after the retained response times.

## Rollout boundary

No new source push, collection dispatch, daily repin, host sync or installed-updater
migration occurred. Next approval must cover the four explicit identity mappings
above. Follow the previous two-stage ordering: exact enrollment fast-forward,
one bounded 56-source run against the freshly rechecked catalog parent, full
artifact/Git/selector/both-reader acceptance, then exact eight-recipe candidate
fast-forward and daily repin. Keep the current daily pin until acceptance.

Pre-delivery rollback must restore the exact prior 52-source catalog as a new
exact-parent commit before restoring old source/pin if a 56-source publication
exists: old code caps sources at 52. No force push or automatic second collection.
Source/catalog drift requires revising the concrete review. Prior accepted source
and pin are d6e742157; prior accepted catalog is 29e37bd9, subject to recheck.

## Final local validation

All 37 affected collector/publisher/workflow/scheduler/capacity tests pass;
[retained log](appimage-exceptions-20261102/affected-tests.log). All five candidate
checks pass, including all eight inert installs/updates and both architectures’
failure/stale paths. Evidence stream hashes/lengths and candidate recipe hashes/
syntax pass. Both patches apply cleanly, preserving the exact raw-manifest bytes.
Broader discovery runs were stopped; no new complete 243-test result is claimed.
