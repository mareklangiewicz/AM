# Upstream recipe reconstruction experiment (120)

## Verdict

Proceed with a small maintained recognition/reconstruction tool. One pinned
upstream GitHub AppImage template represents multiple real recipes using only
app name and repository. Exact reconstruction makes unexplained custom commands
visible without evaluating shell. Do not automatically convert recognized
recipes: compatibility with our selector and installer remains a separate gate.

## Primary source and reproduction

Prototype branch: `prototype/120-upstream-reconstruction`, commit
`69c76db1fd4a789b1ef634d19a45978c8ced6bed`. Prototype code is deliberately absent
from main-marek; the branch contains the full template, fixtures, provenance,
CLI, self-contained HTML walkthrough and receipts under
`tools/recipe-reconstruction-prototype/`.

Local worktree: `/tmp/am-recipe-reconstruction-120`. Open its
`tools/recipe-reconstruction-prototype/demo.html`, or from that worktree run:

```sh
node tools/recipe-reconstruction-prototype/demo.mjs
node tools/recipe-reconstruction-prototype/cli.mjs check tools/recipe-reconstruction-prototype/fixtures/obsidian
node tools/recipe-reconstruction-prototype/cli.mjs render tools/recipe-reconstruction-prototype/obsidian-declaration.json
```

Upstream input is the locally cached `upstream/main` commit
`bbffd15c19d01ef9124fbf99b5b9c41d2661ea22`; no fetch or claim about latest
upstream was made. Template source is `programs/x86_64/obsidian`, version 3.5.
Fixture paths and SHA-256 hashes are in `provenance.json` on the prototype branch.
The template preserves every source byte except the literal APP assignment values
and repository occurrences, which become fixed placeholders. No normalization.

## Observed results

Five real recipes (`obsidian`, `5ire`, `acreom`, `actiona`, `actual`) reconstruct
byte-for-byte. Rendering the sample Obsidian declaration through the CLI also
matches the original fixture with `cmp`. Fixture SHA-256s were checked.

Eight repeatable scenarios produce the expected results:

| Situation | Decision |
| --- | --- |
| Original source | Exact |
| Both literal parameters changed consistently | Exact; declaration changes |
| Added installer command | Review; unmatched command shown |
| Added updater command | Review; unmatched command shown |
| Template version comment changed | Review; template change requires inspection |
| Updater APP differs from installer APP | Review |
| Final newline removed | Review |
| APP uses command substitution | Unrecognized; never evaluated |

The CLI's custom-updater refusal was exercised separately and returned nonzero,
with a replacement hunk identifying the added command. An initial walkthrough
mutation failed to modify its input because SITE separates APP from version0;
the scenario was corrected before the final receipts. The original external diff
subprocess stalled in this environment and was replaced with a small inert-text
diff. Final CLI demonstration completed. The generated HTML's two inline scripts
pass Node syntax checks; no browser visual/interaction verification is claimed.
The walkthrough uses the same recognizer as the CLI. No production suite was
needed or run for this isolated experiment.

Exploratory grouping of cached x86_64 sources found 617 recipes whose entire
contents match the Obsidian family after literal APP/repository substitution.
This is a corpus signal for maintenance value, not 617 validated conversions or
an all-architecture coverage claim; the acceptance sample is the five above.

## What the short declaration means

The prototype's reconstruction declaration is just template identity, app name
and repository. Current short Obsidian already supplies APP and
CATALOG_REPOSITORY. A maintenance sidecar associating that recipe with the pinned
template supplies the missing provenance. Template identity is necessary: the
same app/repository could belong to several historical upstream templates.

The reverse direction cannot safely infer the numeric GitHub repository identity,
our explicit asset pattern/channel or host launcher choices from APP/SITE.
Those require independent data/review. The reconstruction declaration is not a
complete runnable catalog recipe, and an exact match does not authorize replacing
one with the other.

## Runtime compatibility still to address

Compared the pinned template with maintained `modules/appimage.am` and the current
short Obsidian recipe at main-marek `23dad308c` (runtime unchanged from deployment):

| Area | Difference requiring an explicit conversion decision |
| --- | --- |
| Selection | Upstream parses GitHub response text, filters URLs ending in mage and excludes architecture substrings, then takes the first result. Our Obsidian recipe selects catalog facts using an explicit asset-name pattern. Recognition does not establish identical selection or ordering. |
| Updates | Upstream can invoke appimageupdatetool before the ordinary version comparison. Our shared updater uses catalog selection and direct asset acquisition. |
| Replacement | Upstream uses tmp paths and different install/update move behavior including backup creation. Our installer stages and replaces the selected payload through its shared lifecycle. |
| Existing launchers | Our installer explicitly preserves existing desktop entries and custom launcher targets. The upstream template writes its desktop entry and link directly. |
| Desktop extraction | Our installer has an installed-tool extraction fallback; the upstream template invokes the AppImage directly. Upstream strips --no-sandbox; the shared sed does not perform that same transformation directly and may call appimage_desktop if available. |
| Host customization | Our Obsidian declaration adds obsidian-gui and installed-path desktop execution. Neither is part of the upstream template. |

These are review findings, not changes proposed to the deployed runtime. Mark
recognized recipes as candidates until the supported-family compatibility policy
and any app-specific overrides have been reviewed.

## Maintenance cost and next scope

The recognizer needs a complete pinned template plus two restricted literal
parameters; matching is straightforward full-text comparison. The maintenance
cost is template drift: even harmless comment/format changes refuse until
reviewed. Keep that conservative behavior initially. More families add complete
reviewed templates, fixtures and provenance rather than increasingly permissive
normalization or arbitrary shell fragments as parameters.

For an incoming change, first compare against its recorded template: parameter
changes can propose declaration edits; unmatched content produces a diff. A
template-wide change needs one family review, followed by checks of affected
recipes. Unknown content must remain unconverted. The experiment supports this
direction; it does not yet prove a complete upstream-merge workflow.

Follow-up: [121](../issues/121-maintain-upstream-recipe-reconstruction.md).
No recipe conversion, enrollment, publication, installed refresh, deployment or
runtime changes occurred. Prototype and tracker commits are local only.
