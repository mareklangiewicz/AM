# Installed-command container e2e

Ticket [50](../issues/50-container-cli-e2e.md), implementation baseline `7ad0aff39`.
Marek requested tests like mysh's opt-in container matrix. The
[runner and coverage](../../../../test/e2e/README.md) now exercise whole installed
commands in Debian/dash and Fedora/bash environments. The previous catalog suite
remains useful, but its manager integration tests extract functions and replace
sync/verification/discovery services; passing those tests did not establish whole
CLI behavior.

## Whole-command coverage

Each target runs eight scenarios and 21 command invocations, using a normal
container user, real sudo transitions for system AM, a separate unprivileged
AppMan home, the actual module dispatcher and ordinary installation source patch.
Installed manager/module copies begin byte-identical to the source checkout;
no manager functions are extracted or replaced by a test harness. A deliberate
obsolete installed-module marker in the sync scenario must be repaired back to
exact source bytes. App-state fixtures also model old versions, corruption and
interrupted work. These are installed-state transitions, not rewrites of the
production implementation under test.

Scenarios cover installation and expected original retained URLs; tiny standalone
updaters and persistent/current source delivery; actual digest verification;
failed-download preservation/retry; same-version repair; stale/body refusal before
app mutation and exact consent; mixed legacy/catalog continuation and one command
publication pin/lookup; missing optional digest versus known mismatch; and a real
no-argument manager/module sync that retains the batch failure status.

The checkout is read-only. Only logs are mounted writable on the host. Runtime
networking is disabled. Explicit curl/wget adapters serve original retained
observation bytes and inert binary content; unknown requests fail and are retained.
The controlled reader clock is not a statement of current real freshness. The
small executable implements extraction/desktop/icon and an inert version command,
not an actual upstream AppImage. Distro Wget version detection and ordinary date
calls still use installed distro utilities. Notification failure is intentional.

No current upstream metadata/binary requests, GUI/FUSE execution, host app rollout,
public bootstrap-downloader run, workflow activation or source push occurred.
OS package downloads happened during environment-image construction. Tests do not
claim real HTTP/TLS correctness or non-x86_64/BusyBox compatibility.

## Defects exposed, with real regressions

The no-argument test initially failed because sync never printed its synchronization
message, despite fetching the manager. Global `pipefail` makes a large
`echo "$AMCLI_ONLINE_CONTENT" | grep -q AMCLI` condition fail when the producer gets
SIGPIPE after grep's early success. A minimal probe against the actual manager
body reproduced **pipeline status 141 versus here-string status 0**. The same
pattern guarded module bodies. Both checks now use a Bash here-string, preserving
failure propagation in the command pipeline without introducing an upstream
producer in these quiet checks. Source: [manager](../../../../APP-MANAGER).

Once sync ran, the strict transport oracle caught six module requests to the
original repository while manager/catalog requests used the configured source.
`_am_newrepo_check` updated AMREPO, AMBRANCH and package paths but left MODULES_SOURCE
at its startup value. It now refreshes that derived value too. The whole-command
scenario verifies configured manager/catalog/module URLs, repairs a deliberately
older large install module and preserves a legacy app's failure through sync.
Source: [repository configuration and sync](../../../../APP-MANAGER).

The loop went red on these actual behaviors before the fixes, then green through
the same installed CLI. No network or host installation was needed to reproduce
these integration defects. The production delta is one derived source assignment
and two quiet-check replacements. No schedule or catalog format change.

## Repeatable run and retained evidence

```sh
./test/e2e/run debian fedora
python3 -B -m unittest discover -s tools/catalog-collector -p 'test_*.py'
```

The runner preserves separate UTC/PID run directories with build logs, image IDs,
OS/shell identity, input/source hashes, scenario results and each command's output,
exit status and transport records. `tee` preserves failure status. Target validation
and a direct-host-execution guard were checked. Runtime scenarios do not invoke
the old destructive live-download `regress/` scripts. No remote CI or host hook
was changed. See [recorded checks](container-cli-e2e-checks.json) for the exact
final archive, image IDs, tested source/harness hashes and run results.


Final matrix: Debian/dash **8/8**, Fedora/bash **8/8**, 21 CLI commands each, zero
unexpected requests. The existing catalog suite is **149/149**. Runner/fixture
ShellCheck, Bash/POSIX/Python syntax, manager warning-baseline comparison, source
hash checks and `git diff --check` pass. The final archived matrix is
[20261028T162910Z](container-cli-e2e-20261028T162910Z.tar.gz); its exact archive and
source/harness hashes are recorded in the linked checks, including the one-line
obsolete installed-module state used to exercise repair.
