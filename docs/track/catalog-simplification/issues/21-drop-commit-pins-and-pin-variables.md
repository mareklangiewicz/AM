# Drop the commit pins and pin variables

Type: task
Label: implementation:task
Status: open
Triage: needs-triage
Blocked by: 16

## Outcome

As decided in [Decide which commit pins are needed](05-choose-needed-commit-pins.md):
catalog and status documents carry no commit hashes of ours (`inputs`, schema
pins, provenance commits and `recipe.blob`, status catalog pins); `producer` and
summaries keep the run `id` and `attempt`; provenance keeps its content hashes
and builds review links from the pinned catalog commit. The repo variables
`CATALOG_SCHEDULE_REVISION` and `CATALOG_SCHEMA_REVISION` are deleted:
scheduled runs collect at HEAD; `release.py` loses `--repin-schemas` and the
repin step but still refuses to ship a schema change while the live catalog
fails HEAD's contract (a test shows that refusal). The host modules, the page,
their tests and `AGENTS.md`'s ship rule follow.

Readers stop pinning a commit (Marek, November 25, 2026, during ticket 13): the
page and the host read raw files at `main-marek` directly, with no GitHub API
call to resolve the branch. The page drops `?pin=`, "Load latest", the
"Snapshot <pin>" line and the "Pinned snapshots" help; AM drops its
per-command ref resolution and session pin (`modules/catalog-yaml.am`). Files
read in one tab or command may come from neighbouring runs, which is harmless
without cross-file pins; a transient 404 (a CDN lag) is retried.
