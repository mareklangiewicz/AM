# Six Brave recipes on the shared AppImage lifecycle

Ticket [49](../issues/49-migrate-common-appimage-batch.md), November 2, 2026.
This is the first exact subset of the 124-path batch. The other 118 paths across
49 endpoints remain blocked by their own accepted operational observations.
[Accepted Brave rollout](../research/brave-live-20261102.md) supplies real metadata.

All six stable/beta/nightly recipes on x86_64 and aarch64 now use the existing
`appimage.am` implementation. Each preserves its exact original selector in a
small trusted `select_asset` function. No lifecycle module, manager or workflow
change accompanies migration. All twelve original install/update selectors match
actual accepted assets; each generated updater uses the same saved recipe.
Original binary URLs, channel/architecture matching and first-match ordering stay
unchanged. The alternate appimageupdatetool path and duplicated updater bodies
are removed in favor of the existing shared update/refusal/checksum behavior.

Production cost: six recipes shrink from 462 lines / 19,164 bytes to 84 lines /
2,187 bytes: **−378 lines / −16,977 bytes**. Shared-module delta is zero.
Installed system-AM controls, measured through the real installer with inert
binaries, are:

| App | Saved recipe | Generated updater | Remover | Saved installer | Total bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| brave | 571 | 81 | 180 | 360 | 1,192 |
| brave-beta | 574 | 86 | 195 | 363 | 1,218 |
| brave-nightly | 580 | 89 | 204 | 369 | 1,242 |

Each app has 19 saved-recipe lines, three updater lines, six remover lines and
14 saved-installer lines. These costs exclude downloaded binaries, metadata,
desktop/icons and unchanged shared helpers. AppMan path lengths can differ.

The full catalog suite passed 213 tests; the final focused migration suite passed
two tests, including all six recipe lifecycle paths (one additional test was added
after full-suite discovery). Ten support-tool specs pass. Recipe syntax, scoped
shellcheck (SC2034/SC1091 excluded for sourced globals/modules) and diff checks pass.
Retained selectors use actual accepted bytes; host lifecycle and container binary
mechanics use inert fixtures. No ARM executable or GUI runtime is claimed.

New installed-command scenarios cover three channels, standalone updates,
desktop/icons, mixed utility/legacy continuation with aggregate failure, partial
transfer/retry, checksum repair, metadata integrity and stale refusal before app
mutation, exact stale consent and fresh-install refusal. Native Termux covers
AppMan install and standalone update. A fixture edit initially widened two utility
assertion loops accidentally; it was corrected and the clean matrix rerun.
Final matrix results and evidence are appended below at completion.

This migration is local preparation. No recipe source push, daily repin or host
synchronization is included in it; the preceding enrollment rollout is separate.

## Final validation

Clean Debian and Fedora matrices each pass 31 scenarios; the native Termux
Brave scenario passes. The dedicated final installed-cost scenario also passes.
The earlier Debian run's two fixture-only errors are superseded by the clean
Debian run; Fedora in that first matrix used the corrected source and passed.
No production repair was needed.

[Machine results](../research/brave-migration-checks.json) and
[retained final container evidence](../research/brave-migration-evidence.tar.gz),
SHA256 `e2045187be9f7f39e6cde272783abf40932a7cb87d8e45dfd7fbd7eb1f4ed533`, include source fingerprints, exact commands/status/output,
transport traces and actual installed control-file costs. The complete matrix
snapshots predate the final cost-logging addition; the dedicated final scenario
verifies that addition. There were zero unexpected external requests.
