# Keep count and research scripts in the repo

Type: task
Label: implementation:task
Status: open
Blocked by: none

## Outcome

Every number a ticket reports (recipe counts, layout coverage, before/after
comparisons) comes from a script committed in the repo, and the ticket names
that script and the commit it ran on. A later session can rerun it instead of
re-deriving it from prose.

## Why

Retro of the ticket 22/38 session, first item. The scripts behind tickets
31 and 33 lived in a session scratchpad and were lost with it; only their
results and a prose description survived. Ticket 33's 1,236 vs 1,178
recipe counts then had to be reconciled by hand (ticket 33 Comments).

## Scope

- One agreed home for these scripts (for example
  `docs/track/catalog-system/scripts/`), with a line in `AGENTS.md` or the
  tracker README saying that ticket numbers cite a script there.
- Recreate ticket 31's layout coverage count (the per-layout recipe counts,
  including 6,009 for AppImage-in-archive), since the next layout review
  needs it. Its output must match ticket 31's table, or the ticket records
  why not.
- Ticket 33's conversion scripts are not recreated here; ticket 35 replaces
  them with a tested command.

## Comments
