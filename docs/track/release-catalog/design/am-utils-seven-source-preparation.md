# am-utils: seven-source offline preparation

2026-10-28. Partial implementation of [47](../issues/47-enroll-scoped-migration-sources.md),
authorized after the retained identity/release reads. This document supersedes the
missing-compatibility and unchanged-local-count statements in earlier preparation
notes; their actual request/publication evidence remains historical.

## Current stage and operational boundary

The [candidate manifest](staged-manifest-am-utils.json) is a separate file, SHA256
`96fd3477b59a9806584f155c9180be1cd9c7ce368d02e0973b28afd2e0c4da62`.
It preserves the original six manifest rows exactly and adds one source:

- numeric fetch `https://api.github.com/repositories/1225768109/releases`;
- exact alias `https://api.github.com/repos/ivan-hc/am-utils/releases`;
- pinned representation and request ID
  `033cc5f80e8fbd7074c6a2e48cace911348e6ff63652618cbf8f3d95cdfb2700`;
- links to real reviewed public identity and numeric-route evidence.

The operational [six-source manifest](staged-manifest.json) remains byte-identical,
SHA256 `1c550b882e9855a7a652e44516d88db95046641da92f4b6e34fd65b9a6da87b9`.
Workflow paths and the scheduled controller's manifest hash still select it.
The seven-source candidate cannot be selected merely by changing the dispatch's
manifest hash: preflight hashes the actual operational file and refuses mismatch.
No source push, remote source pin, workflow state, schedule, new live request or
installed payload changed in this preparation.

Ticket 41's already authorized daily activation remains six-source operation after
37's expiry closure. Its approval does not include replacing the operational
manifest or collecting/publishing this seventh source. The 50-endpoint AppImage
queue is still deferred and its unknown IDs remain null.

## Recipe correction and compatibility

Commit `033ed3d57` corrects only the two c++filt recipes: match the literal URL
component `c%2B%2Bfilt` in each install and updater filter. A focused regression
failed four original selectors before repair and passes now. Both recipes retain
the same APP identity, dated-release/architecture policy, case-insensitivity,
first-match ordering and actual original binary URLs.

The [post-fix whole-family report](../research/am-utils-release-20261028/selector-report-fixed.json)
checks every current recipe hash and exact selector against the retained 2,722,290
byte response: **356/356 selected URLs are real assets**, zero missing/non-asset
results, 160 multiple matches handled by unchanged first-match policy. No other
selectors changed. This establishes metadata selection for the retained sample,
not executable lifecycle compatibility or future source availability. Ticket 48
still requires operational enrollment before its implementation frontier opens.

## Narrow count changes

- Planner caps the run at seven sources; an eighth refuses before transport.
- Manifest loader accepts six historical rows or seven candidate rows, preserving
  historical publication readability; five/eight refuse before token construction.
- Transport allows each approved request once, bounded by its actual plan length.
- Storage allows at most the active manifest's attempt count, with existing
  identity, duplicate, chronology, body and conditional checks intact.
- Publisher requires exactly the approved manifest's request count, all observed
  or validated, and exact artifact recomputation. Missing/failed/invalid seventh
  results remain unpublishable. Partial-publication policy was not changed.

The 8 MB response, 64 KB headers, 2 MB index, 50 MB current tree, 105 MB artifact,
128 MB local/delivery history and 10/30/300-second connect/request/batch limits
are unchanged. Seven maximum-size responses still cannot fit the tree cap: this
stage is accepted by measured evidence plus fail-closed bounds, not a worst-case
capacity claim. Seven full request budgets total 210 seconds, but the workflow's
five-minute job limit includes preparation/upload overhead and still needs actual
seven-source observation before operational timing is claimed.

## Offline evidence and reproducibility

Run from the repository root, with no network:

```sh
python -B -m unittest discover -s tools/catalog-collector -p test_utility_selectors.py -v
python -B -m unittest discover -s tools/catalog-collector -p test_migration_enrollment.py -v
python -B -m unittest discover -s tools/catalog-collector -p test_supervised_transport.py -v
python -B docs/track/release-catalog/research/am-utils-release-20261028/measure_preparation.py
```

The last script reconstructs the retained six-source baseline, adds the real new
body using **synthetic six-source 304 events**, and exercises actual bounded ZIP
parsing/recomputation and temporary local Git parent/child commits. These test
304s/times are never represented as real upstream checks or published data.

[Measured preparation resources](../research/am-utils-release-20261028/preparation-resources.json):

| Resource | Measured bytes |
| --- | ---: |
| Retained six-source prior tree | 4,898,586 |
| Seven-source candidate tree | 7,621,340 |
| Candidate bodies | 7,600,048 |
| Candidate index / lookup | 15,937 / 5,355 |
| Artifact uncompressed members (18) | 10,351,389 |
| Compressed ZIP | 553,748 |
| Temporary local object files before / after | 430,850 / 578,043 |
| Temporary local object-file growth | 147,193 |

The replay records exact manifest/body/code hashes. These are bounds/correctness
and local compression measurements, not full remote history growth or daily churn.
Git object sizes may differ on later replay due to commit timestamps/compression.
No seven-source live 304, workflow artifact or publication is claimed.

Tests preserve all six old body bytes/receipt times/active aliases, reuse only
matching available validators, advance validation only for simulated valid 304s,
retain old observation ages on timeout, and refuse invalid/missing/oversized data,
wrong conditions/descriptors, count/hash mismatch, stale parent and corrupted
bodies. Real shell and Python reader paths cover the seventh alias, pinned bytes,
inclusive 48-hour freshness and exact stale-consent binding. Local bare-repository
publication exercises the publisher and parent/tree checks without any remote
production operation. The actual transport starts seven local fake workers,
reaps them, and refuses duplicate/eighth calls.

## Remaining acceptance

Ticket 47 stays claimed/partial; 48/49 remain blocked by live availability.
After 37 closes and the authorized six-source daily switch is coordinated,
prepare a separate exact review/approval for replacing the operational manifest,
source push/pin and one bounded seven-source collection/publication. Record the
actual approved full source SHA, candidate manifest hash, exact remote parent,
workflow isolation and seven expected descriptors. Do not guess a future source
SHA, repin during the pilot, replace genuine prior times or dispatch a synthetic
schedule test. Real seven-source collection, repeat conditional behavior,
artifact/tree/history growth and accepted operational cadence remain unperformed.


## Final verification

[Recorded checks](../research/am-utils-enrollment-preparation-checks.txt): full
192-test catalog run passed; one subsequently added workflow-staging regression
also passed in the final seven-test enrollment run (193 distinct tests exercised).
Both recipe syntax checks pass; ShellCheck warning diagnostics match the old
recipes exactly (pre-existing unused SITE assignments). Source/manifest hashes,
local links and diff checks pass. No repeated container run was needed: this
change alters catalog CI counts and two asset filters, with actual selector and
reader/publisher paths covered offline.
