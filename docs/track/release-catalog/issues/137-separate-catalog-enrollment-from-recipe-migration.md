# Separate broad catalog coverage from recipe migration

Type: task
Status: resolved
Triage: ready-for-agent
Assignee: codex

Marek requested cataloging all apps while migrating simple recipes first, then
confirmed GitHub-backed apps first; other hosting services follow separately.
This authorizes local discovery, implementation and verification. Push remains
Marek's call under home guidance; no installed-host refresh is part of this task.

## First slice

Add explicit catalog-only enrollment independent of migrated declarations and
client selection policy. Preserve existing app/source identities, schema and
publication semantics. Keep current budgets while testing the separation.
Prepare ageha-editor using ticket 135's verified repository identity and saved
release page: its icon-link migration exclusion is irrelevant to catalog facts.
Keep its recipe unchanged. Source scope becomes 54 apps / 52 repositories locally;
the published catalog remains unchanged until an authorized push/publication.

## Broad-coverage inventory and follow-up

Run `python3 docs/track/release-catalog/research/catalog-expansion-inventory.py --summary`.
At initial source 1642248c0913564e6f2a276d55484be0d211c523, all four supported
architecture directories contain 10,716 files: 10,333 mention one literal GitHub
repository, 43 mention several, 340 mention none; 8,338 distinct candidate names.
These are textual discovery counts, not verified sources or unique apps. URLs
may refer to dependencies, redirects, documentation or non-release downloads.
The full output binds each recipe's candidates to its content SHA-256. Recipe
shell is never executed. Architecture instances must not inflate browser app counts.

Full coverage requires source verification and a collection redesign before
enrollment expansion: current limits are 52 sources, 96 MiB response bytes and
300 seconds per collection; local prior-tree reads allow 1,024 files. One failed
source currently aborts the entire publication. Raising a single constant would
not address these constraints. Preserve existing 48-hour release freshness and
per-release observations while designing bounded batches and failure behavior.

Simple recipe migration remains a separate queue: reuse exact upstream-template
recognition, selector checks and static payload/lifecycle gates from 133/135.
Catalog-only presence never implies reviewed AM selection or installability.

## Answer

Implemented `collection-apps.json` independently of recipe declarations. Strict
literal identity rows merge with existing recipe enrollment; duplicate apps,
conflicting sources, malformed rows and source-cap overflow refuse. Installation
preparation explicitly uses only migrated recipes. No recipe or compiled client
policy changed. Added ageha-editor locally, preserving its migration exclusion.

[Fresh preflight receipt](../research/catalog-only-preflight.json): all 52 sources
acquired in 65.06 seconds / 56,638,821 bytes; remote-free replay/publication and
readback took 117.90 seconds. Candidate `8c26d7ca2b71f2ce9e8e8660fea31f943afbb67c`
is a child of current observed public parent `03f63def325715a2621b5662b797ff967c8e439c`.
All prior app identities preserved; 54 apps / 52 sources, 9,695,046 YAML bytes,
largest 1,142,139 bytes. All limits unchanged. Replay timing includes validation,
local publication and readback; it is not just normalization or browser timing.
Receipt binds pending working-tree preparation, not a claim those edits existed
in the recorded baseline source commit. Raw responses, identity metadata,
hash-bound full discovery and local Git candidate are retained under
`/home/marek/Documents/Codex/am-catalog-only-20261106-preflight/`.

29 focused checks pass: two catalog-only checks (real saved Ageha releases plus
shared-source exact-parent publication/refusals), six publication checks, three
declaration checks, two saved migration-batch enrollment checks and sixteen inert
installation lifecycle checks. Recipe bodies, client policy, live installation,
Pages prototype and yadm pointers remain unchanged. No app code executed.

First local separation is complete. Source push/publication awaits Marek's call;
no remote catalog or browser coverage change is claimed. Broader coverage and
actual next recipe conversions continue separately in 138 and 139.

## Publication authorization — November 6, 2026

Marek answered “yes” to pushing source and publishing this first catalog-only
addition. Source `46fc16ba22bc0ab4f2c84fd299f98e0b70b4f02d` is pushed to
main-marek. Dispatched the existing catalog workflow on that exact source:
https://github.com/mareklangiewicz/AM/actions/runs/42237434195 .
No installed-host policy refresh is needed: the compiled client policy is unchanged
and Ageha Editor remains catalog-only. Final publication readback follows below.

## Published result — November 6, 2026

Run 42237434195 succeeded at source `46fc16ba22bc0ab4f2c84fd299f98e0b70b4f02d`.
Published `bcae3298f5ffa1461a74ecab42df1a6c41d68492` is a direct child of
`03f63def325715a2621b5662b797ff967c8e439c`.
[Exact-pin readback receipt](../research/catalog-only-publication.json) verifies
54 app identities / 52 repositories, preserving all previous app identities;
all source identities and collection statuses match enrollment. Maintained schema
and distributed-reader validation pass. Total YAML is 9,695,046 bytes; largest
source is 1,142,139 bytes. Ageha has 9 retained releases / 55 assets, with end of
history reached by this collection. All existing limits remain unchanged.

The existing public browser discovers the app through its live apps.yaml map:
https://mareklangiewicz.pl/AM/?app=ageha-editor . Existing pinned visits require
Latest snapshot. No Pages code/deployment changed; no visual browser acceptance
claim is made from this data readback. No recipe migration or installed-host
change occurred. Operational documentation/receipt push is covered by this
publication authorization. Broad coverage and simple migrations remain 138/139.
