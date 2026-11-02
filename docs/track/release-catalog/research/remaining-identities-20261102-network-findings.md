# Remaining identity batch: network evidence

November 2, 2026, ticket [47](../issues/47-enroll-scoped-migration-sources.md).
The user authorized the fresh network-enabled retry. The reviewed runner executed
once with its original payload and bounds. No automatic-approval rejection occurred.

## Result

Twelve sequential identity GETs ran in 5.431264 seconds of summed request time.
Eleven returned HTTP 200 with the expected name, public visibility and positive
repository ID, excluding the collector repository. They establish candidate
mappings for **12 exact release endpoints / 42 recipes**; SuperTuxKart's list and
latest routes share one identity. No numeric release request was made.

Request 12, `https://api.github.com/repos/mysteryx93/NaturalGroundingPlayer`,
returned HTTP 301 with Location
`https://api.github.com/repositories/37950127`. The runner stopped immediately and
did not follow the redirect. The redirect destination is observed evidence only:
its public identity/current name is unverified, and ID 37950127 is not accepted
as an enrollment mapping. No alias substitution is justified by this response.

The remaining **36 identity URLs were not attempted**. Their exact ordered list,
the 12 candidate numeric release descriptors and request IDs, and the failed
redirect appear in [recomputed audit](remaining-identities-20261102-network/audit.json).
The original queue is unchanged: this derived candidate report does not claim
committed identity acceptance, release compatibility or operational enrollment.

## Evidence and checks

[Batch summary](remaining-identities-20261102-network/batch.json) and numbered
request directories retain exact bodies, headers, reports, timing and hashes.
Total retained response bytes: 64,104 body + 15,769 header bytes.
[Offline audit](remaining-identities-20261102-network/audit.py) recomputes all stream
sizes/hashes, exact request-prefix scope, accepted identity fields, own-repository
exclusion, failure position, numeric suffix/query preservation and descriptor IDs
through the existing collector implementation. It passes. A local attributes rule
preserves CRLF header bytes under the repository's `core.autocrlf=input` setting.

Reproduce without network access:

```sh
python3 docs/track/release-catalog/research/remaining-identities-20261102-network/audit.py
```

## Next boundary

Keep completed identities and the redirect evidence; do not restart the full batch
or automatically retry the redirected name. A separately reviewed continuation
can cover the 36 unattempted URLs while leaving this redirect unresolved. Review
its exact supervised continuation payload before execution. Separately, after
accepting the saved mappings, prepare the 12 numeric release evidence GETs and
original-selector replay for their 42 recipes. Operational capacity remains a
separate decision; no source-count guard or collection deadline has changed.

No release GET, binary download, source push, collection/publication, daily repin,
recipe migration or host delivery occurred. Tickets 47 and 49 remain partial.
