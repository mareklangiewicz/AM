# Maintained YAML catalog tools

Current contract: [operating policy](../../docs/catalog-operating-policy.md).
The `.github/workflows/catalog.yml` publication runs `host_catalog.py`.
Collection enrollment is `collection-recipes.txt`, resolved through literal recipe
declarations, plus `collection-apps.json` for catalog-only identities; declaring a
recipe does not enroll it for collection. Catalog-only rows contain exactly
`app`, positive integer `repository_id`, and canonical `repository` (owner/name).
They need verified source identity, but no installer declaration, asset selector,
payload inspection or policy compilation. They do not claim AM installation support.
App identities must be unique across both lists; sources are deduplicated by
numeric ID and conflicting names refuse. When a recipe is migrated, move its
enrollment to `collection-recipes.txt` in the same change, preserving its identity.
The published union contains 500 verified repositories; the enrollment ceiling is
500, now fully enrolled. Further distinct sources require separately measured
scaling work in 138, alongside identity/capacity preflight. Each scheduled run attempts at most
500, oldest collection attempt first (never-attempted sources first, numeric ID
ties). The schedule is hourly, covering the current published scope in one
full successful run. Transfer/time budgets or source failures can reduce successful coverage;
the report lists actual attempts and pending app identities. Selected-release
freshness remains 48 hours, independent of these scheduling attempts.

Batch collection preserves all untouched documents and their schema/observation
times. An upstream failure records a failed attempt without changing previous
release facts or last-success metadata. Auth/rate failures stop further requests
in that run. A failed partial HTTP read conservatively charges its full remaining
read allowance, so repeated failures cannot evade the shared byte budget.
Safe numeric quota headers are reported per response and in the metrics summary.
Before a subsequent request, stop if the live primary budget has at most 100
remaining and its reset has not passed. HTTP 401/403/429 still stop immediately;
there is no automatic retry or sleeping in the request loop. Redirects are refused
before following them, so a counted request cannot secretly add follow-up calls.
Reports include request attempts (zero for offline evidence), charged bytes,
selected/attempted/successful/unattempted counts, budget stop reason, timings,
source-success age counts at 24/36/48 hours, and history object/snapshot allowance.
CI warns about sources without successful observations or older than 24 hours.
These source-success ages do not reobserve retained releases outside page 1 or
replace the client's own selected-release freshness check.

A new app enters apps.yaml only after successful source collection;
an enrolled identity is not a claim of successful publication. Removing retained
sources in batch mode refuses. Source enrollment is still an explicit reviewed
file change, never automatic URL discovery.

The 16 MiB response, 512 MiB per-run transport, 900-second cooperative acquisition,
2 MiB document, 1,024-file read and 256 MiB Git-history bounds apply. The real 500-source scope is published with exact-pin preservation receipts
([latest publication](../../docs/track/release-catalog/research/next-500-publication.md)).
[The larger-batch assessment](../../docs/track/release-catalog/research/refresh-batch-sizing.md)
motivates the 500/hour profile; [rollout 146](../../docs/track/release-catalog/issues/146-roll-out-hourly-metadata-refresh.md)
records validation and operational status. Whole-tree validation and history
storage have not been qualified for thousands.

## Entry points

- `host_catalog.py`: collect one release-list page per attempted repository,
  normalize/retain facts, validate YAML, and publish to a remote-free local Git
  repository at an exact expected parent. The workflow pushes that candidate with
  an exact lease. `--batch-size 500` selects bounded collection;
  `--evidence DIRECTORY` reads saved responses instead of HTTP. Without a batch
  size, strict all-or-nothing collection remains available for at most 500 sources.
