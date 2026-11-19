# Convert the long recipes that are instances of reviewed layouts

Type: task
Label: implementation:task
Status: claimed
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
