# Inactive format-2 prior and publication candidate

Ticket 93 connects authenticated normalized artifacts to existing fixed-repository
Git mechanisms. No active workflow imports this module, and no live catalog write
is part of the experiment. `yaml_delivery.fetch_prior` can separately supply the
collection job's pinned local prior; `yaml_delivery.publish` repeats that same pin
check in a separate private publication repository before artifact verification.

## Prior acquisition

The shared `fetch_pinned_repository` helper is extracted from format-1 delivery:
require caller's exact lowercase 40-hex pin or empty bootstrap pin, query only the
fixed release-catalog ref at the fixed HTTPS repository, refuse any mismatch,
fetch that ref at depth one without tags, and check the fetched commit again.
An empty pin succeeds only when the ref query proves absence; failures are not
absence. No fallback to the latest tip, retry or format conversion is performed.
Existing format-1 delivery retains its reader and future-generation checks.

The format-2 reader bounds listing output before splitting entries, file count,
per-blob and aggregate tree bytes before loading blobs. It accepts regular 100644
blobs named apps.yaml or repositories/ID.yaml only and validates canonical YAML,
path identity, shared schema and complete app references. Format-1 index/bodies,
receipt, executable/symlink/gitlink entries and malformed YAML are rejected.
Repository facts and observation semantics remain those of the retained model;
loading a prior cannot reobserve a release. The exact fetched local pin remains the
input to existing enrollment and artifact verification.

Existing isolated authenticated Git transport retains its 90-second per-command,
64,000-byte remote-output and 128,000,000-byte repository bounds. Local prior Git
reads reuse bounded process I/O with isolated credential-free environment: listing
200,000 bytes, size output 64 bytes and blob output the configured file cap. The
same history bound plus candidate logical bytes gates commit construction. These
are conservative candidate limits, independent of the tree profile, not a new
capacity guarantee; an otherwise valid large tree may fail the history budget.
Validation/staging has no new aggregate deadline, watchdog or worker layer.

## Publication

Preflight binds source, context, manifest and policy before any remote work. The
publisher creates a new private root, acquires the exact remote prior, authenticates
the selected same-run artifact, and runs existing scope/enrollment/retained-state
verification before creating a YAML-only commit using the existing local writer.
Receipt and publication report are local/artifact metadata, never Git tree files.
The writer's local ref update remains atomic. The publisher independently checks
that the new commit has exactly the prior as sole parent (or no parents for
bootstrap) before pushing only that commit to the fixed release-catalog ref.

The push uses an explicit `--force-with-lease=refs/heads/release-catalog:PIN`, or an
empty expected value for bootstrap. This is an exact expected-old-value check,
not reliance on a tracking ref. It guards racing creation, descendant publication,
deletion and backward reset. The direct-parent assertion constrains the candidate
to an append; there is no rewrite/retry/rebase path. The existing format-1 publisher
continues to use its earlier ordinary fast-forward push; this ticket does not
change its publication behavior. No remote-ref probe after a successful push is
required to claim permanent tip ownership: a later publisher can advance it.

Success writes a local publication.json containing commit/parent/ref, source/run,
artifact identity/digest and logical tree bytes. Failed verification or a rejected
lease writes no success report and never retries. Private scratch can remain for
diagnostics, including an already verified artifact and a local candidate commit
when the lease is rejected. A lost push acknowledgement or report-write failure
can be ambiguous after the remote accepted a commit; callers must inspect remote
state rather than blindly retrying or treating the old pin as current. No such
failure recovery workflow has been activated.

## Evidence and remaining work

Nine offline tests use real temporary local bare repositories and Git transport,
fake authenticated GitHub API responses and real ZIP/YAML verification. They cover
bootstrap/refresh direct ancestry and YAML-only history; stale/missing pins and a
change between ref query and fetch; lease races (creation, descendant, deletion,
backward reset); invalid prior format/layout/modes/bytes/count; invalid artifact
and history refusal before push; preflight/existing-output refusal before network.

Remote GitHub permissions, branch protections, hosted-runner capacity, Actions
artifact transfer and workflow provisioning were not exercised. The existing
inactive workflow is bootstrap staging only and still has no publisher. Source
review/promotion, accepted capacity/policy, migration and operational activation
remain separate. No workflow edit, dispatch, catalog push, repin, installed change,
schedule or yadm pointer update is implied by these source APIs.
