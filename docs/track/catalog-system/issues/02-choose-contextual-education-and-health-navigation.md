# Choose contextual education and health navigation

Type: prototype
Label: wayfinder:prototype
Status: resolved
Assignee: codex-education
Blocked by: 01

## Question

Which progressive explanations and navigation let a newcomer understand a real
app's source, observed releases, AM selection, recipe execution and catalog health
without obstructing ordinary discovery?

Reuse the existing A/B/C prototype as an asset and coordinate with
[Choose the catalog browsing experience](../../catalog-pages/issues/03-review-browser-experience.md),
which owns the primary layout and keyboard verdict. This ticket owns educational
presentation and connections to public health, not another competing browser.

Explore a cheap walkthrough/outline with Marek, including a catalog-only app,
a known shared installer, a custom recipe, an unclassified recipe, a stale retained
release in a recent publication, and a failed latest attempt with usable prior data.
Show where “How it works”, exact-revision recipe review, provenance and health
belong, how depth is progressively disclosed, and what remains useful on mobile
and with keyboard/screen reader access. Unsettled classifications and schemas
must be visibly provisional in the prototype.

Resolve only from live human feedback. Record the accepted learning journey and
content responsibilities; leave detailed metric semantics and wire contracts to
their owning tickets.

## Comments — walkthrough ready for feedback, November 7, 2026

Claimed by codex-education. A throwaway Markdown walkthrough compares three
educational overlays on the existing A/B/C browser: explanations beside facts,
an ordered app trail, and a persistent evidence area. It covers the six requested
cases, a short system overview, public health navigation, and proposed keyboard/
mobile/reading-order behavior. It does not choose a browser layout.

Context: local branch `prototype/catalog-education`, commit `47d096a7d`,
worktree `/tmp/am-catalog-education`, artifact
`docs/track/catalog-system/education-walkthrough-prototype.md`.
Recover with:

```sh
git show 47d096a7d:docs/track/catalog-system/education-walkthrough-prototype.md
```

Neovim anchors the proposed learning journey; classification/failure/date cases
are explicitly illustrative, not verified claims about that app. Exact provenance
predicates, review bindings, health definitions and wire consistency remain with
their owning decisions. No implementation, browser acceptance, deployment or push.
The artifact is an outline, so no runtime tests apply; whitespace check passed.

Recommendation for live review: explanations beside relevant facts, the short
overview, and a dedicated health destination; observation age and evidenced failed
attempts visible without expansion. The walkthrough ends with three review
questions. This is an agent proposal, not an accepted answer. Ticket remains
claimed and unresolved pending Marek's feedback. Preserve the existing browser
ticket's claim, A/B/C verdict and Vim-navigation ownership.

## Answer — November 7, 2026

Reporting amendment: operational caveats refer to the timestamped “last reported
run”, which may not be the latest attempt. Never present its failure/success as
the current system state. Link to its specific Actions run and recent collection
runs for investigation; those links may require sign-in, but the public summary
does not. Final-summary-only cadence and possible reporting gaps follow the
[resolved recovery policy](../../catalog-system/issues/04-choose-durable-progress-and-fair-scheduling.md#answer--simplified-recovery-and-final-reporting-november-7-2026).

Marek accepted the recommendation above with “go ahead” in response to the
three-part proposal: short explanations beside relevant app/release facts,
a separate “How it works” overview and “Catalog health” destination, and
observation age plus known refresh failures visible without expansion.

The accepted learning journey starts with ordinary app discovery. At a relevant
fact, a visitor can open a short contextual explanation and follow links to deeper
evidence or the system overview. The overview connects upstream source, observed
release, client selection and installation recipe through a real app example.
Catalog health provides a dedicated destination for operational detail; app/release
context exposes observation age and evidenced refresh failure directly.

Content responsibilities follow that split: contextual text explains the fact
and its caveat; the overview connects the stages; health explains operational
outcomes and gaps. An ordered trail or persistent evidence panel is not required
by this decision. The isolated walkthrough remains supporting proposal material,
not blanket acceptance of every sample sentence or interaction detail.

The existing requirements for catalog-only/shared/custom/unclassified cases,
exact-revision recipe review, stale retained observations, usable prior data after
failure, mobile, keyboard and screen-reader access still apply. Recipe evidence
predicates/bindings, metric definitions, missing-health behavior and cross-revision
contracts remain with their owning tickets. Final copy and DOM/accessibility
behavior require implementation review and real-browser verification.

This resolves educational placement and content responsibilities only. The
existing browser ticket retains its claim and owns the A/B/C and Vim-navigation
verdict. No runtime implementation, deployment or push is authorized by this
planning decision.
