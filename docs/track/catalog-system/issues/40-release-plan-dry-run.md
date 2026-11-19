# `release.py plan`: a dry run of `ship`

Type: task
Label: implementation:task
Status: open
Blocked by: none

## Outcome

`tools/release/release.py plan [--ci NAME]` prints what `ship` would do
from the current checkout, without pushing, setting a variable or
dispatching: each refusal that applies, the push, and whether it would
repin, with the gate paths that changed since the pin. An agent pastes that
output when it asks Marek to push.

## Why

Retro of the ticket 22/38 session, second item. Asking to push meant
describing the push from memory. The auto-mode classifier also blocked one
`ship`, and Marek's "retry" meant switching to manual mode. A plan output
shows exactly what the approved command will do.

## Scope

- `plan` and `ship` share one decision function, so their answers cannot
  differ; tests in `tools/release/test_release.py` check that `plan` makes
  no push, `gh variable set` or `gh workflow run` call.
- Optional, to ask Marek: a Claude Code permission allow rule for
  `python3 -B tools/release/release.py ship`.

## Comments
