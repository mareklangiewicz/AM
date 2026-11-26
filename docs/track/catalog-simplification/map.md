# Simple, understandable catalog

Label: wayfinder:map

## Destination

An agreed simplified catalog: its rules, each one plain sentence plus a one-line
"why", final as the text of the webpage's "How it works"; its layout as a
directory in `main-marek`; its YAML formats and their JSON Schemas. Every code or
format change this needs is listed as an implementation ticket; none is executed
inside this map.

## Notes

Charted November 23, 2026 with Marek. Background, not required reading: the
[catalog-system map](../catalog-system/map.md) (its rules are what this map
simplifies) and the [catalog-pages map](../catalog-pages/map.md) (the webpage).

Test reader: an AM user who has never read the code or docs. A rule that cannot
be said to them in one sentence without glossary terms is simplified or dropped.
When precision and simplicity conflict, the page states the simpler rule; the
precision moves to a linked details section or the YAML, and the simple sentence
must still be true.

Accepted principles (Marek, November 23):

- The catalog records facts and never decides for clients. A changed release or
  artifact under a tag is a fact to record; whether to warn, update silently
  (rolling tags such as nightly) or refuse is the client's decision, for AM in
  its installer/updater and recipe declarations. ADR 0001 states this; ADR 0002's
  same-tag invalidation and replacement contradict it and are open for revision.
- The catalog is a directory in `main-marek`, not orphan branches. If code and
  catalog commits together prove a real problem, a separate repository is a later
  option, not this map's.
- Commit pins only where they have a clear benefit; a needed hash is inherited
  down the YAML structure, like `observed_at` defaults, not repeated.
- Schemas are real JSON Schema, authored as YAML, wired so Marek's Neovim
  (yaml-language-server) validates, completes and hovers automatically. Not prose.
- Behavior and published formats may change; Marek is the only consumer (direct v3
  cutover, catalog-system map). A revised ADR gets a dated note, not a rewrite.
- When a ticket replaces a term, `GLOSSARY.md` changes in that ticket and the old
  term is marked superseded.

Skills: grilling and domain-modeling for grilling tickets, research for
research, prototype for the page text. Research branches stay local.

In flight elsewhere: catalog-system ticket 20 proceeds with rotation of failing
sources and smaller pages for the two oversized ones; its same-tag decision moved
here ([Record same-tag and removed releases as facts](issues/07-same-tag-and-removed-releases-as-facts.md)).

## Implementation

