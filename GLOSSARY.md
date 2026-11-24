# AM catalog language

## Language

**Git reference observation**:
An observation of the commit identified by a named branch or tag, with its own observation time.

**Repository file observation**:
The exact contents and blob identity of a repository file at a particular commit.

**Catalog**:
Published release, Git reference and repository file facts offered to clients, without making their selections.

**Client selection**:
A client's choice of catalog facts for installation, browsing, presentation, or another purpose.

**Asset acquisition**:
Obtaining the bytes of the release asset chosen by client selection, through a full transfer or reconstruction from existing bytes.

**Retained release set**:
The releases currently kept for a source, accumulated from successful collections. It can contain records observed at different times.

**Collection scope**:
The requested sources, releases per page and number of pages (or all pages) for a collection. Completing that scope differs from observing the source's entire history.

**Release observation time**:
The last time a successful collection received an upstream response including that release. It measures that release's freshness independently of collection or publication time.

**Repository observation time**:
When a repository's release page was last received in a successful collection (`observed_at`). Releases, Git references and files without their own observation time share it. Changing it does not reobserve releases left untouched by a collection.
_Avoid_: shared observation time (superseded November 24, 2026), collection time

**Release selection rule**:
A client's explicit rule for choosing among cataloged releases, such as publication time, version, prerelease status, or source-specific conventions.

**Digest prefix**:
The first 16 hexadecimal digits of an asset's SHA-256, recorded to notice that an artifact changed. It does not verify a download.
_Avoid_: digest, checksum (for the prefix)

**Collection time** (superseded November 24, 2026, by repository observation time):
The time a repository's requested collection scope completed successfully. Dropped with `collected_at`: it equalled the repository observation time in all but 2 sources, 1 s apart.

**Failed attempt**:
A collection of a repository that did not complete, recorded with its time and cause until the next successful collection. For choosing which repositories to collect next, it counts as a visit like a success.

**Publication time**:
The time a catalog snapshot was published, distinct from repository and release observation times.

**Complete release observation**:
A collection observation acquired by reaching the end of the source's published release pagination. It does not assert a transactional snapshot or independently verified completeness of embedded asset lists.

**Reconciliation**:
Removal of a retained release that a successful collection proves deleted upstream by reaching the end of the history. A release the collection did not reach is kept. (Redefined November 24, 2026; formerly full-history collections only, never implemented.)

## Recipes

**Original recipe**:
Upstream's full install script for one app and architecture, exactly as upstream publishes it.
_Avoid_: Upstream script, legacy recipe

**Recipe declaration**:
The fork's short form of a recipe: literal settings that name the app, its catalog source and its packaging, with no install steps of its own. The fork's preferred form: it can be trusted without reading install steps. The catalog page labels it "Reviewed installer".
_Avoid_: Short recipe, wrapper, shared installer (the label before November 25, 2026)

**Recipe script**:
Any recipe that is not a recipe declaration (long, fork-owned or original), labelled "Recipe script, read it before installing" on the catalog page.
_Avoid_: Not yet classified, template-based recipe, custom recipe (labels before November 25, 2026)

**Long recipe**:
An original recipe whose install steps are kept, with its release selection replaced by a catalog lookup. The fallback until a reviewed template lets the recipe become a recipe declaration.
_Avoid_: Patched recipe, bound recipe

**Conversion**:
Turning an original recipe into a long recipe or a recipe declaration.
_Avoid_: Migration, translation

**Binding**:
The link from a recipe to its catalog source, carried by long recipes and recipe declarations.

**Fork-owned recipe**:
A recipe the fork maintains itself, either absent upstream or deliberately different from upstream's, which an upstream merge never overwrites.
_Avoid_: Custom recipe, local recipe
