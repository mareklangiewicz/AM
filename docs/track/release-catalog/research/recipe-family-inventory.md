# Recipe families and migration batches

Ticket [45](../issues/45-recipe-inventory-and-migration-batches.md), measured
2026-10-28 at recipe/manager revision `ee56537bcfbdea5d373980f7ad8d7c59cf40bbee`.
This is a local source inventory. No recipe, metadata filter, installed updater,
binary, collection, workflow or network request was executed.

## What is ready, and what is large

Three remaining Neovim AppImages can use the existing catalog and unchanged
shared lifecycle: x86_64 nightly, aarch64 stable and aarch64 nightly. The larger
opportunities require new exact source enrollment: **356 plain executables behind
one endpoint**, then **124 AppImages behind 50 exact endpoints**. These are scoped
review/migration queues, not claims of accepted metadata, current upstream
availability, compatible assets or installed rollout.
[Generated evidence](recipe-family-inventory.json),
[exact aliases and caller audit](recipe-exceptions-and-callers.md).

The first broad extension should be grounded in the 356 am-utils recipes, rather
than adding hypothetical archive adapters or lifecycle hooks. Their common frame
is a real second format: download an executable, chmod, version record, symlink
and updater, without AppImage extraction or desktop integration. Examples:
[7z](../../../../programs/x86_64/7z),
[addr2line](../../../../programs/x86_64/addr2line),
[aarch64 addr2line](../../../../programs/aarch64/addr2line).
The 124-AppImage queue can reuse the existing format implementation after exact
source and asset validation. It is selected to share endpoints and delete actual
repeated lifecycle bodies, rather than produce 124 unrelated read substitutions.

## Method and limits

Run from the repository root:

```sh
python3 tools/catalog-collector/recipe_inventory.py --output /tmp/recipe-family-inventory.json
```

The [inventory script](../../../../tools/catalog-collector/recipe_inventory.py)
reads all direct regular files in the four architecture directories. The evidence
records the input revision, aggregate recipe-content hash, manifest hash and
script hash. It never expands shell variables or runs recipes. It strips full-line
comments/blanks for marker detection, identifies AppImage extraction, unpack
command positions and a conservative plain-executable move/chmod pattern, and
otherwise labels the recipe custom. These buckets describe source markers,
not proved runtime formats. An AppImage recipe with generic archive fallback
commands remains distinct from a proved archive-executable installer.

Lifecycle fingerprints normalize only APP assignments, SITE assignments and whole
`version=` lines, after stripping blank/full-comment lines and surrounding
whitespace. Everything else remains exact. This measures common source frames;
it does not prove that every selector chooses the right asset. The generated
report checks for fingerprints spanning different marker buckets (none here).
Generated updater heredocs, quoted strings and dead branches remain source text.

