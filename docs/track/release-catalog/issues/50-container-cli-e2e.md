# Exercise the installed AM/AppMan commands in disposable containers

Type: task
Status: resolved
Triage: ready-for-agent

## Scope

Marek requested e2e testing like mysh. This user-directed work takes priority over
the recorded recipe-migration frontier. Reuse the useful container pattern:
opt-in matrix, read-only source mount, disposable filesystem and retained logs.
Test the whole installed manager command through real startup/module dispatch,
normal recipe installation, saved standalone updater and mixed batches, without
extracting manager functions or editing production scripts to create a harness.

Start with Debian/dash and Fedora/bash as /bin/sh, using GNU utilities required
by AM's reader. Use retained catalog metadata, a controlled clock, explicit
external transport adapters and inert executable/AppImage extraction fixtures.
Disable container networking during test execution. Cover system AM via normal
sudo and unprivileged AppMan, current/embedded source delivery, unchanged/changed
update, metadata refusal before app mutation, failed-transfer retry, batch
continuation/nonzero status, and optional checksum distinction. Keep build-time
package downloads separate from runtime metadata/binary behavior.

Do not execute legacy regress scripts on the host: they intentionally clear app
and binary locations. No host app migration, live upstream collection, production
workflow change or source push. Explain what is simulated and what end-to-end
coverage does not establish. Add one documented runner and concrete run evidence;
keep this opt-in instead of changing the existing remote workflow during the pilot.

## Answer

Implemented the [opt-in runner](../../../../test/e2e/README.md) with Debian/dash
and Fedora/bash environments, read-only source mounts, disposable installed system
paths, real normal-user/sudo and unprivileged AppMan execution, and retained logs.
No extracted/replaced manager functions or stubbed sync/verification services.
External metadata/file transport and the reader clock are controlled; runtime
networking is disabled and binaries are explicitly inert fixtures.

Eight scenarios / 21 CLI invocations pass on each target (16 / 42 total), including
install/standalone/mixed/no-argument sync, refusal before mutation, download
retry/repair, exact stale consent and optional digest distinction. The tests caught
and verified two real sync defects: pipefail/quiet-grep SIGPIPE skipped large
manager/module checks, and configured repository selection left the module source
at its initial value. Fixed with two here-string checks and one derived source
assignment. An older installed module is repaired to exact source in the regression.

[Findings](../research/container-cli-e2e-findings.md),
[recorded checks](../research/container-cli-e2e-checks.json), and the
[actual final run archive](../research/container-cli-e2e-20261028T162910Z.tar.gz)
retain image/environment/source/harness identity, results, outputs/statuses and
transport traces. Both targets have zero unexpected requests. The 149-test catalog
suite, Bash/POSIX/Python syntax, warning-level runner/fixture ShellCheck, baseline
manager warning comparison and diff checks pass. Direct host execution and unknown
target guards were checked. No production workflow or host app/helper change,
live metadata/binary collection or source push; only test-image OS package downloads.
Ticket 46 remains the implementation frontier; 37/41's timed obligations remain.
