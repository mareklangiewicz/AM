# Read original templates and recognize recipe instances across upstream families

Type: task
Status: claimed
Triage: ready-for-agent

Marek requested reading pinned Git originals instead of copies, discovering all
upstream templates to identify custom logic, and using the tool to simplify
migration preparation/tests. Remove vendored templates/generator excerpts;
discover templates from recorded source revisions. Keep matching conservative:
arbitrary shell inside template parameters is still custom/unreviewed logic,
and a nonmatch alone is not proof of custom behavior. Integrate a reusable
migration inventory and template-driven test cases without changing deployed
recipes, selection policy or collection enrollment. Record actual coverage and
limitations with offline validation. Commit source work locally.
