#!/bin/bash
# Container-only entrypoint; never install into the developer's host.
set -euo pipefail
[ -f /run/am-e2e-container ] || { echo 'Missing container marker' >&2; exit 1; }
mkdir -p /out
printf 'target=%s\n/bin/sh=%s\n' "${E2E_TARGET:?}" "$(readlink -f /bin/sh)" | tee /out/environment.txt
cat /etc/os-release >> /out/environment.txt
export PYTHONDONTWRITEBYTECODE=1
python3 /src/test/e2e/scenarios.py 2>&1 | tee /out/scenarios.log
