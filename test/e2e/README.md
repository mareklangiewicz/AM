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

Fifteen scenarios on each target cover:

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

9. Neovim stable/nightly installation from retained observations, repeated nightly
   download at its unchanged URL, standalone updater, failed transfer/retry and
   stale refusal, preserving a user-level nvim symlink and configuration sentinel.

10. Partial binary transfer writes truncated staging bytes and fails, preserving
    the working installation; retry replaces it with the complete fixture.
11. Normal confirmed removal and reinstall in both system AM and unprivileged
    AppMan, removing app files/command symlink/desktop entry while preserving
    user configuration, then checking the reinstalled standalone updater.

12. Installed manager repository changes select the new catalog repository while
    standalone updaters keep the original embedded source; transport traces verify
    both choices without depending on different fixture contents.
13. Exact inclusive 48-hour freshness acceptance and refusal one microsecond beyond
    it through the installed CLI. Failed acceptance preserves the installed tree;
    successful unchanged checks may refresh optional checksum evidence.

14. Unprivileged AppMan mixed batches: catalog-integrity refusal, legacy updater
    failure and binary-transfer failure each report aggregate failure while later
    apps continue. Successful retry, one shared pin/lookup, user ownership and
    user launchers are checked through whole installed commands.

15. Abrupt SIGKILL of an AppMan command group after partial download staging,
    for fresh installation and existing-app update. Normal retries complete;
    installed files, launchers and user configuration survive interrupted updates.
    This exercises one controlled interruption point, not general crash durability.

Optional real-binary startup checks (cached matrix images required):

```sh
./test/e2e/neovim-smoke /opt/nvim/nvim /opt/nvim-nightly/nvim-nightly
```

This mounts only the specified executable read-only and uses network-disabled,
read-only containers with disposable writable homes/extraction state. It runs
`--version` and headless startup with `-u NONE -i NONE` on both distributions.
It does not load host plugins/configuration or download a new upstream binary.

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

## Native Termux target

```sh
./test/e2e/run termux
./test/e2e/run termux debian fedora
E2E_TEST=TermuxCLI.test_read_only_am_falls_back_without_sudo ./test/e2e/run termux
```

Termux is explicitly selected; the default remains Debian/Fedora. The base is
`termux/termux-docker`, an Android/Bionic userland, not a Debian proot environment.
The image upgrades its packaged dependencies before installing Python/wget/git/file
because old base-package versions can otherwise conflict with current repositories.
The built image ID and exact tested source hashes are retained with each run.
Builds use network; runtime containers use `--network=none` and strict fixture
transport, just like the other targets.

All eight Termux scenarios execute as the native unprivileged `system` user
(uid/gid 1000). Root only prepares a system-AM fixture and result permissions.
There are no `/bin` or `/usr` compatibility links. The native Termux
`libtermux-exec.so` preload supplies normal Termux shebang/path translation;
`PREFIX`, Android environment and the native temporary directory are preserved.
The harness is invoked through the absolute Termux interpreter path.

Coverage:

- Direct AppMan install, saved helpers/source, standalone update and app ownership.
- The unchanged manager installed locally under the command name `am` selects
  AppMan paths without a system-mode marker.
- A read-only system-AM fixture offers AppMan mode without sudo/doas; acceptance
  persists and installs locally using the system-owned helpers, and declining
  leaves the app uninstalled. A writable system directory still refuses without
  sudo/doas. The fixture directory is user-owned with write bits removed so the
  negative test can toggle permissions; manager/module files remain root-owned.
- Partial transfer writes truncated staging bytes before failure; working binary
  and version survive, retry succeeds, and catalog freshness refusal preserves files.
- Normal AppMan removal/reinstall cleans launchers and preserves user configuration,
  with the reinstalled standalone updater exercised.
- Download/install/execution of real Android-native Bash ELF bytes from the image,
  through a controlled legacy CLI recipe and the offline download adapter.

The first actual run exposed AM's early sudo/doas check, which prevented reaching
read-only fallback. The requirement now runs after mode selection, preserving the
system-mode refusal while allowing unprivileged AppMan fallback.

The AppImage-path tests use inert extraction scripts, not native GUI AppImages.
This is x86_64 userland coverage on a Linux container kernel; it does not prove
phone ARM64 binaries, arbitrary GNU/Linux binary compatibility, FUSE, Android
SELinux/app-lifecycle behavior, or real-device installation. The `/opt/am` system
fixture is deliberately prepared by container root to exercise fallback; native
Termux's real user normally cannot create that path.

## Fast support-tool specs

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s test/e2e -p 'test_*.py' -v
```

These run on the host using disposable temporary directories, without importing
container scenarios or touching installed apps. They specify supported transport
output arguments, filesystem snapshot semantics and incremental trace reading.
The full container matrix remains the installed-command verification.
