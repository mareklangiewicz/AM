# Keep count and research scripts in the repo

Type: task
Label: implementation:task
Status: resolved
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

## Answer — November 19, 2026

- Home: `docs/track/<effort>/scripts/NN/`, one folder per ticket. The rule
  is a bullet in `docs/agents/issue-tracker.md`, which `AGENTS.md` already
  sends agents to before tracker work.
- Ticket 31: its scripts were not lost after all; the full text was in the
  appendix of `template-instances-31.md`. They are now files in
  `scripts/31/` (byte for byte from the appendix), with `run.sh OUT_DIR` for
  the pinned commits (`ba061a639`, `36c087049`). Rerun on myxps: 392 template
  versions, 11,782 upstream recipes, and the main table equal to the
  published one in all 172 compared cells (one cell differs only in format,
  `0` vs `0 / 0`); the per-version split adds up to the sub-rows (reviewed
  3,658 / 2,675; `bb53f3180` 1,236 / 1,233; `8b53a7656` 10). The appendix now
  points to the folder; the fifth-form `git show` snippet stays in the doc.
- Ticket 33's scripts stay replaced by `relayout.py` (ticket 35). Its
  `tree_relayout.py` replay reproduces the shipped result.
