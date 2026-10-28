# First naturally scheduled pilot run verified

Ticket [36](../issues/36-activate-hourly-refresh-pilot.md), checked 2026-10-28
at approximately 08:56Z. Exactly one scheduled dispatcher run is listed so far:
[40640684033](https://github.com/mareklangiewicz/AM/actions/runs/40640684033),
created 05:54:26Z, success. Its log reports submission using approved source
466e1facce4e66d4b26c06446fc1e524aa0d76df and prior e8e5cf96295369d90402d7584853eb1d3436463d.
Child [40640700123](https://github.com/mareklangiewicz/AM/actions/runs/40640700123)
was created 05:54:36Z and succeeded in collection/publication. No agent dispatch,
retry, new release request or host app operation was used for this status check.

All six conditional requests returned 200, 4,877,559 body bytes, 3.969 seconds.
Sent conditions match all six prior validator tuples. Exact same-run artifact
ZIP digest matches API metadata. Independent strict ZIP parsing and storage
recomputation against prior reproduce the entire published Git tree. Actual
parent is e8e5cf962; child is 2dd9db2bd4744c6f453869d3dd22fb634bacfbcc.
Source/ref and schedule variables remain unchanged; only the dispatcher and
collector are active, other six registered workflows remain disabled.

Job logs establish dispatcher actions:write/contents:read, collector contents:read,
publisher actions:read/contents:write, with metadata:read in each. No 304 or
independent binary-authenticity claim. Obsidian validated at
2026-10-28T05:54:45.963442Z, fresh through inclusive
2026-10-29T05:54:45.963442Z (06:54:45.963442 Warsaw).

Only one schedule event in roughly nine elapsed pilot hours does not demonstrate
hourly reliability. No failed scheduled runs are listed, so the missing ticks
cannot be attributed to an observed controller failure. Cause of scheduler timing
has not been diagnosed. Continue the bounded observation without adding retries,
extending the window or changing cadence. Dispatch authorization expires
2026-10-29T00:12:16Z; [37](../issues/37-assess-hourly-pilot.md) remains open for
shutdown and whole-pilot assessment.

[Machine checks](hourly-pilot-first-run-checks.json) and
[exact evidence archive](hourly-pilot-first-run-evidence.tar.gz), SHA256
`dbfa13db1404165fc2a8ae645927e919d56775b4be43f4d4e3f929079cc69982`,
retain both run identities, job logs/permissions, ZIPs, full publication history
bundle, independent recomputation scripts and results. These are targeted
verification checks; the implementation suite was not rerun for this evidence-only
work. No additional public-helper invocation or app execution was performed.
