# 107 AppImage recipes migrated locally

November 2, 2026. Tickets [47](../issues/47-enroll-scoped-migration-sources.md)
and [49](../issues/49-migrate-common-appimage-batch.md).
The user authorized the remaining metadata reads, isolation of failing endpoints,
and implementation/testing of compatible migrations as one substantial batch.
This supersedes per-endpoint approvals and stop-the-entire-evidence-batch behavior.
Publication, scheduled activation and host delivery remain separate.

## Result

107 recipes now use the existing shared AppImage lifecycle: 70 x86_64, 31 aarch64,
4 i686 and 2 armv7l. All 214 original install/update selectors select actual saved
assets unchanged, including channel, architecture, query and first-match ordering.
Recipes shrink from 8,695 lines to 1,498. Including the shared validator and
collector/delivery preparation, production drops **7,196 lines / 334,946 bytes**.
Together with the six previously published Brave recipes, 113/124 paths in the
frozen batch have implementations; these new 107 are local preparation only.

The shared validator now accepts dotted app names for eksplode.re/exsplode.re;
hidden names, empty names, separators and shell punctuation still refuse before
mutation. No new lifecycle configuration or app-specific format adapters.

## Identity evidence

All 48 distinct remaining identity URLs have HTTP evidence. Forty-three identities
are public and match their exact expected names; they cover 44 exact release
endpoints because SuperTuxKart list/latest remain separate requests. All 44 release
GETs succeeded and passed release-shape validation. [Batch evidence](appimage-batch-20261102/batch.json),
numbered response directories, and the earlier [12-request prefix](remaining-identities-20261102-network/batch.json)
retain exact bytes/hashes/status/timing. The initial DNS failure remains separately
preserved. No redirects were followed or failed HTTP requests retried. No pagination, binary
download or alias rewrite occurred.

Anonymous quota exhaustion paused untouched requests. The existing GitHub CLI
sign-in then served only the remaining 32 GETs through the same bounded transport.
Its explicitly acquired credential traveled through a private inherited pipe,
never command arguments, environment variables or evidence. Per-response reports
identify authenticated versus anonymous reads. All 80 new response stream hashes
and sizes pass recomputation; the original prefix adds 12 HTTP attempts.

[Migration report](appimage-batch-20261102/migration.json) binds original/candidate
recipe hashes, selected assets and exact evidence paths. [Offline reproducer](../../../../tools/catalog-collector/migration_batch.py)
rechecks frozen source hashes and both selectors; it does not execute installers.

## Five isolated endpoints, eleven unchanged recipes

| Original repository | Result | Recipe scope |
| --- | --- | --- |
| mysteryx93/NaturalGroundingPlayer | 301; target ID 37950127 unverified | 432hz-player, converter432hz, powerliminals-player |
| 3516634930/payloader | 404 | payloader, two architectures |
| DavidVentura/offline-translator-linux | 301; target ID 1069135746 unverified | offline-translator, two architectures |
| Jermolene/TiddlyDesktop | 301; target ID 15743523 unverified | tiddlydesktop, two architectures |
| LifetimeLabsDev/privacynotes.app | 301; target ID 1227817920 unverified | privacynotes, two architectures |

Redirects do not establish a current name/public mapping. These paths retain their
original code and selectors. Their endpoint exceptions require a later explicit
identity/alias review, independently of the completed 107-path preparation.

## Bounded 52-source preparation

[Candidate manifest](appimage-batch-20261102/candidate-manifest.json) preserves all
eight accepted descriptors and adds exactly the 44 evidenced endpoints. Loader
profiles retain historical six/seven/eight counts and accept this exact 52-source
stage; 53-source preflight refuses before credentials. Artifact file cap becomes
108 for 52 candidate bodies, 52 attempt bodies and four metadata files.

The 300-second batch deadline, 30-second request deadline, 8 MB body, 2 MB index,
50 MB tree, 105 MB ZIP and all-source-success publication rules remain unchanged.
Serial requests have no worst-case completion guarantee: 52 slow requests cannot
all finish in 300 seconds. The existing absolute deadline stops incomplete runs,
and publication refuses; preserved prior observations retain their age. No need
to raise time/byte limits or introduce concurrency to prepare this stage.

[Measured offline replay](appimage-batch-20261102/capacity.json): 36,276,153-byte tree,
4,877,885-byte ZIP, 2,759,123-byte temporary Git object growth. Eight existing
responses are explicitly synthetic 304 events; the 44 new bodies are real saved
responses. These figures establish snapshot fit, not future churn, workflow timing
or live conditional behavior. Operational manifest, controller, workflows, source
publication and daily pin remain unchanged. Activate enrollment before publishing
these new recipes for use; their aliases are absent from the live catalog today.

## Validation

Final results and source fingerprints are retained in the neighboring checks JSON,
test logs and container evidence archive. Tests use real metadata with synthetic
publications and inert AppImages, proving control flow rather than ARM/GUI runtime
compatibility. No host installation or installed-updater migration occurred.

Final [checks and source fingerprints](appimage-batch-20261102/checks.json):
243 distinct catalog tests covered. The final combined run passed 242 and exposed
one obsolete assertion expecting a ninth-source refusal; after updating that test
to exercise 52 workers / 53rd-source refusal, all 21 transport tests pass. The six
capacity tests and ten support specs pass. Debian and Fedora each pass 32 whole
installed-command scenarios; native Termux passes the new AppMan scenario.
All 108 scoped shell files pass syntax/lint. The 11 excluded recipes still match
HEAD exactly. [Container evidence](appimage-batch-20261102/container-evidence.tar.gz)
and final logs are retained. Changes remain uncommitted and unpublished.
