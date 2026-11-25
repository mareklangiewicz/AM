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
