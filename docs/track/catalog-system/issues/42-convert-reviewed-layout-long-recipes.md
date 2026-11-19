# Convert the long recipes that are instances of reviewed layouts

Type: task
Label: implementation:task
Status: resolved
Blocked by: none

## Outcome

Every long recipe whose original is an instance of a reviewed AppImage layout
(3.5 `b7c72a974`, 3.6 `cf50304fc`) and that converts with the same selection
becomes a recipe declaration: 791 and 784 on `6ff1c94fa` (ticket 35's dry
runs).

## Why

Ticket 35's first dry runs found them. 732 of the 784 at 3.6 were already
instances at the bulk-conversion base `7b4f831e6`. Declarations take their
install steps from `modules/appimage.am` instead of carrying the template
text, as in ticket 33.

## Scope

- `relayout.py --layout cf50304fc --from long --write`, commit; then the same
  for `b7c72a974`. One commit each.
- Long tests on a `ci/` branch before `main-marek` moves.
- Not in scope: the 12 hand-written declarations that refuse, and the
  `bb53f3180` layout (nothing left to convert there).

## Comments

## Answer — November 19, 2026

Converted with `tools/upstream-merge/relayout.py --from long --write`, one
commit per layout:

- `a2fad9fc8`: layout `cf50304fc` (3.6), 784 recipes, 0 refused.
- `db00f2544`: layout `b7c72a974` (3.5), 791 recipes; `x86_64/darktable`
  (unsupported BRE escape), `x86_64/mattermost-desktop` and `x86_64/postman`
  (unsupported selector pipeline) refuse and stay long.

Each one passed relayout's selection-equivalence check; only
`recipe-url-policies.json` and `modules/catalog-yaml-policy.am` changed among
the derived files, and a fresh `generate()` gave the written module both
times. Tool suites passed locally.

Shipped with Marek's approval: Long tests 44517775060 green on
`ci/reviewed-layouts` (fast, tree, Debian and Fedora e2e); `release.py ship`
pushed `db00f2544`, repinned `CATALOG_SCHEDULE_REVISION` from `a506f3dd5`
(1,576 collection inputs changed), and Fast tests 44519826757 and dispatched
catalog run 44519834411 were both green. `ci/reviewed-layouts` deleted.
