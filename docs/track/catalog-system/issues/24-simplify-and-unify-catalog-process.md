# Simplify and unify the catalog and merge process

Type: grilling
Label: wayfinder:grilling
Status: resolved
Blocked by: none

## Outcome

Marek and an agent agree which parts of the catalog machinery stay, which
merge into one, and which go, written as decisions in the map (and an ADR
where one is reversed).

## Why

Marek, November 16, 2026, on the three installed recipes that needed their own
handling in the first upstream merge: "Why do we have custom treatment for
them? And generally our process is too complicated and time consuming. We
should try to simplify/unify it all." He chose to finish the merge the plain
way first and design the simplification after.

## Starting material

Observed during the first merge (ticket 18), as questions, not proposals:

- A recipe has four forms (upstream original, long recipe, recipe
  declaration, fork-owned), and each merge moves recipes between them with a
  refusal ladder. Could there be fewer?
- One merge rewrites five fork-side files derived from the recipes
  (`recipe-url-policies.json`, `catalog-yaml-policy.am`,
  `collection-recipes.txt`, `collection-apps.json`,
  `unavailable-github-recipes.json`). Which of them could be generated on
  demand instead of committed?
- Tests pin counts and named recipes (115 policies, 49 unavailable recipes,
  `mercury`, `obs-studio`, enrollment baselines), so every upstream change of
  a pinned recipe breaks a test by hand.
- The collector suite takes 18 to 47 minutes. The e2e suite went unnoticed
  broken from the v3 cutover until
  [ticket 23](23-repair-offline-e2e-after-v3-cutover.md). Nothing runs either
  automatically.
- `modules/catalog-yaml-reader.am` and `modules/catalog-yaml-parser.am` are
  format-2 modules the manager deletes on sync; only collector tests use them.
- Open operational follow-ups already ticketed: 19, 20, 21, 22.

## Comments

November 16, 2026: opened after the first merge, as Marek asked.

## Answer — November 16, 2026

Grilled with Marek in two rounds. Decisions:

1. **Target.** An upstream merge is one command plus the hand-merge of the
   three runtime files, needs no test edits and takes under about 15 attended
   minutes. Each change below is judged against that.
2. **Breadth stays.** ADR 0005 stands: upstream is authoritative and
   conversion runs at scale. Conversion is automatic (`apply` took 44 s); the
   cost is in committed derived files, pinned tests and the slow suite.
3. **Forms stay; the declaration is preferred.** Marek rejected retiring the
   recipe declaration: short declarative recipes can be trusted more easily
   and are one of the fork's main advantages. The long recipe is the fallback
   until a reviewed template covers a recipe. Recorded as
   [ADR 0006](../../../adr/0006-recipe-declaration-is-the-preferred-form.md).
   The unnamed fifth form ("other converted" in `merge.py`) goes once none
   remain.
4. **More declarations.** Count recipes per upstream template before a second
   template is reviewed: [ticket 31](31-count-recipes-per-upstream-template.md).
5. **Derived files.** Commit only what is a source of truth or what a client
   fetches; generate the rest: [ticket 29](29-sort-and-generate-derived-catalog-files.md).
6. **Tests.** Frozen fixtures instead of pinned live counts and recipe names;
   whole-tree invariants move into `merge.py gate`:
   [ticket 28](28-unpin-tests-from-live-recipes.md).
7. **CI.** A fast tier on every push that reports and blocks nothing; the full
   collector suite and e2e on demand and before each upstream merge:
   [ticket 30](30-add-ci-fast-test-tier.md).
8. **Merge tool.** Drops the `installed_here_*` host check with no
   replacement ([ticket 26](26-drop-host-check-from-merge-tool.md)); the
   committed receipt shrinks to counts and `attention`
   ([ticket 27](27-shrink-committed-merge-receipt.md)).
9. **Format-2 modules** are removed with their tests:
   [ticket 25](25-remove-format-2-reader-modules.md).
10. Tickets 19 to 22 stay as they are.

The task tickets are ordered smallest first; each shortens the next merge by
itself.

Corrections made during the session, kept so nobody repeats them:

- The tree holds 984 recipe declarations and 8,770 long recipes
  (`tools/recipe-conversion/README.md`). The 37 declarations and 450 long
  recipes in the first merge's receipt are only the recipes that merge
  touched.
- `recipe-url-policies.json` holds the verified source identities that
  re-conversion reads back, so it is not purely derived.

Not checked: where the collector suite's 18 to 47 minutes go, and whether any
fifth-form recipes remain. Each is the first step of its task ticket.
