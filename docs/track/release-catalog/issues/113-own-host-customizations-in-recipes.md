# Make host recipes the source of truth for app customization

Type: task
Status: claimed
Triage: ready-for-agent

Marek requests full locality after 112: this is a single-user fork with only 21
host apps, so do not carry a compatibility registry to preserve older recipes.
Each host recipe should own its selection, archive, toolset, launcher and freshness
settings. Shared machinery may compile/read those declarations, but no separately
maintained host manifest or named archive adapter registry should own them.
Remove obsolete layout/legacy-launcher compatibility. Preserve actual current
host layouts, custom launchers, EmmyLua same-release/fresh-only constraints, and
selection/acquisition separation. Test inert manager installs/standalone updates
and compiler behavior. Source work only; no live deployment or push authorized.