- `catalog_sources.py scan --out FILE`: discover explicit source bindings from
  literal catalog aliases and whole pinned upstream-template instances; do not
  treat arbitrary GitHub links as release sources. `verify --scan FILE --out FILE`
  proposes public numeric identities after rechecking source hashes/bindings and
  a release probe. It checkpoints local evidence and never edits enrollment.
  Review redirects/unsupported cases separately. Set GH_TOKEN for authenticated
  public reads; no visitor credentials, new secret or backend is required.
  `verify --review-redirects` explicitly checks a renamed repository at its
  canonical endpoint, requiring the alias and canonical public numeric IDs to
  agree before probing releases. Default verification still defers redirects.
  Proposal scope is independent of the active enrollment cap; the fixed
  200-request per-invocation bound counts transport attempts, including explicitly
  followed metadata redirects. Redirect review allows at most three hops per GET,
  only to exact HTTPS `api.github.com` repository metadata endpoints; release-probe
  redirects and unexpected destinations refuse before forwarding credentials.
  Receipts mark this accounting as `transport_attempts_v1`. Older unmarked
  discovery receipts counted logical GET calls and do not prove underlying hop
  counts; their stored evidence is unchanged. Proposals never enroll sources.
- `recipe_policy_source.py`: regenerate recipe declaration data in
  `modules/catalog-yaml-policy.am`; selector logic remains maintained shell/awk.
- `recipe_refresh.py`: preview or explicitly apply one installed recipe/source
  snapshot refresh. Follow the operating policy for hashes, backup and runtime
  coordination. It does not update binaries or deploy modules.
- `host_cutover.py`: explicitly scoped maintenance reinstall prepare/apply, as
  documented in the operating policy. This is not the ordinary update path.
- `appimage_policy_source.py`: regenerate the transitional AppImage registry from
  `test-data/appimage-policies.json`. Retain it until reviewed complete declarations
  replace these policies. Do not widen collection or change legacy behavior here.

Snapshot loading validates each document once and uses PyYAML's safe C loader
when available (safe Python fallback). Publication starts its temporary index
from the exact parent, reuses unchanged Git blobs and updates changed/deleted
paths in one index operation. All original-byte, canonical and cross-file checks
remain; snapshots are still materialized in full, so this is not an incremental
reader or qualification for thousands of sources.

`publication.py` owns isolated Git operations, bounded snapshot reads and
remote-free exact-parent publication. `yaml_publication.py` validates documents
with the actual distributed reader at `modules/catalog-yaml-reader.am`.
`bounded.py`, `retention.py` and `writer.py` normalize, merge and encode facts.
The installed client and installer remain shell-only.

## Declared recipe architecture eligibility

The maintained selector filters asset **names**, case-insensitively for platform
and architecture labels, before applying the recipe's case-sensitive asset ERE.
Windows, macOS and Darwin names are excluded. The current source contract is:

| Target | Required label | Excluded labels |
| --- | --- | --- |
| x86_64 | None; unlabelled names remain eligible | aarch64, arm64, armhf, armv7, i386, i686 |
| aarch64 | aarch64 or arm64 | x86_64, amd64, armhf, armv7, i386, i686 |
| i686 | i386 or i686 | x86_64, amd64, aarch64, arm64, armhf, armv7 |
| armv7l | armv7 | x86_64, amd64, aarch64, arm64, i386, i686 |

These are substring rules, not binary architecture verification. `armhf` alone
never admits a target; an explicit armv7 name can additionally contain armhf.
Adding armhf exclusions to the three other targets is ticket 127's source change;
the guard was deployed November 6 at reviewed source `fa36ebb7e` (ticket 132). Transitional
named policies are unaffected. Names and URLs can disagree, so a declaration still
needs reviewed real asset evidence and a sufficiently precise asset pattern.

## Offline verification

Python 3.10+ and PyYAML are required. Lifecycle checks additionally use bash, dash,
GNU tools, git, mawk, gawk, BusyBox awk, tar, xz and unzip.

```sh
python3 -B -m unittest discover -s tools/catalog-collector -p 'test_*.py' -v
python3 -B -m unittest discover -s test/e2e -p 'test_*.py' -v
./test/e2e/run debian fedora
```

The first suite covers current collection/publication, reader grammar and bounds,
retention, declaration compilation, portable selection, installer/updaters and
metadata refresh in disposable directories. Some lifecycle groups iterate over
many transitional recipes and take longer. The container suite executes whole
installed commands with networking disabled; see `test/e2e/README.md`.

