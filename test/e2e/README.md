# Whole-command AM/AppMan tests

```sh
./test/e2e/run                 # Debian and Fedora
./test/e2e/run debian          # one target
./test/e2e/run termux          # native Termux layout
ENGINE=docker ./test/e2e/run
E2E_OUT=/tmp/am-e2e ./test/e2e/run
```

Image builds download distribution packages. Test containers run with networking
disabled, the checkout mounted read-only at `/src`, and only a results directory
mounted writable. The installed manager and modules are copied byte-for-byte;
commands run in real container AM/AppMan locations. External transfer/clock adapters
serve explicitly authored YAML facts and inert assets; unknown requests fail.
Nothing installs into host app directories. Never run scenarios directly on the host.

The suite uses current YAML publication fixtures, independent of historical
collector/storage/migration code. Debian and Fedora cover system and AppMan install,
standalone updater source ownership, nightly refresh, download failure/partial
transfer/retry, interrupted AppMan work, removal/reinstall, selected-record stale
consent, freshness boundaries, mixed-batch continuation and real module sync.
Native Termux retains AppMan, unprivileged/fallback and installed executable checks.
The test log and `results.json` record the actual cases run.

Detailed portable selector, transitional am-utils/AppImage, archive/toolset,
reader/retention and metadata refresh checks live in `tools/catalog-collector`.
Historical format-1 container cases were migrated or retired in ticket 118;
this suite no longer depends on the former collector or migration evidence builder.
Original scenarios and results remain in Git history and ignored local run logs.

Helper-unit checks run without containers:

```sh
python3 -B -m unittest discover -s test/e2e -p 'test_*.py' -v
```

`neovim-smoke` remains an opt-in real AppImage smoke probe in disposable containers.
