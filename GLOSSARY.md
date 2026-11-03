# AM catalog language

## Language

**Catalog**:
Published release facts offered to clients, without choosing which release a client should use.

**Client selection**:
A client's choice of release and assets for installation, browsing, presentation, or another purpose.

**Retained release set**:
The releases currently kept for a source, accumulated from successful collections. It can contain records observed at different times.

**Collection scope**:
The requested sources, releases per page and number of pages (or all pages) for a collection. Completing that scope differs from observing the source's entire history.

**Release observation time**:
The last time a successful collection received an upstream response including that release. It measures that release's freshness independently of collection or publication time.

**Release selection rule**:
A client's explicit rule for choosing among cataloged releases, such as publication time, version, prerelease status, or source-specific conventions.

**Collection time**:
The time a repository's requested collection scope completed successfully. It does not establish the freshness of releases untouched by that collection.

**Publication time**:
The time a catalog snapshot was published, distinct from collection times and release observation times.

**Complete release observation**:
A collection observation acquired by reaching the end of the source's published release pagination. It does not assert a transactional snapshot or independently verified completeness of embedded asset lists.

**Reconciliation**:
Removal of retained releases absent from a successfully completed full-history collection, according to an explicit deletion policy. Absence from a partial collection is not grounds for reconciliation.
