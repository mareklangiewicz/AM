# Cut over to the simplified catalog in one change

Type: task
Label: implementation:task
Status: open
Triage: ready-for-agent
Blocked by: none

## Outcome

One ship moves AM from the v3 branches to the simplified catalog this map
decided, with no compatibility layer: the new contract, the collector writing
`catalog/` in `main-marek`, hosts and page reading it, a one-time conversion
seeding it, and the old branches, pins and migration-era tools gone. Merges
tickets 14, 16, 17, 20, 21 and 22 (their Outcomes are this ticket's spec, minus
every step that only bridges old and new) and drops catalog-system 47.

Marek, November 25, 2026: "We need to switch to new simplified approach ASAP.
No need for complicated migration steps. No one else is using AM besides me and
we always can remove/uninstall my apps manually if needed and install again
when new approach is in place." Chosen then: a one-time conversion of today's
catalog (not a recollection from scratch) and one big change (not two or
three ships).

## Parts

Each part lands test-first on `ci/cutover`; nothing reaches `main-marek` until
the whole ships.

1. **Contract.** `schemas/catalog.schema.yaml`, hand-written, every kind under
   `$defs`, a one-line `description` per field (tickets 10, 20). It states the
   new formats directly: times (06), per-release and asset facts and retention
   (08, 07), encodings (09), failure fields and `status/runs.yaml` (11),
   provenance labels (12). `tools/catalog-contract/build.py` generates the awk
   tables and `definitions.mjs` from it; no byte-identity with v3. The
   generated `schemas/catalog/*.schema.json`, `.vscode/settings.json` and the
   v3/status-v1 field prose go.
2. **Collector.** Writes repository, apps, provenance and status documents under
   `catalog/` and `catalog/status/` of `main-marek`, one commit per run, each
   document's first key `$schema:` (relative, `#/$defs/<kind>`). A rejected push
   fetches, rebases its `catalog/`-only commit and retries a bounded number of
   times (17). No commit hashes of ours in any document (05); `producer` keeps
   run `id`/`attempt`. Scheduled runs collect at HEAD.
3. **Readers.** `modules/catalog-yaml.am` and the page read raw
   `main-marek/catalog/` files with no API ref resolution, no session pin, no
   `--commit`, no `?pin=`/"Load latest"; a transient 404 is retried (21). The
   page states ticket 13's accepted "How it works" text.
4. **Seed.** A throwaway script converts the tip of `release-catalog-v3` (and
   the per-repository failures from `catalog-status-v1`) into the new
   documents once, as the cutover commit's `catalog/`. It lives under
   `scripts/24/`, is run once and never maintained.
5. **Removal.** The writers of `release-catalog-v3`/`catalog-status-v1`, the
   publication binding between them, `CATALOG_SCHEDULE_REVISION`,
   `CATALOG_SCHEMA_REVISION`, `release.py --repin-schemas` and the repin step
   (the live-contract refusal stays, now against `catalog/`), and the
   collector's migration and qualification tools that only served the v3
   rollout (listed for Marek before deletion). `tests.yml` ignores
   `catalog/`-only pushes; `release.py plan` counts them as needing no tests;
   `AGENTS.md` names `git log -- . ':!catalog'`.
6. **Docs.** `GLOSSARY.md` (superseded terms marked), the operating policy, the
   collector README, the How it works page.

After the ship: Marek removes and reinstalls his apps; the old branches'
tips become local `archive/<name>` refs, and are deleted from origin with his
OK; ticket 15 measures the result; 18's twin check and 19 continue on
`catalog/`.

## Comments

November 25, 2026, Marek's answers before part 1 (contract):

- Seams confirmed: contract worked examples through the awk and JS
  validators; one collector run plus a push-race retry; seed fixture
  conversion plus a one-time real-tip selection comparison; host tests on raw
  `catalog/`; page tests; `release.py` counting `catalog/`-only pushes as
  needing no tests.
- **No `format:` or `kind:`**: the `$schema:` fragment (`#/$defs/<kind>`) is
  the kind; each kind's `$schema` value is one constant relative path.
- **Recipe labels live in `apps.yaml`**: `apps: {<app>: {repository:
  "repositories/<name>.yaml", x86_64: "declaration"|"script", ...}}`; no
  `provenance/` files and no cross-file coverage checks.
