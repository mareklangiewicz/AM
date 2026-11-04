# Bound and measure the shared-default reader

Type: prototype
Status: resolved
Triage: ready-for-agent

Follow up 71/79: add portable reader output accounting and finite projection
bounds. Supervise offline queries with worker runtime/address-space limits and
aggregate reserved input, spool, output and receipt storage. Measure current
shared-default fixtures on mawk, GNU awk and BusyBox awk; test exact output
boundaries and zero exposed output on refusal. Limits are trial inputs only.

No production integration, consumer Python dependency decision, live collection,
remote operation, publication, push, repin or installed-host changes.

## Answer

[Findings](../research/yaml-reader-budgets.md): prototype `3a8087613` on
`research/yaml-reader-budgets` adds output accounting, distinct scalar projections
and supervised queries reserving input/spool/output/diagnostics/receipt storage.
Six new groups plus nine inherited reader groups pass on each awk tool; existing
default/retention/adapter matrices also pass. Shell syntax, shellcheck, Python
compilation and whitespace checks pass. The completed 21-case measurement has
15 full-hash successes and six deliberate zero-candidate refusals.

The 16.31 MB retained fixture takes 10.5/21.7/56.4 seconds on mawk/GNU awk/BusyBox
under the trial 60-second watchdog and 128 MiB address-space limit. This leaves
little BusyBox margin and does not accept a portable 16 MiB ceiling. An initial
uncaptured GNU awk refusal did not reproduce; its cause remains unknown and is
recorded separately. No interpreter fix is claimed. Portable consumer deadlines,
acceptable operating budgets, transport/publication integration and separately
authorized live capacity remain under 71. No production or remote operations.
