# Explicit maintainer recipe transactions

Ticket 102, isolated source preparation. This tool is not wired into AM update,
module synchronization, install, or an active workflow. No host execution or
publication is accepted here. It is Python maintainer tooling, alongside the
existing collector tools; ordinary clients retain the shell-only runtime.

## Review package and exact scope

`tools/catalog-collector/yaml_installed_migration.py plan` takes explicit paths
for one installation, a fully bound replacement recipe, manager and module dir;
a local source repository with a full source commit; an AMREPO URL naming that
exact commit; explicit architecture/app; a full publication commit; an expected
legacy installed recipe SHA-256 from a reviewed package; and a file containing
the helper's exact six-line selected-record result. There is no discovery or
implicit /opt inventory. The replacement must already contain the exact helper,
source and recipe bindings. Source recipe bytes are read through `git show` at
the full pin; manager and all six runtime modules must match those exact source
blobs (including format-1 catalog.am). A marker alone cannot enroll an updater:
its bytes must exactly match the known generated exec-recipe trampoline.

The JSON plan records full source and publication pins, source recipe hash,
replacement bytes/hash, old recipe hash and Unix uid/gid/mode, and guards for the
manager, six runtime modules, updater, installed binary and version. Review the
entire plan and the bound replacement before apply. Review must establish that
the replacement was correctly derived from the recorded source recipe and keeps
package kind, directory bindings, URL identity and refresh behavior. This tool
checks critical binding lines but does not parse shell or prove their semantics;
it does not generate a replacement or authenticate the review package. Locally
modified legacy recipes require a separately reviewed expected hash, not a
blind inventory-to-approval shortcut. No remote source acquisition occurs.

The chosen manager/modules must already have been delivered through a separately
reviewed operation. The migrator does not deliver them. Current candidate helpers
still resolve release-catalog when no pin is provided; this tool always supplies
a pin. That does not settle publication ownership/ref migration or format-1
support. No operational invocation is appropriate before those gates are settled.

## Application and recovery

Create a new caller-owned mode-0700 transaction directory outside the installed
recipe path. Invoke `apply --plan ABSOLUTE_PLAN --transaction ABSOLUTE_DIR`.
Every path must be absolute with no symlink ancestors; guarded files must be
single-link regular files without extended attributes. Unsupported ACL/xattr
layouts need an adapter rather than silent metadata loss. Caller must have
permission to preserve old uid/gid/mode. Parent-directory trust and exclusive
control of the installation, manager and modules are prerequisites: the advisory
lock serializes this transaction only, not ordinary AM updates, module sync or
hostile local writers. Stop those separately. There is no concurrency guarantee
against an uncooperative process between hash check and rename.

All guards are checked before preflight. The exact installed trusted helper runs
with the plan's pinned AMREPO and publication commit, without any inherited
command session. Its complete selected-record output must equal the reviewed
six-line result. Stale refusal is default; the explicit
`--accept-stale-selection` applies only to this plan's exact five-field tuple.
It does not grant a catalog/app-wide waiver. Guards and old recipe are checked
again after preflight and immediately before replacement.

A private exact-byte backup and plan intent are written and fsynced before
recipe replacement. Replacement uses a temporary file in the recipe directory,
sets original uid/gid/mode, fsyncs the file, renames it, and fsyncs the directory.
The receipt records old/new metadata/hashes, source/publication pins and selected
record. Retry recognizes old/new recipe hashes, verifies backup and intent, and
can finish an interrupted receipt. Interruption after backup but before intent
can resume only with identical old recipe bytes. Unexpected state refuses.
A receipt is evidence of this recipe transaction, not of a binary update.

`rollback` verifies all original guards and exact post-migration recipe state
before restoration. A durable rollback intent prevents apply from re-entering
a transaction once rollback starts. Restore uses the same metadata-preserving
atomic replacement, and retry reconciles an interrupted restore or receipt.
Reapplying a completed rollback needs a new transaction directory and plan.
Backups remain retained; the tool never deletes them or runs an updater.

## Limits

Recipe replacement and binary update are separate. This tool never executes a
binary upgrade. Its rollback refuses after guarded binary/version drift and
restores only the recipe. Binary rollback after a real update needs retained
artifacts/version state or a separately trusted reinstall procedure. Filesystem
fsync/rename durability is assumed; power-loss and privileged-owner restoration
have not been tested on a real host. Tests inject exceptions after durable write
boundaries, rather than claiming actual power-cut evidence. No installed client
inventory, source promotion, live acquisition, ref transition, stale UI/capacity
acceptance, workflow activation, push or yadm pointer changes follow from this
source increment.
