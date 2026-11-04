# Restricted-token collector core (offline implementation)

Ticket 12; design: `docs/track/release-catalog/design/restricted-collector-v1.md`.
The collector.py core has no network transport, workflow adapter, live CLI or environment
credential lookup. The historical quota/churn probe and workflow remain separate.

From the repository root (Python 3.10+):

```sh
python3 -B tools/catalog-collector/replay.py
python3 -B -m unittest discover -s tools/catalog-collector -p 'test_*.py' -v
```

Replay emits JSON to stdout using synthetic identities, credentials, response bytes
and clocks. No real source enrollment or public-visibility evidence is claimed.
There are no packages to install. `collector.py` has no runnable entry point.

## Interfaces

`plan(tuple_of_sources, workflow_repository_id, previous_state)` returns an
immutable Plan. Sources contain exact descriptors, reviewed immutable repository
IDs, identity evidence pointers and additional aliases (the descriptor URL is
already an alias). Previous state is an ID-to-Prior mapping. Body integrity and
conditional validators are checked before reuse. Unavailable/retired/unknown
priors supply no conditional request. The planner does not enroll or look up IDs.

`collect(plan, transport, clock, credential, workflow_identity=trusted_current_id)`
revalidates the plan against a separately supplied current identity before any
transport call. The extra keyword is intentional: an identity embedded only in
an incoming plan cannot establish the current workflow identity. A future trusted
adapter must supply it from workflow context and establish the built-in token's
provenance. An opaque object is not evidence of token scope by itself.

The credential is opaque to the core; no default, environment variable fallback,
repr/str conversion, command line or saved request Authorization header exists.
The transport receives it explicitly. Transport exception text is never emitted,
including an exception of the core's own Refusal type. A future trusted adapter
must keep credentials out of response events; the core cannot prove the provenance
or behavior of arbitrary injected Python code.

`transport.execute(request, credential, limits)` yields Connected, Headers, Chunk,
then End. Headers also reports the actual conditional values sent; they must
match the planned conditions before the result is accepted. HTTP 200/304 or failure statuses are inert transport results. Partial
responses, timeouts and bound violations have no response completion time or
candidate body. Status/selected headers and attempt finish time may still survive.
The core never updates prior state or writes files. Storage remains responsible
for release content validation, availability and candidate publication validation.
Do not interpret `outcome=response` or run `complete` as successful observation:
these mean complete HTTP transfer(s), possibly including HTTP errors/redirects.

The clock supplies aware UTC `utcnow()` and numeric `monotonic()` methods. Request
start, response completion and attempt finish are measured at separate boundaries.
Monotonic deadlines are absolute and passed to transport: connect 10 seconds,
request 30 seconds including all body reads, batch 300 seconds. Equality reaches
the deadline. Each event is checked against those deadlines; chunks cannot reset
request elapsed time. **The adapter must also interrupt blocking I/O itself.**
This core cannot preempt arbitrary injected Python code or a blocked iterator.
The fake event transport verifies event-boundary semantics, not socket behavior.

Header size accounting includes discarded headers; retained public headers have
individual bounds and duplicate public names refuse. Byte bounds apply to bodies;
a future adapter must also bound allocations before yielding events. No automatic
redirect, retry, pagination, quota check, identity fetch or auth fallback occurs.
Quota reserve/missing-header checks also apply when headers arrived but the body
failed. Two consecutive transport/5xx failures stop; other complete statuses reset
the streak. Missing quota evidence after a received response stops the remaining
plan. Not-attempted request IDs and total received bytes are explicit in reports.

Index/tree/history caps belong to storage/publication and are not falsely rechecked
here on nonexistent publication trees. A future adapter and real reviewed identity
manifest require separate review; nothing here dispatches a live experiment.

## Supervised adapter (ticket 14)

`supervised_transport.py` targets POSIX/Linux pipes and implements the reviewed numeric-ID-only operational
profile. It is an importable API, with no public live command or workflow wiring.
The older `replay.py` remains synthetic and does not invoke the real connector.

Construct `SupervisedTransport` with the validated plan, trusted workflow ID and
matching approved/current full source revision. Pass an explicitly constructed
opaque `Token` to `collect`. These supplied values still require a trusted future
workflow adapter; matching strings and a Token object alone cannot establish their
provenance. This transport is scoped to one run: each planned request may start
once, bounded by the approved plan (at most seven workers; six in the operational manifest). Aliases never become fetch targets and a changed
numeric URL still changes request ID and invalidates old state.

