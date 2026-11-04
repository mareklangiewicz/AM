# YAML pinned prior and publication CAS — November 4, 2026

[93](../issues/93-prepare-yaml-pinned-publication.md), source candidate
`3bf90b411` on `prep/yaml-offline-publication`.

`yaml_delivery.fetch_prior` reuses shared isolated authenticated Git acquisition,
extracted as `delivery.fetch_pinned_repository`. A caller's exact prior must match
the fixed remote release-catalog ref before fetch and the fetched depth-one commit
after fetch. Empty prior requires proven branch absence. Errors/mismatches never
become bootstrap; no fallback, implicit format-1 conversion or retry is provided.
The existing format-1 wrapper retains its own reader/future-generation validation.

The new reader bounds listing output (200,000 bytes), file count, blob-size output
(64 bytes), per-file and aggregate tree bytes before loading/validating canonical
format-2 YAML. Only regular 100644 apps.yaml and repositories/ID.yaml are accepted;
path IDs, shared schema and app references must agree. Receipt, format-1 files,
malformed YAML and executable/symlink entries refuse. Existing per-command Git
90-second/remote-output/history bounds remain; local Git reads use the same bounded
I/O and isolated credential-free environment. The 128,000,000-byte repository plus
candidate-logical-byte check can conservatively refuse a tree that otherwise fits
the separate profile. These are candidate bounds, not hosted-runner guarantees.

`yaml_delivery.publish` preflights trusted context/source/manifest/policy, creates
a private publication root, reacquires exactly the artifact's trusted prior pin,
authenticates and verifies the artifact, and uses the existing local YAML writer.
The resulting commit is independently checked to have exactly the prior as sole
parent (no parents for bootstrap). Only YAML enters its Git tree. Receipt and local
publication.json stay outside history. Retention/shared observation semantics and
explicit all-only reconciliation are unchanged.

The fixed-ref push uses an explicit expected-old-value lease:
`--force-with-lease=refs/heads/release-catalog:PIN`, empty expected value for
bootstrap. This rejects racing creation, descendant publication, deletion and
backward reset; ordinary fast-forward alone does not cover all those cases.
The direct-parent assertion constrains the append; no alternate ref/URL, rewrite,
retry or rebase path is exposed. Existing format-1 publication push semantics are
unchanged. A later publication may advance the ref after success.

Nine new offline tests use real temporary bare repositories/local Git transport,
fake authenticated GitHub API responses and actual ZIP/YAML verification:
bootstrap/refresh ancestry and YAML-only history; exact/stale/missing prior and
query/fetch race; four publication lease races; invalid prior format/layout/mode/
limits; invalid artifact/history refusal before push; preflight and existing-output
refusal before remote work. **64 tests pass** including the previous 55 YAML and
format-1 delivery/shard/shell checks. Compilation and whitespace pass.

Failed operations write no success report; private scratch may remain for review.
A lost push acknowledgement or report-write failure after remote acceptance is
ambiguous and needs remote-state inspection, not automatic retry. No operational
failure-recovery workflow is activated by the source API.

[Detailed source design](https://github.com/mareklangiewicz/AM/blob/3bf90b411/docs/track/release-catalog/design/yaml-pinned-publication.md).
No live artifact, remote catalog tip, GitHub permissions/branch protections or
runner capability was checked. No live catalog push, workflow activation/dispatch,
repin, installed change, schedule or yadm pointer operation occurred. The inactive
workflow remains bootstrap staging only. Source promotion/review, operational
migration, policy/capacity acceptance and activation remain separate decisions.
