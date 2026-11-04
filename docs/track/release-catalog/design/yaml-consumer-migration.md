# Format-2 consumer migration preparation

Ticket 95: offline rehearsal and static map, not an activated consumer or accepted
selection-policy change. Source baseline ff2dc1499; inventory is reproducible with
`python3 tools/catalog-yaml-prototype/consumer_inventory.py`. Recipe bodies are
read and hashed, never executed by inventory generation.

## Current boundary

`modules/catalog.am` resolves one publication, reads lookup.tsv, applies 48-hour
freshness to the response observation and returns exact raw JSON. `modules/appimage.am`
passes this to am_appimage_select_asset or a trusted recipe's select_asset function,
then uses the chosen URL as version identity. It checks acceptance before touching
an installation. `modules/install.am` provisions helper/module paths and writes
bindings for recipes. APP-MANAGER's batch-update path creates a command-private
AM_CATALOG_SESSION: only acquisition bytes/pin are shared, never acceptance results.
Python consumer.py and shell_lookup.py are format-1 helpers/tests, not a new format-2
compatibility contract.

Format 2 must replace this handoff with a structured selection result. Do not
manufacture raw GitHub JSON from YAML or feed serialized YAML into old sed/grep
pipelines: that would preserve the wrong abstraction and selection ambiguity.
The upstream asset digest is an optional fact, distinct from the removed raw-body
hash/size ledger. Git commit pin plus structural validation supplies catalog
identity; per-release observed_at supplies freshness.

## Static current enrollment

The reviewed manifest still maps 255 names / 475 recipe paths to 49 identities;
987 marked paths outside that manifest are excluded, not newly enrolled.

| Family | Paths | Migration work |
| --- | ---: | --- |
| Generic URL filter | 6 | Review URL matching, arch exclusion, case, release order and fall-through explicitly |
| Custom AppImage shell selector | 113 | Translate reviewed intent to structured release/asset selection; do not run old pipelines on facts |
| am-utils custom executable selector | 356 | Preserve APP/arch/static-asset and release-tag rules explicitly; all share ivan-hc/am-utils |

There are 119 AppImage and 356 executable paths. Of all enrolled paths, 466 use a
list alias and nine use /latest: polymc and supertuxkart on x86_64/aarch64,
supertuxkart on i686, vivaldi-stable and vivaldi-snapshot on x86_64/aarch64.
No latest request exists in format 2; these four app-name families require an
explicit release-selection decision, not a silent published-time substitution.

The six generic paths are obsidian, sqlitebrowser, nvim and nvim-nightly on x86_64,
plus nvim/nvim-nightly on aarch64. Only obsidian/sqlitebrowser set ASSET_IGNORE_CASE;
only the two nvim-nightly paths set REFRESH_ALWAYS. sqlitebrowser additionally
filters version/channel URL patterns; nvim excludes nightly while nvim-nightly
intentionally differs. A universal .AppImage suffix filter is insufficient.

## Offline policy reference

`tools/catalog-collector/yaml_selection.py` is a Python rehearsal using existing
publisher dependencies, not a client dependency/proposal to install Python or
PyYAML on hosts. select_local reads a complete structurally validated snapshot
at an exact Git commit. It is deliberately not an optimized network consumer.
Its lower-level select assumes those validated maps.

The explicitly supplied reference policy supports published_desc order, optional
stable-only filtering, asset-name suffix, all include substrings/any exclude
substrings, optional ASCII case folding. Release ties use descending numeric ID;
asset ties/order use UTF-8 byte name then ascending numeric ID. These are visible
reference choices, not recovered GitHub page order, GitHub latest or accepted
policies for the inventoried recipes. Name substring rules do not automatically
translate URL BRE/ERE rules, APP shell interpolation or custom pipelines.

The reference falls through releases with no matching asset, selects first under
the declared rule, then checks the selected release's effective observation time.
A newer collection/publication or fresher but lower-priority matching release
cannot rescue a stale selection. The shared observation default and overrides
both work. A failed latest collection does not by itself make a retained fresh
record unusable. Future observations always refuse. Exactly 48 hours is fresh;
one second over requires explicit stale acceptance.

The rehearsal proposes an exact acceptance object binding commit, repository ID,
release ID, asset ID and observed_at. Wrong/extra/missing fields cannot grant the
stale exception. This replaces the old response-level commit/request/hash tuple
only within the offline reference; operational stale CLI/UI migration is still a
separate decision. No legacy waiver is silently reinterpreted.

## Integration sequence still to prepare

1. Approve concrete policies for a small, named recipe cohort, using saved source
   fixtures to expose differences in release ordering, prerelease/channel handling,
   URL-versus-name matching, per-arch assets and tie/fall-through behavior.
2. Implement those policies using shared shell reader queries and one pinned
   apps.yaml/repository pair. Preserve literal decoded facts and existing byte
   caps/private spooling; no new consumer watchdog framework is required.
3. Replace catalog.am/appimage.am's raw-body selector handoff with a structured
   selected-release/asset result; check selected observation freshness at acceptance.
   Preserve URL version identity, REFRESH_ALWAYS, failure-before-mutation and
   installed updater/module bindings. Keep command acquisition reuse distinct
   from per-selection acceptance.
4. Exercise installation/update/repair and batch flows in disposable fake roots,
   then prepare exact source/consumer pin transition, stale override interface and
   rollback with publication rollout. No live host or catalog transition is made
   by this rehearsal.

Seven offline reference tests pass: structured asset/digest optionality, explicit
stable/fall-through, deterministic name/large-ID ordering, selected-record staleness
and exact waiver, freshness boundary/future/failed collection, exact-pin reads
across a moving local tip, and refusal of implicit latest/invalid rules/missing
apps/assets. Existing runtime and operational modules/recipes are unchanged.
