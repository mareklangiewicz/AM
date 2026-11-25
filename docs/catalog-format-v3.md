# AM catalog format 3

The sole catalog contract. Format 2 is retired: its reader, parser, collector path
and specification were removed (ticket 25); old format-2 commits stay in Git history.
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
accidental application of these schemas to other YAML. A consumer can use these YAML
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
The default document allowance is 2 MiB, ordinary line allowance 65,536 bytes, depth 12,
complete candidate allowance 1 GiB and 20,000 documents. These are implementation
safeguards awaiting the ticket-14 capacity measurements, not qualified operating
ceilings. A repository file's `content` scalar may exceed the ordinary line
allowance within the same 2 MiB document cap; its decoded UTF-8 content is bounded
to 1 MiB. Other fields retain the ordinary line allowance. Never trim a source's
assets, file contents or additional releases to fit.

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
| `repositories/<name>.yaml` | `repository` | Numeric source ID, current verified readable GitHub name, successful scope completion, shared/individual observations, retained release facts and the latest attempt's failure. |
| `provenance/<name>.yaml` | `provenance` | Architecture-specific recipe bindings for exactly the app identities pointing to `repositories/<name>.yaml`. Required for each referenced source, including unknown classifications. |

Only these paths are allowed; the former private global `provenance.yaml` layout
is no longer accepted. Derive the provenance path by replacing the validated
`repositories/` prefix with `provenance/`, retaining the same stable source label.
No second index or moving lookup is needed. Load only that source's provenance at
C when opening an app. Each partition's app keys must exactly match the identities
pointing to its source, including distinct stable/nightly identities. Missing,
misplaced, cross-source or extra provenance documents/bindings refuse a candidate.
The `provenance` kind and architecture/evidence field schemas are unchanged.

Every catalog document's schema URL must bind the descriptor's `inputs.schemas`,
including roots and retained source documents. Collector-only updates retain the
parent's schema pin while its checked-out contract/schema/reader bytes still
match. An explicit `--schemas-revision` transition revalidates retained source
documents under the new contract and changes their schema binding only. Release,
Git and file facts and every observation/collection time remain unchanged for
failed or deferred sources. Incompatible facts refuse the whole candidate.
Mixed-schema snapshots always refuse. The workflow accepts reviewed authority
from `CATALOG_SCHEMA_REVISION`, validates its full commit spelling, fetches that
object in both shallow checkouts, and passes the same revision to collection and
publication. An artifact cannot authorize its own transition. Keep that authority
pin stable on unrelated source/docs changes.

Every app must reference an existing source; each
numeric source appears once, independently of app aliases. Names match
`[a-z0-9][a-z0-9_.+-]*`, at most 64 ASCII bytes. No slash, percent escape or
external URL is a source path. The reviewed [registry](../tools/catalog-collector/source-names.json)
allocates stable labels by numeric identity, seeded from the existing enrollment.
New allocations need a reviewed registry edit. Retired labels never become active
again. Verify numeric identity before updating an upstream owner/name; do not
rename source files on an upstream rename or infer enrollment from a new name.

A repository document holds the facts of successful collections plus, while
the latest attempt failed, `failed_at` (that attempt's time, after
`collected_at`) and `failed_with` (its cause: `not_found`,
`too_large`, `invalid_response` or `transport`; readers still accept
`same_tag_conflict` in older documents, which collection no longer writes). A failure adds or updates only
those two fields, so retained facts and observation times never change; the
next success drops them. A source that never succeeded has a document with only
its identity, the failure fields and `releases: {}`: `collected_at`, `scope` and
`observed_at` are present together or not at all, and the two failure fields
likewise. Run-wide stops (budgets, quota, authentication) record no failure.
Unattempted sources keep the exact prior document. Collection picks the
sources whose latest attempt, success or failure, is oldest. Scope names one
page (100 releases, fewer for named oversized sources) and whether its response
ended pagination, without claiming complete upstream history or asset verification.

`collected_at` is successful requested-scope completion, not publication time.
A release's effective observation is its `observed_at`, otherwise the source's
shared `observed_at`. Overrides equal to the shared value are noncanonical.
Neither may exceed successful source completion. Before changing a default,
materialize old effective times for untouched retained records.

