# Next verified catalog cohort

Local preparation for [147](../issues/147-prepare-next-verified-cohort.md),
November 7, 2026, continuing broad coverage in 138.

## Identity scope

97 additional catalog-only app identities add 96 distinct numeric sources,
bringing local enrollment to 325 apps / 320 sources. The deployed baseline remains
228 apps / 224 sources. [Identity receipt](next-320-identities.json) records 198
bounded metadata/release-probe reads, rechecked original Git and working-tree
recipe hashes, explicit source bindings and public canonical numeric identities.
The pinned discovery source is `f657f4d7876f0164b6705795527f5a33738d0f73`.
The verifier checks every proposed binding against current bytes before promotion.

Anixapp's alias/canonical public numeric identity agrees. `amele` has no public
release in the probe; `aniwings-app` returns HTTP 404. Neither is enrolled.
The scan remains an unverified queue outside these checked identities; no claim
of all-GitHub coverage, recipe migration or installation support follows.

## Local preflight

[Fresh preflight receipt](next-320-preflight.json) records 320 requests and 320
successful sources, zero failures/unattempted sources and all 325 enrolled apps.
The fetched actual parent was `59b3f3f398bc1013c7b5caf0f37b19a4f3fc9821`;
local candidate `56fe85fa98783ef94c33cdd77c765515ae0c8334` passes exact-pin
bounded distributed-reader, canonical and cross-reference readback. All previous
app/source identities and retained release IDs survive; effective release
observation times never decrease. This is a local child, not a remote publication.

| Measurement | Result |
| --- | --- |
| Charged release response bytes | 240,500,606 / 536,870,912 |
| Acquisition seconds | 365.76 / 900 |
| Controller seconds, including initial read and final exact-pin readback | 734.92 |
| Peak controller RSS | 657,068 KiB |
| YAML bytes | 44,626,132 |
| Largest YAML document | 1,372,340 / 2,097,152 bytes |
| Reader files | 321 / 1,024 |
| History guard: existing objects plus candidate YAML | 101,827,247 / 268,435,456 bytes |
| Local Git object bytes after publication | 65,568,511 |

The controller runs with a 1 GiB address-space limit. Its elapsed time includes
additional preservation/readback verification and is not a measured Actions job
or a separate whole-command replay. Receipt hashes bind the working-tree
collection manifest to source base `7c232b86a`; production collector code is
unchanged. Live headers again report core limit 5,000 (4,784 first remaining,
4,465 last); the documented conservative 1,000/hour plan remains unchanged and
the reason for the larger observed allowance remains unresolved.

The first local controller reused a pre-146 response-wrapper signature and failed
before HTTP transport: it omitted the keyword-only quota-reporting argument.
It was stopped and corrected locally; that attempt supplies no upstream evidence
or capacity qualification. The maintained collector is unchanged.

Raw verification checkpoints, release pages, controllers, local publication Git
objects and regression logs are preserved at
`/home/marek/Documents/Codex/am-next-cohort-20261107/`.

## Regression validation and publication package

All **159 collector tests pass** on the final enrollment in 1,232.724 seconds,
including 115 saved AppImage lifecycle cases, manager integration, retained
observation semantics, budget/quota stopping and exact-parent publication tests.
[Validation receipt](next-320-validation.json) binds the complete local log and
manifest hashes. Proposed proof-binding working-tree hashes were rechecked again;
`git diff --check` passes. No production code, recipe or compiled client policy
changes are needed. The largest real document belongs to
`any-listen/any-listen-desktop`.

[148](../issues/148-publish-320-source-cohort.md) is the concrete push/publication
package awaiting Marek's push call. It requires a fresh actual remote parent,
all-source workflow outcomes and exact-pin preservation checks after publication;
this local rehearsal does not replace them.

## Boundaries

The deployed hourly profile and all existing collection, file, transport, history,
reader and selected-release freshness limits stay unchanged. Actual density and
retained growth must pass measured preflight for this real cohort; the earlier
synthetic 500-source fixture is not proof of 500 upstream enrollments. Whole-tree
materialization and the 1,024-file reader still constrain thousands of sources.
No real-browser DOM/CORS/mobile acceptance or website rebuild is included.

Read-only workflow inspection still finds manual run 42366263140 as the latest
catalog run; the first natural trigger at the new hourly cadence is unobserved.
No push, workflow dispatch, installed refresh, app update or yadm pointer operation
is included in local preparation.
