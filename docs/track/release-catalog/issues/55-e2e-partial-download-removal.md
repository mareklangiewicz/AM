# Exercise partial transfers and removal/reinstall through installed commands

Type: task
Status: resolved
Triage: ready-for-agent

## Scope

User prioritized offline e2e improvements: write truncated download bytes before
transport failure, prove working installation preservation and successful retry;
exercise normal removal/reinstall in AM and AppMan with user configuration kept.
Run Debian/dash and Fedora/bash whole-command containers. No host delivery,
production collection, source push or workflow changes.

## Verification design

Partial transfer uses the strict existing transport adapter to write the first
17 fixture bytes to the requested output file, then exit nonzero. The scenario
proves those bytes exist in staging, compares the rest of the installed tree
(including contents/mode/mtime) against its pre-failure snapshot, and verifies a
complete retry and staging cleanup. Removal uses confirmed `-r` through installed
AM and AppMan, checks app-directory/symlink/desktop cleanup and a configuration
snapshot, then reinstalls and executes the saved standalone updater.

## Answer

Implemented both scenarios without production changes. Full Debian/dash and
Fedora/bash matrices pass 11 scenarios each (22 total), with zero unexpected
transport requests. [Run summary and source/image hashes](../research/e2e-partial-removal-checks.json)
retain verification identity; full command and transport traces remain in the
ignored run directory recorded there. Python syntax, runner ShellCheck and
`git diff --check` pass. The unchanged Termux suite was not rerun. No host app
operation, source push, workflow change or live metadata/binary request occurred.
