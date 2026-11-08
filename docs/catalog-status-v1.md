# AM catalog status format 1

Private implementation contract. Resolve status ref once to S and read only at S;
resolve catalog separately to C. Status failure cannot invalidate valid catalog
facts. No document embeds its own enclosing commit. The
[public consistency decision](track/catalog-system/public-contract-decision.md)
owns confirmation lag and last-reported semantics.

Every status document begins with `format: 1`, immutable `schema` pointing to this
file, then `kind`. The exact closed fields/order/types are defined alongside the
catalog in [build.py](../tools/catalog-contract/build.py), generated
[editor schemas](../schemas/catalog/) and the shared shell/browser readers.
Use the [same mapping-only grammar and bounds](catalog-format-v3.md#grammar-and-schemas).

| Path | Kind | Meaning |
| --- | --- | --- |
| `status.yaml` | `status` | Schema-set pin, last reported summary/time, last confirmed publication known to the report, retained summary references and detail coverage. |
| `runs/<id>-<attempt>/summary.yaml` | `summary` | Exact run/attempt and source/policy/recipe/rule/schema inputs, input C state/pin, stage outcomes, counts, limits, measured usage, investigation links. |
| `runs/<id>-<attempt>/sources/<name>.yaml` | `source` | Available final source result, exact numeric identity, input C and optional confirmed output C/timestamps/reason. Missing detail alone proves nothing. |
| `statistics.yaml` | `statistics` | Optional stated measurement time, source-age buckets at exact C, daily reported-attempt aggregates and actual coverage. |

An input catalog uses `input_catalog_state: known` with its exact pin, `absent`
for a verified target-channel bootstrap, or `unknown` when acquisition context is
unavailable; the latter states forbid an invented input pin.

The public tree allowlist includes only these paths. Summary paths must agree with
run/attempt identity and root references; source details require declared retained
detail coverage. Keep at most 64 summaries, complete available detail for the latest
8 reported attempts, and 90 UTC daily aggregate records. Counts bound current-tree
retention, never ordinary source scope. Display actual retained ranges/gaps.

Collection and candidate validation use `ok`, `partial`, `failed`, `unknown`, or
`not_attempted`. Catalog and compatibility publication independently use
`confirmed` plus exact confirmed commit, `conflict`, `failed`, `unknown`, or
`not_attempted`. Other states forbid a confirmed commit. A local candidate is
not publication. An ambiguous write stays unknown. On conflict preserve the newer
catalog and stop publication, with no automatic merge/retry.

Counts are distinct sources: enrolled E, selected Q, attempted A, successful S,
failed F, unknown U, selected-unattempted Q-A, and deferred D (a subset of
unattempted). Known values obey A=S+F+U, Q=A+unattempted, Q<=E, D<=unattempted.
A measurement is `{state: "known", value: ...}` or `{state: "unknown"}`; unavailable
is never zero. App-map coverage is established separately from catalog facts.
Whole requested-scope success requires measured full scope, not just no failures.

Original UTC stage timestamps and monotonic durations remain separate. `metrics`
uses explicit known/unknown values for HTTP attempts, charged/received bytes,
acquisition/command milliseconds, current tree/largest-document bytes, local object
bytes, consistently packed history bytes, remote storage bytes and peak RSS bytes.
A conservative failed-transfer charge is not received bytes. Saved replay has
zero new HTTP attempts; saved response bytes are historical evidence. Unmeasured
remote storage, received bytes and memory remain unknown. Budgets name request,
byte, acquisition-millisecond and document-byte configured allowances.

Freshness buckets are disjoint <24h, 24–<48h, >=48h, no successful observation,
and unknown, evaluated at a stated C/time. They describe successful source scopes,
not the freshness of every retained release. Daily records describe reported
attempts only, with first/last original report times. `unknown_source_count_attempts`
counts reports with unavailable source totals; success/failure sums cover the
remaining known reports. Earlier retained summaries backfill the first aggregate
when no prior catalog context was available. Do not interpolate missing
attempts/days or call absent days zero. Git history is separate from tree retention.

Only closed safe reason codes are allowed: transport, authentication, quota,
request/byte/time budget, source validation, document overflow, candidate validation,
parent conflict, publication transport, internal or unknown. No exception strings,
credentials, environment dumps, raw headers or local paths belong in public YAML.

Each summary links to its actual Actions run and recent collection workflow runs.
These supplement public plain-language outcomes; Actions may require sign-in.
No public start record, running/idle claim, guaranteed final report, retry queue or
missing-run reconciliation exists. Attempt finalization on normal failures;
interruption or reporting failure may leave the previous timestamped “last reported
run”. Do not imply it describes the latest attempt. A newer C may precede status
confirmation; label that lag without splicing facts from different pins.

Ticket 12 implements explicit publication and best-effort finalization, including
64/8/90 retention and bounded untrusted artifact validation. The status channel
remains disabled in the prepared workflow until separately authorized activation.
Status current-tree validation allows 100,000 files (separately from the catalog
allowance), so 8 complete 5,000-source detail sets are not truncated by a
20,000-file catalog limit. Capacity qualification remains ticket 14 work.
