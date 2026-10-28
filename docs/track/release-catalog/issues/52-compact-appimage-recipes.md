# Remove repeated AppImage recipe defaults

Type: task
Status: resolved
Triage: ready-for-agent

## Scope

User requested removing repeated/default recipe setup. Keep app identity, exact
catalog alias, selector and real exceptions in each recipe. Centralize delivery
bindings while preserving standalone source persistence, AppMan, icons, refusal
and existing installed recipe compatibility. Local implementation only; no host
delivery, source push, new collection or workflow change.

## Answer

All six shared AppImage recipes now omit eight repeated declarations: package
kind, AMREPO/export, three installation paths and two helper bindings. A literal
shared-helper source line replaces the helper variable. Ordinary recipes are 13
lines and Obsidian/nightly 15, including comments/blanks; 132 -> 84 recipe lines.
The helper owns defaults/export, and installer preparation inserts persistent
source/path bindings before existing path/source transformations. Expanded older
recipes remain compatible. Production source shrinks 30 lines overall; installed
recipes shrink three lines each. Exact selectors and nightly refresh stay intact.

[Current interface and cost](../design/shared-appimage-lifecycle.md#current-compact-interface-ticket-52).

Validation: full 182-test catalog discovery initially exposed two inherited test
identity substitutions and six batch fixture path assumptions. Corrected those
fixtures, then all 73 lifecycle and 15 batch tests passed; the other 94 passed in
the original full run. All eight historical probe tests passed. Debian/Fedora
whole-command matrix passed 18 scenarios / 56 commands (local ignored logs under
`test/e2e/out/20261028T175335Z-585407/`). A previous expanded Obsidian recipe also
passed isolated install/standalone update with the current helper. Helper/recipe
warning-level ShellCheck, shell syntax and diff checks pass; installer ShellCheck
diagnostics match the prior baseline, including its existing printf error.

No host files, live requests, workflow settings or remote source changed. Keep
37/41 obligations and the no-source-push restriction. Existing private delivery
manifests predate this source change and must be rebuilt/rechecked before use.
