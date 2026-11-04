# Shell-only reader parse deadlines — November 4, 2026

Status: local prototype evidence for [81](../issues/81-test-shell-reader-deadlines.md).
Branch `research/yaml-shell-deadlines` at `5a9e2043d`, directory `tools/catalog-yaml-prototype/`.
No production integration, live requests, source push, remote controls,
publication, repin or installed-host delivery. Utility requirements and numerical
limits remain proposals, not adopted consumer policy.

## Local timeout behavior

This host's unqualified `/usr/bin/timeout` is **uutils coreutils 0.10.0**, not GNU
coreutils. The second implementation is BusyBox 1.37.0 timeout. The raw probe
runs each with `-s KILL 1` against a single exec target and a shell spawning a
separate delayed marker writer. Both stop the single target in about 1.02 s.
uutils returns 124; BusyBox's target termination is SIGKILL (Python returncode -9).
Both leave the tested shell descendant alive long enough to write its marker.
Neither tested invocation supplies the process-tree contract needed to wrap a
whole reader shell. No GNU timeout implementation or other platform was tested.

A second probe exposes BusyBox's applet preference on this build. Despite an
external PATH shim named awk, `busybox timeout ... awk ...` runs its own awk applet.
The external shim is not invoked. Passing its explicit path invokes it and kills
it at deadline. BusyBox sh also reports bare `awk` from `command -v`, whereas dash
returns the shim path. Consequently program-name lookup and shell introspection
alone were insufficient for this interpreter matrix.

The reader now searches PATH explicitly for external awk/timeout files and
executes their paths. It preserves ordering/empty entries, quotes candidate paths,
and requires a real executable file. This prevents accidental applet substitution
and makes the selected interpreter/deadline utility observable in the tests.
A standalone shell offering only a built-in awk without an external executable
refuses. This is an explicit compatibility constraint, not an installed change.

## Mechanism and boundary

`AM_YAML_PARSE_SECONDS=1..3600` enables a local trial guard:
`timeout -s KILL SECONDS /explicit/path/to/awk -f reader.awk`.
Unset/empty preserves direct parser execution. Noncanonical/nonpositive integers
and larger/fractional values refuse. Configured deadline support that is missing
refuses before the parser or spool allocation; no silent unlimited fallback.

Only the fixed trusted awk parser is guarded. It contains no subprocess execution.
The reader shell survives the timed parser, observes its nonzero status, removes
the private spool and exposes no query stdout. A partial spool is discarded.
Successful queries retain byte identity and normal missing/invalid statuses.
Raw timeout status differs by tool; the reader propagates it rather than assuming
one timeout code (locally 124 or shell status 137). Tool/interpreter executables
and PATH are trusted; this is not arbitrary-code confinement.

This deliberately does not wrap a shell process tree. Input size checking, utility
resolution, spool setup and final stdout copying remain outside the parser timer.
There is no shell-only aggregate RSS limit, whole-query/output deadline or kernel
filesystem quota. SIGKILL is subject to OS scheduling/uninterruptible I/O latency.
Final copy errors still require callers to check status. The external timeout
utility is an additional explicit dependency, tested only in these local builds.
The Python whole-worker supervisor from 80 remains separate offline evidence.

## Acceptance and reproduction

```sh
python3 tools/catalog-yaml-prototype/deadline_probe.py
python3 tools/catalog-yaml-prototype/deadline_matrix.py
sh -n tools/catalog-yaml-prototype/reader.sh
shellcheck tools/catalog-yaml-prototype/reader.sh
```

The matrix spans dash and BusyBox sh; uutils and BusyBox timeout; mawk, GNU awk and
BusyBox awk. Six new deadline groups plus nine inherited strict-reader groups per
combination exercise real local tools. All 12 combinations pass: 180 test
executions. The six raw behavior probes are retained in
`deadline-probe-results.json`; the matrix results are in `deadline-results.json`.
Shell syntax, shellcheck, Python compilation and whitespace checks pass. Inherited groups run with deadline unset;
new groups explicitly enable it. Hung-target tests use a shim that records its
PID, ignores TERM and execs sleep; it has no descendant tree. The tests verify
that PID is no longer running, all spool files are removed and query stdout is
empty. A second shim writes partial private output before stalling, with the same
refusal/cleanup guarantees. Successful get/rows/ID queries compare exact bytes
against the unguarded command. Missing timeout, invalid durations, missing fields,
output exhaustion and malformed suffixes preserve refusal semantics and cleanup.

The first harness attempt had a duplicate PATH keyword in environment construction;
it was corrected. The next matrix found that bare awk was bypassing the hanging
shim under BusyBox timeout: timeout appeared to succeed because the wrong parser
ran. The minimized raw probe above demonstrated the applet substitution. Explicit
external paths correct the actual execution seam; the complete matrix passes
with the previously failing TERM-ignoring/partial-spool cases. This confirms the
execution-seam correction without claiming general timeout process-tree support.

No new large-shape benchmark is implied. Ticket 80's shared-default timings and
narrow BusyBox 60-second margin retain their exact source/guard scope. This local
parser timer is not evidence that a 16 MiB operational ceiling is safe or portable.

## Next gates

Choose acceptable consumer performance/memory/deadline requirements and determine
whether an external timeout dependency is acceptable across supported platforms.
If the requirement is a whole-query hard deadline or whole-tree cleanup, this
parser-only option does not satisfy it. Evaluate a different strategy or keep the
stronger offline supervisor for the environments that can use it. Actual bounded
transport/publication integration and default-run live capacity remain separately
authorized work under 71. No operating budget or production adoption follows.
