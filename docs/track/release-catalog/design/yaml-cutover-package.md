# One exact local cutover review package

Ticket 103. Consolidated source branch `prep/yaml-cutover-package` merges
main's authoritative tracking records and every candidate inherited by
prep/yaml-installed-migration. It preserves main's canonical map and ticket-102
results when resolving three documentation conflicts. Main runtime is untouched.
No workflow is activated and no remote ref or installation is changed.

## Inventory boundary

`yaml_cutover_package.py inventory` requires explicit installation roots, manager,
module directory, architecture, AppMan configuration file and AM data directory.
It reads scripts/configuration and streams binary hashes, without executing any
installed code. Its JSON records hashes, sizes, Unix metadata, link kinds and
extended-attribute names; it does not record attribute values or binary contents.
It records configured AppMan root presence, source-override/beta/mode probes,
module/updater path sets and skipped directory symlinks. A configured AppMan root
must be explicitly included or the inventory refuses. No traversal of directory
symlinks and no discovery under home or unrelated repositories occurs. This is a
snapshot of named local roots, not an assertion about other machines or clients.

Before and after package construction, verify the file hashes/metadata,
configuration presence and module/updater sets against the inventory. Changed
inputs refuse; this is not a lock against concurrent uncooperative writers.
A refusal can leave an incomplete output directory; never treat it as accepted.

## Source and installed binding

Build requires full source and legacy-source commit IDs in a trusted local Git
repository. Every shipped source byte comes from that commit, never the working
tree. The package includes a complete Git source archive, exact source manager
and all .am modules, and before-images of the inventoried manager/modules and
installed updater/recipe/version files. It retains original metadata in the
inventory for later delivery/restoration. It does not back up installed binaries
or claim binary rollback. The private output directory must be new.

For each managed client whose exact source recipe opts into format 2, reproduce
its installed legacy recipe from the exact legacy source with the inventoried
literal directory/module/source bindings. Refuse if those bytes differ. Verify
the exact generated exec-recipe updater. Produce the replacement from the exact
new source using those same directory/module bindings and pinned AMREPO; keep
PACKAGE_KIND, REFRESH_ALWAYS and CATALOG_ALIAS assignments unchanged. Unsupported
custom binding forms refuse rather than executing shell. The compact binder is
only the shared-recipe subset of install.am; it is not a replacement for the
manager's arbitrary legacy/platform installation transformations. Shell syntax
and disposable-root behavior are tested. The source and old installed hashes
remain available for review.

Unenrolled managed recipes retain format 1 and are explicitly listed. Old
standalone updaters require separate adapters or reviewed reinstalls; the tool
never takes them over based on an app-name match. This closes the fully bound
replacement gap for eligible clients without pretending all installed clients
are eligible.

## Publication proposal

Inventory found Sunshine still uses format 1 outside the 475-path YAML scope.
The source snapshot also contains additional format-1 shared recipes. Therefore
this candidate proposes fixed `refs/heads/release-catalog-yaml-v2` for format 2,
while existing `refs/heads/release-catalog` remains format 1. The YAML raw client,
exact-prior acquisition and CAS publisher use the separate fixed ref. The shared
prior-acquisition helper permits only the two explicit fixed refs and defaults
to the unchanged format-1 ref. Offline tests cover independent bootstrap/refresh,
ref races and preservation of the format-1 ref. The manual workflow remains an
inactive `.proposed` artifact. Neither ref is created or inspected remotely.

This is an executable source proposal for review, not operational acceptance of
dual publication, its capacity cost, a retirement date or remote controls.
Format-1 can retire only once its supported source and installed consumers are
migrated or explicitly retired. Legacy direct-upstream updaters do not depend
on either catalog; they still remain outside a claim of full YAML adoption.

## Package review and next actions

`build` emits inventory, source archive, runtime, before-images, replacement
recipes and manifest. Every payload file has a SHA-256 and size. `verify` rejects
changed payloads, extra/missing files and symlinks. These checks establish internal
integrity relative to a trusted manifest, not authentication of an arbitrary
manifest received remotely. Record the manifest's SHA-256 separately in the
tracker when freezing a package. With the same inventory and source commits,
manifest/payload construction is deterministic.

The manifest deliberately has apply_ready=false and null publication/selection
pins. Do not fabricate them from saved test fixtures. The remaining sequence is:
review package/source and client scope; settle policy/stale UI and realistic
capacity; authorize source publication and inactive workflow/ref transition;
collect/publish and independently verify exact format-2 facts; guard and deliver
exact manager/modules; create 102's plans from exact selected records and
reviewed old/replacement hashes; rehearse and then authorize installed migration;
accept actual updater and scheduled behavior. Manager/module installation and
binary recovery are still separate from the recipe transaction tool. No active
workflow/pin or implicit migration hook is added by this package.
