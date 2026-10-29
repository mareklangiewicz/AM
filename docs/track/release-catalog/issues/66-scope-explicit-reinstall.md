# Restrict explicit reinstall to named applications

Type: task
Status: open
Triage: ready-for-agent

## Problem

User invoked `am reinstall obsidian`; manager also removed/reinstalled two other
apps whose saved installation recipes differed from the current database.
Help advertises named-app and multiple-named-app forms, so this is surprising
and expands a destructive operation beyond the requested selection.

## Evidence and scope

In modules/install.am's reinstall branch, explicit entries mark selected saved
recipes as changed, then a second _determine_args enumerates every installed app.
The subsequent loop processes every changed recipe without filtering by entries.
No-argument changed-recipe behavior must remain distinct from named-app behavior.

Reproduce through disposable installed-command tests with multiple changed apps,
then constrain explicit selection before any mutation. Verify named single/multiple
selection, no-argument selection, missing names and unrelated app preservation.
Do not reproduce through host removal/reinstallation. No fix applied yet.
