# Maintained YAML catalog tools

The intended production path is format 3 plus independent status format 1.
Marek's November 9 direct-cutover decision supersedes temporary dual output:
myxps is the only affected host, there are no external consumers, and format 2
is no longer produced by the maintained CLI/workflow. Old refs, commits and
snapshots remain available. Remote activation and installed-host writes require
final authorization; preparing this source does not perform either.

See the [cutover package](../../docs/track/catalog-system/myxps-cutover-15.md),
[format 3](../../docs/catalog-format-v3.md),
[status 1](../../docs/catalog-status-v1.md) and
[tracker](../../docs/track/catalog-system/map.md).

## Collection and explicit publication

`host_catalog.py` provides `collect`, `validate`, `schema-revision` and `publish`.
The former implicit v2 collect-and-publish entry point is removed. Collection
never advances a ref. Bootstrap has no v3 parent; subsequent collection reads
only the exact v3 parent:

```sh
python3 -B tools/catalog-collector/host_catalog.py collect \
  --repo /tmp/local-v3.git --parent EXACT_V3_PARENT \
  --evidence /path/to/saved-responses --run-id 123 --attempt 1 \
  --output /tmp/new-candidate
python3 -B tools/catalog-collector/host_catalog.py validate \
  --candidate /tmp/new-candidate/format-3 --channel format-3
```

Omit `--parent` for an empty-channel bootstrap. Omit `--evidence` only for
explicitly authorized live acquisition. Saved mode retains receipt times and
makes no requests (`<numeric-id>-releases.json`, `<numeric-id>-receipt.txt`).
The new output directory contains only `format-3/` and sanitized `report.json`.
No v2 parent, tree, validation, artifact or publication is required. The v3 path
normalizes facts directly, applies 32-plus-stable/exact-tag retention and preserves
failed/unattempted sources exactly. Missing publication time can use creation time
for retention; client policies requiring publication time refuse missing facts.

Production enrollment remains 509 app identities / 500 sources, from
`collection-recipes.txt` plus `collection-apps.json`. Declarations alone do not
enroll recipes. Scope stays unchanged while the direct migration is completed;
no expanded dual-output qualification or automatic enrollment is planned.
Hourly batches request at most 500 sources, ordered by available prior successful
collection times (missing first, numeric-ID ties). Failed attempts are reported in
status rather than stored in repository facts. At the current 500-source scope,
each complete batch attempts all sources. Acquisition uses a 750-request internal
allowance, 100-request primary reserve, 512 MiB charged-body budget, 16 MiB per
response and 900-second cooperative time allowance. Actual quota/budgets and
401/403/429 stops still apply; no redirects, retries or fabricated observations.

Publication against a disposable local test remote:

```sh
python3 -B tools/catalog-collector/host_catalog.py publish \
  --candidate /tmp/new-candidate --remote-url /tmp/test-remote.git \
  --expected-v3-parent EXACT_V3_PARENT --source-revision EXACT_SOURCE_COMMIT \
  --run-id 123 --attempt 1 --result /tmp/result.json
```

Omit `--expected-v3-parent` only when the target ref is absent. The publisher
independently checks paths, sizes, exact run/input/parent hashes, enrollment and
full v3 semantics before the sole catalog write. It uses exact-parent publication,
confirms remote acceptance and reports ambiguity honestly; there is no force
rewind or automatic merge. Final status is attempted independently after normal
outcomes, including invalid/missing artifacts and publication failure. The retained
summary schema's `compatibility_publication` is always `not_attempted`; it records
no active v2 write. Artifacts containing format-2 paths are rejected.

The prepared workflow separates read-only acquisition from its write-enabled
publisher. `CATALOG_V3_ENABLED=true` enables only v3/status production; false
skips collection rather than falling back to v2. Scheduled collection additionally
requires `CATALOG_SCHEDULE_REVISION` to equal the exact workflow source commit,
so manual verification can precede resuming the hourly schedule. Status retains 64 summaries,
available detail for eight reports and 90 daily aggregates. Failed reporting may
leave an older timestamped last report. The workflow does not guarantee schedules,
refresh coverage or remote history capacity.

## Reader and consumer runtime

