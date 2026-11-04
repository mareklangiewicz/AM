# Installed recipe transaction preparation — November 4, 2026

Ticket 102 continues source candidate 0c157af59 on the isolated branch
`prep/yaml-installed-migration`, worktree `/tmp/am-yaml-installed-migration`.
Runtime/tool code reviewed at `974cc963a`; implementation commits are 1cbac1580,
0c8fd45b4 and 974cc963a. This is source preparation, not an installed migration
or production rollout. Main runtime remains unchanged.

## Implemented scope

Candidate-only `docs/track/release-catalog/design/yaml-installed-migrator.md`
and the
`tools/catalog-collector/yaml_installed_migration.py` maintainer CLI implement:

- Explicit single-installation inventory and a reviewable plan binding a full
  source commit/AMREPO, source recipe hash, fully bound replacement bytes/hash,
  explicit architecture/app, full publication pin and exact six-line selection.
- Reviewed expected old installed recipe SHA-256, exact known managed updater
  trampoline, exact source manager and six runtime module bytes, plus binary and
  version guards. Old recipe Unix uid/gid/mode are retained through replacement
  and rollback. Unsupported links and extended metadata refuse.
- Trusted installed helper preflight with explicit publication/source pins,
  exact selection equality and optional consent for only that selected tuple.
  Guards are rechecked after preflight and before changing the recipe.
- Private backup and durable intent, same-directory staged replacement with
  fsync/rename/directory fsync, bound receipts, retries and recovery after each
  durable write boundary. Separate durable rollback intent prevents accidental
  reapplication during an interrupted restore.
- Guarded recipe-only rollback. An applied receipt plus unexplained restoration
  of old recipe bytes refuses. Binary/version drift prevents rollback rather
  than pretending that restoring a recipe restores the installed program.

This tool is Python maintainer tooling alongside existing collector tools;
normal AM consumers acquire no new runtime dependency. It has no integration
hook in normal install/update/sync. It never invokes an updater or changes the
binary/version pair. Manager/module delivery is a prerequisite, not performed
by this tool. It does not acquire source packages remotely or derive a bound
replacement automatically. A reviewer must verify replacement derivation,
package/directory/URL/refresh semantics and exact legacy installed hash.

## Review

The code-review skill ran independent parallel standards/spec reviews against
0c157af59. Standards found zero actionable findings. Spec found one state-machine
defect: durable applied receipt plus externally reverted old recipe bytes could
be silently reapplied. 0c8fd45b4 fixes it, with apply/rollback refusal regression
coverage; the reviewer confirmed interrupted rollback still recovers. Both axes
confirmed final path-validation follow-up 974cc963a with zero remaining
findings. Review does not establish operational acceptance.

## Verification

All executions use disposable installation roots and local bare-Git saved-fact
publications with fake HTTP/download/clock commands. No real app or installed
host was inventoried or executed. Tests invoke actual candidate manager install
fixtures to create the disposable managed trampoline and installed recipe.

Final command (at code revision 974cc963a):

```
PYTHONPATH=tools/catalog-yaml-prototype:tools/catalog-collector python3 -m unittest discover -s tools/catalog-collector -p test_yaml_installed_migration.py -v
```

All 11 tests passed in 119.742 seconds at 974cc963a. Earlier incremental executions
passed the original nine transaction groups, three focused receipt/recovery
groups after the spec correction, and the new path/legacy-hash refusal group.
An initial discovery run also unintentionally collected six imported inherited
AMUtils tests; all six passed. The import was changed to a module import to keep
final discovery scoped. No test failure was observed during this increment;
the state-machine defect was found by review, not by a failed prior test.
`python3 -m py_compile` and CLI `--help` pass; `git diff --check` passes.

The final eleven groups cover apply/idempotence/exact metadata restoration;
selected freshness refusal and exact consent; changed selected output; every
manager/module/updater/binary/version guard and recipe drift; drift introduced
by preflight; exceptions after backup, intent, recipe rename and receipt writes;
interrupted rollback recovery; unexplained post-apply recipe reversion; backup
and post-update version drift; reviewed legacy hash and path validation; and
transaction lock, symlink, hardlink and private-directory refusals.

## Boundaries and remaining work

Crash tests raise exceptions after durable writes. They are not power-cut tests
or a privileged uid/gid restoration demonstration. Ordinary updates/module sync
must be excluded during the transaction: this tool's advisory lock only
serializes this transaction, not other writers. Parent-directory trust, a trusted
local plan and exclusive installation access are prerequisites; no hostile-writer
TOCTOU guarantee is claimed. Tests restore recipe bytes/metadata only and do not
execute a restored format-1 updater after real binary mutation.

A reviewed exact operational package and installed inventory, automatic/reviewed
source-to-installed binding, manager/module delivery, policy/stale UI/capacity
acceptance, publication ownership/ref transition, source promotion and full
operational/binary recovery acceptance remain separate. Candidate helpers still
resolve release-catalog outside explicit-pin calls; a mixed deployment remains
unsuitable until the publication contract is settled. Format-1 clients still
require lookup.tsv/raw bodies; neither 475 source bindings nor this tool proves
that those clients have migrated.

No live acquisition, installed host mutation, source push, catalog publication,
workflow activation/dispatch, repin, main runtime promotion or yadm pointer work
occurred. Candidate and main tracking commits remain local; pushing is Marek's
call. Do not reopen ticket 71's interview or rollout 69.
