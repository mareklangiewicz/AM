# Keep official Obsidian CLI and add an explicit GUI launcher

Type: task
Status: resolved
Triage: ready-for-agent

Marek accepted obsidian-gui as an additional GUI launcher, keeping the official
~/.local/bin/obsidian CLI and existing AM obsidian link. Generate Obsidian desktop
entries with the absolute installed GUI path, preserving arguments and custom
launchers. Make installation/removal handle the extra alias. Apply the launcher
and desktop correction locally without reinstalling or touching vaults/settings.
Push remains a separate decision.

Official CLI registration intentionally installs ~/.local/bin/obsidian and needs
a running GUI: https://obsidian.md/help/cli . The prior startup failure was a PATH
collision; the installed AppImage starts successfully through its full path.

## Answer

The shared installer adds obsidian-gui pointing to the installed GUI and keeps
its existing obsidian link. Obsidian desktop generation uses a quoted absolute
GUI path with existing flags/field codes retained. Desktop string/Exec quoting,
percent literals and sed replacement escaping are covered. Existing custom desktop
entries and GUI aliases are preserved; removal deletes the extra managed alias
only when it still points to this installation.

All nine host-cutover test groups pass, including actual manager installs for all
21 apps, GUI alias/reinstall/removal, custom aliases, and special-character desktop
paths. Shell syntax and diff checks pass. Independent parallel Standards and Spec
reviews have zero remaining actionable findings; a desktop quoting finding was
fixed and rechecked. The first test run needed its request log reset before a
second install to respect the fixture's file-size limit; the corrected suite passes.

Immediate host fix uses ~/.local/bin/obsidian-gui and a per-user desktop override
at ~/.local/share/applications/obsidian-AM.desktop. Its Exec is the absolute
/opt/obsidian/obsidian path with --no-sandbox %U retained. Official CLI bytes are
unchanged. desktop-file-validate succeeds with only the inherited identical
Name/Comment warning. User-reported full-path GUI startup already succeeded;
no new GUI startup is claimed here. No sudo, reinstall, vault/settings edit,
push or yadm operation was used. Local before-image/receipt:
/home/marek/Documents/Codex/am-yaml-cutover/obsidian-gui-launcher/.
The installer module change is source-only until deployed; the per-user launchers
already work independently of that deployment.
