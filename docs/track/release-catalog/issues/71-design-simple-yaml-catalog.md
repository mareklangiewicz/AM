# Design a simple YAML catalog of release facts

Type: research
Status: open
Triage: ready-for-agent

Interview Marek to settle normalized catalog facts, a strict readable YAML subset, client selection responsibilities, and collection coverage. Implementation requires confirmation of shared understanding at the end of the grilling interview.

## Decisions and evidence

See [ongoing design interview](../research/yaml-format-design.md) and [facts/selection ADR](../../../adr/0001-catalog-facts-and-client-selection.md).

Q21 authorizes a bounded read-only measurement of release-history request cost, response bytes, provisional normalized YAML size, and duration. No workflow dispatch, production publication, repin, or push is authorized by this experiment. The separate natural daily run acceptance remains outstanding.

## Remaining

- Collection revised to configurable scopes and retained merges; scheduled default is all sources, one page of 100. Finalize independent safety and retained-size budgets.
- Policy interview decisions settled; see [consolidated review](../research/yaml-catalog-design-review.md). Exact grammar and budgets are the next experiments after confirmation.
- Shared understanding confirmed; schema/reader experiment completed in ticket 72.
- Unicode escape extension accepted; settle production resource strategy and collection ceilings before integration.

## Comments — completed experiment

Marek confirmed the design and authorized the local experiment. [72 resolved](72-prove-yaml-reader-feasibility.md) records its result. Consumer structure validation is feasible without a YAML dependency. The proposed three additional Unicode escapes require a design answer; no production changes or publication occurred.

## Comments — escape extension accepted

Marek accepted \N, \L and \P. The schema draft and findings now record acceptance. The interview no longer awaits that decision; remaining work concerns measured collection ceilings and reader memory strategy before production integration.

## Comments — resource follow-up underway

[73 resolved](73-bound-yaml-reader-memory.md): record-scoped validation and private
output spooling preserve the contract, but portable constant RSS is not established. A [second random sample plus targeted histories](../research/yaml-history-outliers-20261103/findings.md)
found active sources advertising 58 and 63 release pages; they were not fully
acquired. A [concrete resource proposal](../research/yaml-resource-strategy.md)
records candidate ceilings and the remaining exact-format, runner and scheduling
gates. Candidate numbers are not accepted production budgets. No deployment,
remote mutation, natural-run acceptance or installed-host delivery is implied.

## Current design revision — retained observations

Marek's [explicit revision](../research/yaml-retention-revision.md) supersedes
mandatory full-history collection and replacement-only windows. Per-release
observed_at controls installation freshness; successful limited collections merge
fetched records without touching unfetched facts/times. Repository attempt and
last-success metadata record scope separately. [74 resolved](74-revise-scoped-retained-catalog.md)
updates the schema and offline experiments. The reconciliation policy is an
explicit all-only local proposal, defaulting to retention. Resource ceilings,
retained-growth tests and production integration remain open; no remote mutation.

## November 4 — offline acquisition and retained growth

[75 resolved](75-bound-offline-response-normalization.md) adds bounded local JSON
fixture acquisition/normalization. [76](76-measure-retained-growth-and-staging.md)
measures repeated retention, near-cap staging, reader/spool costs and selected
freshness. [Findings](../research/yaml-retained-growth.md) keep the 16 MiB trial
ceiling provisional: BusyBox hits a 55-second CPU allowance on a 16.67 MB revised
fixture. Hard collector/runtime/staging limits and actual default-run capacity
remain open; production integration is not authorized by these experiments.

## November 4 — shared observation default agreed

[77 resolved](77-share-observation-default-and-measure-history.md): shared default
plus differing overrides replaces required physical per-release timestamps.
Effective observations and freshness are unchanged; failures preserve the prior
default and observations. Paired synthetic Git histories measure 3.71–43.31%
packed-object-plus-index savings. The schema/ADR and reader prototype are revised;
production and operational budget approval remain separate.

## November 4 — hard worker follow-up

[78 resolved](78-enforce-offline-worker-limits.md) adds opt-in offline worker
supervision with external elapsed enforcement, address-space/per-file limits and
private-result quarantine. [Findings](../research/yaml-worker-limits.md) record
45 passing executions across three awk tools and retained-state refusal checks.
Aggregate temporary storage, parent staging and reader budgets remain unresolved;
trial limits are unapproved and no live collection or integration is implied.

## November 4 — aggregate managed staging follow-up

