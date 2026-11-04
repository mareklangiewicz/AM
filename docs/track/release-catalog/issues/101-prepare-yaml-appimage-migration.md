# Prepare remaining AppImage format-2 source policies

Type: task
Status: resolved
Triage: ready-for-agent

Continue isolated candidate 7cfd1218f. Audit all remaining 114 enrolled AppImage
paths against actual selectors and saved fixtures. Implement explicit trusted
structured asset policies and recipe bindings for list endpoints. Preserve URL
case/regex semantics, document suspicious pre-existing filters rather than
silently repairing them, and distinguish retained/order/asset-only differences.
Record explicit /latest replacement choices after user context below. Never
manufacture raw JSON from YAML. Verify portable policy on three awk tools,
selected-record freshness/refusal and disposable manager/updater behavior. Use
code-review with separate standards/spec agents against 7cfd1218f.

No live acquisition, workflow dispatch/activation, publication, source push,
repin, main runtime promotion, installed host changes or yadm pointer work.
Installed production migrator and operational acceptance remain separate work.

## Comments

Marek clarified during execution: “I don't use any of these, and no one else is
using our fork.” The isolated candidate proposes newest published non-prerelease
with a matching asset for PolyMC, SuperTuxKart and Vivaldi stable; Vivaldi snapshot
allows prereleases and requires its snapshot URL pattern. These are explicit
replacement rules, not a claim to preserve GitHub latest. Source coverage may
reach all 475 paths; operational acceptance remains separate.

## Answer

Candidate 0c157af59e34513e159bf399cdedc62e5bb36faf on isolated
prep/yaml-appimage-migration prepares all remaining 114 AppImage paths, bringing
exact source bindings to 475/475 enrolled paths. [Findings and verification](../research/yaml-appimage-migration.md).
All 114 saved selections agree between Python and three awk implementations
(342 comparisons); 106 agree with legacy and eight documented selections change
under explicit ordering. Latest replacement choices and incomplete singleton
fixture limits are recorded. 149 tests pass, including all 114 inert installs
and standalone updaters; parallel standards/spec review found zero actionable
findings on each axis. Candidate is clean, local and unmerged/unpushed.

Installed production migration, policy/stale UI acceptance, operational pins,
capacity and publication/ref transition remain separate. No live or installed
host operations or yadm pointer changes occurred.
