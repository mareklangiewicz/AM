# Draft the "How it works" page

Type: prototype
Label: wayfinder:prototype
Status: resolved
Blocked by: 06, 07, 08, 11, 12

## Question

A rough draft of the final "How it works" text and `?` help, one sentence plus
a "why" per rule, from the resolved tickets, for Marek to react to.

## Answer — November 25, 2026

Marek: "Pretty good", with one change: the page reads the current `main-marek`
like every other reader, so the rule about one catalog version per tab and its
help entry are dropped (recorded in [ticket 21](21-drop-commit-pins-and-pin-variables.md)).
The prototype is `web/catalog/PROTOTYPE-how-it-works-13.html` on the local
branch `prototype/how-it-works-13` (commit `1a5c56cba`, never merged); the
validated text:

### How it works

1. The catalog lists the releases GitHub shows for each app AM knows.
   *Why: AM looks up downloads here instead of asking GitHub on every install.*
2. The catalog only records what GitHub lists; AM's recipe for each app decides which release and file to install.
   *Why: one list serves every recipe's own rules, such as stable or nightly, and the processor type.*
3. Each check reads a few hundred repositories, so every repository is read again every few days.
   *Why: GitHub limits how much one check may read.*
4. Each repository shows when its releases were last read from GitHub ("Last seen 3 h ago").
   *Why: so you can tell how current its list is.*
5. We keep each app's 8 newest releases, plus its newest stable one and its newest one with Linux downloads.
   *Why: enough to install and update any app, while the catalog stays small.*
6. A release deleted on GitHub is removed once the catalog reads the repository's whole release list; the catalog's history keeps it. A release kept on purpose that GitHub no longer showed in the latest check shows when it was last seen.
   *Why: the list matches GitHub without guessing that something is gone.*
7. Two releases can share one tag; both are listed.
   *Why: some projects publish one version as two releases, each with part of the files.*
8. When a check fails, the repository keeps its last good list and says why: "last attempt failed 1 h ago: GitHub couldn't be reached."
   *Why: a passing GitHub problem shouldn't empty an app.*
9. A repository not seen for more than 14 days is marked, and AM warns before installing from data this old.
   *Why: old data may point at files that changed or are gone; AM still lets you install.*
10. "Reviewed installer": this app's AM recipe only names what to download; AM's reviewed installer does the rest. "Recipe script": this app's AM recipe is its own shell script; read it before installing.
   *Why: a reviewed installer can be trusted without reading shell; a script can do anything.*
11. We guess from file names which downloads are for Linux and which processor they need; a guess doesn't mean AM can install it.
   *Why: GitHub doesn't say which file is for which system.*
12. Downloads come from each project on GitHub, not from the catalog, and the catalog doesn't check that a file is safe.
   *Why: the catalog records facts; trust is between you, the project and the recipe.*

### `?` help

- **Search**: App search looks at app names. Inside an app, the filter searches its release titles, tags and file names.
- **Last seen**: When this repository's releases were last read from GitHub. A release with its own "last seen" wasn't in the latest check: GitHub may have deleted it.
- **Kept releases**: The 8 newest releases, plus the newest stable one and the newest one with Linux downloads. Older ones are in the catalog's history, not on this page.
- **Failed checks**: The last good list stays. "Never collected" means no check has succeeded yet, so there's nothing to install from.
- **Old data**: Not seen for more than 14 days. AM warns before installing from it, then continues.
- **Recipes**: "Reviewed installer" or "Recipe script, read it before installing", per processor type. An app without a recipe for a processor type isn't listed for it.
- **Guesses**: Linux and processor type are guessed from file names (AppImage, linux, x86_64, aarch64, i686, armv7l and their aliases). A guess doesn't mean AM can install the file.
- **Same source, several apps**: Several AM apps can install from one GitHub repository; each has its own recipe and rules.
- **Catalog health**: The last 64 checks: how many repositories each read, how many failed, and why a check stopped early. Also how old the data is: under 24 hours, up to 2 days, up to 14 days, older, or never collected.

Rule 3's "every few days" is measured, not promised: runs come every 5–11 hours
with 500 of about 8,288 repositories each.

Implementation: the page text replaces `helpTopics` and the "How it works"
handler in `web/catalog/app.mjs` with the format change in
[ticket 14](14-write-slimmer-release-facts.md); entries whose behavior lands
later (old-data warning, ticket 23; status, ticket 22; no pins, ticket 21) ship
with those tickets.

## Comments

November 25, 2026, from ticket 12: the sentences for "Reviewed installer",
"Recipe script" and platform guesses are in 12's Answer; ticket 06's and 07's
answers carry the time and release sentences.