A fresh isolated Python worker gets one bounded bootstrap over private stdin.
Its argv/environment never contain the token; only LANG is inherited, Python uses
-I/-S, unneeded descriptors close, stderr is discarded and no debug/request trace
is enabled. No proxy/netrc/gh/config identity discovery or default credential path
exists. The child explicitly connects DNS/TCP/TLS, emits Connected after handshake,
then sends one direct HTTPS GET with identity content encoding and actual approved
conditional headers. System CA verification and api.github.com hostname checks stay
enabled. No redirect/retry path exists.

The parent uses nonblocking bounded IPC and select with absolute connect/request/
batch deadlines, kills/reaps on timeout or cancellation, and requires clean worker
exit before exposing End. Cleanup has a one-second reap bound after kill; it does
not extend allowed network time. A blocking DNS/socket worker and a trickling pipe
cannot indefinitely stall the parent. OS process scheduling/reaping remains an
operating-system assumption, not a hard real-time promise.

Before HTTP header parsing, the limited socket reader bounds total wire headers
at 64,000 bytes and individual lines at 8,192. Retained public values keep the core
bounds. Body chunks are <=8,192; body cap is 8,000,000 with one possible consumed
rejection sentinel. IPC lengths are rejected before payload allocation. Core
received-byte metrics count forwarded body events, not that private overflow
sentinel or HTTP framing bytes. HTTPResponse handles transfer decoding; JSON bytes
remain exact. Duplicate Content-Length, TE+CL ambiguity, compression, malformed
chunk delimiters, chunk extensions and nonempty trailers refuse. This strict
profile can refuse otherwise legal HTTP responses; record and review such a refusal
rather than broadening it implicitly. Cumulative chunk framing has its own 64,000
byte cap, in addition to the initial header budget.

Tests add real local subprocess/pipe timeout, trickle, cancellation and cleanup
checks, plus fake socket parsing and core integration. They never connect outbound
or to a loopback HTTP server; any production socket creation in the parent tests is
blocked, and the internal bootstrap test supplies an invalid config before connect.
No real token is used. Parser compatibility has been exercised on the recorded local
Python version, not every Python 3.10+ release. Real TLS/DNS, GitHub route behavior,
workflow context provenance and the missing SQLite ID still need separate review.

## Inactive run package (ticket 15)

The staged manifest in docs/track/release-catalog/design/staged-manifest.json now
contains reviewed SQLite Browser identity 19416551. workflow_adapter.py still
refuses any missing identity before transport/token creation. This helper has no CLI or ambient token
lookup. The exact candidate workflow is catalog-collector.yml.proposed beside the
manifest, outside .github/workflows. See the tracked adapter-review-and-run-package.md
research report for review, approval boundaries and 48 offline checks. Malformed or
folded HTTP header lines now refuse before Python's permissive header parser.

Ticket 16 installs the separately approved workflow as
.github/workflows/catalog-collector.yml. Each live dispatch still requires explicit
authorization. The .proposed file remains the historical review artifact.

## Observation storage integration (ticket 17)

storage.py applies inert measured results to a bounded, validated byte tree. The
manual workflow now exports candidate/index.json, derived candidate/lookup.tsv
and candidate/bodies/ with
storage-report.json beside the original response evidence. See
docs/track/release-catalog/design/storage-collector-integration.md for format and
transitions. artifact_io.py reads closed candidate directories; publication.py
provides local-only atomic Git commits and pinned freshness-checked reads. Neither
has a network/remote publication path. No installer calls these helpers.

## Persistent delivery (ticket 18)

The manual workflow now accepts previous_publication: an exact release-catalog
commit, empty only for branch creation. It loads validated available observations
into conditional planning and applies storage against that prior. A separate
publisher job validates the same-run artifact and recomputes it before a normal
fast-forward push to release-catalog. See docs/track/release-catalog/design/catalog-delivery.md
for permissions, bounded ZIP/Git handling, conflict behavior and limits. No schedule
or installed-app integration is enabled.

## Read-only Python reference (ticket 19)

consumer.py returns one exact stored response for a reviewed URL, using either one
ref resolution plus a pinned index/body pair or an explicit --commit. Example:

```sh
python3 -B tools/catalog-collector/consumer.py \
  https://api.github.com/repos/obsidianmd/obsidian-releases/releases/latest \
  --metadata /tmp/am-catalog-read.json | jq -r .tag_name
```

Only body bytes go to stdout. --accept-stale requires the full COMMIT REQUEST_ID
BODY_SHA256 tuple from the stale refusal; it cannot bypass unavailable, future or
integrity failures. There is no direct upstream fallback or installer side effect.
See docs/track/release-catalog/design/catalog-consumer.md for scope and bounds.

## Shared shell reader (tickets 23–29)

