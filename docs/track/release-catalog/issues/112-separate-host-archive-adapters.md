# Separate host archive knowledge from the shared package lifecycle

Type: task
Status: resolved
Triage: ready-for-agent

Audit from 111 found additional application knowledge in modules/appimage.am:
- am_archive_stage knows EmmyLua's four filenames, rclone's archive directory
  glob/executable, btop's root/bin layout, and Kitty's bin/kitty + bin/kitten.
- am_package selects/coheres/downloads EmmyLua's four assets, and maps archive
  layouts to launcher/remover names (including kitten).

Move app-specific archive mappings, toolset membership and launcher choices into
recipes or narrow app-owned adapters, keeping download/staging/replacement,
selection freshness and custom-launcher handling shared. Preserve currently
installed recipes during module refresh; they lack any new settings. Do not
silently break their next standalone update. Preserve exact same-release and
fresh-only EmmyLua rules, archive failure behavior and all 21 host layouts.
Use actual-manager/standalone and inert archive tests, including deployment from
old installed recipes. Avoid a generic acquisition backend or hook framework.

The catalog-yaml-policy.am source registry and generated explicit selection
policies intentionally hold trusted client policies; their app-specific records
are not by themselves the same installer coupling. EmmyLua's separate fresh-only
refusal in catalog-yaml.am should be considered alongside its toolset adapter,
without weakening or bypassing it. Review source-of-truth duplication with
host-apps.json and host_cutover.py as part of the concrete adapter design.

This ticket is source follow-up, not authorization for live deployment or pushes.

## Implementation

The host manifest now owns archive kinds, root paths, executable/launcher mappings
and toolset membership/fresh-only policy. Its compiler generates a narrow
`archive-policy.am` adapter registry, delivered by normal module sync. Existing
layout names remain its interface so old installed recipes need no rewriting.
Shared extraction/lifecycle code contains no Kitty/btop/rclone/EmmyLua identities.
The same EmmyLua tool list generates selection, staging and launcher settings;
`catalog-yaml.am` delegates fresh-only consent refusal to that trusted policy.
`host_cutover.py` reads the manifest instead of repeating app identity switches.

## Answer

Completed source separation. The adapter module is generated declarative app
knowledge, not a hook/acquisition framework. Generic raw/flat-tar defaults stay
shared. Explicit legacy launcher targets preserve custom wrappers without
inferring ownership from their location.

Validation: all 16 host test groups pass, including 21 actual-manager inert
installs/standalone updates, old-module installs of all four special archive apps
followed by module-only refresh and forced updates, mixed-release refusal,
per-tool stale observation refusal, fresh-only consent refusal with zero HTTP,
missing executable/traversal/partial extraction failures, and custom wrapper
preservation. Eleven YAML manager integration tests and compiler repeatability
pass. Final review fixes were verified with focused reruns; shell syntax and
diff whitespace checks pass. Initial two-axis review caught inferred legacy
ownership and late consent refusal; both were fixed and confirmed clear.

The new wrapper regression initially exceeded the fake HTTP client's capped call
log because it did not reset between install and reinstall; resetting that test
log fixed the fixture, and the regression passes. No production workaround was
needed. These remain scoped inert tests, not real archive/GUI execution.

No push, live module synchronization, reinstall, publication, workflow or yadm
operation. The natural scheduled catalog cycle remains a separate observation.
