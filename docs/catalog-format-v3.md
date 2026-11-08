# AM catalog format 3

Private implementation contract; the deployed format-2 channel remains supported.
Resolve the catalog ref once to a full SHA-1 commit C. Read every required document
at C. Neither a descriptor nor a local candidate establishes remote publication.
See [revision consistency](track/catalog-system/public-contract-decision.md) and
[status format 1](catalog-status-v1.md). This contract adds no installed runtime.

## Grammar and schemas

Every document starts with `format: 3`, an immutable `schema` URL to this document,
then `kind`. Recognize kinds/versions locally; never fetch a schema as authority
for untrusted bytes. The maintained [definitions](../tools/catalog-contract/build.py)
fix every allowed field, its canonical order, type and required/optional status.
The generated [closed editor schemas](../schemas/catalog/) use draft 2020-12.
The repository's editor associations target candidate channels explicitly, avoiding
accidental application of v3 schemas to format 2. A consumer can use these YAML
contracts from Lua without adopting a required library or Python/jq runtime.

The grammar is mappings only, two ASCII spaces per level, LF-terminated nonempty
lines, no blank lines, trailing spaces, raw controls, comments, lists, nulls,
anchors, tags or general YAML features. Empty mappings use `{}`. Fixed field names
are bare; every dynamic table key is double quoted. Table keys are unique and
ordered numerically for release/asset IDs, by ASCII name elsewhere. IDs and unsigned
integers are canonical exact decimal values in 0–9223372036854775807; identities
are positive. A float or rounded JavaScript Number cannot represent these facts.

Strings are double quoted UTF-8, with only `\"`, `\\`, `\n`, `\r`, `\t`, `\N`,
`\L` and `\P` escapes. The final three encode NEL, line separator and paragraph
separator without YAML folding. Unknown escapes, including general `\u`, fail.
Timestamps are real UTC seconds from 1970, `YYYY-MM-DDTHH:MM:SSZ`.
The default document allowance is 2 MiB, line allowance 65,536 bytes, depth 12,
complete candidate allowance 1 GiB and 20,000 documents. These are implementation
safeguards awaiting the ticket-14 capacity measurements, not qualified operating
ceilings. Never trim a source's assets or additional releases to fit.

Structural editor schemas cannot enforce original-byte grammar/order, duplicate
keys already lost by a YAML loader, exact arithmetic in a rounding editor, calendar
validity, URL reconstruction, observation relationships, tag uniqueness or snapshot
identity. Maintained shell/browser domain validation and whole-tree checks remain
required. Shared fixtures deliberately include structurally valid semantic failures.

## Documents at C

| Path | Kind | Meaning |
| --- | --- | --- |
| `catalog.yaml` | `catalog` | Exact `inputs` revisions for source, policy, recipes, classification rules and schema set; producer run ID/attempt; fixed `32-plus-stable-exact-tag-v1` retention rule. No enclosing commit. |
| `apps.yaml` | `apps` | AM app names directly to `repositories/<name>.yaml`; stable/nightly remain separate keys. |
| `repositories/<name>.yaml` | `repository` | Numeric source ID, current verified readable GitHub name, successful scope completion, shared/individual observations and retained release facts. |
| `provenance/<name>.yaml` | `provenance` | Architecture-specific recipe bindings for exactly the app identities pointing to `repositories/<name>.yaml`. Required for each referenced source, including unknown classifications. |

Only these paths are allowed; the former private global `provenance.yaml` layout
is no longer accepted. Derive the provenance path by replacing the validated
`repositories/` prefix with `provenance/`, retaining the same stable source label.
No second index or moving lookup is needed. Load only that source's provenance at
C when opening an app. Each partition's app keys must exactly match the identities
pointing to its source, including distinct stable/nightly identities. Missing,
misplaced, cross-source or extra provenance documents/bindings refuse a candidate.
The `provenance` kind and architecture/evidence field schemas are unchanged.

Every app must reference an existing source; each
numeric source appears once, independently of app aliases. Names match
`[a-z0-9][a-z0-9_.+-]*`, at most 64 ASCII bytes. No slash, percent escape or
external URL is a source path. The reviewed [registry](../tools/catalog-collector/source-names.json)
allocates stable labels by numeric identity, seeded from the existing enrollment.
New allocations need a reviewed registry edit. Retired labels never become active
again. Verify numeric identity before updating an upstream owner/name; do not
rename source files on an upstream rename or infer enrollment from a new name.

A repository document describes successful facts only. Failed or unattempted
sources keep the exact prior document; a new failed source has no app-map entry.
Failures belong to run evidence/status, so a failed refresh never changes retained
observation times. Scope currently names one page of 100 and whether its response
ended pagination, without claiming complete upstream history or asset verification.

