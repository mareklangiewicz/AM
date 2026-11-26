# Drop the leftover .vscode schema associations

Type: task
Label: implementation:task
Status: resolved
Triage: ready-for-agent
Blocked by: none

## Outcome

Ticket [10](10-choose-schema-form-and-wiring.md) said the `.vscode` schema
associations go; `.vscode/settings.json` still has them (noted in ticket 25).
Remove them, or the file if nothing else is left in it.

## Answer

`.vscode/settings.json` held only the four `yaml.schemas` associations, so the
file (and with it `.vscode/`) is deleted. Every catalog document and example
names its schema with its first-key `$schema` (ticket 10), which
yaml-language-server follows without editor configuration (ticket 03).
