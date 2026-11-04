# Exercise a simple offline app-to-release consumer

Type: prototype
Status: resolved
Triage: ready-for-agent

After authorized source pushes, continue the simple consumer candidate with an
offline shell example: resolve an app identity from apps.yaml, check repository
file identity, and list release facts with effective observations. Leave version
selection to the caller. Exercise retained observations, aliases and ordinary
missing/invalid inputs using the existing reader/tools. No network fetch, installed
AM behavior, publication, schedule or pin change.

## Answer

[Findings](../research/yaml-simple-browse.md): prototype `f7650b660` adds a small
shell example using the simple reader for app lookup, repository identity and
release facts. Six cases on three awk tools pass (18); syntax, shellcheck,
compilation and whitespace checks pass. No selection/cache/supervisor/transport
layer or installed integration was added. Source pushes were explicitly authorized;
publication, pin, workflow dispatch and installed behavior remain unchanged.