The installed-user path is `modules/catalog.am`, distributed through AM's normal
shell module sync. It uses shell and existing utilities; neither Python nor jq
is required by the reader or migrated recipes. Read-only invocation from a checkout:

```sh
AMREPO=https://raw.githubusercontent.com/mareklangiewicz/AM/main-marek \
sh modules/catalog.am \
  https://api.github.com/repos/obsidianmd/obsidian-releases/releases \
  --commit FULL_PUBLICATION_SHA
```

It emits exact original response JSON only after pinning, freshness and integrity
checks. An unpinned call resolves one publication commit. Stale refusal prints the
exact `--commit SHA --accept-stale SHA REQUEST_ID BODY_HASH` arguments to repeat.
No stale flag overrides availability, integrity or future/unsupported timing.

The publication repository follows the selected **AMREPO**, just like the AM
package source. Our fork reads mareklangiewicz/AM, with no upstream-AM fallback.
Missing/empty, unsupported-host/local and malformed sources refuse before network
IO. The manager embeds the selected source in generated standalone updaters and
passes its current AMREPO explicitly during managed updates. An unprepared recipe
requires AMREPO in its environment. Upstream acceptance is not a fork dependency.
The [historical fork validation](../../docs/track/release-catalog/research/fork-shell-public-read-findings.md)
used a modified reader copy because of the now-fixed ownership defect; current
source-selection regression checks use the unmodified helper. See the
[implementation and ownership correction](../../docs/track/release-catalog/design/shell-consumer.md).

The ordinary x86_64 Obsidian, SQLite Browser and nvim installers and newly generated
updaters now invoke the shared
reader before app-state changes. The manager embeds its managed module location,
and processes normal all-app and explicit mixed batches sequentially. Each path
reports unchanged/updated/refused/failed; failures continue and aggregate to a
nonzero command status. Migrated apps share one source-bound publication pin and
lookup per command, with per-app freshness, exact stale consent and body checks. Existing
installed updaters are unchanged until explicitly migrated. Binary URLs and the
existing release-list selection filter are preserved; the appimageupdatetool
alternate metadata path is removed for this recipe.

The checkout-only `--catalog-version` mode from tickets 20–21 is retired. Its
[historical evidence](../../docs/track/release-catalog/issues/21-obsidian-live-read.md)
and the Python consumer remain references; that option is no longer accepted by
the app script. Use the shared reader for a read-only query. Invoking the ordinary
app script is an installer operation.

SQLite Browser uses its already enrolled exact `releases?per_page=100` alias;
its stable x86-64 AppImage filter and original GitHub binary URL are unchanged.
Like Obsidian and nvim, it refuses before app-state changes if catalog data is
unavailable or stale. Normal batches continue with other apps after refusal. Existing installed
legacy updaters are not rewritten by a repository recipe change. No additional
source collection or runtime service is needed for this migration.

See [normal batch update semantics and verification](../../docs/track/release-catalog/design/normal-batch-updates.md).

## Accepted daily refresh policy (ticket 40)

The schedule is once daily at 03:17 UTC (`17 3 * * *`), using the enrolled
source requests and separate exact-prior publisher. The reviewed
source pin remains required. Hourly pilot window/count variables are not part
of the daily controller. Activation follows the current bounded pilot's shutdown;
local code alone does not change the pinned remote workflow or installed helper.

Shell and Python readers now accept observations through the inclusive **48-hour**
boundary measured from actual validated_at. The extra day provides headroom for
GitHub scheduling delays, not a promise of two-day availability. Failures retain
prior ages; beyond 48 hours, the same exact publication/request/body stale consent
is required. Future, unavailable, malformed and corrupt observations still refuse.
Neither collection nor metadata hashes independently authenticate app binaries.

## Static recipe-family inventory

`python3 tools/catalog-collector/recipe_inventory.py --output /tmp/recipe-family-inventory.json`
reads the four architecture recipe directories and the reviewed manifest without
running shell, filters or HTTP. It reports marker buckets, normalized source
frames, exact alias coverage and concrete AppImage/plain-executable review queues.
It does not enroll sources, prove asset compatibility or migrate installed apps.
The report records input revision/content and script/manifest hashes. See the
[measured findings and next batches](../../docs/track/release-catalog/research/recipe-family-inventory.md)
for method limits, projected versus actual deletion, and capacity/enrollment gates.


## Whole-command container tests

