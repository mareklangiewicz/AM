# Share the executable lifecycle and migrate the am-utils family

Type: task
Status: resolved
Triage: ready-for-agent
Dependency: ticket 47 utility-source stage accepted on 2026-10-31

## Scope

Operational prerequisite accepted: [live enrollment evidence](../research/am-utils-live-20261031.md)
verifies publication `a113cd0aca3247111b6ba231f6a30b6477ac2c75`, all 356 original
selectors against actual returned bytes and seven-source daily repinning. This
ticket's implementation is completed in the Answer below. Ticket 47's broader
AppImage-source enrollment is separate.

After its exact source is accepted/published under ticket 47, migrate the 356
`plain_utility_batch` recipe paths in
[the frozen inventory](../research/recipe-family-inventory.json): 178 names each
on x86_64/aarch64, all reading `https://api.github.com/repos/ivan-hc/am-utils/releases`.
This is an actual plain-executable family, not an archive or AppImage adapter:
inspect representative source bodies and retained assets before settling the
small interface. Preserve every filename/date/architecture selector and original
binary URL; APP-dependent selectors must keep their actual app identity.

Share real download/version/chmod/symlink/removal/update mechanics with the existing
lifecycle where it makes total logic simpler. Keep small trusted recipes, saved
selectors and tiny standalone launchers, manager-owned modules/source embedding,
AppMan paths, command session reads and normal mixed batches. No speculative hooks
or archive formats. Design from real callers and measure the total interface and
implementation; do not merely add a second copied lifecycle or copy a generated
updater body into every recipe.

Prove representative names and both architectures with retained metadata plus
isolated controlled downloads. Exercise installer/standalone/manager dispatch,
unchanged/changed/refused/failed paths, metadata acceptance before mutation,
checksum repair/retry, current/embedded AMREPO and optional digest distinction.
Check every original selector against accepted retained bytes, report missing
assets rather than replacing policy, and audit all 356 path conversions for
complete removal of their displaced lifecycle bodies.

Baseline: 18,868 recipe lines / 673,192 bytes. A 20–24-line recipe target implies
10,324–11,748 recipe lines deleted before any new shared runtime; this is not a
promised net saving. Audit actual production, installed and generated code cost.
Preserve legacy support still used elsewhere. Complete code/tests/docs and commit
locally in useful chunks. No host migration, new collection or workflow activation
is implied by implementation. If only the utility source stage of ticket 47 is
complete, cite its actual accepted evidence before unblocking this ticket.

## Offline preparation 2026-10-28

At Marek's request, completed the [representative review and proposed shared
interface](../design/shared-executable-preparation.md), with a reproducible static
audit of every frozen recipe. All 356 have one lifecycle shape after removing only
identity and selector declarations; current size is 18,868 lines / 673,212 bytes
after the reviewed c++filt fixes. Existing AppImage validation rejects c++filt and
ld.bfd; extended-regex selectors need preservation through the existing custom
selector seam. Plan shares lifecycle mechanics with a format-specific integration
branch and preserves installed entry-point compatibility. No implementation or
operational enrollment; this ticket remains open and blocked by 47.

## Answer — 2026-10-31

Implementation and regression tests are committed locally as `a70082248`.
Claimed after the user authorized continuing the accepted utility migration.
[Implementation, interface, costs and limits](../design/shared-executable-lifecycle.md)
extend the existing managed lifecycle with the closed executable kind, retaining
the AppImage module/entry point and shared metadata/download/version/update/removal
mechanics. All 356 recipes are now 15 lines, with their exact original selector
suffix and actual app identity preserved. Manager integration skips desktop/icon
post-processing for executables; the new whole-command tests demonstrated the old
icon-fetch fallback before the fix. No executable payload is invoked by this path.

[Reproducible audit](../research/utility-migration-audit.json) records 18,868 → 5,340
recipe lines and 673,212 → 142,230 bytes. Including shared runtime and installer,
production falls by 13,508 lines / 530,292 bytes. Actual representative installs
use 20-line saved recipes and three-line standalone updaters; control-file and
one-time shared-module costs are counted separately in the design/evidence.

[Final checks](../research/utility-migration-checks.json): 206 catalog tests,
10 support specs and 72 Debian/Fedora/native-Termux container scenarios / 257 whole
commands pass, with zero unexpected requests. Tests cover all selectors against
accepted live bytes, both architectures' representative identities, installer,
standalone and manager routes, metadata refusal before mutation, transfer and
filesystem failures/retry, checksum repair, optional digest distinction, source
ownership, mixed batches, sync and removal/config preservation. Syntax passes for
all 356 recipes; ShellCheck has no new diagnostics (existing installer and identity
assignment baseline retained).

[Retained evidence](../research/utility-migration-evidence.tar.gz) includes successful
matrix results, logs, source fingerprints, actual installed code measurements and
the initial failing icon-request traces. Existing historical audits remain unchanged
and are superseded for current recipes by `audit-utility-migration.py`.

Resolved for local implementation and controlled compatibility verification.
No host migration, live source request/collection, source push, schedule repin or
workflow change occurred. Existing installed legacy utility updaters still require
separate delivery. Ticket 47 remains partial and 49 blocked on its own enrollment;
natural seven-source repeat behavior is also a separate pending observation.

### Publication — 2026-10-31

Following the user's “go ahead”, verified remote/default/source pin, publication
and workflow isolation against the handoff. Fast-forward pushed the three completed
commits through `7b31340a818a226c399130a776c5b03e78241438` and set
`CATALOG_SCHEDULE_REVISION` to that exact revision. Final read-only checks confirmed
source/pin equality, only collector and daily dispatcher active, the other six
workflows disabled, no unfinished runs in the latest 100-run response, and unchanged
publication `a113cd0aca3247111b6ba231f6a30b6477ac2c75`.
Collector production and workflow bytes are unchanged from the accepted source;
retained implementation validation remains applicable. No manual collection, host
sync or installed-updater migration occurred. Natural seven-source repeat remains
unobserved. This publication note was recorded locally after the pinned commit.
