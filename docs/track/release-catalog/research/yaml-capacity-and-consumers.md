# YAML capacity and consumer preparation — November 4, 2026

[95](../issues/95-measure-yaml-capacity-and-prepare-consumers.md), source candidate
`a295d7a2d`. Measurements use maintained runtime baseline `ff2dc1499`; added
harnesses and full results are in the candidate. Exact profile SHA256 remains
`d464ee0c14d8712ef625d47308d8faf47f5faf459fc565b926d2952d98a73e7b`.

## Local capacity evidence

| Case | Result | Local wall | Largest-process RSS |
| --- | --- | ---: | ---: |
| Synthetic 49 × 100 releases × 8 assets | All sources staged/verified; 13,297,011 YAML bytes | 287.855 s | 103,884 KiB |
| Synthetic one source × 100 × 80 assets | collection_limit; failed metadata only | 1.764 s | 48,528 KiB |
| Synthetic retention, 100 new releases/round | Round eight refuses; prior 700 preserved | 20.810 s | 89,324 KiB |
| Saved real list responses, 41 sources | 914 releases / 14,242 assets validate | 70.480 s | 123,412 KiB |

The all-source synthetic case uses real static enrollment (255 names/49 identities)
but invented release/asset facts. 49 requests, 12,525,709 response bytes, 4,900
releases / 39,200 assets; largest YAML 305,994 bytes, receipt 96,051 bytes. The
maintained collect_stage path plus an extra read_staged pass are measured. The
mock clock advances one second per request (49 total), not real API latency; wall
includes validation outside the 300-second transport deadline and does not include
a full publisher job. This is not live-default or hosted-runner capacity evidence.

Dense scope uses an explicit schema-2 one-source manifest. A 2,434,589-byte body
fits the response cap, but normalized YAML exceeds 2 MiB, producing honest failed
metadata without observations/releases. The proposed job would fail its all-ok gate.
No dense all-source success is claimed. Growth reaches 700 retained releases /
1,866,839 bytes, then refuses the next 100 without eviction or partial merge.
The 1,866,872-byte failed document preserves schema, all facts/observations and
last success. Synthetic arrival rate is not a real daily-growth estimate.

Saved replay checks original body lengths/hashes and receipt times: 27,821,797 raw
bytes, 5,261,143 YAML bytes, largest file 1,251,974 bytes. Forty responses are page
size 30, only one is size 100; three latest endpoints are excluded. It validates
normalization/canonical trees, not fresh acquisition or full staging context.
These match earlier recorded replay quantities on maintained source.

Measurements are serial. GNU time aggregates child CPU and reports one process's
maximum RSS, not aggregate peak memory. Harness-only per-process address-space
and CPU limits are not a new runtime worker/watchdog or aggregate deadline.
The profile remains a trial: this evidence supports ordinary-shape feasibility and
shows explicit density/retention refusal, not a decision to raise caps or evict.
A separately authorized bounded real full-default measurement is still needed.

## Consumer migration preparation

Static inventory covers 475 enrolled paths / 255 names / 49 repositories and
excludes 987 other marked paths. 119 paths are AppImages and 356 executables.
Six use generic URL filtering; 469 use custom shell selectors (113 AppImage,
356 am-utils). All executable paths share the am-utils release source. Nine paths
use /latest: polymc, supertuxkart, vivaldi-stable and vivaldi-snapshot across their
recorded architectures. Their client release rules require explicit decisions;
format 2 does not acquire GitHub latest.

Current raw-JSON handoff is catalog.am → appimage.am → generic/custom selector.
Install-module bindings, URL version identity, REFRESH_ALWAYS, failure-before-
mutation and command-private acquisition reuse must be preserved deliberately.
Do not manufacture raw API JSON from YAML to keep old selectors running.

`yaml_selection.py` is an offline Python policy reference, not an installed client
or proposed Python/PyYAML host prerequisite. It loads a fully validated exact-pin
local snapshot, applies an explicit published-desc/stable/suffix/name-substring
policy with documented tie rules, then checks the selected record's effective
observation time. These illustrative policies do not automatically translate
legacy URL BRE/ERE/custom shell intent or become accepted per-app rules.

Recent collection/publication cannot rescue stale selected facts; a fresher but
lower-priority record is not silently substituted. Failed recent collection does
not invalidate an otherwise fresh retained record. Exactly 48 hours remains
fresh, future observations refuse. A proposed exact commit/repository/release/
asset/observed_at acceptance object scopes a stale waiver inside this rehearsal;
the operational stale interface still needs migration review.

Seven selection checks pass (structure/digest optionality; stable/fall-through;
name and large-ID ties; exact stale waiver/no fresher substitution; freshness
boundary/future/failed collection; pinned read across changed tip; invalid policy/
missing app/assets). Five existing inactive-workflow checks also pass (12 total).
Compilation and staged whitespace checks pass. Inventory JSON was compacted to
one recipe per line with semantic equality verified against the original output.

[Capacity design](https://github.com/mareklangiewicz/AM/blob/a295d7a2d/docs/track/release-catalog/design/yaml-capacity.md),
[consumer map and sequence](https://github.com/mareklangiewicz/AM/blob/a295d7a2d/docs/track/release-catalog/design/yaml-consumer-migration.md).
Next preparation is a small named recipe cohort with explicit policies and saved-
fixture comparisons, then portable shell integration/lifecycle tests. Capacity/
policy acceptance, maintainer promotion, format transition/rollback and activation
remain separate. No active workflow, module, recipe, manager, live API/catalog
publication, repin, installed consumer or yadm pointer changed.
