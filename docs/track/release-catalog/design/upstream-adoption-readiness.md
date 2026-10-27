# Historical upstream adoption assessment (superseded)

> **2026-10-28 ownership correction:** [Ticket 29](../issues/29-respect-configured-catalog-repository.md) supersedes
> this record's fixed-upstream ownership assumption. This fork's catalog follows
> AMREPO and must not fall back to upstream AM. Upstream acceptance/publication
> is not a prerequisite for this fork. Results and archived bytes below retain
> their historical source/revision meaning; they do not define current policy.
> The upstream-first rollout recommendation below is withdrawn as the current
> continuation plan. It describes optional future upstream adaptation only.

Ticket [28](../issues/28-upstream-adoption-readiness.md).
Source audited: `b6892ff2f3f8e89a23415e5188bc26bceb67469a`.
This is an internal integration assessment, not an upstream submission or rollout
approval. Local source and retained publication evidence are its inputs; no
current upstream branch, permissions, policy or workflow state was queried.

## Result

The bounded fork delivery/read works, but the source cannot be submitted as one
ready-to-enable upstream patch. Collector/publisher ownership is deliberately
fork-specific, while the installed shell reader already trusts upstream AM.
Merging the ordinary Obsidian substitution before a working upstream publication
would make new installs/newly generated updaters refuse. Keep upstream publication
and helper delivery ahead of recipe activation. Keep the existing fork as the
experiment until upstream maintainers choose to adopt the design.

## Concrete adaptation inventory

| Boundary | Checked-in sites | Required upstream decision/change |
| --- | --- | --- |
| Dispatch allowlist | `.github/workflows/catalog-collector.yml`, both job guards | Select exact upstream repository and approved source branch; retain manual dispatch and exact revision checks. |
| Code-level context | `tools/catalog-collector/workflow_adapter.py`, `preflight` | Match that same fixed repository/branch. Changing YAML alone still refuses. |
| Publication target | `tools/catalog-collector/delivery.py`, `REPOSITORY`, `URL`, `REMOTE_REF` | Use the approved upstream owner and dedicated ref for both prior fetch/push and artifact API reads. Preserve parent checks and fixed-ref normal pushes. |
| Artifact branch provenance | `delivery.py`, `download_artifact` | Replace the explicit `head_branch == 'main-marek'` check consistently. Changing only target constants still refuses valid upstream artifacts. |
| Collection identity | workflow context, manifest/collector validation, stored `workflow_repository_id` | Obtain actual upstream repository identity through reviewed evidence. Keep own-repository exclusion and publisher/context identity checks. Do not relabel fork observations as an upstream workflow run. |
| Enrolled requests | `docs/track/release-catalog/design/staged-manifest.json`, `manifest.py` | Review exact six numeric routes, aliases and enrollment evidence. Six sources is enforced in the loader and publication gate; one-app collection is a separate scope change. |
| Shell publication format | `shell_lookup.py`, `storage.py`, `artifact_io.py`, `delivery.py` | Deploy generation, closed-tree/ZIP allowlists, validation and publisher recomputation together. A JSON-only publication cannot serve the shell reader. |
| Installed ownership | `modules/catalog.am` | Already fixed to ivan-hc/AM; do not replace it with the fork or add an arbitrary owner override to enable a demonstration. |
| Helper delivery | `APP-MANAGER` module inventory, `modules/install.am` path embedding | Ship normal managed-module synchronization before activating recipes that require the helper. Preserve the reviewed manager preflight/refusal behavior. |
| Ordinary app behavior | `programs/x86_64/obsidian`, foreground manager route | Activate after upstream publication and helper availability are verified; old installed updaters require an explicit later migration. |
| Python reference identity | `public_http.py` URLs, `reader.py` repository ID | Still deliberately fork-bound reference scaffolding. If included for upstream verification, adapt both transport and expected identity; neither is an installed dependency. |
| Historical quota probe | `.github/workflows/catalog-quota-probe.yml` | Historical fork experiment, not a prerequisite for upstream runtime. Do not expand its allowlist or enable it as part of consumer adoption. |

A text-wide fork-to-upstream replacement would mix experiment/history with
production boundaries and miss numeric identity requirements. Keep explicit
allowlists. No new runtime configuration system is needed for this assessment.
The actual upstream ID, preferred source branch, publication permissions and any
existing release-catalog ref remain unverified.

## Offline continuation check

[Machine evidence](../research/upstream-adoption-readiness-checks.json) records
source hashes and a targeted check against the exact ticket-27 child bundle.
The current workflow adapter accepts this format-only child as pinned previous
state and plans all six conditional requests with byte-identical prior bodies
and original validator tuples. Adding lookup.tsv did not strand the next manual
fork collection. This invokes `prepare`, not transport or a live workflow; its
run ID 1 is explicitly synthetic, and it makes zero network requests.

Changing only the context repository to ivan-hc/AM, changing only the source branch
to main, or changing only the event to schedule each refuses with
`unapproved_context`. The current fork guards are intact. These checks establish
the adaptation boundary, not upstream permission or a live conditional response.
No implementation defect was demonstrated, so no guard was loosened.

## Proposed rollout order

1. Marek reviews the implemented slice and chooses whether to discuss it with
   upstream. The repository's CONTRIBUTING.md requires authors to understand and
   take responsibility for all submitted code, write their own commit messages
   and request descriptions, and handle reviewer discussion themselves. This
   internal record is not a substitute for that human review.
2. Prepare an isolated upstream publisher/lookup slice for that agreed owner,
   branch and repository identity. Keep the ordinary Obsidian recipe unchanged
   in that slice. Verify owner/context/artifact guards, source enrollment, exact
   parent conflicts, privilege separation and derived format offline. Historical
   experiment archives and quota probes need not become production dependencies.
3. With upstream maintainer authorization, publish an upstream-owned lookup
   candidate with accurate provenance and a concrete reviewed parent/absence
   condition. A retained-data candidate needs an explicit import/provenance plan;
   copying the fork index and changing its owner/run ID is not such a plan. A new
   collection is separately authorized work, not necessary merely to test filters.
4. Verify the upstream production reader at an explicit upstream publication pin,
   body/lookup hashes, freshness and original selection filter. Scope an optional
   ref-resolution read separately. A one-off observation will expire; maintainers
   must agree how freshness is sustained before ordinary users depend on it.
   The experiment has no schedule approval. On expiry the existing reader refuses;
   do not silently fall back to a proxy or fabricate a new validation time.
5. Ship helper/module delivery and the reviewed manager/install routing, then
   activate the single Obsidian recipe after the publication is usable. Verify
   refusal and recovery at actual manager entrypoints; retain the single-app
   limitation. Approve installed updater migration separately.

The remaining work is upstream ownership/provenance/operation and human review,
not another fork publication, source collection or fleet migration. Neither a
running workflow nor host app installation is needed to review this record.
