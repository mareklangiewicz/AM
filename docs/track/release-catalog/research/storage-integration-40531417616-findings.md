# Live collector/storage integration

2026-10-27. [Run 40531417616](https://github.com/mareklangiewicz/AM/actions/runs/40531417616)
succeeded on attempt 1, from source/workflow/approved revision
`9679305de5912a390030547c67f10f5f88cb11dc`. Marek approved continuation, pushes and
workflow runs. Exactly one new six-source validation was dispatched in this step;
there was no retry, schedule, source expansion, catalog branch publication or
installer change. The prior first adapter run remains separate evidence.

## Result and independent checks

Collection at 16:29:11–16:29:17 Europe/Warsaw returned six complete
HTTP 200 responses, 4,877,758 bytes in 6.598681172 seconds, with no stop reason
or skipped request. Runtime recorded Python **3.12.3 / Linux** on the configured
Ubuntu 24.04 runner. The unchanged enrolled manifest hash is
`1c550b882e9855a7a652e44516d88db95046641da92f4b6e34fd65b9a6da87b9`.

Storage accepted all six public release bodies and generated six available entries
with 12 active aliases, an index of **16,217 bytes** and a closed byte tree of
**4,893,975 bytes**. Index SHA256:
`1d3c72259e810d63a3ea77e0318262d31cb8eded4592e9b4ba40890079fdf8c9`.
The exact manifest is embedded and its digest independently matches the workflow.
Receipt/validation times match measured response completion, not generation time.

After downloading the artifact, independently ran artifact_io.read_candidate and
storage.validate. Every candidate body matched its original evidence file, report
length/hash and storage-report entry. Verified run/attempt/revision provenance,
six available observations, alias mapping and full candidate closure. Created a
local publication commit `8804292307d7564da7d571b2876315f9cd7a806c`, exercised all 12 aliases at that full commit,
and verified stale-parent refusal. The local Git bundle is preserved in the
archive so the fixture commit remains inspectable. It has no configured remote,
was never pushed and is not an operational publication branch.

## Persistent evidence

[Archive](storage-integration-40531417616-evidence.tar.gz) includes the exact
candidate index/bodies, original report and storage report, original collection
bodies, workflow/manifest snapshots, Actions metadata, post-run workflow states
and local-publication.bundle. Candidate bytes were verified again from the archive.
Archive: 967962 bytes; SHA256 `797562df9ce7a1e6b1179e3aa1aca1d2a0c529d75ff0ecbcde6886e3d53b2e07`.
[Machine checks](storage-integration-40531417616-checks.json) retain each observation's
hash/time, runtime, totals and local publication verification. Git-tracked evidence
persists beyond the seven-day Actions artifact retention.

## Implementation and limits

[Integration design](../design/storage-collector-integration.md) documents pure
apply/validate, bounded candidate-directory reading, local atomic publication and
pinned freshness lookup. 62 offline tests passed before the live check, including
saved real evidence and synthetic failure/304/retirement/integrity/clock cases.
The workflow retains original inert evidence even if storage refuses the batch.
Both local Python 3.14.4 checks and this live Python 3.12.3 path now have direct
results; no broader compatibility matrix or adversarial audit is claimed.

The live workflow currently calls apply with no previous tree and thus stages a
fresh six-source baseline each run. The module's tested prior-state/304/failure
retention paths are not yet connected to cross-run persistence or remote catalog
history. No live conditional response was tested. Bounds apply to this candidate,
not an established fleet retention policy or capacity guarantee.

Remote delivery requires a trusted prior-state reader and a separate writer job
that validates artifact provenance/closure before normal fast-forward publication;
collection still has contents:read only. The writer must not execute artifact code,
recollect on publication failure, force push, or grant its credential to collection.
The next integration should use this retained candidate evidence before considering
another upstream collection. No day observation/wait is needed.

Post-run isolation still shows only Restricted catalog validation active, with all
six other workflows disabled_manually. No unrelated workflow was enabled.
