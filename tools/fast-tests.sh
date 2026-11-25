#!/usr/bin/env bash
# The Fast tier: lint, every tool suite, then the collector's fast tier.
# "Fast tests" and the fast job of "Long tests" run exactly this.
# RUFF names the ruff command: CI sets it to a pip-installed ruff; ruff.toml's
# required-version refuses any other version.
set -euo pipefail
cd "$(dirname "$0")/.."

${RUFF:-uvx ruff@0.17.4} check tools test
for suite in tools/recipe-conversion tools/recipe-reconstruction tools/upstream-merge tools/release test/e2e tools/catalog-contract tools/catalog-collector; do
  echo "== $suite" >&2
  python3 -B -m unittest discover -s "$suite" -p 'test_*.py'
done
