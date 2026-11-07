# Next real-source cohort up to the deployed 500-source ceiling

Local preparation for [149](../issues/149-prepare-500-source-cohort.md),
November 7, 2026, continuing broad coverage in 138.

## Verified identity scope

184 additional catalog-only app identities add 180 distinct numeric sources:
local enrollment is **509 apps / 500 sources**, comprising 57 recipe identities
and 452 catalog-only identities. Published enrollment at preparation start is
325 apps / 320 sources. No recipe, production collector, compiled client policy
or installed-host change is included.

Two checkpointed verifier invocations record 200 and 183 logical public
metadata/release-probe GET invocations. [First identity receipt](next-500-identities-1.json)
records 95 proposals / 92 new sources; [second identity receipt](next-500-identities-2.json)
records 89 proposals / 88 new sources after seeding the first verified proposals.
Each source binding is rechecked against both the original Git bytes at discovery
commit `f657f4d7876f0164b6705795527f5a33738d0f73` and the current working tree.
Only explicit supported recipe bindings are promoted, independently of migration.

Eight alias/canonical public numeric identity checks agree: armcord, arwing,
arwing2, ascrobble, asrpro, atropos, auryo and bananas. `amele` still has no public
release in the probe; `aniwings-app` still returns HTTP 404. Both verifier
invocations recheck and exclude them; these are two distinct excluded apps,
not four new exclusions. Other discovery entries remain an unverified queue.

Accounting limitation found by code inspection: the verifier's `_get` uses the
default urllib redirect handling, so its counter bounds logical GET invocations;
automatic rename hops can add underlying transport requests. These receipts do
not instrument or prove the exact wire request count. [151](../issues/151-bound-discovery-redirect-request-accounting.md)
tracks explicit shared-budget transport accounting. The independent collector
preflight below uses its existing redirect-refusing opener and actual attempt
metrics; this discovery limitation does not alter verified numeric identities.

## Real cohort preflight

[Fresh preflight](next-500-preflight.json) succeeds for all 500 sources in one
bounded batch: 500 actual collector requests, zero failures/unattempted sources
and all 509 enrolled apps present. The remote-free local candidate
`bee5c0e03bb3d07298aea02449f3ab2ea99660a2` is a child of the fetched baseline below.
Both prior and candidate snapshots pass the maintained bounded distributed-reader,
canonical byte and cross-reference checks. Exact-pin readback equals the candidate;
prior app/source identities and retained release IDs survive, and effective
release observations never decrease.

| Measurement | Actual real-source cohort |
| --- | --- |
| Charged response bytes | 341,439,272 / 536,870,912 |
| Acquisition seconds | 551.56 / 900 |
| Controller seconds including prior read and final exact-pin readback | 965.85 |
| Peak controller RSS | 728,864 KiB |
| YAML bytes | 63,690,470 |
| Largest document | 1,372,340 / 2,097,152 bytes |
| Reader files | 501 / 1,024 |
| History guard: existing object bytes plus candidate YAML | 122,689,269 / 268,435,456 bytes |
| Git object bytes after publication | 71,225,593 |

The controller runs under a 1 GiB address-space limit. Its elapsed time includes
additional preservation and full exact-pin readback checks: it is neither a
measured Actions job nor a separate whole maintained-command replay. Receipt
hashes bind the working-tree manifest to source base `0880b2d70`; collector code
is unchanged. The largest document remains `any-listen/any-listen-desktop`.
Live core headers again report limit 5,000, remaining 4,606 first / 4,107 last.
The cause of this larger allowance remains unresolved; conservative documented
1,000/hour planning is unchanged. Actual collector attempts are reported
independently. No source lacks success and the 24/36/48-hour source age counts
are zero, without reobserving retained releases outside the fetched page.

The fetched baseline for the rehearsal is
`08a0fbd526156a456a8648e71d9d2be11734bc74`; it is the actual remote parent at fetch
rather than the older historical rollout pin. All 500 sources were measured
under unchanged deployed limits. This remains local preparation, not publication.
Raw checkpoints, responses/receipt times, controllers, local publication objects
and focused test logs remain at
`/home/marek/Documents/Codex/am-500-cohort-20261107/`.

## Focused regression validation and publication package

All **12 focused tests pass** on the final 509-app / 500-source manifest in
327.920 seconds: source discovery/identity/rename gates, catalog-only enrollment,
declarations and the actual maintained workflow-command publication/failure-
preservation regression. [Validation receipt](next-500-validation.json) binds
source/manifest/log hashes. All 193 recipe bindings behind the 184 proposals were
independently rechecked against original Git bytes and the current working tree.
`git diff --check` passes. The previous 159-test full collector suite passed for
the preceding 320-source manifest; it was not rerun in full for this data-only
expansion. No production Python, recipe or compiled policy bytes change here.

[150](../issues/150-publish-500-source-cohort.md) is the concrete source push and
live publication package awaiting Marek's call. Live publication must use the
actual remote parent and repeat exact-pin checks; these local measurements are
not evidence of a 500-source CI run.

## Boundaries

The deployed 500/hour profile and its 512 MiB charged response, 900-second
acquisition, 16 MiB/response, 2 MiB/document, 1,024-file reader, 256 MiB local
history and 48-hour selected-release freshness limits remain unchanged.
The earlier synthetic 500-source fixture is not proof about this real cohort;
the fresh preflight above now measures its actual density and retained history.
Whole-snapshot materialization, retained growth and attribution of unsupported
bindings across all four architectures remain before qualifying thousands.
No all-GitHub completion or browser DOM/CORS/mobile acceptance is claimed.
No source push, remote publication, installed refresh, app update, recipe migration,
website rebuild or yadm pointer operation is included in local preparation.
