# Test the fork in native Termux userland containers

Type: task
Status: resolved
Triage: ready-for-agent

## Scope

User authorized adding/running a Termux container target, covering direct AppMan
and AM's fallback into AppMan mode. Reuse mysh's native Android-userland base,
but run commands unprivileged and do not silently add FHS compatibility links.
Exercise actual byte-unmodified installed commands, catalog integration and a
controlled CLI executable; distinguish native userland from real Android-device
coverage. Retain actual failures and fix demonstrated paths where justified.
No host app/config delivery, production collection, source push or workflow change.

## Answer

Added the opt-in native Termux container target, unprivileged shared command
execution, native transport adapters and seven whole-command scenarios. Direct
AppMan, local AM auto-mode, read-only AM fallback accepted/declined, writable
system refusal without sudo/doas, catalog/transfer preservation and a real native
Android CLI ELF all pass. No FHS compatibility links or proot environment.

An actual failure exposed the early sudo/doas requirement before fallback. Moved
that requirement after mode selection and verified both successful unprivileged
fallback and retained system-mode refusal. [Actual findings and evidence](../research/termux-container-findings.md)
record red/green runs, image/ELF provenance and explicit coverage limits.

Final validation: 25 Termux/Debian/Fedora scenarios / 70 CLI commands pass; final
Termux evidence/ownership rerun 7/14 passes. All 184 catalog tests, syntax, new
harness ShellCheck and diff checks pass; manager lint matches its prior baseline.
No host app/config/helper delivery, production collection, source push/repin or
workflow change. Timed 37/41 obligations remain independent; recheck private payload
manifests before any future host delivery.
