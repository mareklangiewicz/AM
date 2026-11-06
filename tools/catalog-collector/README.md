# Maintained YAML catalog tools

Current contract: [operating policy](../../docs/catalog-operating-policy.md).
The daily `.github/workflows/catalog.yml` publication runs `host_catalog.py`.
Collection enrollment is `collection-recipes.txt`, resolved through literal recipe
declarations; declaring a recipe does not enroll it for collection.

## Entry points

- `host_catalog.py`: collect one release-list page per enrolled repository,
  normalize/retain facts, validate YAML, and publish to a remote-free local Git
  repository at an exact expected parent. The workflow pushes that candidate with
  an exact lease. `--evidence DIRECTORY` reads saved responses instead of HTTP.
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
installed/deployed selectors remain unchanged until a separate rollout. Transitional
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
