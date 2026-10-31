# Accepted am-utils source enrollment — October 31, 2026

Marek approved the exact rollout package with “go ahead”, covering source
`c787efe3a42fac015f743255006fddd7ea9b3817`, one bounded collection/publication,
acceptance, daily repin and bounded rollback. The live preflight matched the
reviewed source/pin, default branch, publication parent and workflow isolation;
no unfinished work was listed. The exact source was pushed as a fast-forward.

[Run 41232846271](https://github.com/mareklangiewicz/AM/actions/runs/41232846271)
attempt 1 completed successfully. A sandbox connection failure before submission
was followed by read-only inspection confirming no candidate run; the network
submission then succeeded. Exactly one candidate run was created. The old daily
pin stayed in place through acceptance.

Publication `a113cd0aca3247111b6ba231f6a30b6477ac2c75` has exactly the approved
parent `067f236b205d8fe01c6f4e79744887e4979437fc`. All seven attempts completed
with HTTP 200, in 6.151289 seconds total. The original six carried exact prior
ETags; the two latest routes also carried Last-Modified. Initial am-utils was
unconditional. Collection received 7,600,077 body bytes. Collection job duration
was 15 seconds, publication 13 seconds; the run spanned 19:09:12–19:09:46 UTC.

The collection artifact is `13054515903`, ZIP SHA256
`ebaf3218cd8d2e9621b4f11d5d5665795a2409fd79029b7627a088724b15d205`,
878,954 bytes. Publication artifact `13054905412` retains provenance. Both
original ZIP digests match their API metadata and are archived before expiry.
Recomputed the complete candidate from original transfer evidence and exact prior
Git blobs with `delivery.verify_artifact`; checked every published path, mode,
size and Git blob hash, complete tree, exact single parent and branch advancement.
Re-rendered lookup bytes and checked index integrity. All original aliases remain active.

Actual am-utils body: 2,722,290 bytes, SHA256
`7c5bd17d1924508767ed1e309d74cfe8732e505f045d92bb1e78d7f490e298ed`.
The original fixed-selector audit passes 356/356 differential comparisons and
real asset selections, zero missing/non-assets, with all recipe hashes unchanged.
Both actual shell and Python readers, pinned to this publication, returned exactly
these bytes. Actual observation validation and measured age are retained in
`python-reader.json`; age was within the inclusive 48-hour policy. No installer,
updater, host sync or app execution was used.

Candidate tree: 7,624,027 bytes; index: 18,585; lookup: 5,365. The complete fetched
catalog history contains 11 commits and 1,117,836 object-file bytes. Packed
reachable disk size grew from 995,645 to 1,113,160 bytes (+117,515); this measures
the fetched pack, not runner shallow/loose storage. All unchanged body, header,
index, tree, ZIP, history and request/batch/job bounds passed. Exact conditions,
timings, resource evidence, provenance and verifier are in the archive.

After acceptance, patched `CATALOG_SCHEDULE_REVISION` to the exact approved source.
Read-only checks verified source/pin equality, default `main-marek`, only collector
and daily dispatcher active, the other six workflows disabled and no unfinished
runs. Cadence remains `17 3 * * *`. No second manual run was dispatched. Seven-source
repeat and natural daily behavior remain to be observed; first-run 200 success
does not establish 304 behavior or punctual scheduling.

The utility-source stage of ticket 47 is accepted and ticket 48 is unblocked.
Ticket 47 remains partial/claimed; ticket 49's separate 50-endpoint enrollment
remains blocked and unapproved. Recipe migration is separate work.

[Retained evidence](am-utils-live-20261031-evidence.tar.gz), SHA256
`c95d6a6ca917e2153bdb3b094405578e3343514ee4052ff063b5b5eaf725ffc3`,
contains public artifacts/API data and no credentials or host inventories.
