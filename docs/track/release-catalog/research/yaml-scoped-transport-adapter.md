# Scoped YAML transport candidate — November 4, 2026

[89](../issues/89-prepare-scoped-yaml-collection.md), candidate `2f9292218`
on `prep/yaml-offline-publication`, extends [88](yaml-list-transport-adapter.md).

`collect_scoped` in `tools/catalog-collector/yaml_adapter.py` schedules numeric
list pages lazily through the existing collector. A caller-supplied page-plan
factory constructs existing transport instances with the reviewed revision and
workflow identity. Each page plan is revalidated and unconditional; next requests
are constructed from numeric identity/page number after Link metadata validates,
rather than following an arbitrary URL. Consumer machinery is unchanged.

Scope is one page by default, a positive finite limit, or `all`. The retained
merge consumes responses lazily, so malformed JSON, duplicate release IDs or
invalid pagination stop the source before another acquisition. Completion at a
finite limit succeeds even when a next link exists; `all` requires EOF. Distinct
page receipt times remain distinct effective release observations. A later
failure preserves all previous release facts, shared defaults/overrides and
last-success metadata. Explicit reconciliation remains all-only and commits only
on whole-scope success, as in the agreed retained model.

Request count and body-byte allowances are explicit caller inputs shared across
sources/pages. A shared monotonic elapsed allowance (at most the existing
300-second batch ceiling) clamps the existing transport's connect, request and
batch deadlines. Body chunks count even when they cross the allowance; the
crossing response is rejected and its iterator closes. This logical accounting
can exceed the configured limit by a received chunk; it is not an exact wire-byte
or filesystem quota. Default source request ceiling is 64, independently of the
shared run ceiling. No budget numbers are accepted as production policy here.
Reader validation and candidate staging are outside the transport elapsed bound;
there is no additional watchdog/process-supervision layer.

An incomplete scope at a run budget fails with collection_limit. A source-local
request ceiling rolls back that source and permits later sources. Transport-wide
quota/auth/protocol stops, shared exhaustion, and two consecutive transfer/server
failures stop further acquisition. A final allowed request that completes scope
succeeds. Unattempted sources remain unchanged and are reported by numeric ID,
without inventing attempt times. Return values are a fully validated candidate
tree and aggregate/source outcomes, with no publication side effect.

Validation: 19 adapter checks (six prior plus 13 new), 21 existing supervised
transport checks, 17 collector checks and six attempt-adapter checks pass.
New coverage includes multi-page EOF/distinct receipts, finite scope, duplicate
membership, malformed later bodies, shared request/byte/time stops, iterator
closure, rate stops, per-source ceilings, invalid options, two-server-failure
stops, success on the final budgeted request, and reconciliation success/rollback.
Python compilation and whitespace checks pass. Transport tests are offline;
no new live pagination framing or full default-run capacity evidence is claimed.

Remaining: real AM app-map and bootstrap enrollment, pinned prior wiring,
accepted production budgets, and reviewed workflow/artifact staging. The module
still shares components under catalog-yaml-prototype. No live request, workflow
edit/dispatch, catalog publication, repin, installed change, natural-run inspection
or yadm pointer operation occurred. Source pushes remain separately authorized.