`./test/e2e/run` adds opt-in Debian/dash and Fedora/bash coverage around the whole
installed AM/AppMan executable, real module dispatch, sudo/environment clearing,
standalone updater and real no-argument sync. Containers use retained metadata,
inert binaries and strict offline external-command adapters with runtime networking
disabled. See [runner, scenarios and limits](../../test/e2e/README.md). This
supplements the Python suite, whose narrower integration tests extract functions
and stub manager services.

## Seven-source offline preparation (ticket 47)

The planner now caps a run at seven sources. Manifest validation retains the
six-source historical profile and accepts a separate seven-source candidate;
transport/storage/publisher count checks bind to the approved plan. Byte/time
caps and all-source publication success requirements are unchanged.
`design/staged-manifest-am-utils.json` under the release-catalog tracker adds the
reviewed am-utils endpoint while preserving the six original rows. The October 31
[rollout package](../../docs/track/release-catalog/design/am-utils-seven-source-rollout.md)
prepares the local operational manifest and controller hash for that exact candidate.
Published operation remains six-source until the package's separately approved
push, first collection/publication and daily source repin. See the historical
[prepared contract, tests and measured limits](../../docs/track/release-catalog/design/am-utils-seven-source-preparation.md).

### Offline Brave candidate (2026-10-31)

The planner cap is eight; manifest parsing preserves the six- and seven-source
historical profiles and accepts an eight-source candidate. The operational
manifest and dispatcher remain the accepted seven-source bytes. Only
`design/staged-manifest-brave.json` proposes Brave, based on retained public
identity/release evidence and twelve original selector checks. Exact manifest hash
approval still gates collection, with no ninth source and no increased byte/time
limits. See the [offline package](../../docs/track/release-catalog/design/brave-eight-source-preparation.md).

## Thousand-recipe throughput continuation

