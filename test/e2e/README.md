# Installed AM/AppMan e2e tests

Opt-in disposable-container tests, following mysh's environment-image/read-only-
source/retained-log pattern. They execute the **whole installed manager**, not
functions sliced out of `APP-MANAGER`.

```sh
./test/e2e/run                 # Debian and Fedora
./test/e2e/run debian          # one target
ENGINE=docker ./test/e2e/run   # Podman is the default
E2E_OUT=/tmp/am-e2e ./test/e2e/run
```

Image builds download distribution packages. Test containers run with
`--network=none`; the only writable host mount is the results directory. The
checkout is mounted read-only at `/src`, and installed manager/module copies are
checked against their original hashes. AM operates at its real `/opt` and
`/usr/local` paths inside the throwaway container. No privileged container or host
app-directory mount is used. Container sudo policy and adapters are test-only.

## What runs

- Debian uses dash as `/bin/sh`; Fedora uses bash. Both retain GNU utilities,
  including the fractional UTC date behavior required by the reader. This is an
  x86_64 matrix; it does not claim other-architecture or BusyBox support.
- A normal `e2e` user invokes system AM and real passwordless container sudo.
  A separate AppMan home proves unprivileged installation and helper/source
  delivery without writing a system app directory.
- The manager and its modules are copied byte-for-byte from the checkout into
  normal installed locations. Tests do not patch manager functions or recipes,
  inject shell functions, or stub sync/verification/discovery. The ordinary
  installer performs its own production recipe transformations and saves the
  standalone three-line updater.
- External curl/wget operations use a strict fixture adapter: known repository
  files, exact retained catalog observations and explicitly inert binary bytes.
  Unknown requests fail and are recorded. Wget version detection and ordinary
  date operations use the distro tools; only the reader's clock is controlled.
  Notifications deliberately fail to exercise the nonfatal desktop path.
- The synthetic executable implements AppImage extraction of a desktop entry/icon
  and an inert `--version`. Optional binary-digest verification uses its actual
  checksum. A small legacy recipe is installed through normal AM dispatch to
  exercise a mixed batch; it is not a migrated catalog recipe.

Eight scenarios on each target cover:

1. System recipe installation, expected retained URL, desktop extraction, binary
   symlink, source embedding, real checksum verification and standalone updater.
2. Unprivileged AppMan installation and standalone helper/source delivery.
3. Failed binary download preserving the working binary/version, retry and
   same-version checksum repair.
4. Body-integrity/stale refusal preserving app files and interrupted work, then
   exact stale consent through the real CLI.
5. Initial stale install creating neither app directory nor binary launcher.
6. Mixed catalog/legacy continuation and aggregate failure, with one command pin
   and lookup and independent body checks.
7. Missing optional digest evidence succeeding versus a recorded checksum
   mismatch failing.
8. No-argument update preserving failure through actual manager/module sync,
   repairing an obsolete installed module and using the configured repository for both code and catalog reads.

The existing Python catalog tests remain the faster, more detailed retained-data
regression suite. This matrix closes the whole-command, privilege/environment and
cross-distro gap; it supplements those tests.

## Results

Each invocation creates `out/<UTC timestamp>-<runner PID>/<target>/`, preserving
failed and repeated runs separately. It contains:

- build log and image ID;
- OS and `/bin/sh` identity;
- source hashes and structured scenario result;
- each command's arguments, stdout, stderr and exit status;
- one small transport record per request, including unexpected requests.

Logs are ignored by Git. The runner returns nonzero for a failed build or scenario
and continues to the other target. `container-test.sh` preserves the Python status
through `tee`. Scenarios refuse direct host execution without the container marker.

## Limits

This proves installed shell control flow with controlled external IO. It does not
exercise real HTTP/TLS, current upstream availability, an actual AppImage/FUSE
runtime, GUI behavior, the public AM bootstrap downloader, or publication/scheduling.
Retained observation timestamps keep their meaning; the test clock is explicitly
simulated and says nothing about current operational freshness. Production recipes
are served unchanged; binary downloads are synthetic. No host app or helper rollout
is performed, and no production workflow is enabled.

The old `regress/` suite uses live app downloads and clears app/binary locations.
This runner does not invoke it or make it a host pre-commit gate. No remote CI
workflow is added while the bounded catalog pilot is active.
