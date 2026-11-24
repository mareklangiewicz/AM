# Simplify recipe labels and platform guesses

Type: grilling
Label: wayfinder:grilling
Status: resolved
Blocked by: 01

## Question

Keep the four classification labels (Shared installer, Template-based recipe,
Custom recipe, Not yet classified) and filename-based platform matching, or
simplify them, and how is each explained in one sentence?

## Answer — November 25, 2026

Marek's answers to two grilling rounds.

Evidence: ADR 0006 (a declaration can be trusted without reading shell; the page
flags apps without one); `tools/catalog-collector/provenance.py` (`shared` =
declaration naming this source, `template` = exact upstream-template instance,
`custom` only with a reviewed record, which the workflow never passes); ticket
01 row R28 on catalog `a8ee4e2fe9` (7,150 shared, 9 template, 0 custom, about
2,765 present unknown); `web/catalog/app.mjs` `guess()` (untested; Linux,
Windows, Mac; `arm64`/`x64` only); on main-marek `69b5dc011`, 9,476 of 9,885
`programs/x86_64/` recipes mention AppImage, 12 a tarball, 2 `.deb`, 0 `.rpm`
(`grep -l`).

- **Two labels**: "Reviewed installer" for a recipe declaration, "Recipe script,
  read it before installing" for any other recipe (long, template instance,
  fork-owned or original). `custom` goes (cannot occur); an architecture with no
  recipe is not listed (ticket 09).
- **Provenance**: each app's architecture entry is `recipe: "declaration"` or
  `recipe: "script"`, replacing `classification`, `availability` and the
  `recipe` binding. Template evaluation, `custom` reviews and the `evidence`
  block go; classification is recomputed each run (the implementation measures
  one full run; if slow, reuse keys on the recipe's SHA-256 only). The review
  link is the pinned catalog commit plus `programs/<arch>/<app>`.
- **Platform guess**: Linux or not (name contains `appimage` or `linux`, case
  ignored), no Windows/Mac; architectures in AM's names: `x86_64` (`x86_64`,
  `amd64`, `x64`), `aarch64` (`aarch64`, `arm64`), `i686` (`i686`, `i386`),
  `armv7l` (`armv7`, `armv7l`, `armhf`).
- **One rule**: the guess is defined once, read by the page and by ticket 08's
  retention ("newest with a Linux download"), with a test over real asset names.

Page text:

- Reviewed installer: "This app's AM recipe only names what to download; AM's
  reviewed installer does the rest."
- Recipe script: "This app's AM recipe is its own shell script; read it before
  installing." (with the review link)
- Guesses: "We guess from file names which downloads are for Linux and which
  processor they need; a guess doesn't mean AM can install it."

Implementation: [ticket 14](14-write-slimmer-release-facts.md); the sentences go
to [ticket 13](13-draft-how-it-works.md).