API tokens use the existing [AWK lexer's](../../../../tools/catalog-probe/inventory.awk)
quote/trailing-parenthesis rules. Independent comparison agrees on all **20,928**
code-context tokens for x86_64/aarch64. Added i686/armv7l coverage produces **20,974**
occurrences across **10,438** files and **8,340** distinct literal release URLs.
The earlier [8,337-URL inventory](request-inventory-findings.md) covered only
x86_64/aarch64 at its recorded revision. Neither count is a reviewed collection
manifest or a runtime request count. No query, case, renamed repository or
pagination aliases are silently merged. Dynamic forms stay unresolved.

## Current family counts

| Static bucket | x86_64 | aarch64 | i686 | armv7l | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Shared AppImage recipe | 3 | 0 | 0 | 0 | 3 |
| AppImage, no unpack-command marker | 3,689 | 582 | 14 | 2 | 4,287 |
| AppImage with unpack-command markers | 4,586 | 984 | 4 | 0 | 5,574 |
| Archive/unpack, no AppImage extraction | 410 | 37 | 7 | 0 | 454 |
| Plain-executable move/chmod pattern | 179 | 178 | 0 | 0 | 357 |
| Other/custom | 32 | 6 | 3 | 0 | 41 |
| Total | 8,899 | 1,787 | 28 | 2 | 10,716 |

All counts, source-frame hashes, examples and partition checks are in the
[generated evidence](recipe-family-inventory.json). Of the 357 plain-executable
marker matches, 356 share the am-utils endpoint/frame; the extra match is not
silently added to that batch.

There are 397 normalized source frames. The largest contains 5,453 AppImage
recipes with generic 7z/tar/zip handling (4,476 x86_64 + 977 aarch64): see
[1aivault:15–21](../../../../programs/x86_64/1aivault#L15).
The next three contain 1,426, 1,328 and 1,267 AppImage recipes without that generic
unpack block. Examples:
[0x808](../../../../programs/x86_64/0x808),
[432hz-player](../../../../programs/x86_64/432hz-player),
[0ad](../../../../programs/x86_64/0ad).
The plain executable frame contains 356 files; a real archive/unpack frame
contains 237, including [afetch](../../../../programs/x86_64/afetch).
This is evidence of substantial repetition, not permission to replace all frames
with a single assumed format. In particular, an `any download URL` selector plus
an unpack block needs actual retained asset evidence before choosing AppImage.

## Exact coverage today

The [six-source manifest](../design/staged-manifest.json) covers all extracted API tokens in six
recipe files: three already migrated and the three remaining Neovim variants.
One additional recipe, nightly WezTerm, is partially covered. 278 recipe files
have no extracted GitHub API token; **10,431** have only unenrolled or unresolved
ones. These are textual file buckets, not verified source or network behavior.

Neither enrolled `/releases/latest` alias has a recipe caller. Stable WezTerm's
plain `/releases` is distinct from the enrolled `?per_page=100`; nightly WezTerm
also uses `/events` for its update identity. Its shared-format fit is unresolved,
so neither WezTerm recipe is placed in an enrollment-free batch. The full
[exceptions audit](recipe-exceptions-and-callers.md) cites the exact selectors,
nightly identity and remaining token/quota/proxy/alternate-updater callers.

## Concrete continuation order and projected deletion

1. [46: remaining Neovim AppImages](../issues/46-migrate-remaining-neovim-appimages.md).
   Three files, 231 current source lines, with the existing catalog alias and
   unchanged shared interface. At the current 21-line recipe shape this removes
   approximately **168 source lines**. Preserve each stable/nightly/architecture
   selector and original URL; report absent retained matches honestly.
2. [47: reviewed enrollment for the concrete larger batches](../issues/47-enroll-scoped-migration-sources.md).
   Start with the single am-utils release-list endpoint, then the exact 50-endpoint
   AppImage queue. Keep identity evidence, aliases, pagination, approved network
   operations and published observation state explicit. Preparation is offline;
   actual new identity/release requests and publication require a concrete approval.
3. [48: am-utils executable lifecycle and 356 recipes](../issues/48-shared-executable-am-utils-batch.md).
   178 app identities on each of x86_64 and aarch64, one exact endpoint and one
   source frame, currently **18,868 lines / 673,192 bytes**. A target of 20–24 lines
   per trusted recipe would delete **10,324–11,748 recipe lines before adding any
   shared implementation**. This is a design target, not measured net savings.
   Deduct all new shared code and generated/installed code in the final audit.
4. [49: common AppImage batch](../issues/49-migrate-common-appimage-batch.md).
   The frozen queue has **124 recipes**: 80 x86_64, 38 aarch64, 4 i686 and 2 armv7l,
   **50 exact endpoints**, and two normalized no-unpack frames. Current source:
   **10,068 lines / 436,026 bytes**. At 21 lines per recipe, expected recipe deletion
   is **7,464 lines**, before any measured shared-code changes. Preserve all channel
   and architecture filters; exact filename selectors may differ while sharing
   the same retained response. Exclude/refuse missing or unsuitable assets rather
   than silently switch endpoint, format or selector.

The proposed enrollment pool is 51 exact requests and 480 legacy recipes, separate
from the existing six sources/three migrated recipes. Fifty endpoints were chosen
from the two largest no-unpack AppImage frames, requiring two identical version
lines and one literal release endpoint per file; maximize shared callers first,
then sort exact URL as a deterministic tie break. This is a useful deletion-first
queue, not a popularity ranking. The broader same-frame pool is 2,333 endpoints /
2,675 recipes; it is not all automatically ready. Full paths, line/byte counts,
request occurrences and fingerprints for both concrete batches are preserved in
[the JSON evidence](recipe-family-inventory.json).

## Enrollment capacity and rollout are separate work

The current collector is intentionally bounded to six requests, with an 8 MB
body cap, 300-second batch deadline and 50 MB tree cap. Manifest loading also
requires exactly six sources; storage accepts at most six attempts. Thus 51 new
URLs cannot simply be appended and enabled. Source review must first decide and
prove the incremental/bounded plan, starting with one high-yield endpoint. Do not
raise safety limits, batch every request into one run or promise daily freshness
for 57 sources using six-source observations alone.
[Manifest](../../../../tools/catalog-collector/manifest.py),
[collector](../../../../tools/catalog-collector/collector.py),
[storage](../../../../tools/catalog-collector/storage.py).

The proposed recipes are still legacy until implemented and their host payloads
are delivered. No installed app was inspected or migrated here. A future concrete
rollout must distinguish managed module delivery, saved recipes/generated launchers,
source embedding and existing installed version/repair state; required sudo commands
are supplied for Marek to run. Pilot expiry/shutdown and the accepted daily switch
remain tickets 37/41, with no mid-pilot source push or new enrollment activation.

Legacy support cannot be removed globally. Source still contains alternate-updater
text in 9,891 recipe files; installer, normal legacy update, force-latest, rollback,
template/preview and manual-launcher paths retain real callers. Zero current
old-proxy literals does not establish that installed historical-proxy repair is
unused. Only each migrated recipe's displaced code can currently be deleted.
[Caller evidence and counts](recipe-exceptions-and-callers.md).


## Verification

[Recorded checks](recipe-inventory-checks.json) confirm byte-identical repeated
output, exact agreement with the independent prior AWK token scan on its two
architectures, reconciled family/coverage partitions, disjoint/unique batch paths,
current recipe line/byte counts and every retained token's source line reference.
The Python tool compiles and `git diff --check` passes. No consumer, manager,
recipe or workflow implementation changed, so runtime tests were not rerun for
this documentation/static-tool inventory.
