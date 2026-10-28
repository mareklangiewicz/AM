# Verify post-download filesystem failures and retry

Type: task
Status: resolved
Triage: ready-for-agent

## Scope

User authorized tracker cleanup and investigation of post-download chmod, binary
replacement and version-write failures. Exercise the actual shared lifecycle and
saved standalone updater with inert downloads in temporary roots. Establish
failure reporting, surviving state and retry behavior; fix demonstrated defects
with regression evidence. Do not promise atomic multi-file rollback. No live
requests, source push/repin, workflow or installed-host changes.

## Investigation

Existing lifecycle tests cover transfer failures but do not explicitly inject
these three filesystem failures. Use the existing retained-data shell fixture
and real lifecycle rather than another harness/module extraction.

## Answer

Added four tests in `tools/catalog-collector/test_appimage_lifecycle.py`, covering
six failure/retry cases through the actual recipe and generated standalone updater:

- Update chmod failure: nonzero, old binary bytes/mode and version preserved;
  complete downloaded staging file retained. Retry installs an executable and
  removes staging.
- Update replacement failure: nonzero, old binary/version preserved; executable
  staging file retained. Retry completes replacement and version recording.
- Update version-write failure: a real shell redirection failure (a directory at
  the version path) returns nonzero after binary replacement. The new executable
  remains, staging remains, and retry succeeds after the obstruction is removed
  and old version metadata restored. This is partial completion, not rollback.
- Fresh install: each of the same three failures returns nonzero before creating
  the standalone updater or command launcher. Removing the obstruction and
  rerunning installation completes normally; generated updater has three lines,
  staging is removed, and normal removal succeeds.

No production defect was demonstrated and no production fix was necessary.
Command adapters inject chmod/move failures before mutation; this does not model
partial cross-filesystem moves, ENOSPC after version truncation, sudden process
termination, or whole-manager behavior under these exact faults. Version-write
coverage establishes failure reporting and recoverability, not atomic metadata
or multi-file durability. All downloads and catalog requests are offline fixtures
in temporary roots; no installed host app was touched.

## Validation

The four new tests pass under the host's `/bin/sh` (dash), and under bash using
an in-memory `run_script` override plus a temporary `sh` symlink so the generated
updater's `exec sh` also uses bash. No production or tracked fixture patch was
needed. Focused execution covers six failure cases and six successful retries
per shell. Host-safe focused command, from `tools/catalog-collector`:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v \
  test_appimage_lifecycle.AppImageLifecycle.test_chmod_failure_preserves_binary_and_version_then_retry \
  test_appimage_lifecycle.AppImageLifecycle.test_replacement_failure_preserves_binary_and_version_then_retry \
  test_appimage_lifecycle.AppImageLifecycle.test_version_write_failure_reports_partial_update_and_retry_recovers \
  test_appimage_lifecycle.AppImageLifecycle.test_fresh_install_filesystem_failure_then_retry
```

Broader validation: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q
 test_appimage_lifecycle test_batch_updates` from `tools/catalog-collector`
passes **94 tests** in 192.062 seconds. `git diff --check` passes. Existing container
matrices were not repeated: production and container harness code are unchanged.