`collected_at` is successful requested-scope completion, not publication time.
A release's effective observation is its `observed_at`, otherwise the source's
shared `observed_at`. Overrides equal to the shared value are noncanonical.
Neither may exceed successful source completion. Before changing a default,
materialize old effective times for untouched retained records.

Each release has exact tag, URL, prerelease flag and all its retained assets.
Title, created/published/updated timestamps and source archive URLs are optional
when upstream has no value. At least publication or creation time is required.
A successful scope replaces older incarnations of the same exact tag before
retention, even with a different release ID. Two IDs for one tag in a single
scope invalidate that source. Retain the newest 32 by publication, falling back
to creation, then numeric ID descending; also the newest non-prerelease when
none of those 32 is stable. Keep all assets, at most 33 releases. Failed validation,
missing timestamps or exceptional document overflow preserve the prior source.
Earlier Git commits preserve metadata, without guaranteeing binary availability.

## Lossless compact asset facts

An asset has name, size, exactly one `url` or `url_suffix`, optional `media_type`
and optional original digest. A release may define `download_base`, ending in `/`.
A suffix requires a base; reconstruct by literal concatenation, including an empty
suffix. Never URL-join, decode, interpolate tags, normalize or re-encode. Full HTTPS
URLs remain available for exceptional hosts/paths; source archive URLs stay full.
Choose a prefix shared by at least two URLs only when it reduces canonical encoded
bytes including field/base overhead. Maximize savings, then prefix byte length,
then ASCII byte order. No positive savings means no base.

Omitted media type means exactly `application/octet-stream`; `""` preserves the
actual empty upstream string. Only unescaped `zip` aliases `application/zip`.
A value beginning with `=` is literal: remove **exactly one** leading `=` and return
the remainder without alias lookup or another decoding pass. Thus `=raw` → `raw`,
`=zip` → `zip`, and `==raw` → `=raw`. Even `=` represents the empty literal string;
the canonical writer keeps the existing `""` representation for empty upstream data.

The writer omits octet-stream, emits `zip` for upstream `application/zip`, keeps
empty strings and ordinary full media types unchanged, and prefixes `=` for other
values, including every original value already beginning with `=`. No case or
parameter normalization occurs. Unescaped unknown bare aliases still fail.
Missing upstream content type still fails normalization; omission never invents it.
Readers expose the decoded `media_type`; `content_type` remains an API alias.
The literal escape stays in the existing compact field; there is no additional
`media_type_literal` field.

## Recipe evidence

Each architecture binding has numeric source identity, `availability` (`present`,
`absent`, `unknown`) and `classification` (`shared`, `template`, `custom`, `unknown`).
Present recipes bind repository, exact commit, architecture/app path and Git blob.
Absent is allowed only after checking that exact recipe tree; transport failure
means unknown. Catalog-only enrollment does not imply absence or lack of support.

Known labels require evidence evaluation time, recipe SHA-256, exact rules revision
and pinned dependencies. Shared uses whole-wrapper literal recognition, including
the complete executable tail, with the full shared modules/policy tree binding.
Template requires a whole pinned-template `instance`, not `parameter_review` or
nonrecognition; template and generator hashes are dependencies. Custom requires an
explicit reviewed record matching exact recipe/rules/dependencies and a description.
Otherwise show Not yet classified. Reuse identical input evidence without expiry;
changed inputs require rechecking or unknown. Processing never executes recipes.

Review links use the recipe's own commit/path:
`https://github.com/<repository>/blob/<recipe-commit>/<recipe-path>`.
Custom recipes require a prominent review link. These labels establish neither
binary authenticity nor installation selection/support or installed-updater state.
Do not equate unknown with custom, absent, unsupported or false.

## Reader and collection APIs

`sh modules/catalog-contract-reader.am validate FILE` validates the entire document.
`get FILE KEY...`, `apps FILE`, `releases FILE`, `assets FILE RELEASE` query it.
`get` expands effective observations, full asset URLs and media types. Exit 0 means
valid/result present, 3 means absent, 2 means refusal/error. Output is privately
spooled until full validation succeeds. The format-2 reader is unchanged.

The browser [reader](../tools/catalog-contract/reader.mjs) exports `parseDocument`,
`releaseFacts` and `validateSnapshot`; integer values are BigInts, and query facts
expand the same compact fields. Callers must keep reads/caches bound to C. Real
DOM/fetch/accessibility qualification belongs to tickets 13–14.

`host_catalog.py collect` acquires once and writes independent candidates from each
format's own exact parent. Format 2 retains its historical merge and numeric paths;
it is never projected from pruned v3 records. `validate` is credential/network free
and optionally checks expected input pins. Explicit `publish` validates transferred input/run/parent/hash bindings, confirms
exact-parent remote outcomes and independently attempts final status publication.
The prepared workflow now uses these explicit operations, with target channels
disabled until the separately authorized rollout. The legacy local invocation
remains compatible for existing maintenance callers.