Each release has exact tag, URL, prerelease flag and all its retained assets.
Title, created/published/updated timestamps and source archive URLs are optional
when upstream has no value. At least publication or creation time is required.
Releases are keyed by ID; several IDs may share one tag, in one scope or across
scopes, and none replaces another. A successful scope removes a retained release
it did not return only when it reached the end of the history: GitHub's list is
not strictly ordered by any timestamp, so a partial page proves nothing.
Retain the newest 32 by publication, falling back
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

## Git reference and repository file observations

A source may include `git_scope` and `git_refs` together. Neither fabricates a
release or asset identity. `git_scope.tags` records whether tags were requested;
`tags_history_complete` means the bounded first page ended, and must be false
when tags were not requested. `branches` maps the SHA-256 of each full branch
reference name to that name (up to four branches). `git_refs` is keyed by the
SHA-256 of the UTF-8 full reference name, with unique names and commits expressed
as full 40-character lowercase Git object IDs.

Each reference has `name`, `commit` and `observed_at`. Tags have a zero-based
`position` in the observed API order: positions are unique and contiguous, with
at most 100 tags. Branches may have up to four `files`, keyed by the SHA-256 of
the UTF-8 path. Each file has `path`, exact `content` (at most 1 MiB), Git `blob`
identity and `observed_at`. Absolute/traversing paths refuse. File observations
cannot precede their branch observation or follow successful scope completion.

Acquisition resolves the branch first and reads each file at that exact commit,
verifying its reported size and Git blob hash. Release and additional Git reads
share the same request, byte, time and quota budgets. Any partial source failure
produces no successful acquisition; prior successful facts remain retained.
Git observations have their own times; collecting releases or publishing a new
snapshot does not make old Git observations fresh.

The native `git_facts` projection emits tab-separated quoted reference name,
commit, observation time, tag position and optional file path/blob/content/observation time after
the reference key. `release_facts` emits release metadata even without assets.
`catalog-yaml.am` policies declare asset, release, Git tag, branch or file
selection. File selection validates both branch and file times, refusing a future
file observation even when its branch was observed earlier. Like asset selections, an old
observation warns once and is used. Non-asset selections require an explicit output
such as `--tag`, `--published-at`, `--updated-at`, `--release-url`,
`--release-id`, `--source-tar-url`, `--source-zip-url`, `--git-commit`, `--git-file`
or `--git-snapshot`.
The snapshot output is commit, newline, then exact file content. JuNest consumes
this once for both VERSION and the commit archive URL. Each command pins all
catalog reads to one publication commit. Custom recipes establish a private
command session for multi-step standalone updates too. Source archive URLs remain
release facts, never synthetic assets. `--version-url` orders eligible URLs with
`sort -V` and then age-checks that exact winner against the same facts.
`--urls` lists eligible records without hiding old choices; a URL menu must pass
its selected URL back through `--selected-url ... --url` before download.

## Reader and collection APIs

`sh modules/catalog-contract-reader.am validate FILE` validates the entire document.
`get FILE KEY...`, `apps FILE`, `releases FILE`, `assets FILE RELEASE` query it.
`get` expands effective observations, full asset URLs and media types. Exit 0 means
valid/result present, 3 means absent, 2 means refusal/error. Output is privately
spooled until full validation succeeds.

The browser [reader](../tools/catalog-contract/reader.mjs) exports `parseDocument`,
`releaseFacts` and `validateSnapshot`; integer values are BigInts, and query facts
expand the same compact fields. Callers must keep reads/caches bound to C. Real
DOM/fetch/accessibility qualification belongs to tickets 13–14.

`host_catalog.py collect` acquires once and prepares a format-3 candidate from its
exact parent. `validate` is credential/network free
and optionally checks expected input pins. Explicit `publish` validates transferred input/run/parent/hash bindings, confirms
exact-parent remote outcomes and independently attempts final status publication.
The prepared workflow now uses these explicit operations, with target channels
disabled until the separately authorized rollout. The legacy local invocation
remains compatible for existing maintenance callers.
