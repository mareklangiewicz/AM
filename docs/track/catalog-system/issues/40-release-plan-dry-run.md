# `release.py plan`: a dry run of `ship`

Type: task
Label: implementation:task
Status: resolved
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

## Answer — November 19, 2026

`tools/release/release.py plan [--ci NAME]` prints `ship`'s first refusal
(`would refuse: ...`, exit 1), or the push and either `would repin ... and
dispatch catalog.yml` with each changed collection input or `... stays PIN`
(exit 0). Both commands call one function, `release.decide`, which holds every
check `ship` made before its push and now also reads the pin and the gate diff.
So `ship` reads the pin before pushing instead of after; nothing else changes.

Tests: `tools/release/test_release.py` `Plan` (3), on the existing scripted
`git`/`gh` replies, each also failing on any push, `gh variable set` or `gh
workflow run`. Mutants that never report a repin, or raise a refusal instead
of printing it, each fail them. Run for real on a pushed HEAD: `would refuse:
nothing to ship`, exit 1. The `README.md` of `tools/catalog-collector` names
it next to `ship`.

The optional Claude Code allow rule for `ship` is not added; that is Marek's
call.

November 19, 2026: shipped with Marek's approval as part of `6ff1c94fa` (Long tests 44514966125 on `ci/release-watch`, Fast tests 44516166447 green; no repin). `release.py plan` and `watch` were used for real in that ship.
