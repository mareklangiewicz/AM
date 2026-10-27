# Shared shell consumer: implemented slice

Ticket [23](../issues/23-shell-consumer-and-small-recipe-migration.md).
The Python consumer remains a reference/test oracle. Installed Obsidian recipes
and their newly generated updaters execute `modules/catalog.am` with `sh`.
Nothing was installed or migrated on the host during this work.

## Publication and lookup contract

`storage.apply` derives `lookup.tsv` from the fully validated canonical index.
`storage.validate` recomputes it byte for byte when present. Artifact staging,
closed-tree loading and remote publisher validation admit only that additional
path, with the existing 2 MB metadata bound. Publisher recomputation requires the
new file for newly generated candidates. Old publications without it remain valid
prior state; the shell reader refuses such publications. Original JSON response
bytes, aliases, request IDs and descriptors stay unchanged.

The ASCII TSV has a seven-column header: `AM-CATALOG`, format `1`, publication
UTC epoch, collector revision, run ID, attempt, and canonical index SHA-256.
Each thirteen-column record contains exact alias, active bit, availability,
request ID, body SHA-256, byte count, receipt UTC epoch, validation UTC epoch,
exact numeric upstream URL, API version, Accept value, upstream repository ID,
and observation scope. Missing observation fields use `-`. Timestamps retain
microseconds; they are derived only from validated response-completed provenance.
Fields cannot contain controls, tabs, newlines or non-ASCII bytes. Catalog text
is never sourced or evaluated. The six-source retained fixture adds **4,628 bytes**.

The shell reader validates framing, alias uniqueness and the selected record.
It relies on publisher validation for full manifest/provenance and release-JSON
schema validation; it does not implement a second JSON/manifest validator. This
is the same AM publication trust boundary as the canonical index. The index hash
in the header is provenance, not an independently authenticated signature.

## Shell and transport requirements

The actual supported slice is Linux with POSIX shell (checked with dash and bash),
GNU date fractional epoch output, curl, awk, grep, sha256sum, mktemp, wc, cat and rm.
AM already uses these utilities: curl/grep/cat are core dependencies; sha256sum
is optional in AM's general dependency list and **required for this reader**.
Date/awk/mktemp/wc/rm are existing manager utilities. No Python, jq, checkout,
standalone runtime package or runtime download hook is added. Missing tools or
unsupported date output refuse visibly. BSD/BusyBox portability is not claimed.

