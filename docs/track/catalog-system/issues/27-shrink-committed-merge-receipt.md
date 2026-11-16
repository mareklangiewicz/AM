# Shrink the committed merge receipt

Type: task
Label: implementation:task
Status: open
Blocked by: 26

## Outcome

The receipt committed under `docs/track/` holds the parents, the counts and
the `attention` section. The per-recipe list (12,302 rows in the first merge)
is written to a scratch path, or recomputed by `gate` from the two parents.

## Why

Nobody reads the long list as a record, and `gate` can derive it. Decided in
[ticket 24](24-simplify-and-unify-catalog-process.md#answer--november-16-2026).

## Scope

- Check first that `gate` can recompute every per-recipe outcome from Git
  objects alone; if an outcome depends on something outside Git, say which and
  keep only that.
- `upstream-merge-20261116.json` stays as committed.

## Comments
