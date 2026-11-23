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

## Decisions so far

- [Choose the catalog directory layout in main-marek](issues/04-choose-catalog-directory-layout.md): one `catalog/` (status in `catalog/status/`), one commit per run is the snapshot, readers pin `heads/main-marek`; bot commits skip code CI and rebase-retry; move after slimming, old branches archived locally; per-repository `failed_at`/`failed_with` replace ticket 20's status map.
- [Inventory the catalog's rules](issues/01-inventory-catalog-rules.md): 62 rules, encodings and pins traced; selection sorts by last success, causes hidden as `source_validation`, the page misstates retention and history, digests/media types/most pins read by nothing.
- [Choose what to catalog per release and asset](issues/08-choose-what-to-catalog-per-release.md): derive URLs, drop `media_type`/`updated_at`, `sha256pre` (16 hex), all assets stay; keep 8 newest + newest stable + newest with Linux; ≈80 MB estimated.
- [Measure where the catalog's bytes go](issues/02-measure-catalog-size.md): 448 MB, 80% assets; URLs are 29% and 99% derivable from repository, tag and name; 8 newest releases would keep 38%.

## Not yet specified

- The installer side of facts-only same-tag records: how AM's updater reads
  them and where rolling tags are declared. Specify after ticket 07.
- Run limits (16 MiB per response, request/byte/time budgets): probably never
  user-facing except through failures; revisit after ticket 11.

## Out of scope
