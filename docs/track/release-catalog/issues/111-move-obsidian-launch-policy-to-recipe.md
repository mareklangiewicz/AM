# Move Obsidian launch policy into its recipe and audit similar coupling

Type: task
Status: resolved
Triage: ready-for-agent

Marek requested removal of Obsidian-specific behavior from shared appimage.am and
asked whether similar problems exist. Keep the accepted CLI/GUI behavior: official
CLI untouched, additional obsidian-gui alias, absolute desktop GUI path, retained
arguments and custom launchers, owned-alias removal. Use small recipe settings;
prove shared behavior also works for another app. Audit current YAML runtime and
record concrete remaining misplaced policies rather than expand this into an
archive/selection rewrite. No live install, source push or yadm operation.

## Answer

Obsidian's generated recipe now declares EXTRA_APP_LAUNCHERS=obsidian-gui and
DESKTOP_EXEC=installed. Its manifest/compiler inputs retain these settings during
regeneration. Shared installation, desktop encoding and remover generation use
these settings without any Obsidian identity check. Defaults preserve other apps.
An inert Neovide recipe exercises the same settings with two aliases.

Review found and fixed an inherited extra-alias ownership bug: an alias pointing
to an app-local wrapper was incorrectly considered managed. Exact requested target
recognition now handles extra aliases, and primary launcher calls explicitly name
known legacy alternatives. Custom aliases survive reinstall/removal as intended.

The generator's nvim-nightly identity override was also removed: the manifest's
existing refresh_always field now records true, producing the identical nightly
recipe and keeping its refresh behavior. Compiler tests check repeatability and
all 21 generated recipes against committed source.

[Audit](../research/shared-installer-policy-audit.md) scopes the similar findings:
shared archive layouts, tool membership/coherence and launcher mappings for Kitty,
btop, rclone and EmmyLua, plus repeated maintenance-window launcher mappings.
[112](112-separate-host-archive-adapters.md) records the concrete follow-up and
existing-installed-recipe compatibility requirement. The explicit client selection
registry has a different purpose and remains in place. This is not an all-recipe
or historical manager-feature audit.

No installed files, app data, publication, push or yadm changes. Existing local
GUI alias/desktop override remains usable. Existing installed recipes are not
rewritten by module sync; new recipe settings arrive on install/reinstall.

Validation: 13 test groups pass (all 11 host-cutover groups, manifest compiler
repeatability/source equivalence, and real module-sync/standalone integration).
These include all 21 actual-manager inert installs/standalone updates, a second
app using the interface, invalid options before download, quoted desktop paths,
and custom app-local alias preservation. Shell syntax and whitespace checks pass.
Independent Standards and Spec reviews confirmed zero remaining actionable
findings after the alias ownership fix. No real GUI startup is claimed by inert
payload tests.