`fixture_*.py`, `reference_*.py` and `test-data/` support tests. Saved upstream
responses are hash-checked against retained evidence under `docs/track/`; no
fixture loader collects data or runs historical migration commands.

Historical format-1 collector/workflow, sharded dispatch, staging, migration,
quota/churn probes and runnable YAML experiments were retired in ticket 118.
Their source and experiment results remain in Git history at `007ea4871`.
Tracked research evidence and local deployment backups were retained. Current
publication accepts existing YAML state only; the one-time format-1 bootstrap
option has been removed. There is no historical collector fallback.

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

## Private format-3 candidates (ticket 11)

The deployed workflow still uses the legacy entry point above. New local work uses
explicit operations, with no publication/ref advancement during collection:

```sh
python3 tools/catalog-collector/host_catalog.py collect \
  --repo /tmp/remote-free-legacy.git --parent EXACT_FORMAT_2_COMMIT \
  --evidence /path/to/explicitly-saved-responses \
  --run-id 123 --attempt 1 --output /tmp/new-candidate
python3 tools/catalog-collector/host_catalog.py validate \
  --candidate /tmp/new-candidate/format-3 --channel format-3 \
  --expected-source EXACT_MAINTAINED_SOURCE_COMMIT
python3 tools/catalog-collector/host_catalog.py validate \
  --candidate /tmp/new-candidate/format-2 --channel format-2
```

For subsequent target updates supply `--v3-repo REPO --v3-parent EXACT_COMMIT`;
bootstrap has no prior target facts and does not translate/prune the old channel.
Each format merges from its own parent. Omit `--evidence` only within separately
authorized live acquisition scope. Saved mode never reads credentials or calls
HTTP and keeps original receipts (`<numeric-id>-releases.json`,
`<numeric-id>-receipt.txt`). Responses are never reacquired for dual output.
Collection uses one-page/oldest-attempt scheduling and existing bounded transport.
It writes `format-2/`, `format-3/` and sanitized `report.json` in a new output
folder, with exact parents/inputs, run/attempt and content hashes. No raw response,
credential, executable recipe or temporary recovery store is emitted.

Inputs default to the exact maintained checkout revision, except that subsequent
v3 collections retain the validated parent's schema revision by default. The
schema/reader/contract checkout must still match that pin; collector-only changes
therefore reuse source blobs without changing their schema binding. Actual schema
changes refuse that default before acquisition. An explicit `--schemas-revision`
can advance the binding, but every retained source must then have that revision;
failed or deferred old-schema sources refuse the entire candidate before output.
No source observation is rewritten to make a schema transition pass. Independent
`--source-revision`, `--policy-revision`, `--recipes-revision`, `--rules-revision`
and `--schemas-revision` must match the actual relevant checked-out bytes.
The publisher independently derives its default schema pin from its trusted exact
`--expected-v3-parent`, fetching and validating that parent; artifact contents
cannot choose it. Explicit transitions also need trusted `publish
--schemas-revision PIN`. This extra parent validation/fetch is part of the pending
full workload resource qualification. The prepared scheduled workflow retains
the parent default; a contract transition requires a separately prepared explicit
CLI invocation or workflow change.
Dirty/untracked input files refuse. `--registry` must contain the exact reviewed
registry from the policy pin; it is not permission to allocate a source implicitly.
`--reviews` optionally supplies explicit reviewed custom classifications by
app/architecture, each bound to exact recipe repository/commit/path/blob,
recipe SHA-256, rules revision, dependencies and description. Classification
never executes recipes. Whole-wrapper/template recognizers stay conservative;
unsupported cases remain unknown. Review links use recipe commits, not catalog C.

The [format-3](../../docs/catalog-format-v3.md) and
[status-1](../../docs/catalog-status-v1.md) contracts describe exact fields, grammar,
encodings and reader APIs. `publish` is the explicit publisher/finalizer. It revalidates bounded artifacts,
checks trusted workflow input/run/parent/content bindings, publishes format 2 first,
then optionally v3/status, confirms remote acceptance and reports ambiguous writes
as unknown. The prepared workflow uses separate acquisition/publisher jobs; new
channels remain disabled until reviewed rollout activation. The legacy command
remains compatible for existing local maintenance callers. Scale/resource defaults and
real-browser delivery are not qualified by these parser/fixture checks.

