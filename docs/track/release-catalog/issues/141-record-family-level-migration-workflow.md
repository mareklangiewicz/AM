# Record family-level migration validation and bulk exact-instance workflow

Type: task
Status: resolved
Triage: ready-for-agent
Assignee: codex

Marek's latest steering in the November 6 handoff replaces routine per-app payload
inspection and lifecycle rehearsals with family-level translation validation,
then bulk migrations of exact instances preserving literal settings. Catalog all
GitHub-backed apps first, independently of recipe migration.

## Answer

Updated the [maintained reconstruction README](../../../../tools/recipe-reconstruction/README.md#current-migration-workflow--family-validation-then-bulk-translation)
with the family contract, reuse of existing evidence, compact per-batch accounting,
focused checks and exception handling. Full relevant regressions are required
when shared mechanics change, rather than merely resuming or adding exact instances.
Tickets 138/139 and the map point to this policy. Historical results remain intact.
Trusting upstream recipes is an explicit assumption, not a verified claim about
upstream review. Recognition alone does not establish runtime equivalence, and
this documentation change certifies no new family or app. Known payload exclusions
remain pending focused resolution.

Documentation-only: checked local links and whitespace. No runtime/tool changes,
new downloads, test-suite reruns, recipe migrations, enrollment, push, dispatch,
installed-host changes or yadm pointer bump. The prepared 131-app / 128-source
publication package in 140 still awaits Marek's call.
