# Hourly pilot closed — 2026-10-29

Ticket [37](../issues/37-assess-hourly-pilot.md). At approximately 09:15 UTC,
disabled catalog-schedule.yml and verified disabled_manually. Exclusive expiry
was 00:12:16 UTC. All observed runs completed; no collector in flight.

Four natural dispatches produced successful children on October 28 at 05:54:36,
13:09:47, 18:55:10 and 23:18:40 UTC. This is sparse schedule delivery, not an
hourly reliability demonstration. The October 29 05:57:44 dispatcher failed with
inactive_schedule_window and produced no child. No replacement dispatch occurred.

Each child made six conditional release requests: 24 HTTP 200 responses, zero
304s, 19,510,852 received body bytes total. Every sent validator tuple matches
its prior publication. Exact API artifact digests verified; independent artifact
validation reproduces all four publication trees and the actual parent chain.
Final publication: 3cb2bada61744479531b7093d6cf3167c463cf36.

Full reachable history grew from 32 objects / 14,655,869 uncompressed bytes to
76 objects / 34,253,897 bytes: +19,598,028 bytes. The complete history bundle is
388,716 bytes. These distinct measurements do not predict larger enrollment or
long-term storage. The latest six validations span 2026-10-28T23:18:49.491690Z
through 23:18:53.478263Z. Under the pilot's 24-hour policy each expires October 29
at its corresponding time; under accepted 48-hour policy, October 30. No failed
observation was assigned a fresh timestamp.

[Machine checks](hourly-pilot-closure-checks.json) and
[exact evidence](hourly-pilot-closure-evidence.tar.gz), SHA256
bfb470e2faa03918baa29677ebe4f9aebb58fc2268dfea280b0d1c37ebc02682,
retain metadata, variables, all nine controller/child logs, eight artifact ZIPs,
full history bundle and replay scripts. To replay, extract to a temporary directory,
clone catalog.bundle as bare catalog.git there, and run verify.py with the AM
checkout path as its argument. Captured repository metadata is public fork metadata.

Default branch remains main-marek; other six workflows remain disabled. Collector
remains active but dispatch-only. Daily activation is the separate ticket 41.