Ticket [67](../../docs/track/release-catalog/issues/67-expand-appimage-migration-throughput.md#verified-identities)
records actual metadata, exceptions, the exact prepared inventory and rollout state.
`large_evidence.py` is an explicitly invoked, frozen-queue evidence runner;
`large_migration.py` verifies original selectors and prepares compatible patches.
It does not apply recipes. `large_replay.py` validates saved-body ZIP/artifact/Git
publication offline, with explicitly synthetic conditional repeats.

`shards.py` composes at most 32 independently bounded storage trees under one
atomic publication. Each keeps the existing 52-source, 64-KB manifest, 50-MB tree
and per-body limits. Root index and lookup remain <=2 MB; compressed Git objects
remain <=128 MB. The root's aggregate uncompressed ceiling follows the explicitly
reviewed shard inventory. Shell reader paths and TSV framing stay unchanged.
The Python reader supports selective schema-2 root/shard reads. Legacy schema-1
publications continue to work.

`catalog-shards.yml` binds the entire inventory, collects at most four shards at
once and publishes only after every same-run artifact recomputes against the
exact parent. Each run remains separately authorized. Local candidate code and
scheduled-dispatch edits do not by themselves change the remote source pin.
After applying the compatible recipe patch, the explicit full-batch inert
install/update check is `python3 -B tools/catalog-collector/check_large_lifecycle.py -v`.

## YAML source adapter candidate

`yaml_adapter.py` prepares numeric list plans from the reviewed manifest,
coalescing latest/tag/list endpoint variants by repository identity. Requests
are unconditional, with explicit `per_page` and page 1. `collect_one_page`
uses the existing collector and a caller-supplied transport/opaque credential,
merges original receipt times into retained format-2 facts, and returns a fully
validated YAML candidate tree plus collection/source outcomes. It has no CLI,
ambient credentials, workflow integration or publication side effect.

Supply an explicit file allowance, reviewed app map and repository identities,
and an actual immutable source revision. Existing pinned YAML can be loaded with
`yaml_publication.load_local`; bootstrap/enrollment is the caller's responsibility.
A transport stop leaves unattempted repository state unchanged and reports their
numeric IDs. Pagination links must retain numeric identity, list route, page
size and consistent relations; malformed metadata fails that source. Completing
page 1 with a next link is successful partial scope, never full history.

`collect_one_page` implements the default one-page scope. `collect_scoped` adds
finite page limits or `all`, optional explicit all-only reconciliation and shared
transport budgets. Actual AM app enrollment/bootstrap, accepted production budgets
and reviewed workflow/artifact staging remain necessary before operational use.
It imports the current shared YAML candidate components rather than copying
another normalizer/writer. No operational workflow imports this module.

Offline checks: `python3 -m unittest discover -s tools/catalog-collector -p test_yaml_adapter.py`.

`collect_scoped` takes a `transport_factory(page_plan)`, constructing the existing
`SupervisedTransport` for each validated page plan with trusted workflow identity
and reviewed source/approved revisions. It requires explicit aggregate request
and body-byte allowances, caps elapsed transport time at at most 300 seconds,
and passes the shared absolute deadline to existing transport limits. The default
per-source request ceiling is 64; all numbers remain caller policy/trial inputs.
Responses stream through the existing bounded collector; the budget counts body
chunks, including the chunk crossing the allowance, and rejects that source.
This is logical byte accounting, not a filesystem or exact wire-byte quota.

Pages are acquired lazily by the retained merge: malformed bodies, duplicates or
invalid links stop that source without acquiring another page. A later failure
rolls back all fetched facts/times for that source. Finite completion on its last
allowed request succeeds. An incomplete scope at a request, byte or deadline
boundary fails; unattempted sources retain prior state and are reported by ID.
Source-local caps allow other sources to proceed; quota/auth/protocol stops and
two consecutive transfer/server failures stop the run. Reader validation/staging
is outside the transport elapsed deadline; no additional process supervisor was
introduced.

`yaml_enrollment.enroll` derives the format-2 app map from current marked shared
recipes and exact aliases in a reviewed manifest. It reads static APP and
CATALOG_ALIAS assignments without shell evaluation, coalesces architecture paths
by app name, rejects identity conflicts, and reports recipe hashes/excluded paths
for review. `shared_recipes(root)` scans only the four AM recipe directories.
Readable bootstrap names come from the manifest's enrolled owner/name aliases;
they are display identities, not a new canonical-name acquisition.

`prepare_pinned` loads an exact local format-2 commit (or explicitly bootstraps
with commit=None), keeps previous repositories and aliases, enrolls additions and
rejects reassignment. `collect_pinned` connects that state to scoped collection
and returns the previous pin in its report. Neither updates Git refs. A later
publisher must compare-and-swap against that same pin; this is still a source
candidate, with workflow staging/publication unwired.

New identities carry no collection/observation metadata until actually attempted.
If any remain unattempted, `IncompleteBootstrap` refuses the entire candidate and
exposes its aggregate `.report`, including bootstrap_unattempted_repositories.
The caller can retain diagnostics and retry; it cannot publish placeholder
attempts. Actually attempted failures may be represented honestly with collection
failure metadata and no last-success/observations. Existing pinned sources can
remain unattempted unchanged. File allowance remains an explicit trial/policy
input, and no remote format-1-to-2 conversion is implicit.

Enrollment/pinned checks: `python3 -m unittest discover -s tools/catalog-collector -p test_yaml_enrollment.py`.

`yaml_staging.py` adds an inactive workflow/artifact source candidate. It checks
manual run context plus manifest/policy/scope hashes, stages a private normalized
YAML package with a receipt, and verifies closed directory layout, enrollment,
pinned state and preservation rules. `yaml-policy.json` supplies explicit review
limits. See [the staging design](../../docs/track/release-catalog/design/yaml-staging.md)
and inactive `catalog-yaml-staging.yml.proposed` for boundaries and default scope
hashing. No active workflow imports this module; download authentication, remote
prior loading and publication remain unwired.

## Inactive YAML artifact acquisition candidate (ticket 92)

`yaml_delivery.acquire` reuses authenticated `delivery.download_artifact` with the
inactive proposal's `yaml-bootstrap-RUN-ATTEMPT` name and an explicit ZIP cap.
Trusted caller context and upload artifact ID/digest are required; receipt values
are not an authentication source. GitHub metadata must match repository, run,
source SHA, branch, artifact name and digest; downloaded bytes must hash to that
digest before decoding. No live API capability was exercised by the offline tests.

The decoder bounds ZIP central-directory size/count before parsing, then accepts
only `receipt.json`, candidate YAML and optional structural directories. It reads
store/deflate members into bounded data, never extracts paths, and refuses duplicate,
traversal, NUL, symlink, executable, special-file, encrypted and extra members.
Uncompressed YAML/receipt policy bounds apply independently of the ZIP envelope.
The ZIP envelope allows tree + receipt + 1,000,000 bytes of framing/compression
overhead (136,266,304 bytes for the candidate profile). Excess is refused rather
than inferred safe from compression ratio. ZIP64 and multidisk are unsupported.

Full staging verification runs before creating a new private output directory;
no failed authentication/verification leaves accepted output. The caller must
already have the exact-pin local prior. Remote prior acquisition, publication CAS,
reviewed source promotion, runner provisioning and workflow activation remain
unwired. Only YAML belongs in future catalog history; receipt stays artifact-only.

Offline checks: `PYTHONPATH=tools/catalog-collector:tools/catalog-yaml-prototype python3 -m unittest test_yaml_delivery`.
