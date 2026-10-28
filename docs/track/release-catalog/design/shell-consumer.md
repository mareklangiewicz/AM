# Shared shell consumer: implemented slice

Tickets [23](../issues/23-shell-consumer-and-small-recipe-migration.md) and
[29: corrected repository ownership](../issues/29-respect-configured-catalog-repository.md).
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

Catalog ownership follows **AMREPO**, the selected AM package source. This fork's
source is `https://raw.githubusercontent.com/mareklangiewicz/AM/main-marek`, so its
catalog reads use mareklangiewicz/AM. The reader requires that environment value,
validates the supported raw-GitHub owner/repository/branch form and derives the
repository centrally. Missing/empty, malformed/multiline, other-host and local
file sources refuse before any network request. There is no default upstream
owner, alternate-repository fallback or source-API fallback. The source branch
selects the repository; the catalog ref stays release-catalog, independently of
source branch (including source branch names containing slashes).

One optional unauthenticated GitHub commit read resolves heads/release-catalog
in that selected repository using the documented SHA media type. An explicit full
commit skips resolution. Lookup and body use only that full commit in the same
repository on raw.githubusercontent.com. There is no proxy, token, redirect or retry.
Curl ignores
its config and proxy settings; reads have size and time limits, with a temporary
file-size rlimit as an additional disk bound. At most three catalog GETs, each
limited to 30 seconds, may occur; the reader refuses elapsed reads beyond 90
seconds before releasing bytes. This is bounded transfer/refusal, not a hard
process wall-clock guarantee under arbitrary local tool stalls.

The inclusive 48-hour limit (accepted daily policy in ticket 40), future/unmeasured/unavailable/retired/removed-alias
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
Installation also embeds the selected AMREPO value in both recipe and generated
updater, escaped as literal shell data, for standalone execution without the
manager or inherited environment. The source is exported to the shared helper.
Managed updates explicitly pass the manager's current AMREPO, even if it is not
exported, overriding the installation-time default. An explicit empty value
refuses rather than selecting a fallback. An unprepared recipe needs AMREPO set;
it has no hardcoded repository. Existing installed scripts are not rewritten by
this source change; migration remains separate.
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

Ticket 44 supersedes the initial single-app restriction: marked updaters now
participate in normal all-app and explicit mixed batches. The command shares one
source-bound publication pin/lookup, retains per-app acceptance, continues after
refusal/failure and aggregates nonzero status. Standard `--debug` is consumed
before reader invocation; launcher-only operations retain their separate route.
Both configured app locations are processed when present; duplicate roots and
explicit targets run once. Old installed updaters remain legacy until explicitly
migrated. See [current batch semantics](normal-batch-updates.md).

After a successful managed updater run, AM's optional `_use_verify` still probes
original upstream binary digest URLs (`.zsync`, digest suffixes). A recorded
checksum failure returns nonzero. This is separate from catalog verification and
may perform additional network reads. A standalone updater, as before, does not
run that manager check. No claim of zero additional binary-source reads is made.

## Cost and displaced machinery

Compared with source `0a21fef3c`: the shared reader is **102 lines**, manager changes
are **+53 net lines**, installation module changes **+32**, and Obsidian **+7**:
**+194 net client source lines** for this first app after the ownership correction and
[ticket-25 integration fixes](../issues/25-review-shell-adoption.md). The initial
ticket-23 slice was +139; review added 40 lines to preserve recovery and preflight
semantics at real manager entrypoints. Ticket 29 adds 15 lines for validated source
selection and persistent configuration handoff. These counts do not prove simplification. The CI-only TSV generator is
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
mutation on refusal, binary download failure, the initial batch refusal (superseded
by ticket 44), and visible manager
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

The initial tickets 23–25 had no live shell publication/read result and incorrectly
required an upstream-owned catalog even for this fork. That ownership assumption
is superseded by ticket 29. Ticket 27's retained candidate and successful public
read are fork delivery evidence. Our fork does not require upstream acceptance.
No host app installer/updater or installed migration ran in this work.

Further public checks use the actual configured repository and unmodified reader,
with a concrete full publication pin and measured freshness or explicitly approved
exact stale consent. They do not require another publication, source collection
or binary download merely to validate source selection. Recheck workflow isolation
before any separately approved workflow validation. Sustained freshness and any
installed migration remain explicit operational steps, without an implied schedule.

## Subsequent bounded fork validation (ticket 27)

[Approved fork publication/public read](../research/fork-shell-public-read-findings.md)
now verifies one retained-data format-only child, a0fdd1255, and an explicit-pin
shell read through an archived fork-only reader copy. Exactly two real HTTP 200
catalog GETs returned the candidate lookup/body bytes and unchanged filter URL,
with normal measured freshness, exit 0 and empty stderr. Only the two literal
owner strings differed in that historical test copy; the production reader at
that revision was incorrectly fixed to ivan-hc/AM. Ticket 29 removes that defect
and makes a fork-only modified copy unnecessary.
This supersedes the earlier absence of a live shell result for the development
fork only. Historical upstream adoption limitations are not fork-use blockers.
Live unpinned resolution and installed migration remain unverified. No workflow, collection, schedule or app execution.


## Configured-source regression verification (ticket 29)

The final current suite passes **107 tests**. The pre-fix ownership regression
failed on the actual upstream-AM request despite a fork AMREPO; it now passes.
Actual installation dispatch clears AMREPO across the privilege wrapper and uses
the embedded source. The generated standalone updater works with no inherited
AMREPO. The actual newrepo-selection function supplies a changed, nonexported
source to managed execution. Missing/empty/unsupported/local/multiline sources
and selected-catalog HTTP failure never try a fallback repository. Syntax and
reader/recipe lint pass. Full [findings](../research/catalog-source-correction-findings.md)
and [tracker correction](../issues/29-respect-configured-catalog-repository.md)
record what supersedes the historical fixed-upstream claims. No new live read
was performed by this repair.

## SQLite Browser migration (ticket 38)

The x86_64 sqlitebrowser recipe now uses the same shared reader and generated
updater route, with its already enrolled exact releases?per_page=100 alias.
Both original asset-selection pipelines are byte-identical after substituting
verified catalog bytes for the direct API response. Retained metadata selects
DB.Browser.for.SQLite-v3.13.1-x86.64-v2.AppImage from its original GitHub URL.
No new endpoint, manifest change, collector request or shared runtime code.

Preflight precedes app directories, launcher repair and incomplete-install cleanup.
Standalone source persistence and current managed-source handoff use the existing
install/manager markers. Interrupted downloads retry after accepted preflight;
checksum-failure state forces same-version repair. Notifications are nonfatal.
The recipe's appimageupdatetool bypass is removed, and the marked manager route
skips displaced legacy token/proxy/quota handling. The general legacy machinery
still has unmigrated callers and is not deleted. This recipe changes by +19 net
lines; it is reuse of the existing reader, not proof of overall line reduction.

Six new retained-data integration tests cover installation/generated updater,
no-change and changed updates, stale refusal/exact acceptance, preserved partial
state, failed-download retry, checksum repair, manager source selection, and
actual install-module dispatch with privilege environment clearing followed by
standalone execution without AMREPO. Real app/network operations are stubs in
isolated roots. Existing installed SQLite Browser updaters are not migrated.
The prior Obsidian pilot and pinned remote scheduler remain unchanged.
