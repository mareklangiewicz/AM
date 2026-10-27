# Identify the upstream adoption boundary after fork validation

> **2026-10-28 ownership correction:** [Ticket 29](29-respect-configured-catalog-repository.md) supersedes
> this record's fixed-upstream ownership assumption. This fork's catalog follows
> AMREPO and must not fall back to upstream AM. Upstream acceptance/publication
> is not a prerequisite for this fork. Results and archived bytes below retain
> their historical source/revision meaning; they do not define current policy.
> The upstream-first rollout recommendation below is withdrawn as the current
> continuation plan. It describes optional future upstream adaptation only.

Type: task
Status: resolved
Triage: ready-for-agent

## Scope

Following Marek's push-and-continue instruction, audit the checked-in collector,
publisher, manifest and consumer ownership boundaries. Record concrete upstream
adaptation sites and a rollout order that does not activate an unusable ordinary
recipe. Separate already verified fork evidence from upstream readiness. No
upstream submission, guard changes, collection, dispatch or installed migration.

## Answer

[Readiness assessment and rollout order](../design/upstream-adoption-readiness.md)
identifies exact fork guards, artifact branch check, publication targets, reference
identity and consumer delivery boundaries. Upstream activation must be staged:
publisher/lookup plus usable upstream publication, then helper/manager delivery
and ordinary recipe activation. Sustained freshness needs an explicit operating
choice; one successful fork sample is not that choice.

Targeted offline check against the exact published child confirms six conditional
requests preserve prior bodies and validators. Upstream repository, branch-only
and scheduled-event contexts still refuse. Source hashes and checks are retained
in [machine evidence](../research/upstream-adoption-readiness-checks.json).
No runtime code, allowlist, live workflow, publication, source collection or app
state changed. The two prior source commits were pushed successfully before this
assessment. Upstream submission and human ownership review remain separate.