The fixed publication owner is **ivan-hc/AM**, not Marek's development fork.
One optional unauthenticated GitHub commit read resolves `heads/release-catalog`
using the [documented SHA media type](https://docs.github.com/en/rest/commits/commits#get-a-commit).
An explicit full commit skips resolution. The lookup and selected body then use
only that full commit on raw.githubusercontent.com. There is no proxy, token,
redirect, retry, alternate publication owner or source-API fallback. Curl ignores
its config and proxy settings; reads have size and time limits, with a temporary
file-size rlimit as an additional disk bound. At most three catalog GETs, each
limited to 30 seconds, may occur; the reader refuses elapsed reads beyond 90
seconds before releasing bytes. This is bounded transfer/refusal, not a hard
process wall-clock guarantee under arbitrary local tool stalls.

The inclusive 24-hour limit, future/unmeasured/unavailable/retired/removed-alias
refusal, exact `--commit SHA --accept-stale SHA REQUEST BODY_HASH` consent,
body byte count/hash and post-transfer freshness/clock checks live in this one
reader. Refusal emits no body. The body hash checks publication consistency;
it does not independently authenticate the upstream binary.

## Distribution, recipe and manager behavior

The manager names `catalog.am` in its normal shell-module inventory so sync and
obsolete-module cleanup retain it. Its `AMCLI` marker satisfies existing sync
validation. `install.am` requires the already managed local module and embeds its
absolute location in both recipe and generated updater, including AppMan and
system-package module locations. Shell metacharacters are escaped when embedding
the path; it is never reconstructed from a checkout or bootstrapped by an updater.
A missing helper requires normal module synchronization and refuses execution.
System launcher-directory creation and broken-link repair are deferred into the
recipe after preflight. The installation dispatcher preserves incomplete app state
when its replacement recipe is unavailable; it does not run the previous remover
or the legacy destructive interruption handler before catalog acceptance. A valid
reviewed recipe can repair the incomplete installation after preflight, including
when installed from an explicit local script.

Obsidian's installer preflights before creating app directories/remover files.
Its generated updater preflights before creating tmp or changing app/version
files. Both keep the identical existing asset-selection pipeline and original
GitHub binary URL. The checkout-relative Python `--catalog-version` scaffolding
and appimageupdatetool alternate-source bypass are removed. Shell execution errors
and download errors propagate; notification failure is nonfatal. Interrupted update
work is cleared only after successful preflight, so a failed download can be retried.
A recorded checksum failure forces a same-version binary download after preflight,
without deleting the installed version before acceptance. Optional managed binary
verification still runs afterward; stale verification is not independent proof of
the replacement binary's authenticity.

A marked newly generated updater uses a foreground single-app manager route
before legacy token edits, quota probing and cleanup. Use `am -u obsidian`, with
optional reader arguments forwarded to the updater. The standard `--debug` manager flag is consumed before reader invocation.
Launcher-only operations retain their separate existing route. Batch/mixed
selection involving a catalog updater refuses; it is not a fleet implementation. Color-filter pipelines
preserve nonzero status. Duplicate roots are deduplicated; ambiguous app locations
refuse. Old installed updaters remain legacy until a separately authorized migration.
The marker denotes an AM-generated installed script, not a discovery mechanism
that executes saved installer text.

After a successful managed updater run, AM's optional `_use_verify` still probes
original upstream binary digest URLs (`.zsync`, digest suffixes). A recorded
checksum failure returns nonzero. This is separate from catalog verification and
may perform additional network reads. A standalone updater, as before, does not
run that manager check. No claim of zero additional binary-source reads is made.

## Cost and displaced machinery

Compared with source `0a21fef3c`: the shared reader is **96 lines**, manager changes
are **+53 net lines**, installation module changes **+29**, and Obsidian **+1**:
**+179 net client source lines** for this first app after the
[ticket-25 integration fixes](../issues/25-review-shell-adoption.md). The initial
ticket-23 slice was +139; review added 40 lines to preserve recovery and preflight
semantics at real manager entrypoints. The CI-only TSV generator is
33 lines, plus small validation/path-allowlist changes. This slice removes the
consumer language/checkout requirement and centralizes safeguards; it does not
claim a net source-line reduction from migrating only one app. The retained Python
oracle is neither distributed nor invoked by this installed-user path.

The catalog route displaces this app's API token patching, release quota probing,
proxy rewriting, updater patching and checksum-failure version deletion before
preflight. Installer catalog refusal bypasses legacy repair/retry and exits nonzero.
General code remains because actual callers still exist:

- `_update_github_api_key_in_the_updater_files` and quota accounting serve unmarked
  GitHub updaters; marked updaters are excluded from both.
- `_alt_gh_on/off/filter` still serve legacy update/install, rollback in
  `modules/management.am`, and source previews/templates in `modules/template.am`.
- Header injection still serves unmigrated recipes and third-party/download paths.
- `_use_verify` remains a separate optional binary check; removing it would change
  existing behavior rather than eliminate a displaced metadata proxy.

No whole-subsystem removal or blanket audit is claimed.

## Verification and adoption boundary

Offline tests execute the real reader, recipe and heredoc-generated updater in
unrelated temporary roots. Curl/clock, binary download, extracted app contents,
notifications and optional binary verification are controlled fixtures/stubs.
They use retained measured Obsidian bytes, not newly collected release data.
Checks cover exact bytes/filter equivalence, fresh/stale edge and tuple binding,
clock regression/expiry, malformed/duplicate/unavailable lookup, size/hash failure,
missing tool/helper, module-path embedding, unchanged/changed updates, no app-state
mutation on refusal, binary download failure, batch refusal and visible manager
failure through color filtering. Existing collector/storage/delivery contracts
exercise atomic lookup recomputation and old-publication compatibility. The final
ticket-23 suite passed **89 tests**. Shell syntax checks passed for the manager, installation
module, reader and recipe. ShellCheck passed for the reader and at warning severity
for the recipe; two pre-existing informational recipe findings remain unchanged.

[Ticket 24](../issues/24-shell-publication-roundtrip.md) additionally verifies the
cross-boundary path: ZIP/recomputation, actual local bare-remote publication,
conditional repeat, branch movement during shell reads and stale-consent binding
across real publication commits. Actual module inventory/sync/obsolete cleanup
also preserves an already generated standalone updater and can replace or deliver
its managed reader. These checks use retained measured bodies and fixture workflow
context, not a newly downloaded live artifact. The combined suite passes **92 tests**.

[Ticket 25](../issues/25-review-shell-adoption.md) reviews standards and spec
separately. Four spec defects were found and repaired: retry work-directory
handling, checksum repair, installation mutation before acceptance (including
unavailable replacement recipes), and collateral launcher-only refusal. Tests now
execute the full installation module dispatch/functions in temporary roots, with
external AM services stubbed, not just extracted recipe/patch fragments. These
cover both refusal without app/link/directory mutation and successful deferred
incomplete-install repair. The first passing suites did not establish these
properties; their counts above remain historical evidence. The final reviewed suite passes
**100 tests**, with the syntax and ShellCheck checks above repeated successfully.

There is no live shell publication/read result. Upstream has not accepted this
format, and the fixed upstream reader will refuse until an AM-owned publication
provides it. No workflow was changed or run, no upstream collection was performed,
no schedule enabled, and no host app installer/updater or installed migration ran.

Before any public adoption: review the upstream AM-owned publication source and
permissions, publish one recomputed retained candidate through an explicitly
approved publication action (no fresh collection required), and record its full
commit. Then authorize **two public catalog GETs** for one explicit pin: lookup
and the Obsidian body, with no binary download or installer. Compare returned
bytes/hash/filter to the retained candidate. A separately authorized ref smoke
can add exactly one SHA-resolution GET. Recheck workflow isolation before any
fork workflow validation; its ownership remains development evidence, not the
installed reader's trust target. Installed-state migration remains a separate
user action after public validation and upstream acceptance.
