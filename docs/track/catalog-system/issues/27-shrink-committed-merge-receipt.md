# Shrink the committed merge receipt

Type: task
Label: implementation:task
Status: resolved
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

## Answer — November 16, 2026

The receipt is format 2: parents, counts, fork-side file hashes, `attention`
and `recipes_sha256`. `apply` writes the per-recipe listing to
`.git/upstream-merge-recipes.json`; `gate` reads it from there (or from
`--recipes FILE`) and refuses a listing whose hash differs from the receipt.
`plan --recipes FILE` writes the listing for reading. A format-1 receipt, which
carries the listing, gates as before.

The gate still checks the merge against a listing made at `apply` time. It
does not recompute the plan: that would let the same code vouch for itself and
would add about a minute to the gate.

Checked by recomputing the first merge's plan for `cf9b5cc9b` and `ba061a639`
(54 s): the listing equals the 12,302 rows committed in
`upstream-merge-20261116.json`, counts, file hashes and `attention` agree, and
the receipt is 12 KB against 2.0 MB. Tool tests: 16 pass. Not run: `apply` and
`gate` on a real merge in progress, since upstream has nothing new to merge.
