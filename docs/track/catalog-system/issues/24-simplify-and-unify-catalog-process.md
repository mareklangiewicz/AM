# Simplify and unify the catalog and merge process

Type: grilling
Label: wayfinder:grilling
Status: open
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
- The collector suite takes 18 to 47 minutes; the e2e suite is broken
  ([ticket 23](23-repair-offline-e2e-after-v3-cutover.md)) and nothing runs
  either automatically.
- Open operational follow-ups already ticketed: 19, 20, 21, 22.

## Comments

November 16, 2026: opened after the first merge, as Marek asked.
