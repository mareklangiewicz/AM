# Proposed opt-in Obsidian update adoption

Ticket 22. Proposal, not accepted policy or implemented update behavior.

**Superseded adoption recommendation (2026-10-27):** Marek accepted a shared shell
reader and shell-friendly published lookup metadata, no consumer Python runtime,
and small simplifying recipe/generated-updater diffs. Do not implement the Python
zipapp/local-runtime packaging or expand the checkout-only query mode described
below. [Ticket 23](../issues/23-shell-consumer-and-small-recipe-migration.md) is the
current next-session frontier; [the spec](../spec.md#accepted-adoption-direction-2026-10-27)
records the accepted direction. The source observations below remain relevant and
the original proposal is retained as historical evidence.
Source inspected: 6177083f2 on main-marek. Tickets 20–21 established a working
checkout-only read query; they did not provide consumer distribution or change
ordinary updates. Keep catalog observations separate from app selection policy.

## Actual constraints

- APP-MANAGER's _update_app backgrounds _update_run_updater. That function
  normally discards updater stdout/stderr, patches the installed updater, can
  delete its version file after checksum failure, then verifies and prints a
  success-looking elapsed-time message without gating it on updater exit status.
  Catalog refusal must not enter this path and be presented as successful update.
- _use_update performs online/key/cleanup/quota work before launching updates.
  Catalog preflight must precede mutation for the selected catalog app. Simply
  setting an environment variable around AM-updater would not achieve this.
- _sync_modules downloads shell .am modules from MODULES_SOURCE. It does not
  distribute tools/catalog-collector or ensure a coherent Python module set.
  A consumer.py file alone is insufficient: its local import closure is reader,
  public_http, storage, manifest and collector (seven Python files total).
- programs/x86_64/obsidian embeds a standalone AM-updater in a quoted heredoc.
  Installed scripts cannot locate a checkout by walking two parent directories.
  Its appimageupdatetool fast path can update through another metadata source
  after version selection. A catalog-selected URL does not control that path.
- modules/install.am patches downloaded scripts, executes them and retains the
  original app script under .am-installer. Existing copies may differ from the
  reviewed source. Do not select an adapter solely from the app directory name.

## Recommended first usable slice

Limit support to explicit single-app Obsidian x86_64 opt-in. Keep the ordinary
updater as the default. Prepare the support below in repository code and temporary
fixtures before any installed-app migration is authorized.

1. Distribute a coherent consumer runtime independently of observation data.
   Build a Python zipapp from the explicit seven-file import closure above, with
   __main__ delegating to consumer.main. Pin the code revision in build metadata;
   verify the artifact before activation and replace it atomically. The publication
   branch remains inert index/body data and never supplies executable runtime code.
   Keep Python 3.10+ and /usr/bin/curl dependencies explicit. This proposal retains
   the implementation's POSIX/Linux scope. First prove a locally built artifact
   offline; remote delivery/update trust is a separate review, not a download hook
   hidden in an app updater.
2. Have AM resolve its configured runtime by an absolute, explicitly managed path.
   Do not infer it from the app directory or accept an arbitrary ambient executable
   variable in a privileged run. No runtime network bootstrap during app updates.
   Missing/incompatible runtime refuses opt-in with a visible actionable error.
3. Add a foreground preflight for the explicitly selected supported app before
   existing update mutations or workers. It resolves once or accepts a full pin,
   runs the app's reviewed filter and yields an in-memory URL plus observation
   metadata. Unavailable, invalid, stale or empty selection skips that app visibly
   and returns nonzero. It must not fall through into the legacy updater. Existing
   direct operation remains a separate explicit user choice.
4. Freshness refusal prints the exact commit/request/hash acceptance tuple.
   A subsequent explicit invocation supplies that tuple and pin; never translate
   a generic yes, environment variable or saved boolean into blanket stale consent.
   No background prompts or persistent consent store in the first slice. Consent
   cannot bypass time, availability or integrity errors. Revalidate freshness before
   download if preflight work can materially delay the action; a receipt is not an
   unlimited authorization to reuse a once-fresh URL.
5. Only a reviewed catalog-capable Obsidian adapter may consume this result.
   It must bypass appimageupdatetool in catalog mode, use the selected URL directly,
   and propagate refusal/failure. Preserve the current app asset-selection filter;
   do not rewrite arbitrary installed shell pipelines or execute saved installer
   text to discover a filter. Enrollment needs an explicit supported adapter/version
   marker and a reviewable install/migration action; existing updaters stay legacy
   until that separate action is requested.
6. Report skipped/refused, unchanged, updated and failed outcomes distinctly.
   Do not print updated on a catalog refusal, checksum failure or updater failure.
   Existing binary verification is a separate concern: a catalog body hash proves
   consistency with the publication, not independent binary authenticity. Audit
   _use_verify's source/network behavior before claiming a catalog update makes no
   additional source metadata calls.

## Next implementation boundary

Build the explicit runtime artifact locally and exercise its actual CLI offline
against retained publication evidence through an injected test transport. Verify
its seven-file closure, execution from an unrelated working directory, refusal
semantics, metadata and exact bytes. Use the real consumer modules, not a second
reader implementation. Do not add a live bootstrap or alter installed state.

After that, implement a foreground single-app preflight with temporary fixture
roots and stubbed app operations. Cover stale refusal and exact acceptance,
unsupported/missing runtime, no mutation before successful preflight, no fallback,
no appimageupdatetool in catalog mode, and failure propagation. The final command
spelling and runtime installation path should be settled alongside AM/AppMan
ownership rules before activation. No fleet flag, default migration, scheduling,
new endpoint enrollment or upstream proposal is implied.

## Alternatives considered

Using the current checkout-relative app mode directly from installed updaters
requires retaining a checkout and couples app layout to repository layout. Fetching
individual Python files through shell module sync permits mixed revisions. An
updater-only environment switch hides stale diagnostics and leaves early AM
mutations/quota handling intact. These do not meet the first slice's boundary.
