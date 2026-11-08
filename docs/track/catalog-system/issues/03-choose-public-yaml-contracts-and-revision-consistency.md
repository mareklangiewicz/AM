# Choose public YAML contracts and revision consistency

Type: grilling
Label: wayfinder:grilling
Status: resolved
Assignee: codex-contracts
Blocked by: 01

## Question

What versioned document boundaries and revision relationships provide one coherent
public YAML interface while preserving existing catalog readers?

Decide catalog versus operational-summary placement, schema/version negotiation,
grammar/domain-validator separation, unknown/missing/refused data, snapshot
resolution, and source/recipe/policy/run revision bindings. Existing browser reads
remain pinned and lazy unless explicitly reopened through evidence.
Handle the whitelist that currently accepts only apps.yaml and repositories/*.yaml.

Specify how the latest failed attempt is discoverable while the last good catalog
stays unchanged, including unavailable summaries and publication races. A file
cannot embed its enclosing commit hash. Define cross-revision consistency without
silently mixing unrelated facts, and distinguish all four time concepts.

Compare bounded alternatives with Marek. Own document/consistency contracts here;
[Choose truthful health summaries and bounded statistics](08-choose-truthful-health-summaries-and-bounded-statistics.md)
owns metric meanings and summary contents. Produce linked contract sketches
and compatibility requirements, not production schemas or reader implementation.

## Comments

### Current amendment — final-summary-only reporting, November 7, 2026

Marek replaced all public-start requirements with best-effort final summaries for
every normal outcome, including collection, validation and publication failures.
Abrupt termination or summary publication failure may leave no report. The
previous report retains its original timestamp and the label “last reported run”,
never a latest-attempt assertion. Include the specific Actions run link and recent
collection runs; Actions may require sign-in, while the public summary must not.
The linked contract sketch is updated. The earlier start/finish amendment below
is superseded history; no registration or guaranteed report-delivery service.

### Recovery simplification amendment — November 7, 2026

Marek accepted redoing unfinished work after runner loss and public health updates
only at start/finish. The linked contract sketch now removes custom run-order
allocation, continuous progress and cross-run recovery infrastructure as
requirements. A start without a finish is explicitly incomplete evidence. Exact
pinning, last-good catalog preservation and independent health reporting remain.
Minimal ordering/concurrency and failed-start-update handling still need simple
questions in the remaining decisions; no new machinery is selected here.

### Accepted app-to-file references — November 7, 2026

Marek accepted using upstream-aligned AM app names as keys and explicit,
human-readable repository YAML paths as values in the next catalog contract:

```yaml
apps:
  "nvim": "repositories/nvim.yaml"
  "nvim-nightly": "repositories/nvim.yaml"
```

The referenced `repositories/nvim.yaml` retains upstream identity metadata:

```yaml
repository_id: 16408992
repository: "neovim/neovim"
```

The two app names directly reference one shared source document; they are not
aliases for each other's installation/channel policy. Every app-map value has
the same meaning: a file path, not a mixture of numeric IDs and app aliases.
Readers follow the explicit path rather than constructing a numeric filename or
resolving an alias chain. Keep numeric GitHub IDs for source identity verification
and deduplication; readable filenames do not replace those checks.

Paths are relative to the pinned catalog root and restricted to
`repositories/<name>.yaml`. Validate that each reference exists in that snapshot,
that each source name is unique, and that referenced documents have consistent
numeric/source identities. Reject absolute paths, traversal and external URLs.
Several app names may intentionally refer to the same document. Require one
canonical document per numeric source, rather than duplicate release data.

Still decide the precise source-name grammar/allocation and collision policy,
app/source rename and compatibility behavior, and versioned reader/writer
migration. A readable source name need not change automatically when a GitHub
repository is renamed. Preserve the original numeric identity through renames;
do not silently rebind an existing source to a different repository.

The examples retain the currently supported quoting convention. Ordinary YAML's
ability to omit quotes is not acceptance of a grammar change. This is accepted
target direction, not a change to deployed format 2, published files or readers.
The broader contract/consistency question remains open.

### Side-conversation requirements and proposals — November 7, 2026

Marek requires avoiding repeated download URL prefixes in the next representation.
Choose a lossless common-base/suffix representation with an exact full-URL escape
hatch; do not assume upstream URLs can always be reconstructed from tag and asset
name. Specify escaping, resolution and exceptions explicitly before implementation.

Marek proposes omitting `application/octet-stream` as the defined default and
using compact aliases such as `zip` for `application/zip`, potentially replacing
`content_type` with a shorter field. This direction needs a precise contract:
choose the field name (`type` versus the less ambiguous `media_type`), exact alias
table, full-MIME fallback and representation of an explicitly empty upstream value.
Distinguish upstream media type from inferred package format: a `.zip` filename
does not mean upstream reported `application/zip`. No alias/default design or field
name was finally selected in the side conversation.

Marek also requests normal machine-readable schemas for editor assistance, beyond
the existing Markdown specification and executable validators. The restricted
format remains valid YAML; JSON Schema can describe document structure and provide
completion, hover documentation and diagnostics through tools such as Neovim's
YAML language server. Define schemas for each public document kind (app map,
repository/release/assets, and future summary/health documents), with descriptions,
examples and documented defaults. Choose schema version/identity and test that
schemas, writer and strict readers agree on accepted document structure.

Retain strict validation for canonical grammar/order, exact integer handling,
cross-document identities and observation semantics that ordinary structural
schemas cannot fully enforce. The existing `schema` field points to immutable
Markdown documentation, not an editor-recognized JSON Schema association.
Editor `yaml.schemas` associations can initially work without changing data;
the usual schema modeline comment conflicts with the current no-comments grammar,
and adding a `$schema` field would also require a deliberate contract change.
Do not silently alter the current schema pointer's meaning or relax validation.

Editor integration reference:
[YAML language server documentation](https://github.com/redhat-developer/yaml-language-server#readme).
These are inputs to this still-open decision, not a format migration or authorization
to change readers, publication or installed consumers.

## Answer — November 7, 2026

Marek explicitly delegated this decision with “you decide” after being told the
next question was public YAML contracts and revision consistency. This is direct
decision authority for this ticket, replacing its normal interview requirement;
it is not fabricated human feedback or authorization for production changes.

Selected [Public YAML contracts and revision consistency](../public-contract-decision.md)
as the target design. It defines separate exact-pinned catalog and operational
status channels, format-3 catalog document boundaries, source/recipe/policy pins,
publication confirmation and lag/race behavior, stable readable source naming,
lossless asset URL prefixes/full-URL escape hatch, `media_type` defaults/aliases,
editor schemas, strict per-kind validation and format-2 compatibility gates.

Health can report a failed run independently of last-good release publication.
Status confirmation is explicitly allowed to lag catalog publication; the UI
labels mismatched contexts instead of silently combining unrelated revisions.
The companion contract sketch owns the detailed resolution and examples.

Metric meanings, run registration/recovery, recipe evidence predicates, storage
retention and rollout timing stay with their existing owning decisions. No new
ticket is required: the existing questions cover the remaining work. Production
schemas and exact field-order tables follow those decisions; this resolution
fixes the contract design, not unimplemented acceptance evidence.

The deployed format-2 specification/readers/files remain unchanged. No external
research or remote-state claim was needed for these design choices. Documentation
link/dependency and whitespace checks accompany this planning change; no runtime
tests, remote refs, deployment, installed changes or push are part of it.

## Implementation conflict for decision — November 8, 2026

Ticket 12's saved-data rehearsal found the original bare content-type value `raw`
on 6,691 assets in 10 sources. The accepted rule that unknown bare aliases refuse
cannot represent these facts losslessly. See [inspection evidence](../mime-conflict-12.json)
and [ticket 12 progress](12-implement-incremental-publication-and-final-health.md#progress--november-8-2026).
Marek has been asked to choose an explicit `media_type_literal` escape or retaining
the current refusal policy. No wire-rule amendment has been accepted or applied.

## Accepted literal escape — November 8, 2026

Marek explicitly chose a leading `=` in the existing compact `media_type` field:
`=raw` → `raw`, `=zip` → `zip`, `==raw` → `=raw`. Remove exactly one leading `=`
and return the literal remainder without alias lookup. Existing unescaped alias,
full media-type, omission and empty-string semantics remain. Writers escape bare
literal strings and every upstream value already starting with `=`. Unknown
unescaped aliases still refuse. This supersedes the pending `media_type_literal`
proposal above; no new field is introduced. Update the executable contract,
schemas, shell/browser queries and lossless round-trip fixtures, then resume
saved-catalog rehearsal in ticket 12. This is local implementation authorization,
not publication or deployment authorization.
