# Next ten existing AppImage recipes: local conversion and enrollment

Ticket [135](../issues/135-prepare-next-ten-existing-recipes.md), November 6, 2026.
Marek requested “Continue” after the completed twenty-recipe rollout. Ten further
unchanged existing recipes now have short source declarations and local collection
enrollment. Local scope is **53 recipes / 51 numeric repositories**, below the
unchanged 52-source limit with one spare slot. Production remains **43 / 41** at
`daf47edb2b382bc6b7df832b00c43fae12bb73d2`; the installed host remains 21 apps.
No source push, publication, dispatch, installed/live refresh or yadm change was
performed for this batch. The ten apps were not installed or launched.

## Source and payload gates

[Source/runtime review](next-ten-runtime-review.md) checks all 22 initial candidates
against original Git objects. Current recipe hashes match the R36 originals;
whole-template reconstruction and repeated app/repository/FUNCTION consistency
pass. Original templates/generator remain authoritative, without copied bodies.
The [portable receipt](next-ten-evidence.json) and [evidence archive](next-ten-evidence.tar.gz)
retain complete first-party API pages, numeric identities, canonical names,
exact original/maintained selector winners, source/template hashes, full payload
sizes/digests, static filesystem listings and desktop/icon metadata/link chains.
The manifest verifies all **193** members, including task acquisition/replay code.

Of 22 screened recipes, five were excluded at metadata stage: affinity,
agent-desktop and agent-os exceed the fixed 400 MiB per-file payload cap;
agent-loom and agent-orchestrator redirect identity and need separate review.
Twelve reached full payload inspection; ten pass. Five further metadata-ready
candidates remain deferred. All twelve downloaded files match the recorded
published SHA-256 and total **1,424,767,846 bytes**, below the 4 GiB batch cap.
Full payloads are non-executable evidence under
`/home/marek/Documents/Codex/am-next-ten-20261106/`; they are omitted from Git.
Static unsquashfs tooling is used; no AppImage, AppRun, downloaded launcher or
other application code executes. Published digests bind bytes to saved upstream
metadata; they are not independent publisher authentication.

| Recipe | Canonical repository / numeric ID | Inspected selected asset |
| --- | --- | --- |
| aevum | `Alonera/Aevum` / 1288679691 | `Aevum-x86_64.AppImage` |
| afsplug | `zhangxianhe666/AFSplug` / 1290784521 | `afs-1.7.0-x86_64.AppImage` |
| ag-repatch | `etosheartem/ag-repatch` / 1365153976 | `ag-repatch-linux-x64.AppImage` |
| agaric | `jfolcini/agaric` / 1220744390 | `Agaric_0.22.0_amd64.AppImage` |
| agency-agents-app | `msitarzewski/agency-agents-app` / 1262882328 | `Agency_Agents_0.3.2_amd64.AppImage` |
| agent-arcade | `DanWahlin/agent-arcade` / 1213992071 | `Agent.Arcade_0.6.4_amd64.AppImage` |
| agent-buddy | `DanWahlin/agent-buddy` / 1365556684 | `agent-companion-desktop-0.18.1-linux-x86_64.AppImage` |
| agent-comm-hub | `JochenYang/agent-comm-hub` / 1333821463 | `agent-comm-hub-app_1.7.0_amd64.AppImage` |
| agent-launcher | `agent-launch/agent-launcher` / 1364985464 | `AgentLauncher-0.1.1-linux-x86_64.AppImage` |
| agent-pulse | `Dipen-Dedania/agent-pulse` / 1211202862 | `Agent.Pulse-1.4.0.AppImage` |

Each passing payload has an x86_64 ELF64 type-2 AppImage runtime, one visible
logical root desktop, no desktop actions/hidden entries, nonempty icon data and
supported internal metadata links. Whole filesystem listings and native image
ownership remain evidence; raw layout does not deploy that root-owned tree.
All current/old selector URL winners agree on complete saved first pages. This
is observed-page equality, not all-history ordering equivalence or GUI testing.

`agent-launcher` and `agent-pulse` use generic upstream download selectors; their
actual first-response winners were separately replayed and verified as direct
AppImages. No archive/sidecar assumption was inferred from template recognition.
Two payload exclusions remain unchanged: **ageha-editor** and **agency** have
absolute build-host icon links. Their original recipe hashes still match;
there is no per-app fallback or shared-runtime exception to force conversion.

All ten explicitly use `DESKTOP_STRIP_NO_SANDBOX=true`, retaining observed
original desktop transformations. The shared policy remains any release channel,
publication time then numeric release ID, bytewise name then asset ID, structured
name-based architecture/platform filtering, retained release facts, URL identity,
ordinary 48-hour observation freshness with explicit stale acceptance, and direct
selected-asset acquisition. Patterns are anchored to product/platform/architecture
names; only clear dotted numeric versions generalize. Fixed names remain exact;
new suffix/prerelease spelling requires review. Shared runtime logic is unchanged.

## Enrollment and capacity preparation

The [capacity receipt](next-ten-enrollment-capacity.json) retains the exact prior
41 published source documents unchanged, then adds the ten normalized saved
first pages and validates/publishes an exact-parent **local-only** candidate.
It measures **9,661,826 YAML bytes**, with the largest file still **1,142,139
bytes**, below 2 MiB. The ten responses add **6,681,964 bytes**; combining their
recorded sizes with the prior 41-source acquisition gives **56,385,915 bytes**,
below 96 MiB. Normalization/validation/local publication takes about 33.43 seconds.
This is a combined recorded-data capacity check, not fresh simultaneous 51-source
transport/elapsed evidence or a production publication. A future authorized push
needs a fresh full-scope preflight and exact-pin publication/readback.

The 52-source, 16 MiB response, 96 MiB total, 300-second collection and 2 MiB YAML
limits are unchanged. Existing source document hashes, published prior app IDs
and prior catalog pin remain intact. Capacity beyond this scope is unassessed;
no limit increase or all-app conversion schedule is implied.

## Verification

**70 focused tests pass**: 41 original reconstruction/runtime/batch methods; one
retained twenty-recipe and one next-ten enrollment replay; six publication groups;
three declaration groups; two compiler groups; and sixteen host integration/
cutover groups. The batch harness adds a receipt-path seam and a subclass, keeping
one implementation of exact provenance/identity/selector checks and actual-recipe
inert install, unchanged/changed updater, desktop/data preservation and removal.
Thirty new selection comparisons agree across mawk, gawk and BusyBox awk.

Enrollment replay likewise takes a receipt and pinned former enrollment revision.
Earlier batch tests preserve their historical scope when later recipes appear;
the maintained current-workflow test still exercises the full configured scope.
The new replay publishes from a former 43/41 synthetic baseline through the real
collector and distributed YAML reader, preserving the old local pin and refusing
a malformed new source without advancing the candidate. Host fixtures cover all
53 local enrolled recipes with authored inert payloads. No real app execution,
GUI test, installed migration or full catalog/container suite is claimed.

Local source conversion and enrollment preparation are complete. The named batch,
evidence, exclusions, tests and capacity are reviewable before a separate remote
push/publication/live-policy decision. Previous recovery directories, installed
recipes/snapshots/binaries/launchers and official Obsidian CLI remain untouched.


## Subsequent authorized operation

[136](../issues/136-publish-next-ten-and-refresh-live-policy.md) completes the
separately authorized push, manual publication and protected compiled-policy
refresh. Production is now 53 recipes / 51 sources at `b54c4f267ef8a1eb0aca76f01b68e391ee24a0f7`; all ten
inspected selections pass and all apps remain uninstalled. Statements above
retain this report's local-preparation result before that operation.
