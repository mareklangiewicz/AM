# Convert the two inspected existing AppImage recipes

Type: task
Status: resolved
Triage: ready-for-agent

Marek's November 6 go-ahead accepts the next step proposed after 129: preserve
20x's old desktop behavior by explicitly stripping `--no-sandbox`, add focused
inert tests, convert 20x/2fac with verified IDs/narrow patterns and the proposed
selection policies, regenerate declarations and validate locally. Commit locally.
Collection enrollment, push, live installation/deployment and publication remain
outside scope. Keep 4nier-patrimonio outside scope.

Add one opt-in literal desktop argument setting to the shared installer, default
to preservation, validate before acquisition, and test actual install/update/
removal with inert metadata matching the observed symlink shapes. Do not run
real payloads. Retain 129's provenance and evidence as historical records.

## Answer

Converted only `programs/x86_64/20x` and `programs/x86_64/2fac` to the existing
literal declaration/shared-wrapper interface. Numeric IDs and exact narrow
patterns follow 128/129. Both use any channel, raw AppImage layout, command desktop
execution and URL version identity. Shared publication-time/ID and name/ID
ordering, structured asset membership, retained-release selection, name-based
architecture/platform guards, normal freshness consent and direct acquisition
are accepted for this source conversion by Marek's go-ahead; unconditional legacy
selector parity is not claimed. Original hashes/payload evidence remain in 129.

Added optional `DESKTOP_STRIP_NO_SANDBOX=true|false` (default false), validated
before acquisition and during declaration compilation. Only 20x opts in. The
shared installer removes space-delimited literal flags on newly generated Exec
lines, preserving other keys, similarly named arguments and field codes. This
is a narrow textual transformation, not a quoted/escaped desktop argument parser.
Existing desktop entries remain preserved. The short reconstruction reader accepts
the literal setting but still makes no behavioral equivalence claim for its
legacy upstream rendering interface.

Regenerated declaration registry adds only the two recipe identities. No
collection enrollment changed (21 recipes / 19 numeric repositories). Without
separately authorized enrollment/catalog coverage, source declarations do not
make these apps available from the production catalog. Installed transition
still needs ownership/remover/old-desktop inventory as described in 129.

Validation: all 35 reconstruction/runtime tests, three declaration/compiler/
selection tests and 16 existing host lifecycle/cutover groups pass (54 distinct
tests). The new tests exercise actual converted wrappers with authored inert
payloads supplying the retained real desktop/icon bytes and symlink shapes;
install, standalone no-change and changed-URL updates, custom desktop
preservation, icon resolution and removal pass. Invalid boolean refusal occurs
before download; unrelated desktop keys/arguments remain intact. Saved full
upstream responses select the expected exact URLs with actual declarations on
mawk, gawk and BusyBox awk. Prior evidence hashes, deterministic regeneration,
unchanged enrollment, shell syntax, documentation links and whitespace checks
pass. The seven runtime tests were rerun after the final sed adjustment.
No complete catalog/container suite or independent code review is claimed.

No real AppImage/launcher/downloaded script executed. No live installed files,
recovery directories, collection list, workflow, publication, push or yadm pointer
changed. Source work is complete and committed locally; enrollment and deployment
remain separately scoped next steps.
