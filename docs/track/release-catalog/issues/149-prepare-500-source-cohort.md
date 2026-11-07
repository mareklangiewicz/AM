# Prepare a verified cohort up to the deployed 500-source ceiling

Type: task
Status: resolved
Triage: ready-for-agent
Assignee: codex
Blocked by: 148

Continue 138 from the published 325-app / 320-source baseline. Verify additional
hash-bound explicit recipe-source identities in checkpointed batches of at most
200 metadata/probe requests, targeting at most 500 distinct sources. Keep renamed,
unavailable and no-release candidates explicit and un-enrolled unless verified.

Use the actual latest catalog parent for fresh full-scope bounded collection and
remote-free publication rehearsal. Measure real density, byte/time/history/reader
bounds and resource use; preserve prior app/source identities, retained releases
and effective observations. Keep the 500/hour profile and existing limits.
If real sources exceed a bound, record/exclude the affected candidate or prepare
a smaller measured cohort instead of silently increasing limits. Prepare a concrete
push/publication package. No recipe migration or installed-host change is implied.

## Discovery counter clarification

Inspection found that the maintained verifier's 200-request bound counts logical
`_get` invocations; urllib may follow rename redirects outside that counter.
[151](151-bound-discovery-redirect-request-accounting.md) records the transport
accounting follow-up. The two identity batches record 200 + 183 logical invocations;
underlying HTTP attempts were not instrumented. Numeric identity/binding evidence
remains valid. The separate fresh collector uses its NoRedirect transport and
reports actual acquisition attempts.

## Answer

Prepared 184 verified catalog-only app additions / 180 distinct numeric sources,
reaching 509 apps / 500 sources locally. Two bounded logical-GET batches record
200 + 183 calls; eight explicit rename checks agree and two ineligible identities
stay excluded. All 193 proposed recipe bindings recheck against Git/current bytes.
Fresh collection makes 500 actual collector requests with 500 successes, zero
failures/unattempted/pending apps. Exact-parent local publication and exact-pin
reader/canonical/reference plus prior identity/release/observation preservation
checks pass. Response bytes total 341,439,272; YAML 63,690,470, largest 1,372,340;
551.56 seconds acquisition / 965.85 seconds complete controller including readback,
728,864 KiB peak RSS under 1 GiB. All existing limits remain unchanged.
All 12 focused regressions pass; [report/receipts](../research/next-500-catalog-expansion.md)
distinguish the prior 159-test result and discovery counter limitation.
[150](150-publish-500-source-cohort.md) is the concrete publication package awaiting
Marek's push call. No source push, remote publication or installed-host change.
Broad 138 remains claimed; 151 records discovery redirect accounting follow-up.
