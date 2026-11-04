# Format-2 network and manager source candidate

Ticket 98. Isolated `prep/yaml-consumer-integration` branch, based on 7e62a68cc.
This changes candidate runtime source and five recipes, not main's active source,
installed AM, workflow activation or a published catalog. It is not a complete
format transition or an accepted selection/capacity/consent policy.

## Shared runtime distribution

Four plain files under modules/ are the maintained runtime:

- catalog-yaml.am: configured-source acquisition and selected-record acceptance.
- catalog-yaml-reader.am: existing bounded shell validator/projection wrapper.
- catalog-yaml-parser.am: existing POSIX awk schema reader with asset facts.
- catalog-yaml-policy.am: existing five named-cohort policy reference in POSIX awk.

The awk files are trusted source, not downloaded catalog data. Their .am names
and AMCLI comments let the existing manager module discovery/sync/cleanup ship
and retain them. APP-MANAGER declares all four module names; install.am checks
all dependencies before running a format-2 recipe and embeds its installed
helper path. tools/catalog-collector retains compatibility symlinks for the two
awk entry points and a shell trampoline for reader.sh. There is one maintained
parser/policy, rather than copies that can drift between experiments and hosts.

## Exact-pin raw-file acquisition

The helper accepts ARCH/APP followed by --commit SHA and/or the proposed
--accept-stale-release SHA REPOSITORY_ID RELEASE_ID ASSET_ID OBSERVED_AT.
It rejects old format-1 --accept-stale consent, unsupported policies/options and
repeated explicit commits/waivers. Its stale diagnostic prints an exact retry.
The five named policies are the unaccepted proposals from ticket 96; no generic
translation of legacy selectors or /latest semantics is introduced.

AMREPO supplies the selected owner/repository, including branch names containing
slashes. With no explicit pin the helper resolves that repository's release-catalog
ref once; apps.yaml and the selected repositories/ID.yaml come only from the
resulting exact commit. Empty, local or unsupported AMREPO refuses. There is no
upstream-AM, direct-API, format-1 or other-source fallback. No Git checkout,
Python/jq, credentials or new host dependency is used by the client path.

Transport follows existing format-1 restrictions: curl -q, HTTPS, no proxy,
redirects/retries or credentials, identity encoding, explicit Accept/API-version,
10-second connect/30-second transfer limits, HTTP 200 only, max-filesize and a
file-size rlimit. Ref allowance is 128 bytes; YAML input and projected output use
the unchanged 2 MiB trial cap. Private umask/spooling prevents partial output.
Original scalar URLs survive decoding unchanged; data is never eval'd or sourced.
There is no new consumer worker/watchdog/reservation framework.

A single date call returns UTC epoch seconds and ISO time. Cooperative checks
refuse regressed clocks or reads over 90 seconds. After acquisition/projection,
policy selects first and then checks that release's effective observation.
The final clock triggers a second check over the same facts before output;
crossing freshness during acquisition/selection cannot grant earlier acceptance.
Exactly 48 hours is fresh; future observations refuse. This is ordinary elapsed
checking, not hard supervision or a whole-process-tree deadline claim.

## Manager, installer and updater handoff

Only these candidate recipes opt into CATALOG_FORMAT=2 and an explicit trusted
CATALOG_RECIPE: x86_64/obsidian, x86_64/nvim, aarch64/nvim,
x86_64/nvim-nightly and aarch64/nvim-nightly. The shared lifecycle verifies the
recipe/app binding, calls the YAML helper, checks its six-line structured result
and uses its original URL as version identity. All acceptance precedes cleanup,
download or replacement. Nightly REFRESH_ALWAYS, normal same-URL skip, checksum
repair and failure/retry behavior use the existing lifecycle body.

Install parsing removes catalog option operands from the legacy app-name splitter
and forwards them as an argument array through privilege execution. It persists
AMREPO and installed helper/module paths in the recipe used by the generated
standalone updater. --force-latest refuses for these named policies rather than
silently rewriting an unused raw-API alias. An early refusal exits nonzero through
the real installer dispatch. Icons and AppMan path/source binding remain supported.

Batch update accepts the distinct selected-release waiver and runs the existing
sequential managed/legacy dispatcher. Its private AM_CATALOG_SESSION contains a
yaml-v2 namespace bound to the selected source and resolved commit. It shares
only acquired apps/repository bytes; every selection revalidates files, reruns
policy and checks the current clock/consent. Neovim stable/nightly share one
repository acquisition. Acquisition failure latches the command; stale consent
failure is per selection. The manager continues legacy/other apps and aggregates
failure without preflight cross-app cleanup. Each standalone helper removes its
own scratch; the manager owns command-session cleanup. Installer invocations
still acquire independently; no parallel/shared persistent cache is introduced.

## Verification

All transport is a local fake curl reading saved normalized fixtures from an
actual temporary bare Git repository. No request was made to GitHub. Fake binary
downloads create inert AppImages only within disposable roots. AM external
services are stubbed; the actual install module and actual manager dispatch,
update, module sync and cleanup functions execute.

- 11 new integration groups pass: all five real-recipe install/updater paths;
  AppMan/missing-module refusal; exact stale installation consent and option
  forwarding; batch pin/document reuse and per-selection waiver; failed transfer
  latching/legacy continuation; malformed/oversized refusal; nightly/repair/retry;
  source override; tip movement; sync/cleanup with no Git/Python/jq runtime;
  final-clock/later-app checks and unsupported-option refusal.
- 80 format-1 lifecycle compatibility, 15 format-1 batch and 17 format-1 shell
  consumer checks pass. Compatibility fixtures explicitly remove the cohort's
  new mode declarations; the new suite exercises actual format-2 declarations.
- Eight prior portable cohort/lifecycle groups, nine reader groups, nine enrollment
  and twelve staging checks pass. The portable cohort matrix retains three awk
  implementations and three shell entry points at the ticket-97 scope, not a full
  network-client/platform cross product. No fresh capacity benchmark is claimed.
- The 11-group integration run preceded the final stale retry wording change;
  targeted stale-install diagnostic/forwarding coverage passes afterward.
- ShellCheck (shell files), shell syntax, Python compilation and whitespace pass.

Initial test runs exposed stale fixtures: importing test classes accidentally
collected unrelated compatibility suites; the old batch date patch no longer
matched the clock stub. Explicit module imports and a format-aware date stub
correct those defects. One new real installer refusal test caught a returned
failure being swallowed by dispatch; the named-policy guard now exits nonzero.
No failing output is treated as passing evidence.

## Promotion and transition boundary

470 enrolled recipe paths still require format-2 policy/migration work. A single
release-catalog ref cannot be switched to format 2 while those format-1 consumers
remain dependent on lookup.tsv/raw bodies. Separate code paths and a private
cache namespace do not solve publication or already-installed consumer migration.
There is no accepted mixed-format rollout, dual-publication scheme or empty-prior
migration bypass here. Source code is not ready for operational activation.

Next source work should review the integration candidate, then expand explicit
policies/migrations and prepare exact consumer/source pins, installed-updater
migration, stale UI acceptance and rollback/transition. Capacity acceptance,
maintainer promotion, live capacity acquisition, workflow activation/publication,
repin and natural-run acceptance remain separate. main-marek production runtime
source and both active workflows remain unchanged by this ticket.
