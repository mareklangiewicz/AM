# Remaining AppImage source preparation

Ticket 101. Candidate source 0c157af59e34513e159bf399cdedc62e5bb36faf on isolated
prep/yaml-appimage-migration,
based on 7cfd1218f; /tmp/am-yaml-appimage-migration. Local source only, unmerged
and unpushed. The earlier executable and integration candidates remain separate.

## Scope and explicit choices

All remaining 114 enrolled AppImage paths now have exact format-2 recipe
bindings and trusted numeric repository policies. Together with the earlier
361 paths, source coverage reaches 475/475 in the staged manifest. This does not
inventory installed hosts or enroll the 987 marked paths outside that manifest.

Actual URL selectors and original recipe hashes are frozen in the candidate's
tools/catalog-yaml-prototype/appimage-policies.json. The development compiler
embeds these explicit rules in the existing awk policy; no JSON/compiler/Python
is delivered as a client dependency. Tests confirm stripping the two new binding
lines restores original source hashes. BRE literal pipes, each stage's case
flags, numeric version directories and architecture/channel predicates survive.
The generic asset_facts projection adds prerelease as column eight, preserving
the original first seven columns.

Marek clarified that he does not use the nine /latest paths and nobody else uses
the fork. The source candidate explicitly replaces latest with newest published
non-prerelease matching assets for PolyMC, SuperTuxKart and Vivaldi stable, and
newest published matching snapshot assets allowing prereleases for Vivaldi
snapshot. These are local selection choices, not latest equivalence.

Several suspicious filters are deliberately preserved and documented: aarch64
Lapce selects x86_64; armv7l Headlamp/Wekan exclude armv7l; Opera and four Wine
variants have literal architecture-pipe strings in BRE; Chatterino nightly shares
ordinary Chatterino eligibility; soil-editor has no soil-specific predicate.
Separate policy cleanup can address them without hiding behavior in migration.

## Saved evidence and differences

`python3 tools/catalog-yaml-prototype/appimage_cohort.py` hash-checks original
saved bodies, normalizes and fully validates YAML, runs the actual legacy
selectors over those original JSON bytes, and compares complete selected tuples
between Python and mawk/GNU awk/BusyBox awk. The final report records each recipe
hash, legacy body hash/location, both URLs, selected IDs and repository evidence.

114 policies / 342 three-awk comparisons agree with the reference. 106 selected
URLs match legacy; eight change: Brave beta/nightly on both architectures,
DBFlux on both architectures, soil-editor and Wine Proton. Published-time/ID
release ordering changes Brave/DBFlux/Wine; bytewise asset-name ordering changes
soil-editor. Retained coverage, asset-only matching, complete decoded URLs and
these ordering rules are explicit policy differences, not equivalence claims.

45 saved repository fixtures contain 988 releases / 14,799 assets. Normalized
repository sizes range from 2,821 to 1,251,974 bytes under the unchanged 2 MiB
trial cap. PolyMC and Vivaldi have only saved /latest objects: their one release
is normalized directly as an incomplete fixture, without forging a list response
or claiming list-route acquisition. For SuperTuxKart, the new policy uses saved
list facts while the legacy comparison uses its actual saved latest object.
These historical samples establish no current upstream, default 100-release or
retained-growth capacity guarantee.

An initial audit-helper rerun wrongly required unrelated Obsidian /latest
evidence; its assertion failed before report replacement. Restricting requested
latest fixtures to this 114-path cohort corrected the helper. That failed run is
not counted as passing evidence. Initial ShellCheck without external-declaration
exclusion reported SC2034 on variables consumed by the shared module; final scoped
validation excludes SC1091/SC2034, without changing source to silence them.

## Verification and review

Independent code-review standards and spec axes reviewed 0c157af59 against
7cfd1218f, with zero actionable findings on each axis. The spec reviewer separately
checked all 114 actual selector translations, manifest numeric identities, nine
latest replacement policies, projection/freshness semantics and all 475 exact
source bindings. No fixes were requested. Heavy tests were run by the primary
agent rather than duplicated by reviewers.

The following completed commands passed at the candidate runtime source:

```sh
python3 tools/catalog-yaml-prototype/appimage_cohort.py
python3 -m unittest discover -s tools/catalog-collector -p 'test_yaml_*cohort*.py' -v
python3 -m unittest discover -s tools/catalog-collector -p test_yaml_manager_integration.py -v
python3 -m unittest discover -s tools/catalog-collector -p test_yaml_am_utils.py -v
PYTHONPATH=tools/catalog-collector python3 -m unittest test_appimage_lifecycle test_batch_updates test_yaml_enrollment test_executable_lifecycle test_utility_selectors -v
```

The cohort command passes 15 tests in 53.729 s, manager integration 11 in
84.581 s, executable migration six in 102.432 s, and compatibility 112 in
221.793 s. These suites were independently scheduled and some ran concurrently;
timings are local execution evidence, not new performance/capacity guarantees.
All 114 changed recipes pass dash syntax and ShellCheck with the external-module
SC1091/SC2034 exclusions. Four changed/new Python files compile and whitespace
checks pass. No additional platform/real-network cross-product is claimed.

The final new command
`python3 -m unittest discover -s tools/catalog-collector -p test_yaml_appimages.py -v`
passes five groups in 530.089 s: all 114 inert manager installs and generated
standalone updaters, exact source/registry/enrollment, nine latest replacement
flags/fall-through/selected freshness, reassignment/stale refusal before mutation,
and adversarial independent raw-JSON/three-awk URL matching. Combined with the
other suites above, all 149 tests pass. No test failure remains.

The candidate branch's
`docs/track/release-catalog/design/yaml-appimage-migration.md` records full
semantics and boundaries; that design is not merged into main.

## Remaining work and operations

The installed production migrator is still not implemented; the earlier installed
transition remains a contract/disposable rehearsal. Policy/stale UI acceptance,
exact operational pins, capacity acceptance and publication/ref transition remain.
Candidate helpers still resolve release-catalog; all-path source coverage does
not authorize a single-ref switch or mixed operational deployment. Binary update
rollback is also separate from restoring recipe bytes.

No live acquisition, workflow activation/dispatch, source/catalog publication,
repin, installed host change or yadm pointer work occurred. No push is implied by
local commits or source coverage.
