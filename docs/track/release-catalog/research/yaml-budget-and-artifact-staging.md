# YAML budget profile and artifact staging — November 4, 2026

[91](../issues/91-prepare-yaml-budget-and-artifact-staging.md), candidate
`c51b40dc1` on `prep/yaml-offline-publication`.

The concrete profile is 2 MiB/file, 64 aggregate requests, 96 MiB aggregate body
bytes, 300-second shared transport deadline, 64 source requests, 128 MiB candidate
YAML, 128 candidate files and a 1 MiB receipt. Existing 8,000,000-byte body,
64,000-byte header, 10-second connect and 30-second request limits remain.
The reviewed 49-source default fits the request allowance arithmetically, but its
100-release response/retained-growth capacity has not been measured. Crossing
chunks count as received, so logical accounting can exceed a byte allowance by
one received chunk before refusal. Validation/staging is outside the transport
deadline. Numbers are a concrete review candidate, not accepted operational
policy or evidence that a full live default run fits.

Exact profile bytes SHA-256:
`d464ee0c14d8712ef625d47308d8faf47f5faf459fc565b926d2952d98a73e7b`.

`yaml_staging.py` reuses existing manual workflow preflight and binds source/
workflow SHA, manifest digest, exact profile digest and canonical scope digest to
caller-supplied trusted context. `collect_stage` connects pinned collection to
verification and a new private output directory. Failure during writes removes
partial output; existing output refuses before transport. No extra consumer
watchdog, worker or staging-reservation framework was added.

The closed package is receipt.json plus candidate/apps.yaml and
candidate/repositories/ID.yaml. It contains normalized YAML and public review
metadata, no raw API bodies or executable code. Only the candidate YAML would
belong in a future catalog snapshot; no body hash/size ledger is published.
The reader bounds files/count/aggregate bytes, rejects symlinks/executables/extra
paths, and checks structural/canonical YAML and complete app references.
The verifier recomputes static enrollment from the reviewed checkout, validates
source/schema/context/policy/scope/prior pin and source outcome metadata, and
checks failed/unattempted state preservation. It does not independently rebuild
successful upstream facts from raw JSON. That is deliberate under the format-2
trusted-workflow boundary, not an authenticity claim for arbitrary receipts.

A future downloader must establish same-run artifact identity and GitHub artifact
digest before verification; receipt context alone cannot authenticate a package.
ZIP acquisition/extraction and remote previous-state loading remain unwired.
The local pinned API still reads exact commits; future publication must use that
same prior pin in compare-and-swap and keep receipt.json out of catalog history.

The inactive manual workflow proposal stages explicit bootstrap only, with read
contents permission and existing recorded action pins. It does not infer that
an operational catalog branch is absent. It validates dependency/context without
a token, passes an opaque token only to existing transport, checks the written
package again, and uploads staging output. Incomplete bootstrap logs its report
without producing a candidate. Attempted failures remain honest metadata, but
the proposed job reports failure if any source failed or remained unattempted.
The candidate source must first be reviewed/merged; provisioning PyYAML in the
reviewed runner is a prerequisite. No new action pins or runner capacity were
verified remotely. This proposal is neither activated nor dispatch-ready approval.

Detailed source design and proposal at this candidate revision:
[staging design](https://github.com/mareklangiewicz/AM/blob/c51b40dc1/docs/track/release-catalog/design/yaml-staging.md),
[inactive workflow](https://github.com/mareklangiewicz/AM/blob/c51b40dc1/docs/track/release-catalog/design/catalog-yaml-staging.yml.proposed).

Eleven staging checks pass: directory round trip without ref update, context/
policy/scope preflight refusal, strict profile parsing, wrong receipt context/pin/
scope/schema, structural/cross-file mismatch, closed-layout modes/paths, size/
count bounds, write-failure cleanup, incomplete bootstrap, preserved prior facts
and existing-output refusal. Nineteen adapter, nine enrollment/pinned and six
attempt-adapter checks also pass: 45 total relevant executions. Workflow YAML and
both embedded Python scripts parse; Python compilation and whitespace pass.
Tests use fake transport and local Git only.

Next integration seams are authenticated bounded artifact acquisition, remote
format-2 prior loading and publication compare-and-swap, plus a separately
reviewed activation/capacity decision. No active .github workflow edit, live
request, dispatch, catalog publication, daily repin, installed change,
natural-run inspection or yadm pointer operation occurred. Source pushes remain
separately authorized.
