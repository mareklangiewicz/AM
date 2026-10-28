# Executable lifecycle preparation

Status: proposed implementation plan; static review at `8feef1f47`.
Ticket [48](../issues/48-shared-executable-am-utils-batch.md) remains blocked by actual
accepted source publication in 47. This preparation does not claim that work.

## Evidence from real callers

The [reproducible static audit](../research/audit-executable-lifecycle.py) checks
all frozen recipes against the hashes in the existing retained-selector evidence.
Its [report](../research/executable-lifecycle-audit.json) establishes one lifecycle
shape across 356 paths / 178 identities / two architectures, after replacing only
APP declarations and version-selector lines. Both install/update selectors agree
within each recipe. Existing selector evidence establishes 356 actual saved-asset
matches, including 160 multiple-match paths whose first-match order must remain.
No need to repeat those completed selector executions for this static review.

Representative callers are `7z` (numeric-leading identity and multiple assets),
`arch` (single match), `c++filt` (encoded plus signs in asset URLs), and `ld.bfd`
(literal dot in app identity). Review both architecture paths for each. These are
single executable downloads with URL-as-version, chmod, command symlink, remover,
and generated standalone updater; no archive unpacking or desktop extraction.

Two identities fail the current AppImage identity validator: `c++filt`, `ld.bfd`.
Keep actual identities and original selectors, including the existing regex dot
behavior for ld.bfd. Do not normalize names or introduce escaping that changes
which retained URL wins. The reviewed c++filt selector uses `c%2B%2Bfilt`.

## Proposed interface and seam

Deepen the existing managed lifecycle rather than clone its body. Keep the current
`modules/appimage.am` source path and `am_appimage` entry point as compatibility
adapters for existing installed recipes. Add one neutral lifecycle entry point
in that managed module, with a closed `PACKAGE_KIND=executable|appimage` choice;
the old entry point continues to default to AppImage. A later rename is unnecessary
for this migration and would add installed delivery dependencies.

Small trusted executable recipes provide APP, exact CATALOG_ALIAS,
PACKAGE_KIND=executable and one `select_asset` function, then source the managed
module and invoke the shared entry point. Retain the original `grep -Eoi` suffix
verbatim for the first migration. Existing pattern declarations use basic regex,
whereas this family uses extended regex `{8}` and APP expansion. Custom selectors
already provide the required seam; adding a regex-mode setting is unnecessary.
Catalog response bytes remain inert. There is no executable hook, archive adapter,
per-app transport configuration or copied updater implementation to add.

Shared implementation owns metadata acceptance, selection, update comparison,
checksum-failure repair, staging/download, chmod/replacement, version recording,
remover, saved recipe, three-line standalone updater and command symlink. Format
choice only controls AppImage integration and its required desktop/icon paths.
Executable installation must never invoke the downloaded binary for extraction.
Use a neutral staged filename instead of requiring an `.AppImage` suffix.

Validate executable identities against the observed supported characters with an
explicit safe leading character, rejecting slash, empty identity, traversal and
leading dash. Preserve existing AppImage validation unless a real caller needs a
change. Keep path quoting and source selection centralized.

## Behavior to preserve and deliberate improvements to prove

Catalog/source/freshness/integrity/selector acceptance precedes any app mutation.
Use the shared catalog helper and command session pin, exact stale consent,
original download URL, and manager AMREPO versus standalone embedded source rules.
Equal URL is unchanged unless checksum repair requires a retry. A failed transfer
leaves the installed binary and version intact. Executable updates require no
binary execution and no desktop dependencies. Retain optional manager digest
verification as a separate operation; catalog body hashes do not authenticate a
downloaded executable.

Legacy utility updates use `mv --backup=t` then remove backup files on success.
The shared implementation currently stages downloads then replaces in place;
do not claim either gives atomic multi-file rollback. Verify transfer/chmod/move
failure and retry behavior explicitly. Keep working installs intact on retry,
create the remover/updater without append duplication, and refresh symlinks through
the shared mechanism. These are deliberate shared behavior choices to validate,
not promises of byte-identical legacy side effects.

Installer integration in `modules/install.am` currently recognizes the exact
appimage module source line, inserts persistent bindings and rewrites its entry
point for `--icons`. Reuse that module path and binding logic. The new executable
entry point must ignore the irrelevant desktop option at manager level rather
than acquire extraction behavior. Preserve catalog recipe/updater markers used
by normal mixed batches, module synchronization and legacy-preprocessing exclusion.

## Implementation sequence after enrollment

1. Cite accepted publication evidence and unblock 48. Claim it before coding.
2. Refactor the shared lifecycle with existing six AppImage recipes unchanged;
   prove representative executable recipes for both architectures in isolated roots.
3. Verify real installer, standalone and manager commands: install, unchanged,
   changed, refused metadata, transfer failure, checksum repair and retry. Exercise
   AppMan paths, embedded/current source, mixed-batch continuation and optional
   digest verification. Use inert executable fixtures; no new upstream downloads.
4. Convert all 356 paths mechanically, compare every selector to the retained
   original and check complete removal of displaced lifecycle/updater bodies.
5. Report actual production, installed and generated code costs and compatibility
   results. Keep legacy machinery with other callers. Commit coherent local chunks.

The existing baseline is 18,868 lines / 673,192 bytes before the two c++filt
selector fixes; the audit records current bytes. Projected recipe deletion is not
an implemented saving. Source push, workflow changes, host delivery and further
source enrollment remain separate operations.
