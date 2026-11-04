# YAML staging candidate

Inactive source review artifacts; no workflow is installed or dispatched.
`catalog-yaml-staging.yml.proposed` stages an explicit bootstrap only. It does not
assume absence of the operational catalog branch and cannot publish or replace
it. Merge/review the complete source candidate before considering activation.
The existing local pinned-refresh API remains separate from remote prior loading.

The proposed job reuses the currently recorded checkout/upload action pins and
requires PyYAML already provisioned in its reviewed Python runner environment.
It checks the dependency before acquiring credentials. No new action versions
or runner provisioning have been verified remotely. A 15-minute job allowance
covers staging and upload around the shared 300-second transport allowance;
this is a configuration proposal, not measured default-run capacity.

`tools/catalog-collector/yaml-policy.json` selects these candidate limits:

| Scope | Limit |
| --- | --- |
| Repository/app YAML file | 2 MiB |
| Aggregate requests | 64 |
| Aggregate response-body bytes | 96 MiB |
| Shared transport deadline | 300 seconds |
| Per-source page requests | 64 |
| YAML candidate tree | 128 MiB |
| YAML candidate files | 128 |
| Artifact receipt | 1 MiB |

The existing transport retains its 8,000,000-byte body and 64,000-byte header
limits, 10-second connect and 30-second request deadlines. YAML retains the
reader's line bound. Raw-byte accounting includes a crossing received chunk;
no filesystem quota or exact wire-byte ceiling is claimed. Validation/staging
is outside the transport elapsed deadline. The 2 MiB allowance accommodates the
recorded saved replay's largest 1,251,974-byte document; future retained growth
or a 100-release default may exceed it and must refuse without eviction. The
49-source first page fits the 64-request allowance arithmetically; actual
100-release default capacity remains unmeasured. Scope is never truncated into
success when a budget prevents completion. Profile numbers require review before
operational adoption and supersede no accepted deployment policy here.

Preflight reuses the manual workflow context checks, exact source/workflow SHA
approval and manifest digest. It additionally binds the exact policy bytes and
canonical scope JSON to expected SHA256 values. Default scope canonical bytes
(no final newline) are:

```json
{"page_limit":1,"page_size":100,"reconcile":false,"sources":null}
```

Use storage.canonical to compute hashes, rather than hashing pretty-printed JSON.
The receipt contains the exact context, scope, source outcomes, enrollment review
metadata and previous publication pin. The package is closed:

```
receipt.json
candidate/apps.yaml
candidate/repositories/ID.yaml
```

No raw response bodies, executable files, symlinks, arbitrary paths or published
hash/size ledger enter this package. The receipt is an artifact review record;
only candidate YAML belongs in a future catalog snapshot. Producer staging uses
a new private directory and removes partial output after write failure. An
incomplete bootstrap returns no package; the proposal logs its aggregate refusal
report. Attempted source failures are valid metadata, although the proposed job
returns failure when any source failed or remained unattempted.

The verifier checks bounded file/directory layout, complete schema/canonical YAML,
app references and source/schema revision; recomputes static enrollment from the
reviewed checkout; checks prior pin, scope/outcome metadata and preserved failed/
unattempted state. It does not independently reconstruct upstream facts from raw
JSON, which is deliberately absent. Format 2 relies on the trusted collection
workflow. A future downloader/publisher must establish same-run artifact origin
and GitHub artifact digest before using this verifier; self-reported receipt
context alone is not artifact authentication. ZIP acquisition/extraction,
remote prior fetching, publication compare-and-swap and schedule integration are
not implemented here. No source YAML artifact can authorize those operations.

Offline checks:
`python3 -m unittest discover -s tools/catalog-collector -p 'test_yaml*.py'`.
