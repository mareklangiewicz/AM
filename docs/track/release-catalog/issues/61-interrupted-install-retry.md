# Verify interrupted installed AppMan commands and retry

Type: task
Status: resolved
Triage: ready-for-agent

## Scope

Continue offline coverage with actual process interruption during a staged binary
download, both fresh installation and update of an existing AppMan app. Stop the
whole command process group only after the adapter records partial bytes, then
retry through normal installed commands. Check existing files/configuration and
launchers, successful recovery and no unexpected requests on Debian and Fedora.
No production or host app change, live download, workflow/source/pin change or
new enrollment. Do not claim crash durability outside this tested interruption.

## Investigation

Extended the existing strict download adapter with an opt-in pause after 17
staging bytes, an atomically published ready marker, and no network operation.
The command harness waits up to its existing 45-second deadline, then kills the
command's process group with SIGKILL. It records interruption evidence and verifies
the downloader was in that same group; a timeout without the checkpoint fails.
No timing-based guess determines when to interrupt. Ordinary command logs/statuses
are captured before interruption assertions.

The initial full matrix passed all 30 scenarios. Before final verification, made
the readiness marker atomic to prevent partial JSON reads and moved interruption
assertions after command-log capture. These were test-harness refinements; no
production defect was demonstrated or fixed.

## Answer

The four-command AppMan scenario passes on both distributions:

1. Interrupt fresh installation after partial staging. The command dies by
   SIGKILL; staging contains exactly the partial fixture bytes, with no version
   record or command launcher.
2. Retry normal installation. Expected version, launcher and complete binary
   are installed; staging is removed.
3. Force an update and interrupt after partial staging. Every pre-existing app
   file outside staging is preserved, and the launcher still resolves correctly.
4. Retry normal update. Expected version is recorded, staging is removed and
   configuration snapshot is preserved. No system Obsidian installation is created.

Final Debian/dash and Fedora/bash matrix: **30 scenarios / 108 commands**, zero
unexpected requests. Four actual SIGKILL interruptions are recorded across both
targets; nine support-tool specs, ShellCheck and diff checks pass.
[Checks and tested identities](../research/e2e-interruption-checks.json) retain
source/image/log hashes and process-group/status evidence. Full logs remain in
ignored run directories. Termux unchanged and not rerun. One controlled
interruption point is not arbitrary crash durability, filesystem failure coverage
or atomic multi-file rollback. No production fix, live request, source push,
workflow/enrollment change or installed-host operation. Tickets 37/41 remain.
