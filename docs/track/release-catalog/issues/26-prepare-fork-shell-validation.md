# Prepare retained-data fork publication and shell read

> **2026-10-28 ownership correction:** [Ticket 29](29-respect-configured-catalog-repository.md) supersedes
> this record's fixed-upstream ownership assumption. This fork's catalog follows
> AMREPO and must not fall back to upstream AM. Upstream acceptance/publication
> is not a prerequisite for this fork. Results and archived bytes below retain
> their historical source/revision meaning; they do not define current policy.

Type: task
Status: resolved
Triage: ready-for-agent

## Scope

Prepare a concrete child of the fork's current release-catalog publication using
retained exact bytes, adding only recomputed lookup.tsv. Preserve original index,
observation timing and bodies. Record target, source, parent and candidate commit.
Prepare an explicit fork-only copy of the shell reader for read-only validation;
keep the installed reader fixed to ivan-hc/AM. Verify locally before requesting
publication approval. No workflow dispatch, collection, schedule or host installer.

## Answer

Prepared and locally verified exact child `a0fdd125558c4629a07c7edd0d7f6f7f96b1dcc1`
of read-only-confirmed fork parent `d612ff34b492b337fe51128f769ec9d262d0ee86`.
Only a recomputed 4,638-byte lookup.tsv is added; index, all original bodies and
measurement times are unchanged. Exported exact commit bundle and per-file hashes.
The explicit fork-only reader copy passed local Git transport/body/filter checks
with the real clock; normal push was rehearsed only against a temporary bare repo.
See the [reviewable plan and evidence](../research/fork-shell-validation-plan.md).

No production reader change, remote publication, live shell read, workflow, source
collection, schedule, binary download or host app operation. Publication/read
approval remains the next separate action; preparation is complete.
