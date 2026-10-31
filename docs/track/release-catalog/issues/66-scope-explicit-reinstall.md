# Restrict explicit reinstall to named applications

Type: task
Status: resolved
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
Do not reproduce through host removal/reinstallation. No fix had been applied at
ticket creation; the continuation below supersedes that initial state.

## Reproduction and diagnosis — 2026-10-31

The initial disposable Debian test installed Obsidian and Neovim through the real
manager, changed only Neovim's saved recipe, and invoked `reinstall obsidian`.
`InstalledCLI.test_named_reinstall_preserves_unrelated_changed_app` failed on the
Neovim filesystem snapshot: the unrequested app had been reinstalled. After the
first selection correction, the same command passed (one test, 5.6 seconds).

Expanded tests added an unrelated incomplete installation. They demonstrated
that filtering only inside the reinstall module was too late: startup's
`_check_version_for_auto_updatable_apps` discovers all apps whenever a version
cache exists, and discovery can execute incomplete apps' removal scripts.
Targeted call tracing confirmed this path. Reinstallation's child commands also
perform discovery; all belong to the same selection boundary. Temporary debug
instrumentation was removed.

## Implementation

The manager captures a named reinstall selection before startup discovery and
exports it for its child removal/installation commands. `_determine_args` filters
discovered paths by exact basename before its existing cleanup logic. Missing
names cannot turn into an all-app operation; matching does not interpret regexes
or shell globs. The optional leading global assume-yes switch is recognized.
No-argument, `--all` and `--launcher` commands retain their existing discovery
behavior.

The reinstall module no longer changes saved recipes to force a reinstall.
Explicit selection directly forces the existing reinstall branch; no-argument
selection still compares saved and current recipes. This preserves saved recipe
bytes until actual reinstallation.

Six whole-command scenarios cover single names, multiple/duplicate names,
missing/regex-like names, mixed present/missing names, no arguments and global
assume-yes. Each runs in system AM and AppMan on Debian/Fedora, and native AppMan
on Termux. They check unrelated app trees and incomplete installations, exact saved
recipes, exactly one binary transfer per selected app and preserved user settings.

## Answer and validation

Resolved locally. Named reinstall now restricts startup and descendant discovery
before any app cleanup or reinstall mutation; unrelated changed and incomplete
apps are preserved. No-argument changed-recipe behavior remains intact.

- `./test/e2e/run termux debian fedora`: 14 native Termux and 21 scenarios on
  each GNU/Linux target pass, 56 total. Logs:
  `test/e2e/out/20261031T175936Z-350072/`.
- After separating a declaration from assignment to remove a new lint warning,
  the final Termux source was verified again: 14 tests pass in
  `test/e2e/out/20261031T180323Z-425157/`. Final Debian/Fedora and repeated Termux
  manager/module/scenario hashes match the working tree. No unexpected requests.
- `python3 -B -m unittest discover -s tools/catalog-collector -p 'test_*.py'`:
  198 pass on final source.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s test/e2e -p 'test_*.py' -v`:
  10 support-tool specs pass.
- Bash syntax and `git diff --check` pass. ShellCheck has no new diagnostics
  relative to HEAD: 181 existing findings remain versus 182 before this change.

No host app was installed, removed, updated or run. No source push, schedule repin,
manual collection or new enrollment occurred. Publication and normal host sync
remain separate actions requiring the reviewed source/pin handoff.