Regenerate editor schemas, browser definitions and shell field tables with
`python3 tools/catalog-contract/build.py`. Focused shared checks:

```sh
python3 -B -m unittest discover -s tools/catalog-collector -p test_contracts.py -v
```

These require Node and jsonschema in addition to maintainer Python/PyYAML, plus
mawk, gawk and BusyBox for portability checks. Installed clients require only
shell/awk. Browser parsing uses exact BigInts; `releaseFacts` exposes reconstructed
URLs, media types and effective observations. Parser checks do not establish DOM,
CORS, performance, accessibility or upstream/binary trust.


## Incremental candidates and explicit finalization (ticket 12)

`incremental.Snapshot` streams the exact parent through the maintained readers
once per process and retains source identity/attempt/success metadata. It keeps
no full decoded source tree. `Records` loads only selected sources; `Candidate`
validates changed bytes and whole-tree references, reusing untouched Git blobs.
Trust is an in-memory object bound to exact parent commit and a digest of all
validation code/schema inputs. Imported validation receipts never establish trust;
a new process or changed rules performs full parent validation again. No durable
checkpoint/trust store is added. Fallback cost is recorded in collection evidence.

New collection flags expose source/request/response/total-byte/time/reserve
settings. The private command allows 10,000 enrolled sources, default batch 500
and request allowance 750; actual quota/reserve and byte/time guards still stop
safely. These settings await ticket-14 representative measurements. A batch is
requested scope, not a claim that every enrolled source was refreshed. Deployed
legacy defaults remain unchanged until prepared workflow source is activated.

Explicit publication against a **disposable local test remote**:

```sh
python3 tools/catalog-collector/host_catalog.py publish   --candidate /tmp/new-candidate --remote-url /tmp/disposable-remote.git   --expected-v2-parent EXACT_FORMAT_2_PARENT --source-revision EXACT_SOURCE_COMMIT   --run-id 123 --attempt 1 --enable-targets --result /tmp/publication-result.json
```

For an existing target pass `--expected-v3-parent EXACT_TARGET_PARENT`. Without
`--enable-targets`, only the compatibility channel is written. That switch is an
explicit write scope, not deployment authorization. Production write/dispatch,
public-channel activation and installed-host changes need their existing approval.
A failed/refused/ambiguous stage stops further catalog writes. Final status is
attempted independently when target channels are enabled. Missing/invalid candidate
artifacts yield unknown source counts; no fake zeroes or publication pin. The CLI
returns failure after finalization for invalid or unconfirmed active stages.

Status retains 64 summaries, available source details for 8 reported attempts and
90 daily aggregates, with original timestamps and explicit unknown-count coverage.
Source detail includes known selected-unattempted sources. A newer catalog can
coexist with the unchanged older status report after reporting failure. No public
start record, automatic merge/write retry or report-delivery queue exists.

The collection-only local Action installs no dependencies or write credentials.
The prepared hourly/manual workflow checks out exact source with credential
persistence disabled, installs pinned dependencies before step-scoped tokens,
transfers one-day-retention data artifacts and uses a separately checked-out
trusted publisher. Artifact paths, type/size, input/run/parent/hash bindings and
catalog semantics are checked again; artifact code is never executed. Remote Git
auth is scoped to the fixed repository URL and HTTP redirects are disabled.
The prepared workflow keeps `CATALOG_V3_ENABLED` unset/false until rollout review.

`rehearse_pipeline.py` runs the saved retained seed plus replay/subset/full synthetic
updates in an isolated repo, with separate-process RSS, Git blob reuse and
consistently packed reachable-history measurements. It never fetches HTTP or
mutates the preserved evidence repository. The saved-data MIME conflict is resolved by the accepted leading-`=` literal
escape in `media_type`: strip one `=` and return literally before alias handling.
The writer escapes bare literals and original leading `=` values. Existing default,
empty, full-type and `zip` alias semantics stay unchanged. Saved rehearsal results
belong to ticket 12; they do not establish live acquisition or scale qualification.
