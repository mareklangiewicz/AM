# Share repeated AppImage asset selection

Type: task
Status: resolved
Triage: ready-for-agent

## Scope

User accepted shared tokenization/filter/first-match mechanics with declarative
patterns for typical recipes and a custom selector escape hatch. Preserve exact
six-recipe policy, including order and case sensitivity. Local implementation and
isolated validation only; no host delivery, collection, push or workflow changes.

## Answer

All six recipes now declare URL/include/exclude patterns rather than repeat the
JSON-tokenization/grep/head pipeline. Shared selection defaults to the ordinary
AppImage URL pattern, preserves candidate order and supports the original per-stage
case sensitivity. A custom `select_asset` still overrides defaults and preserves
its exit status, including for existing expanded installed recipes.

[Interface and cost](../design/shared-appimage-lifecycle.md#current-selection-interface-ticket-53):
recipe lines 84 -> 82; helper adds ten lines, production net +8. The gain is shared
mechanics and simpler declarations, not substantial source or installed shrinkage.
No selectors are moved into the collector or inferred from new upstream data.

Validation: 184 catalog tests pass, including retained-response equivalence,
126 differential cases across the six recipes (ordering, casing, empty input,
architecture/channel rejection), and custom-selector output/failure propagation.
Debian/Fedora whole installed command matrix passes 18 scenarios / 56 commands;
local ignored logs: `test/e2e/out/20261028T180532Z-636180/`. Shared helper and six
recipes pass warning-level ShellCheck; helper shell syntax and diff checks pass.

No host delivery, source push, live collection or workflow change. Timed 37/41
obligations remain; private host delivery manifests must be rebuilt/rechecked for
these changed sources before any delivery.
