# Share the executable lifecycle and migrate the am-utils family

Type: task
Status: open
Triage: ready-for-agent
Blocked by: 47

## Scope

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
