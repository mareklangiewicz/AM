# Verify AppMan mixed-batch failure and continuation

Type: task
Status: resolved
Triage: ready-for-agent

## Scope

Continue offline coverage after 58/59: exercise whole installed AppMan commands in
Debian/dash and Fedora/bash containers, with managed catalog apps and one legacy
fixture. Verify metadata refusal, legacy failure and download failure each leave
later apps running while preserving aggregate nonzero status; retry succeeds.
Keep user-owned paths, shared catalog acquisition and no unexpected transport
requests explicit. No host installation, live app download, workflow/source/pin
change or new enrollment.

## Existing evidence

System-AM mixed-batch continuation is covered by installed-container tests.
Function-level tests cover AppMan roots and command-session cleanup, but do not
combine whole installed AppMan dispatch with this failure matrix. Extend the
existing container scenario suite rather than introduce another harness.

## Investigation

The first matrix run reached the new scenario's third failure case but its
assertion expected `e2e-legacy: updated` after the fixture had already recorded
`legacy-new`. The actual updater completed successfully and reported `unchanged`,
while the failed catalog download still returned aggregate nonzero and SQLite
continued. Both distributions failed only this incorrect new assertion; all 13
existing scenarios passed on each. Corrected the expectation, with no production
or fixture behavior change. The final rerun also exercises successful recovery.

Initial sandbox launch stopped at Podman runtime setup before container tests;
the authorized retry used ordinary disposable containers, no runtime network,
read-only checkout and writable ignored results directory only.

## Answer

Added one scenario per distribution with five whole installed AppMan commands:
install two catalog apps plus a legacy fixture; refuse one corrupt catalog body
while continuing both later apps; fail the legacy updater while continuing both
catalog apps; fail an actual binary transfer while preserving installed bytes
and old version; then retry the whole batch successfully. Aggregate statuses,
per-app reports, user ownership/launchers and absence of system installations
are asserted. The refusal command acquires exactly one pin, one lookup and two
independently checked bodies.

Final Debian/dash and Fedora/bash matrix: **28 scenarios / 100 commands**, zero
unexpected requests. New scenario: five commands on each target. Nine support-tool
specs, ShellCheck and diff checks pass. [Checks and tested identities](../research/e2e-appman-batch-checks.json)
retain final results plus the initial assertion failure; complete logs remain in
the ignored run directories. No production defect/fix, live request, source push,
workflow change, enrollment or installed-host operation. Termux suite unchanged
and not rerun; retained metadata/inert AppImages do not prove current live freshness
or GUI compatibility. Tickets 37/41 retain expiry and daily-switch obligations.
