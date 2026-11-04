# Installed consumers and publication transition — source preparation

Ticket 100 proposal. No host inventory, installed edits, remote reads, publication,
repin or activation is authorized by this document. Do not silently migrate an
installed recipe as a side effect of ordinary update or module synchronization.

## Publication constraint and proposed path

The existing release-catalog ref must keep format-1 lookup.tsv/raw bodies for
old managers and standalone updaters. A format-2 consumer's private cache does
not solve that requirement. Current candidate helpers still resolve that ref;
they are suitable for offline source tests, not an operational mixed deployment.

Proposed transition: introduce a separately named format-2 publication ref while
leaving release-catalog format 1 intact. This is a concrete proposal, not accepted
dual publication or permission to create either ref. Acceptance must settle the
new ref's exact name, ownership, collector/source pins, publication CAS target,
retention/capacity and duration/retirement of format-1 support. Both publications
must retain their own provenance and observation ages; never synthesize raw JSON
from YAML. No record trimming or empty-prior bypass is implied.

A single-ref switch is an alternative only with an explicit maintenance window
and a justified inventory showing every supported client has migrated, including
standalone updaters. Without that evidence it cannot be the default. Completing
source coverage alone cannot establish the installed inventory.

## Exact source package

Prepare a review manifest containing full source commit, configured owner/repo,
architecture and each target app; exact trusted recipe and runtime-module hashes;
the expected format-1 installed recipe/updater hashes; and the chosen publication
contract. The containing source commit is supplied after source preparation, not
an invented self-referential pin embedded in its own content. The manifest must
bind the actual installed path substitutions and embedded source/module locations,
not only an unpatched repository recipe hash. No rolling branch tip at apply time.

Ship both catalog.am and all format-2 modules plus the dual-format appimage.am.
The manager source must retain references to both families so cleanup preserves
standalone format-1 updaters during the support interval. An old manager's module
cleanup is a separate compatibility risk: require the reviewed manager revision
before switching its installed recipes. Exact source acquisition does not grant
catalog staleness consent.

## Explicit per-installation apply contract

1. Inventory only explicitly selected installation roots, recording manager mode,
   architecture, source binding, recipe/updater/module hashes, permissions and
   supported managed marker. Refuse unknown or locally modified layouts by
   default; never guess the architecture from an app name. Legacy non-shared
   updaters need a separate adapter, not this recipe-only operation.
2. Produce and review a bound replacement recipe from the exact source package.
   Keep app name, package kind, installed directories, original URL identity and
   refresh behavior. Verify the current recipe/updater hashes still match the
   plan immediately before replacement; refuse drift. Preserve an exact backup
   and its ownership/mode outside the replaced pathname.
3. Require the reviewed manager/modules and preflight the exact target recipe
   against the selected format-2 publication commit. Validate all facts and
   selected effective freshness; obtain any exact per-record stale consent.
   Refusal leaves recipe, updater, binary, version and interrupted work untouched.
4. Stage on the same filesystem with the final permissions, then atomically
   rename the replacement recipe into place. A generated managed updater that
   already execs recipe.am needs no rewrite. Record old/new hashes, package source
   pin, publication pin and result in the migration receipt. Re-running an
   already-applied plan should verify its state and report unchanged.
5. Run the managed updater with that publication pin and per-selection consent.
   A matching URL preserves the existing binary; checksum repair and intentional
   refresh retain their normal behavior. A failure is reported without substituting
   format 1 or granting another app's waiver. Batch failures remain per app.

This proposal deliberately separates binding replacement from binary upgrade;
there is no claim that two unrelated files or an entire batch switch atomically.
An interrupted single recipe rename leaves either the old or new recipe. The
receipt/retry design must reconcile a completed rename with an unwritten receipt.

## Rollback and acceptance checks

Before restoring anything, compare current installed hashes to the recorded
post-migration hashes; refuse drift. Restore the exact prior recipe by same-
filesystem rename, including ownership/mode. Retain the matching format-1 helper,
manager support and publication data while rollback is promised. Recipe rollback
alone does not restore a binary already changed by a subsequent update; binary
rollback needs a separately retained artifact/version pair or an explicit trusted
reinstall procedure. Do not claim more from a same-URL fixture.

The disposable test in test_yaml_am_utils rehearses stale refusal before recipe
replacement, a successful same-URL format-2 update without binary/version changes,
and byte-exact recipe restoration. It does not acquire exact remote source pins,
execute the restored format-1 updater, test crash/receipt recovery, preserve
privileged metadata, handle locally modified legacy updaters, or implement a host
migration command. Those remain required implementation/verification work before
operational acceptance. Capacity, remaining 114 recipe paths, policy/stale UI
acceptance and natural-run verification are independent gates.