[79 resolved](79-bound-offline-aggregate-staging.md) adds aggregate logical-byte
reservations and bounded input snapshots, retaining candidate charges across
sources. The file-oriented API avoids parent input/result JSON decoding.
[Findings](../research/yaml-staging-limits.md) record 48 passing staging executions
and 45 existing worker executions on three awk tools. These are trusted managed
files, not filesystem quotas; real transport/publication staging and parent elapsed
bounds remain unproven. Reader budgets and separately authorized live capacity
remain open. No production integration or remote operations occurred.

## November 4 — reader budget follow-up

[80 resolved](80-bound-and-measure-shared-default-reader.md) adds output-byte
accounting and distinct scalar projection bounds. Offline supervision reserves
input, spool, copied output, bounded diagnostics and receipt; refusals expose no
candidate. [Shared-default measurements](../research/yaml-reader-budgets.md):
15 full-hash successes and six deliberate refusals. BusyBox's 56.4 s on a 16.31 MB
retained fixture leaves little margin under the 60 s trial; no portable ceiling is
accepted. An initial GNU awk status-2 attempt remains unexplained; bounded
diagnostics now preserve recurrences. Portable consumer hard deadlines, accepted
operating budgets, real transport/publication integration and separately authorized
live capacity remain open. No production changes or remote operations occurred.

## November 4 — shell-only parser deadlines

[81 resolved](81-test-shell-reader-deadlines.md) exercises an opt-in parser-only
watchdog using local timeout utilities. [Findings](../research/yaml-shell-deadlines.md):
180 executions across two shells, two timers and three awk tools pass. Both raw
timeout probes leave shell descendants alive, so no whole-shell/tree contract is
claimed. BusyBox applet preference bypassed a bare PATH-selected awk; explicit
external tool paths fix that execution seam. The timeout dependency and broader
platform support remain unaccepted. Whole-query/output deadlines, acceptable
memory/performance budgets, real transport/publication integration and separately
authorized live capacity remain open; no production or remote operations.

## November 4 — whole-query/output boundary

[82 resolved](82-probe-whole-query-deadline-boundaries.md): six focused offline
cases demonstrate complete reader-shell supervision, partial private-output
quarantine and BusyBox cat backpressure termination. [Findings](../research/yaml-whole-query-deadlines.md)
distinguish private-file acceptance from irreversible streaming delivery. Parent
snapshot acquisition remains outside the existing timer; consumer platforms,
operating budgets and integration remain open. No production or remote changes.

## November 4 — simplicity takes priority

Marek directs simpler consumers over excessive defensive machinery.
[83 resolved](83-simplify-consumer-reader.md): remove the optional parser timer;
keep full validation, byte caps and private spooling. Nine direct measurements
and 45 checks pass. [Recommendation](../research/yaml-simple-consumer.md) proposes
2 MiB source/output caps with mawk/GNU awk preferred for larger snapshots and
BusyBox compatibility retained. This is not an accepted production cap. Further
whole-query/snapshot supervision is optional research, superseding earlier notes
that framed those experiments as necessary next gates. Real integration and
collection/publication requirements remain; no live or remote action occurred.

## November 4 — simple offline consumer exercised

[84 resolved](84-exercise-simple-offline-consumer.md): a short shell app-to-release
example passes 18 cases across three awk tools, preserving effective observations
and rejecting malformed/mismatched files. [Findings](../research/yaml-simple-browse.md)
record its three reader calls and repeated repository parse explicitly. User
approved source pushes; no publication, pin, dispatch or installed change occurred.
Next substantive work is an offline format-2 writer/publication candidate reusing
existing mechanisms, not another defensive consumer layer.

## November 4 — offline writer/publication candidate

[85 resolved](85-prepare-offline-yaml-publication.md): canonical emitter extraction
and a small local Git publisher connect retained merges to the simple consumer.
[Findings](../research/yaml-offline-publication.md) record three-tool pinned reads,
failed-source preservation and unchanged refs on candidate refusal. Reconstructing
prior state from pinned YAML and feeding saved responses through the complete loop
is next; no actual format switch or new consumer machinery is implied.

## November 4 — offline loop closed

[86 resolved](86-close-offline-yaml-refresh-loop.md): pinned YAML loading, saved
JSON normalization, retained merge and local publication now form one offline
path. [Findings](../research/yaml-offline-refresh.md) record preserved unselected
bytes, successful retries and rollback after a later-page failure on three awk
tools. Next is realistic saved-response replay and a small production adapter
review, without adding defensive consumer machinery. No operational format switch.
