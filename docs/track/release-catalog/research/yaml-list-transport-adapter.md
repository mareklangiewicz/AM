# One-page YAML list transport adapter — November 4, 2026

[88](../issues/88-prepare-yaml-list-transport-adapter.md), source candidate
`5b1d4919b` on `prep/yaml-offline-publication`.

`tools/catalog-collector/yaml_adapter.py` connects the existing collector to the
shared YAML normalizer, retained merge and validated candidate-tree writer. It
has no CLI or ambient token lookup. The caller supplies transport and opaque
credentials; no operational workflow imports it.

The reviewed 52-endpoint manifest loads offline and endpoint variants coalesce
by numeric repository identity. Every prepared request is an unconditional list
request with explicit page 1 and page size (default 100). No latest-only response
is treated as a list. Explicit source subsets reject unknown/duplicate IDs.
Identity evidence comes from the reviewed manifest, not generated replay aliases.

For successful responses, Link metadata must retain numeric identity, list route
and page size. Duplicate relations/parameters, wrong next/previous pages,
unknown relations and inconsistent last/next links refuse the source. This is a
strict candidate grammar, not a general Link parser. Synthetic explicit-size
links cover the new request shape; no live 100-release paginated response was
acquired to establish upstream framing. A next link on page 1 marks partial
coverage while successfully completing this entry point's one-page scope.

The adapter validates caller-supplied previous state/app references before
transport, preserves response receipt timestamps through retained merges, and
returns a fully validated YAML tree plus source outcomes. It does not publish.
Schema URLs name mareklangiewicz/AM at an explicit 40-character source revision;
tests resolve actual reviewed revision `125a2ff9d`, rather than using an example
owner/hash. The trusted caller must establish which revision is approved.
Unselected state is carried forward; a transport-wide stop leaves unattempted
state unchanged and reports those numeric IDs without inventing attempt times.

Six focused checks pass: real manifest deduplication; successful partial merge,
recorded receipts and unselected preservation; pagination refusal with retained
facts; rate-stop/unattempted preservation; invalid input before transport; and
pagination target/relation consistency. Existing collector checks (17) and
attempt-adapter checks (6) pass. Python compilation and whitespace checks pass.
Tests use fake transport, actual manifest bytes and fixture app names/facts.
The explicit 2 MiB allowance in tests remains a trial input.

Remaining work is concrete: configurable multi-page orchestration with shared
transport budgets; real AM app-map/bootstrap enrollment and pinned prior wiring;
accepted production limits; and reviewed YAML workflow/artifact staging. The
candidate depends on shared components still under catalog-yaml-prototype; it is
not a completed production-format migration. No live request, workflow edit or
dispatch, catalog publication, daily repin, installed change or natural-run
inspection occurred. Source pushes are separately authorized.
