#!/data/data/com.termux/files/usr/bin/bash
# Root is only used to prepare a read-only system AM fixture and writable logs.
set -euo pipefail
[ "${E2E_TARGET-}" = termux ] && [ -f /src/APP-MANAGER ] || exit 1
mkdir -p /run
touch /run/am-e2e-container
[ ! -e /bin ] && [ ! -e /usr ] || { echo 'Unexpected FHS compatibility links' >&2; exit 1; }
mkdir -p /opt/am /out
cp /src/APP-MANAGER /opt/am/APP-MANAGER
cp -a /src/modules /opt/am/modules
# Only the directory is user-owned so a negative test can toggle its mode.
# Manager/modules remain root-owned and byte-verified after each scenario.
chown 1000:1000 /opt/am
chmod -R a-w /opt/am
ln -sf /opt/am/APP-MANAGER "$PREFIX/bin/am"
chown 1000:1000 /out
printf 'target=termux\nPREFIX=%s\nLD_PRELOAD=%s\n' "$PREFIX" "$LD_PRELOAD" > /out/environment.txt
# Use the base image's real privilege drop, preserving the native execution environment.
status=0
/system/bin/su -s "$PREFIX/bin/env" system -- \
    HOME="$HOME" PATH="$PATH" PREFIX="$PREFIX" TMPDIR="$TMPDIR" \
    ANDROID_DATA="$ANDROID_DATA" ANDROID_ROOT="$ANDROID_ROOT" \
    LD_PRELOAD="$LD_PRELOAD" TERMUX_VERSION="$TERMUX_VERSION" \
    E2E_TARGET=termux E2E_TEST="${E2E_TEST-}" PYTHONDONTWRITEBYTECODE=1 \
    "$PREFIX/bin/python3" /src/test/e2e/termux_scenarios.py 2>&1 | tee /out/scenarios.log || status=$?
# Return results to the invoking rootless-container user, preserving test status.
chown -R 0:0 /out
exit "$status"
