# Shared installer policy audit — November 5, 2026

Scope: current YAML lifecycle in `modules/appimage.am`, YAML acquisition/selection
modules, host manifest/compiler and maintenance-window launcher mappings. Baseline
is ccce49c1c. This is not an audit of every historical installation recipe or every
manager feature.

## Fixed in 111

Obsidian identity checks coupled its extra GUI command, remover and desktop
preference to the shared lifecycle. Its generated recipe now declares
`EXTRA_APP_LAUNCHERS=obsidian-gui` and `DESKTOP_EXEC=installed`. The shared module
handles alias lifecycle and desktop encoding without knowing Obsidian's identity.
The production host manifest holds the corresponding generator inputs so running
`host_policy_source.py` cannot erase the declarations. Other recipes keep their
existing defaults. An inert Neovide recipe exercises the same interface with two
extra names, proving the implementation is independent of the Obsidian identity.

`host_policy_source.py` also had an explicit nvim-nightly refresh override despite
already supporting the manifest's refresh_always property. That property now
records true for nvim-nightly and the identity override is removed. The generated
Neovim nightly recipe and its existing refresh behavior remain unchanged.

The shared link helper also inherited a faulty ownership inference for extra
aliases: a custom alias pointing to an app-local wrapper could be overwritten,
while the actual managed root-executable target was called custom. Extra aliases
now recognize only their exact requested target; primary launcher calls explicitly
supply any known legacy alternative. The app-local custom-wrapper regression
covers reinstall and removal.

## Remaining app-specific lifecycle knowledge

`am_archive_stage` knows EmmyLua tool names, rclone directory/executable names,
btop archive roots and binary paths, and Kitty's two expected binaries. `am_package`
contains EmmyLua toolset selection/coherence/download iteration plus archive
layout-based launcher/remover choices for btop, Kitty and EmmyLua. The private
maintenance-window `host_cutover.py` repeats launcher mappings.

These choices should live in recipes or app-owned adapters, while safe staging,
replacement, link ownership and lifecycle orchestration remain shared. This is
larger than the Obsidian fix: existing installed archive recipes depend on the
current module behavior, and EmmyLua's four-asset same-release/fresh-only contract
must survive. [112](../issues/112-separate-host-archive-adapters.md) records the
follow-up and its compatibility/test requirements. No attempt was made to hide
this coupling behind renamed branches or a generic callback framework.

## Intentional selection policy

`catalog-yaml-policy.am` is explicitly a trusted client selection-policy registry,
compiled from reviewed source. Its app-specific repository/channel/asset facts
are appropriate to that module's purpose; moving them into the package lifecycle
would undo the existing separation between selection and acquisition. The source
manifest is not inert upstream catalog data.

EmmyLua's named fresh-only refusal in `catalog-yaml.am` crosses into the toolset
contract and should be reviewed together with its adapter in 112, preserving the
current safety rule. No claim is made that every named check is equivalent to the
Obsidian launcher mistake, or that this audit settles all future seams.

## Deployment

This source refactor does not rewrite installed recipes or launchers. Existing
user GUI alias/desktop override remains usable. Module synchronization updates
shared machinery; recipe declarations arrive on install/reinstall. A module-only
refresh continues ordinary updates of existing recipes, and old archive settings
remain supported pending 112. No live installation or publication was performed.

## Follow-up: 112

The remaining archive/toolset knowledge is now generated from the trusted host
manifest into `archive-policy.am` and the explicit catalog selection policy.
`appimage.am` and `catalog-yaml.am` contain no host app identities. Shared
orchestration uses archive kind, root, required executable paths, launcher mappings
and explicit known legacy launcher targets. EmmyLua's single manifest tool list
supplies asset selection, staging and launchers; its fresh-only setting rejects
consent in policy preflight before HTTP and still refuses stale individual tools.
Old installed layout names select the same adapter records after module refresh.
The maintenance cutover reads those records instead of its own app switches.

This addresses the scoped findings above; it is not an audit of other historical
recipes. No live deployment or publication was performed.
