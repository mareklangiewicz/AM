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
The prepared union is limited to 224 repositories (published baseline remains 128 until rollout). Each scheduled run attempts at most
52, oldest collection attempt first (never-attempted sources first, numeric ID
ties). The schedule is every three hours, nominally covering the prepared scope in five
runs. Transfer/time budgets or source failures can reduce successful coverage;
the report lists actual attempts and pending app identities. Selected-release
freshness remains 48 hours, independent of these scheduling attempts.

Batch collection preserves all untouched documents and their schema/observation
times. An upstream failure records a failed attempt without changing previous
release facts or last-success metadata. Auth/rate failures stop further requests
in that run. A failed partial HTTP read conservatively charges its full remaining
read allowance, so repeated failures cannot evade the shared byte budget.
A new app enters apps.yaml only after successful source collection;
an enrolled identity is not a claim of successful publication. Removing retained
sources in batch mode refuses. Source enrollment is still an explicit reviewed
file change, never automatic URL discovery.

The 16 MiB response, 96 MiB per-run transport, 300-second cooperative acquisition,
2 MiB document, 1,024-file read and Git-history bounds remain. The prior 128-source
step is published; the next 224-source scope requires its recorded preflight before
publication. Whole-tree validation has not been qualified for thousands.

## Entry points

- `host_catalog.py`: collect one release-list page per attempted repository,
  normalize/retain facts, validate YAML, and publish to a remote-free local Git
  repository at an exact expected parent. The workflow pushes that candidate with
  an exact lease. `--batch-size 52` selects bounded collection;
  `--evidence DIRECTORY` reads saved responses instead of HTTP. Without a batch
  size, strict all-or-nothing collection remains available for at most 52 sources.
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
  200-request per-invocation bound remains, and proposals never enroll sources.
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