All 529 maintained YAML recipe declarations now use `CATALOG_FORMAT=3`.
`catalog-yaml.am` resolves `release-catalog-v3` once, fetches the descriptor,
app map and readable source path at that exact commit, checks kind/schema bindings
and passes native `asset_facts` to the existing maintained selection policy.
Command caching binds the source/pin and shared source documents; validation
failure latches acquisition, while stale selection consent remains an exact tuple.
Installed runtime requires shell/awk/curl, with no Python, jq or Git dependency.

The active runtime is `catalog-yaml.am`, `catalog-contract-reader.am`,
`catalog-contract-parser.am`, `catalog-contract-tables.am`,
`catalog-yaml-policy.am`, `appimage.am` and the manager's `install.am`.
`APP-MANAGER` retains these files during module sync. Historical v2 shell readers
and bounded offline validators remain for old snapshots and test evidence;
they are not a producer or fallback in the operating path.

Maintainer tools use Python/PyYAML. `Snapshot` validates the exact parent once per
process; `Records` decodes selected sources and `Candidate` validates changed
bytes plus snapshot references. Trust is in-memory and bound to the exact parent
and validation rules, never imported from a receipt. Schema/contract transitions
require all retained source bindings to match. Input pins must match checked-out
source/policy/recipe/rule/schema bytes. The default schema pin comes from the exact
parent descriptor; explicit transitions require `--schemas-revision` at collection
and publication. Classification is evidence-bound and never executes recipes.

The local 256 MiB object guard accounts for compressed changed blobs and fetched
objects before ref advance. It is independent of the 2 MiB/document, 1 GiB/tree
and 20,000-document limits, and does not bound remote reachable history. Expanded
capacity targets remain deferred, not silently accepted by this migration.

## Focused verification and maintenance

```sh
python3 -B -m unittest discover -s tools/catalog-collector -p test_contracts.py
python3 -B -m unittest discover -s tools/catalog-collector -p test_pipeline_publication.py
python3 -B -m unittest discover -s tools/catalog-collector -p test_yaml_manager_integration.py
python3 -B tools/catalog-collector/recipe_policy_source.py
python3 -B tools/catalog-contract/build.py
```

The tests use disposable installations/remotes and inert assets. Historical v2
fixtures support comparisons, not active production. Completed unrelated browser,
scale and manual recovery evidence is reused; do not rerun expanded dual-output
qualification. `qualify_selections.py --native-reader` checks the actual native v3
shell fact projection against saved maintained selections. Physical myxps delivery,
real GitHub acquisition/publication and deployed-browser checks remain explicit
cutover actions, not claims made by offline tests.

`recipe_refresh.py` previews a pinned declaration replacement without executing
installed scripts or reinstalling app binaries. Use the cutover package's exact
metadata scope for myxps. Git history and manual recovery suffice; no new rollback
service, automated restoration or continued v2 publication is part of the plan.

## Preparing recipe migrations

Use the shared [upstream template recognizer](../recipe-reconstruction/README.md)
to inventory a pinned upstream recipe tree before selecting conversion batches:

```sh
python3 tools/recipe-reconstruction/reconstruct.py inventory \
  --recipes-revision COMMIT --summary
```

The same classifier drives the template-driven reconstruction tests and full
JSONL inventories (`--summary` omitted). Standard instances still require runtime
selection/installer review; matching layouts with custom parameters and unmatched
recipes get explicit inspection actions. Recognition does not change these
maintained declaration/selector policies or collection enrollment. Already-short
fork declarations are not upstream-template instances; use the explicit `render`
interface to compare their upstream meaning rather than treating a layout
nonmatch as evidence of custom shell logic.


Saved-batch enrollment tests use one replay implementation with a receipt name
and the pinned former enrollment Git revision. They read the original collection
list from `b61eb2733441d2dd5f998f350ce32a3da1ebc2f9` and
`10a4c03eca229434a346fb3e3303f19621484a80`; those objects must be available for
local tests. The normal current-workflow test follows the complete present
configuration. [Ticket 135](../../docs/track/release-catalog/issues/135-prepare-next-ten-existing-recipes.md)
prepares 53-recipe/51-source enrollment;
[136](../../docs/track/release-catalog/issues/136-publish-next-ten-and-refresh-live-policy.md)
records its authorized publication and protected compiled-policy deployment.
