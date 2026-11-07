# Choose public YAML contracts and revision consistency

Type: grilling
Label: wayfinder:grilling
Status: open
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
