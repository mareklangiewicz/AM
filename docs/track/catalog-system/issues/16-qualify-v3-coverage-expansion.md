# Qualify future v3 coverage expansion

Type: task
Label: implementation:task
Status: claimed
Assignee: codex
Blocked by: 15

## Outcome

After current-scope v3 works, qualify any proposed expansion against the retained
5,000-source / 12-hour refresh / 25% unused allowance / 12-month history targets.
These targets remain unqualified; the direct migration does not accept them.

## Scope

Deferred by Marek's November 9 instruction to prioritize current scope. Reuse
completed v3 tree, incremental, browser and retention evidence from
[ticket 14](14-verify-scale-compatibility-and-rollback.md) and its qualification
document. Measure only affected v3 capacity gaps using actual operating evidence.
No more expanded dual-output qualification, v2 optimization, new rollback system,
automatic enrollment or assumption of new live quotas. Present a concrete
coverage/refresh/storage tradeoff if required, preserving historical snapshots.

This ticket is unclaimed and authorizes no work or enrollment expansion now.

## Scope reopened — November 9, 2026

Marek requested full migration of all apps, then clarified **all GitHub-backed
apps**. This supersedes the deferral above and authorizes implementation toward
complete GitHub source coverage and v3 recipe conversion. Reuse ticket 138's
discovery evidence and the established family-validation/bulk-translation
workflow. Include explicit accounting for ambiguous, unavailable, no-release and
custom recipes; do not count enrollment or declarations as successful collection.
Preserve ordinary installed selections and retain the schedule pin whenever a
subsequent source push is authorized. Other-host adapters and installed-host
changes are outside this scope. Home guidance still requires asking before a
new push.

Further live clarification: make all GitHub-backed coverage consistent as soon
as practical; the 500-source enrollment was temporary. Freshness is not an
optimization target regardless of cost, and the 48-hour selection rule or similar
operating rules may be adjusted if needed. Use one v3 catalog for verified sources,
with quota-bounded acquisition, rather than requiring further freshness/capacity
optimization before coverage can proceed. Do not claim the older 12-hour/annual
capacity targets have thereby been measured.

Marek then explicitly chose to extend v3 for non-release sources. Preserve Git
reference/file observations as their own facts rather than inventing release or
asset IDs. [Local release-backed bulk checkpoint](../github-migration-16.md)
records the initial applied scope and portable identity/recipe evidence.

## Local rollout package — November 9 continuation

Recipe preparation now includes custom, non-release and missed literal SITE
sources, plus explicit refusal for identities that remain unverified. The
[migration report](../github-migration-16.md) owns the counts and portable evidence.
The [rollout package](../github-rollout-16.md) specifies the reviewed contract pin,
schedule transition, bounded acquisition/publication and five-file shared runtime
delivery. Work remains claimed pending Marek's required push approval and actual
publication results; no expanded successful acquisition is implied by enrollment.

## Approved rollout attempt — November 9

Marek approved the prepared package. Source push and schema/schedule pins were
applied, but the initial run failed before acquisition on a retained ArduLoops
repository-name transfer with unchanged numeric ID. The catalog did not advance;
independent status publication recorded the failure. Runtime delivery remains
pending successful publication. The narrowly reviewed transfer correction passes
14 batch tests and replay against the exact public parent. Its source push needs
approval; [rollout outcome and next steps](../github-rollout-16.md) and
[portable result](../github-rollout-result-16.json) record the concrete state.

## Approved retry and installed runtime — November 9

Marek approved the ArduLoops correction push. Source/schedule pin is
`5be202a7376aa9c1349046cb4180e6152602fd41`; run 42715139284 confirmed catalog and
status publication. The five shared runtime modules were delivered with verified
hashes, native catalog validation and actual manager help. The snapshot has 618
sources; 7,695 enrolled sources still lack successful data. This run collected 119
successfully, failed one and deferred 380 of its selected 500.

Wekan's oversized single response ended the batch and would starve later new
sources on each rotation. A local correction now isolates that failure while
preserving per-response/shared bounds and charging; shared-budget exhaustion
still stops. Two-run regression and exact published-metadata replay cover the
failure. Further source push approval and actual rotation results are required;
do not resolve this ticket or claim complete coverage. See the latest
[rollout result and next steps](../github-rollout-16.md) and
[portable success/delivery evidence](../github-rollout-success-16.json).
