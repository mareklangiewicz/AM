# Test shell-only reader parse deadlines

Type: prototype
Status: resolved
Triage: ready-for-agent

Follow up 71/80: compare installed timeout implementations using their actual
behavior, then test a shell-only deadline for the single trusted awk parser.
Distinguish parser execution from shell descendants, input acquisition and final
output delivery. Refuse missing deadline support instead of silently falling back.
Test byte identity, statuses, zero query output and spool/process cleanup.

An extra timeout utility is an explicit trial dependency, not an accepted portable
consumer requirement. No production integration, live requests, source push,
remote controls, publication, repin or installed-host delivery.

## Answer

[Findings](../research/yaml-shell-deadlines.md): prototype `5a9e2043d` on
`research/yaml-shell-deadlines` adds an optional single-parser guard using explicit
external awk/timeout paths. Six new groups plus nine inherited reader groups pass
in 12 shell/timer/awk combinations (180 executions), with six raw behavior probes.
Shell syntax, shellcheck, Python compilation and whitespace checks pass.

Both tested timeout tools leave the probed shell descendant alive; neither tested
invocation supplies whole-tree supervision. BusyBox applet preference initially
bypassed the PATH-selected awk; explicit external paths fix the real execution
seam and make the interpreter matrix meaningful. Configured missing support
refuses, timed parser output stays private, and spool/process cleanup passes.

This is a parser-only deadline with an additional timeout dependency, tested on
the installed Linux tools. Consumer platform support, whole-query/output deadlines,
acceptable memory/performance budgets and production integration remain unapproved.
No live collection, publication, push, dispatch, repin or installed-host changes.
