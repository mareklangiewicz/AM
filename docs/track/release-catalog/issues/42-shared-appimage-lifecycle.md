# Share AppImage install/update implementation and shrink two recipes

Type: task
Status: open
Triage: ready-for-agent

## Accepted direction and priority

Marek endorsed the design of small recipes describing catalog input, asset
selection and package format, with AM owning common lifecycle mechanics, and
asked to record it in the tracker. This is the next implementation task; prove
it with Obsidian and SQLite Browser before further read-call-only migrations or
batch routing work. Independent of tickets 37/41's timed operational transition.
No implementation or deployment has been performed by this tracker update.

## Problem

The current shared reader removes per-app metadata transport concerns but recipes
still repeat directory/remover creation, binary transfer/replacement, launcher/icon
extraction, version comparison, retry/repair and heredoc-generated updaters. The
asset-selection filter and source defaults are duplicated inside those updaters.
Moving only catalog reads leaves most recipe maintenance cost intact.

## Implementation scope

Create one shell implementation for the common AppImage lifecycle, delivered by
AM's existing managed-module mechanism. Convert x86_64 Obsidian and SQLite Browser
together to prove a small interface with two real callers. A recipe should need
only app identity, exact catalog alias, package format and its selection function,
plus an explicit hook only for a real app-specific difference.

Install and update must invoke the same asset-selection implementation. Retain
the small trusted recipe/configuration in installed state and use a small generated
standalone launcher to call the managed implementation. Do not generate another
copy of selection/download/update logic or require the source checkout at runtime.
The precise names/files/interface belong to implementation; the illustrative
APP/PACKAGE_KIND/CATALOG_ALIAS/select_asset snippet is not an immutable schema.

Central implementation owns accepted metadata preflight, standard paths/remover,
version comparison, upstream binary download, interrupted-download retry,
replacement, checksum-repair behavior, AppImage desktop/icon extraction and
launcher setup. Share actual install/update mechanics; remove displaced duplicate
code rather than adding a wrapper around old recipe bodies. Keep genuine format
or app exceptions explicit instead of growing a configuration language or a long
list of hypothetical optional hooks.

## Contracts to preserve

- Catalog ownership follows AMREPO; validate pin/freshness/integrity centrally,
  preserving exact response bytes and explicit exact stale consent. Current local
  accepted policy is 48 hours; do not rewrite historical observation times.
- App-specific release/architecture/channel filtering stays in the consumer;
  preserve both existing pipelines and their selected original upstream URLs.
  Collector does not become a per-app version/download resolver.
- Metadata/filter refusal precedes app/version/remover/link mutations, including
  incomplete-install cleanup. Failed download does not destroy the working app;
  retry and recorded checksum repair keep working. Notification failure nonfatal.
- Preserve managed versus standalone AMREPO behavior, literal escaping and helper
  path embedding, including privilege environment clearing, AM/AppMan paths and
  no inherited configuration. Do not fetch runtime code from an updater.
- Catalog JSON remains inert data. Installed recipe code is trusted AM recipe
  code, not code reconstructed/evaluated from the observation body.
- Use shell and existing supported utilities; no Python/jq runtime, full checkout,
  external service, binary mirror or new independently operated metadata source.
- Keep optional binary verification semantics distinct from catalog hash checks.
  Preserve unrelated legacy callers; remove only actually displaced machinery.

## Acceptance and verification

1. Both recipes lose their duplicated common lifecycle and generated update body;
   each retains one selector. Installed standalone launchers use the same managed
   implementation as install/update with coherent normal module delivery.
2. Compare total client/runtime/installed generated code before/after, including
   new modules and manager changes. Show actual duplicated code removed and the
   remaining recipe interface. Do not claim simplification from recipe length
   alone or hide a larger framework behind a tiny recipe.
3. Exercise the real shared interface and actual install-module/manager delivery
   in temporary roots using retained bytes and stub binary/network operations.
   Cover both apps, install/update/no-change, AppMan/system paths, standalone source
   persistence, refusal before mutation, exact stale consent, missing helper,
   failed download/retry and checksum repair. Replace obsolete recipe-level tests
   with interface/integration coverage; do not maintain two test implementations.
4. Syntax/lint and relevant existing suites pass; document supported formats and
   actual exceptions. Archive historical evidence unchanged.

No new collection, endpoint enrollment, workflow dispatch/publication, source push
that disturbs the pinned pilot, installed migration or host app execution is needed
for this work. Per Marek's preference, provide concrete commands for any later
privileged host changes. Source changes can be committed locally while the pilot
continues. Follow-on tasks: [43](43-migrate-nvim-shared-lifecycle.md),
[44](44-normal-batch-catalog-updates.md), [45](45-recipe-inventory-and-migration-batches.md).
