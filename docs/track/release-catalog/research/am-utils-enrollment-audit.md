# am-utils offline enrollment audit

2026-10-28; ticket [47](../issues/47-enroll-scoped-migration-sources.md).
Source inspection only, at `389b6bb1f`; no network requests, recipe execution,
collector run, manifest mutation or remote state inspection.

## Identity and exact request

The frozen [family inventory](recipe-family-inventory.md)
identifies 356 recipes sharing the exact consumer alias
`https://api.github.com/repos/ivan-hc/am-utils/releases`. The current
[manifest](../design/staged-manifest.json) does not enroll it. The
[saved identity audit](saved-identity-audit.json) covers the original six
descriptors; it supplies no am-utils repository-ID evidence. Neither the recipe's
`SITE` nor release/asset IDs establish repository identity. No numeric am-utils
repository ID is established by the evidence reviewed here; this is not an
assertion about every historical archive or the live repository.

The next proposed identity request is exactly one unauthenticated GET to
`https://api.github.com/repos/ivan-hc/am-utils`, with no redirect, retry or follow-up.
Use the existing [enrollment review's](../design/transport-enrollment-review.md#separate-identity-enrollment-request-proposal--not-dispatched)
10-second connect / 30-second total / 64,000-byte body and headers /
8,192-byte retained-header-value bounds and pinned representation. Require 200,
positive integer `id`, expected `full_name` (case-insensitive), `private=false`
and `visibility=public`. Preserve exact body/hash, selected public headers and
start/completion evidence. A mismatch stops; it does not approve a renamed target.

Only after that evidence is reviewed can a numeric fetch descriptor be formed:
`https://api.github.com/repositories/REVIEWED_ID/releases`. It must retain the
exact named consumer alias above, with no added query or `/latest` substitution.
The [descriptor implementation](../../../../tools/catalog-collector/collector.py)
hashes exact URL, API version `2022-11-28` and Accept
`application/vnd.github+json`. The new numeric descriptor therefore needs its own
computed request ID, evidence anchor and initial unconditional request. The numeric
route has not been observed here. No initial validator may be invented or borrowed.

## All count boundaries must agree

Appending a seventh row alone cannot work:

| Boundary | Current contract |
| --- | --- |
| [Manifest loader](../../../../tools/catalog-collector/manifest.py) | Exactly six rows; raw manifest at most 64,000 bytes; numeric fetch URL, matching request hash, aliases, evidence |
| [Collector plan](../../../../tools/catalog-collector/collector.py) | One through six requests, unique descriptors/aliases, trusted workflow repository excluded |
| [Transport](../../../../tools/catalog-collector/supervised_transport.py) | At most six calls; 10-second connection, 30-second request, 300-second batch deadlines |
| [Storage](../../../../tools/catalog-collector/storage.py) | At most six attempts; valid embedded manifest; 2,000,000-byte index and 50,000,000-byte tree |
| [Delivery verification](../../../../tools/catalog-collector/delivery.py) | Complete report, exactly six attempts, every transition observed/validated, exact candidate recomputation |

Existing body cap is 8,000,000 bytes per response, headers 64,000 bytes and
retained values 8,192 bytes. Delivery ZIP and total uncompressed members are bounded
by 105,000,000 bytes, with at most 100 files and a 64,000-byte central directory.
Publication/delivery history-object bound is 128,000,000 bytes;
[local publication](../../../../tools/catalog-collector/publication.py) also adds
candidate tree bytes to existing object-file bytes before accepting publication.
The [workflow](../../../../.github/workflows/catalog-collector.yml) gives each job
five minutes, including its other work; a 300-second transport budget does not
guarantee that the complete collector job fits.

Seven maximum-size bodies alone total 56,000,000 bytes, exceeding the tree bound
before metadata. Keeping the existing caps is appropriate; measure actual bodies,
candidate index/lookup/tree, duplicate artifact bodies, ZIP and history growth.
No capacity conclusion follows from the endpoint count alone. A seven-source
stage requires coordinated count changes and refusal tests at each boundary,
without widening body/tree/history/deadline limits speculatively.

## Retention, failure and delivery pitfalls

[Workflow preparation](../../../../tools/catalog-collector/workflow_adapter.py)
validates the exact previous publication and reconstructs priors for matching
available request IDs. Existing six IDs/descriptors/aliases must remain exact.
[Storage](../../../../tools/catalog-collector/storage.py) marks sources absent
from the new manifest retired, so a one-row am-utils-only manifest is not an
acceptable way to preserve six active sources. Conditional 304 requires genuine
matching available prior bytes/validators; temporary failures preserve prior age.

The current publisher requires every transition to be observed or validated.
Consequently a candidate can retain failure evidence/old observations without
being publishable: a failed seventh observation currently prevents publication of
the whole run. Preserve that distinction in the stage review; changing it would
be a separate explicit contract decision within ticket 47, not an incidental
relaxation of the attempt count.

The source, workflow and approved revision must match, as must the manifest hash
and exact previous publication pin. Collector credentials are read-only; the
separate publisher consumes same-run artifacts as data and recomputes storage.
Retain artifacts/logs before their seven-day retention expires. Do not use an
enrollment experiment to repin or disturb the ongoing hourly pilot.

An approved release-body read would still need whole-family selector verification
against retained exact bytes. For example, [7z](../../../../programs/x86_64/7z)
tokenizes the response, uses a case-insensitive architecture/date/app-name pattern,
then takes the first match. A structurally valid release list does not prove every
one of the 356 selectors has a result, or that returned Linux executables run on
Termux. Keep metadata compatibility, lifecycle migration and installed delivery
as separate claims. Preserve first-page response scope and Link evidence; no
automatic pagination or endpoint substitution is authorized.

## Remaining evidence

1. Bounded identity response and reviewed numeric repository mapping.
2. Separately approved numeric release response, exact body/headers/timings and
   resource measurements, with all 356 original selectors checked offline.
3. Reviewed coordinated seven-source implementation, historical six-source
   readability/retention checks, exact source/manifest hashes and pinned prior.
4. Separately authorized collection/publication evidence and accepted cadence;
   extension to the 50-endpoint AppImage queue remains a later measured stage.

This audit supplies no live identity, route success, current body size, asset
compatibility or remote publication guarantee.
