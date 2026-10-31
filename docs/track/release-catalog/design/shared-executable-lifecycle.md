# Shared executable lifecycle — ticket 48

The accepted am-utils source stage in [47](../issues/47-enroll-scoped-migration-sources.md)
provides actual publication `a113cd0aca3247111b6ba231f6a30b6477ac2c75` and
356 verified asset selections. This change migrates exactly the frozen 356 utility
recipes (178 identities, two architectures), with every original selector suffix
and upstream binary URL policy preserved. It adds no source enrollment.

## Interface and compatibility

Each 15-line trusted recipe declares APP, `PACKAGE_KIND=executable`, the exact
am-utils catalog alias and one `select_asset` function. Its `sed | grep -Eoi |
head -1` suffix is byte-identical to both original install/update selectors.
The c++filt encoded-plus correction, ld.bfd regex dot, architecture/date matching,
case policy, first-match ordering and actual app identity are retained.

The recipe sources the existing managed `modules/appimage.am` and invokes
`am_package`. Existing installed AppImage recipes continue through `am_appimage`,
which calls the same implementation; the module location and default AppImage
kind remain compatible. The internal selector interface still supports both the
existing declarative AppImage patterns and custom trusted selectors.

The shared implementation accepts only `appimage` and `executable`. Executable
identities begin with an ASCII lowercase letter or digit; subsequent characters
may include digits, letters, dot, plus, underscore and dash. Slash, traversal,
leading dash and shell punctuation refuse before catalog IO. AppImage identity
validation remains unchanged.

Catalog acceptance and selection precede app-directory changes. Both formats
share URL comparison, checksum-failure repair, staged downloads, chmod/replacement,
version recording, quoted removers, saved recipes, three-line standalone updaters
and command symlinks. The staged filename is neutral (`tmp/$APP`). Equal accepted
URLs remain unchanged unless explicit refresh or checksum repair requires work.
Failed transfer/chmod/move preserves an installed executable and its version;
version-write failure can occur after replacement and reports failure. This is
not an atomic multi-file transaction.

Executable installation returns before AppImage extraction or desktop/icon
integration. The normal installer also skips its desktop/icon/MIME post-processing
for a compact executable catalog recipe. Whole-command testing caught its old
unconditional icon fallback; the retained failing traces show those requests,
and the final matrix requires zero unexpected requests. No executable binary is
invoked by installation or update.

Normal installer expansion supplies persistent app/bin/desktop/helper bindings,
manager-owned module paths and configured AMREPO. The saved recipe has 20 lines;
standalone updates use its embedded source, while manager updates use the current
configured source. Existing catalog markers retain normal mixed-batch routing,
command publication reuse and exclusion from legacy preprocessing. Existing legacy
install/update machinery remains for its other callers.

## Actual code cost

[Reproducible source audit](../research/audit-utility-migration.py) and
[per-path report](../research/utility-migration-audit.json) compare against approved
source `c787efe3a42fac015f743255006fddd7ea9b3817`:

| Production source | Before | After | Change |
| --- | ---: | ---: | ---: |
| 356 recipes, lines | 18,868 | 5,340 | −13,528 |
| 356 recipes, bytes | 673,212 | 142,230 | −530,982 |
| Shared lifecycle, lines | 107 | 121 | +14 |
| Installer, lines | 1,436 | 1,442 | +6 |
| Total production lines | | | **−13,508** |
| Total production bytes | | | **−530,292** |

The baseline bytes include the earlier two c++filt fixes; older inventory bytes
retain their historical meaning. Exact-shape auditing proves all 356 displaced
installation/updater bodies were removed rather than hidden in generated recipes.

Actual system-AM installs in a network-disabled Debian container measure four
representative apps (`7z`, `arch`, `c++filt`, `ld.bfd`). Each has 43 control-file
lines: saved recipe 20, standalone updater 3, remover 5 and original-recipe record
15. Their respective totals are 1,198 / 1,208 / 1,233 / 1,218 bytes under the fixture
source URL. Path/source lengths affect byte counts. Shared catalog and lifecycle
modules occupy 250 lines / 11,722 bytes once per manager, not once per app.
These counts exclude executable payloads and version/checksum data; they are actual
controlled installations, not a measurement of the user's installed payloads.
Original generated updater bodies are 21 lines each; the new saved-recipe/updater
pair totals 23. The separate original-recipe record drops from 53 to 15 lines.
The source audit distinguishes those costs instead of counting only the shorter
standalone launcher.

## Verification and delivery scope

The catalog suite compares every actual converted selector with both original
selectors against the accepted live body and requires all selected URLs to be
real assets. It additionally checks adversarial first-match/regex-dot ordering,
encoded plus signs, representative installs/updates/removals on both architectures,
invalid identity/format, integrity/stale/empty-selection refusal, transfer/chmod/move
failure, post-replacement version failure, retry and equal-URL checksum repair.

Whole-command tests use the real installer/manager and saved updater in disposable
Debian/dash, Fedora/bash and native Termux environments. Retained catalog responses
and inert binary downloads are the only transport inputs; runtime networking is
disabled. Coverage includes system AM and unprivileged AppMan, current versus
embedded source, mixed catalog/AppImage/legacy continuation, no-argument sync,
metadata refusal before mutation, exact stale consent, checksum repair, optional
digest absence versus mismatch, removal and user configuration preservation.
Utility fixtures record any attempted binary execution as a test failure.

No live metadata read, host sync/migration, source push, schedule repin or workflow
activation accompanies this implementation. Existing installed legacy utility
updaters require separate delivery; changing source recipes does not migrate them.
Native architecture binary compatibility and arbitrary crash durability are not
claimed from inert fixtures. The next source push must coordinate the exact
reviewed daily pin. Ticket 49 still needs its separate source-enrollment approval.

## Final validation record

[Checks](../research/utility-migration-checks.json) record 206 passing catalog
tests, 10 support specs and 72 passing container scenarios / 257 whole commands:
Debian 28/110, Fedora 28/110, Termux 16/37. Zero unexpected requests. All tested
production and module fingerprints match the final implementation. The Debian
fixture-loader input hash predates a correction to a host-only audit assertion;
the loader itself was unchanged, and later platforms record the corrected file.

All 356 recipes pass shell syntax. The lifecycle is clean under warning-level
ShellCheck; the installer retains its 18 baseline diagnostics (including its
existing SC2182), and 146 recipes retain SC2209 on the same original unquoted
identity assignment. There are no new diagnostic classes or installer diagnostics.

[Evidence archive](../research/utility-migration-evidence.tar.gz), SHA256
`80f8b6fe2ff6b1dc6ef440b7231dc1a13cd98daa4660b84f644e15a6a3eaffa7`,
retains complete successful command/transport results, source fingerprints, the
actual footprint measurement script/output, syntax/lint context and initial
icon-fallback failure traces. It contains controlled container paths/data only.