- **No `catalog.yaml` and no `status/status.yaml`**: once the pins go, the
  first holds only `producer` and the second nothing. The run that wrote a
  commit is in `status/runs.yaml` and the commit message. `catalog/` is
  `apps.yaml`, `repositories/`, `status/runs.yaml`, `status/statistics.yaml`.

November 25, 2026, progress on `ci/cutover`:

- Part 1 (contract) `36832f30d`, `e01b53758`: `schemas/catalog.schema.yaml`,
  `docs/catalog-format.md`, `modules/catalog-parser.am`/`catalog-tables.am`,
  `tools/catalog-contract/parse.mjs`/`schema.mjs`, worked examples (Long tests
  45610783644 passed). Readers do not check retention; it is the writer's.
  `git_scope.branches` goes (branches are the `refs/heads/*` keys).
- Part 2 (collector) `fb073d5cd`: `tools/catalog-collector/documents.py` and
  `catalog_run.py collect|publish`; `tools/catalog-contract/platforms.json` is
  the one Linux/architecture guess. A full labelling run: 8,466 apps in 2.3 s,
  7,163 `declaration`, 2,781 `script`. Left for part 5: `catalog.yml` and the
  composite action call `catalog_run.py`; `git_observations` returns the new
  shape directly (drop `documents._git`).

November 25, 2026, part 4 (seed), Marek's answer: retention also keeps, for
each guessed processor type, the newest tag with an `.AppImage` file. Evidence
(`scripts/24/compare.py`, v3 tip `8b6d58033` under main-marek `8335c92f6` vs
the seed under HEAD, 9,869 recipes, one fixed clock): with ticket 08's rule
alone, 9,780 selected the same file, 15 were the twins (refused by v3 too), and
74 stopped resolving (47 x86_64, 27 aarch64; 64 AppImages), because their only
matching file sat in an older release; e.g. `ai-security-scanner` ships only a
`.deb` since v0.7.0 and its last AppImage was v0.1.7. "Newest with a Linux
download" did not cover them: `.deb` files and Linux tarballs count as Linux.
Page and schema text say so (ticket 13's rule 5 and "Kept releases" gain the
clause). Also part 4: the 14 twin repositories (v3 `same_tag_conflict`, never
collected) are left out of the seed, so the first collection reads them.
Marek, earlier the same day: `host_cutover.py` and its tests deleted (part 3).

November 25, 2026, part 4 Long tests 45649586477 passed. Marek's answers
before part 5 (removal), to the traced list (imports from `catalog_run.py`,
`seed.py`, `release.py`, `merge.py`, `convert.py`; every `.github/` and
`fast-tests.sh` call):

- Delete: the eight collector `qualify_*.py`; `bulk_enrollment`,
  `bulk_sources`, `retire_sources`, `recipe_refresh`, `installed_recipe`; the
  v3 write path (`incremental`, `pipeline_publication`, `publication`,
  `contracts`, `retention_v3`, `writer`, `wire_validation`); `provenance` once
  `documents` imports `reconstruct` directly; `collection_interface` once
  `registry_names` moves to `host_catalog`; catalog-browser
  `qualify_boundaries.mjs`, `qualify_restore.py`, `prepare_boundaries.py`,
  `preview.py`; catalog-contract `build_v3.py`, `definitions.{json,mjs}`,
  `reader.mjs`; `modules/catalog-contract-*.am`; `schemas/catalog/`; v3 docs;
  their tests. `host_catalog` keeps `configuration()`/`collect()` only;
  `.vscode/settings.json` points at `schemas/catalog.schema.yaml`.
- Kept, not migration-era: `bulk_recipes`, `bulk_recipe_urls`,
  `catalog_sources` (used by `recipe-conversion/convert.py`, which `merge.py`
  uses), `pinned_recipes` (recipe-reconstruction tests). Tests on
  `fixture_v3`/`reference_*` that cover the kept selection policy are ported,
  not deleted.
- The collector pushes to `main-marek` with the job's `GITHUB_TOKEN`,
  `contents: write` on the commit job only.
- The agent deletes `CATALOG_SCHEDULE_REVISION`/`CATALOG_SCHEMA_REVISION`
  (`gh variable delete`) when the cutover ships.

November 25, 2026, parts 5 and 6 on `ci/cutover`:

- `60658389a`: `catalog_run.py`, `seed.py`, `merge.py` and `convert.py` import no
  v3 module (`git_observations` returns the document's shape; `registry_names`
  in `host_catalog`, so an unnamed enrolled repository refuses the run).
