# Move the catalog into `catalog/` in main-marek

Type: task
Label: implementation:task
Status: open
Triage: needs-triage
Blocked by: 14, 15, 17

## Outcome

The collector writes facts and status under `catalog/` and `catalog/status/` of
`main-marek` in one commit per run, as decided in
[Choose the catalog directory layout in main-marek](04-choose-catalog-directory-layout.md);
hosts (`modules/catalog-yaml.am`) and the webpage (`web/catalog/`) resolve
`heads/main-marek` and read `catalog/` at that commit; the confirmed-publication
binding between channels is removed; `tests.yml` ignores `catalog/`-only pushes
and `release.py plan` counts them as needing no tests; `AGENTS.md` names
`git log -- . ':!catalog'`. Every document's first key becomes `$schema:`, a
relative path to `schemas/catalog.schema.yaml` with its kind as fragment,
replacing `schema:` and the host's pinned-URL check; `.vscode/settings.json` is
deleted ([ticket 10](10-choose-schema-form-and-wiring.md)).

After the switch the collector stops writing `release-catalog-v3` and
`catalog-status-v1`; their tips become local-only `archive/<name>` refs and,
after a week of clean directory runs and with Marek's approval, the branches are
deleted from origin.
