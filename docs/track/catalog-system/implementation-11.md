# Contracts, readers and collection interface — local acceptance

November 8, 2026. Implements [ticket 11](issues/11-implement-contracts-readers-and-collection-interface.md)
under the accepted local-only implementation scope. Source implementation starts
at `4144d5b53012262f94b7e06094b473c8b09ef6fe`; subsequent acceptance changes add
schema annotations/examples and stricter 33-record validation. No remote operation
or installed-host delivery was performed.

## Result

- Explicit [format-3](../../catalog-format-v3.md) and
  [status-1](../../catalog-status-v1.md) document contracts, canonical field order,
  closed generated editor schemas with examples/default annotations, a browser
  validator/query API and a shell/awk validator/query API. Grammar and domain
  schema tables are separate; unknown kinds, fields, versions and retention rules
  refuse locally. The format-2 reader/whitelist remain unchanged.
- One maintained `host_catalog.py collect|validate|publish` command surface.
  Collection writes inert candidate directories/report only; validation needs no
  credentials/network. `publish` explicitly refuses until ticket 12 supplies the
  publisher/finalizer. The deployed legacy invocation remains supported until that
  workflow migrates in ticket 12.
- One acquisition/normalization feeds each format's own exact-parent merge.
  Format 3 applies exact-tag replacement, 32-plus-stable, timestamp fallback and
  source-isolated overflow/validation refusal. Format 2 keeps its old retention
  semantics and numeric references. Bootstrap v3 starts without prior v3 facts;
  it does not translate the v2 retained set into a new retention-policy snapshot.
- Reviewed stable labels for the existing 500 numeric sources, without enrollment
  changes. Parent/name and cross-document source/app/provenance identity checks
  reject rebinding. Independently pinned inputs must match actual maintained bytes.
- Positive whole-wrapper/template/reviewed-custom predicates, conservative unknown,
  architecture-specific recipe availability and immutable recipe review URLs.
  The complete shared modules tree or pinned template/generator forms dependencies.
  Classification reads Git bytes and executes no source shell or payload.

## Focused checks

| Command/check | Result |
| --- | --- |
| `python3 -B -m unittest discover -s tools/catalog-collector -p test_contracts.py -v` | 9 tests pass; final run 9.986 seconds. Includes 9 positive / 24 negative shared wire fixtures, writer/reader round trips, exact IDs and compact encodings, actual pinned recipe predicates, custom-input changes, dual-parent collection, overflow preservation, input-pin refusal and deterministic generation. |
| `python3 -B -m unittest test_normalization test_retention test_observation_defaults test_batch_collection test_snapshot_canonicality test_yaml_reader -v` from `tools/catalog-collector` | 71 tests pass in 72.281 seconds. Includes repeated imported reader cases; this count is test invocations, not 71 distinct new behaviors. Legacy files/behavior remain unchanged outside the optional normalized-input seam and command dispatch. |
| Shared fixture parity on mawk, gawk, BusyBox awk | All 33 fixtures pass the expected accept/refuse outcome on each implementation. Portable decimal count arithmetic avoids Number rounding. |
| `shellcheck -s sh modules/catalog-contract-reader.am` | Pass. |
| `git diff --check` | Pass. Only the deliberate blank-line-at-EOF negative fixture has a narrowly scoped whitespace attribute. |
| Real subprocess `host_catalog.py collect`, then `validate` for both channels and expected input pins, at source `4144d5b53012262f94b7e06094b473c8b09ef6fe` | Pass without monkeypatching: current 500-source enrollment, selected batch 1, synthetic saved empty response/receipt, 0 HTTP attempts, 2 format-2 documents, 4 format-3 documents, exact receipt preserved and seed publication ref unchanged. Temporary bare repository/candidates cleaned on exit. This is CLI wiring evidence, not real-source collection/coverage qualification. |

The new shared fixture checks include full URLs and literal suffixes (including
empty), exceptional host/query/percent/Unicode bytes, default/empty/alias/full MIME
values, NEL/Unicode separators, IDs beyond 2^53 through int64 max, observation
inheritance, 33-record stable exception, closed versions/fields and malformed
calendar/grammar/evidence/count relationships. Shell queries suppress earlier
output when a later field is invalid; absence remains exit 3, refusal exit 2.

The historical format-2 runtime/e2e evidence is reused for untouched installed
modules and recipes; no broad per-app lifecycle/payload run was repeated.

## Deliberate limits and next boundaries

Editor schemas check structure, not original-byte grammar, canonical ordering,
calendar validity, exact arithmetic in rounding editors, URL reconstruction,
observation/count relationships or whole-snapshot identities. These deliberately
schema-only limits are documented with semantic negative fixtures. JSON Schema
`default` is an annotation, never invented upstream input.

Common retained facts and effective observations/URL/MIME encodings round-trip.
Whole release sets intentionally differ: v3 supersedes reused exact tags and prunes
to 32-plus-stable; v2 retains its historical set. A client can therefore lose an
older v2 selection in v3; this is the accepted retention-policy difference, not a
lossless whole-set/selection-equivalence claim. Broad consumer and saved real-cohort
selection checks remain in ticket 14 before activation.

The new full-snapshot validator does not yet reuse trusted unchanged-blob validation
evidence; ticket 12 owns that mechanism, exact-parent publication, transferred
artifact validation, final reporting and workflow permission separation. Existing
500-source/legacy limits remain operational baselines; provenance/root size,
thousands-of-source processing, Git-history/headroom and refresh qualification
remain ticket 14 work. No new production limit or cadence change is activated.

Node/awk checks establish parser/domain behavior, not DOM/fetch/CORS, keyboard,
mobile, performance or accessibility acceptance. Ticket 13 integrates the main-owned
browser; tickets 14–15 qualify capacity/rollback and prepare the concrete rollout.
No push, acquisition, dispatch, enrollment, installed-host, Pages, remote channel or
yadm pointer operation is included here.