- `043514fc7`: `release.py` without pins, repin or dispatch; `docs/` and
  `catalog/` need no Long tests; a `catalog/`-only push waits for no Fast
  tests run; a change to `catalog/` or the contract validates HEAD's
  `catalog/` with HEAD's awk and node readers; the deployed `schema.mjs` is
  compared.
- `d6f44a570`: the agreed deletions; `catalog.yml` runs `catalog_run.py`
  (collect read-only on `main-marek`'s tip, publish with the job's
  `GITHUB_TOKEN` as an HTTP header); the composite action is inlined;
  `tests.yml` ignores `catalog/`. `CATALOG_V3_ENABLED` gates nothing now
  either: it joins the variables to delete at the ship, if Marek agrees.
  Tests ported for behaviour that stays; new run tests for failure fields, a
  run-wide stop and retirement (`removed.json` had none).
- `a7ce93701`: part 6 docs.

November 25, 2026, shipped with Marek's OK: `release.py ship --ci cutover`
pushed `a5095cbc4` (the seed from v3 `3ba427e2a`; `catalog/` valid under
both readers, about 2 minutes) after Long tests 45654975965; Fast tests
45658635274 passed. The page was redeployed (45658736679; the deployed
`schema.mjs` serves). `CATALOG_SCHEDULE_REVISION`, `CATALOG_SCHEMA_REVISION`
and `CATALOG_V3_ENABLED` deleted; `ci/cutover` deleted. The first collector
run, 45658789307, committed `0644037da` (only `catalog/`, 500 files, with the
job's token): 500 selected, 498 read, 0 failed, 345 MB, 7 minutes, and
`stop_reason: request_budget`: part 5 dropped the v3 workflow's 750-request
allowance, so `host_catalog.REQUEST_CAP` (500) left no room for the Git reads
of `git-sources.json` (8 requests). Fixed by `REQUEST_CAP = 750`, with a test
that a full batch and every Git read fit. Left: Marek reinstalls his apps;
then the old branches become local `archive/<name>` refs and leave origin
with his OK.

November 26, 2026, myxps: `am -s` installed the new reader modules and removed
the `catalog-contract-*.am` ones (all modules and `APP-MANAGER` byte-equal to
`main-marek`); Marek removed and installed his 19 catalog apps from his
terminal (`am -R`/`am -i`, `am reinstall kitty zmx`); every `recipe.am` now has
`AMREPO=…/main-marek` instead of the `5429e09d` pin. `am -u` exit 0 over all
apps through the new reader, no warnings. `fastfetch` (an old-style updater
calling `catalog-yaml.am`) and `firefox`, `appimagetool`,
`appimageupdatetool` (no catalog) were left as they were.

November 26, 2026, with Marek's OK: `release-catalog-v3` (`3ba427e2a`, the seed's
source, unchanged since) and `catalog-status-v1` (`f09881956`) deleted from
origin; their tips are kept in the myxps checkout as `refs/archive/<name>`.
A host still on the old modules (they read `release-catalog-v3`) needs
`am -s` and its apps reinstalled; `git push origin
refs/archive/release-catalog-v3:refs/heads/release-catalog-v3` restores the
branch if one must keep working meanwhile.

November 26, 2026, mylenovo (the second host on this fork): it had the old
`catalog-contract-*` modules, but its 18 recipes were already the new ones
(`CATALOG_FORMAT=3`, `AMREPO=…/main-marek`; kitty's byte-equal to myxps's),
so no reinstall was needed. `am -s` added `catalog-reader.am`,
`catalog-parser.am` and `catalog-tables.am` and removed the
`catalog-contract-*` ones; `APP-MANAGER` and all 11 modules then matched
`main-marek` (sha256). `am -u` exit 0 over all apps (9 updated, among them
kitty to 0.51.1; zmx already 1.0.1), no errors, no sudo prompt.

November 26, 2026, both hosts, Marek's call: firefox removed (`am -R`, and
Ubuntu's `firefox` snap-stub package purged), zellij removed, fastfetch
installed on mylenovo and reinstalled on myxps; all exit 0. fastfetch still
has no `recipe.am`: `programs/x86_64/fastfetch` is one of 1,072 x86_64 scripts
in the inline form (its own `AM-updater` calling `catalog-yaml.am`) against
8,308 with `CATALOG_FORMAT=3`, so a fresh install gives the same files on
both hosts (sha256-equal). That form reads the new catalog too.