Marek, November 25, 2026: switch to the simplified approach as soon as
possible, no migration steps; he reinstalls his apps. One change,
[Cut over to the simplified catalog in one change](issues/24-cut-over-to-the-simplified-catalog.md),
merges 14, 16, 17, 20, 21 and 22 and seeds `catalog/` by a one-time conversion.
Done: 18 (claimed, twins pending), 23 (warn on old data).
Collector inputs (ticket 25): 30, 33 (after yamx#22). Done: [28](issues/28-enroll-from-apps-yaml.md) (enrollment is `apps.yaml`; `retired-names.yaml`; no never-read file in `catalog/` until hosts run `am -s`), [31](issues/31-platforms-and-run-outputs-as-yaml.md) (not now: both stay JSON), [32](issues/32-drop-vscode-schema-associations.md) (`.vscode` gone), [29](issues/29-derive-git-sources-from-recipes.md) (Git scopes derived from the recipes), [27](issues/27-accept-a-never-read-repository-file.md) (never-read repository files), [26](issues/26-move-policy-rows-into-recipes.md) (policy rows are recipe lines; both policy JSON files gone).

## Decisions so far

- [Derive the collector's inputs from catalog/ and the recipes](issues/25-collector-inputs-from-catalog-and-recipes.md): enrollment = `apps.yaml` (never-read stub files for new apps); names derived, 25 retired names in `retired-names.yaml`; policy rows move into their recipes (26; ticket 25 correction); Git sources as `CATALOG_GIT_*` in their scripts; platforms and run outputs as YAML; one catalog grammar for all new YAML; implemented in 26–32.
- [Draft the "How it works" page](issues/13-draft-how-it-works.md): 12 rules with a "why" each plus 9 help entries, accepted; readers read `main-marek` directly, no pinned snapshots (revises 04; in 21).
- [Show failures and staleness](issues/11-show-failures-and-staleness.md): per-source state only in repository files (detail files go), four `failed_with` codes with sentences, "Never collected", host warns (never refuses) past 14 days; one slim `status/runs.yaml`, five age buckets; implemented in 22 and 23.
- [Simplify recipe labels and platform guesses](issues/12-simplify-recipe-labels-and-platform-guesses.md): two labels (Reviewed installer / Recipe script); provenance `recipe: declaration|script`, no template evaluation or evidence; Linux-only guess with AM's four architecture names, one tested rule for page and retention; implemented in 14.
- [Simplify the format encodings](issues/09-simplify-format-encodings.md): whole `url:` only as exception, plain status integers, Git maps keyed by name/path, no absent provenance rows, no `retention`/`page_size`/`pages_fetched`; IDs stay keys; grammar unchanged plus `$schema`; implemented in 14 (now unblocked).
- [Decide which commit pins are needed](issues/05-choose-needed-commit-pins.md): none — no commit hashes of ours in catalog or status data, `producer` keeps run id/attempt, provenance keeps content hashes; both `CATALOG_*_REVISION` variables go, `release.py` keeps the live-contract check for schema changes; implemented in 21 after 16.
- [Choose the schemas' form and editor wiring](issues/10-choose-schema-form-and-wiring.md): one hand-written `schemas/catalog.schema.yaml` (kinds under `$defs`, no `$id`) is the source; documents name it with a first-key relative `$schema:` + `#/$defs/<kind>` (yamlls honors all three, probed); field prose moves into descriptions; JSON schemas and `.vscode` associations go; implemented in 20 and 16.
- [Record same-tag and removed releases as facts](issues/07-same-tag-and-removed-releases-as-facts.md): the 14 failures are same-second twins, recorded as two releases; no tag replacement; releases proven deleted upstream by a complete history (597 of 612 overrides) are removed; assets = latest list; no first-seen; retention counts tags; implemented in 18 (now) and 14.
- [Simplify the catalog's times](issues/06-simplify-catalog-times.md): one repository `observed_at` (page receipt), no `collected_at`; releases keep `observed_at` only when older ("Last seen"); Git refs/files, `created_at` and provenance `evaluated_at` dropped; status times go to 11; implemented in 14.
- [Probe YAML-authored JSON Schemas in Marek's Neovim](issues/03-probe-yaml-schemas-in-neovim.md): works as is — a first-line `$schema=` modeline to a `.yaml` schema (relative path or raw GitHub URL at a commit) validates, completes and hovers with yamlls 2.0.0; no editor config needed (the yaml extra and SchemaStore.nvim are not involved).
- [Choose the catalog directory layout in main-marek](issues/04-choose-catalog-directory-layout.md): one `catalog/` (status in `catalog/status/`), one commit per run is the snapshot, readers pin `heads/main-marek`; bot commits skip code CI and rebase-retry; move after slimming, old branches archived locally; per-repository `failed_at`/`failed_with` replace ticket 20's status map.
- [Inventory the catalog's rules](issues/01-inventory-catalog-rules.md): 62 rules, encodings and pins traced; selection sorts by last success, causes hidden as `source_validation`, the page misstates retention and history, digests/media types/most pins read by nothing.
- [Choose what to catalog per release and asset](issues/08-choose-what-to-catalog-per-release.md): derive URLs, drop `media_type`/`updated_at`, `sha256pre` (16 hex), all assets stay; keep 8 newest + newest stable + newest with Linux; ≈80 MB estimated.
- [Measure where the catalog's bytes go](issues/02-measure-catalog-size.md): 448 MB, 80% assets; URLs are 29% and 99% derivable from repository, tag and name; 8 newest releases would keep 38%.

## Not yet specified

- The installer side of facts-only same-tag records: how AM's updater reads
  them and where rolling tags are declared, charted as
  [ticket 19](issues/19-how-am-updater-reads-release-facts.md).
- Run limits (16 MiB per response, request/byte/time budgets): probably never
  user-facing except through failures; revisit after ticket 11.

## Out of scope
