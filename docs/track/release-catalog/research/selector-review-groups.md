# Shared selector review groups at the pinned upstream revision

Ticket [124](../issues/124-investigate-selector-review-groups.md), November 6, 2026.
Research only: no classifier, recipe, runtime, enrollment or installed-file change.

## Evidence and counting

Source recipes are Git objects at
`bbffd15c19d01ef9124fbf99b5b9c41d2661ea22` (R36); historical templates/generator
also use `bb53f3180ec92f862020f8bdccef0f6614015bae` (R35).
These are local pinned sources, not a statement about current upstream.
The [inventory summary](upstream-template-inventory.json) reproduces 9,234
recipes: 2,080 instances, 5,124 parameter-review and 2,030 unmatched.
Full JSONL SHA-256 is
`cf773085d71da2325f81359db1fd7db9e4cf17fbce5e8b87312d41f12567ccd7`.

Each recipe is counted once using its first matching template in the recorded
catalogue order. Archive layouts match both revisions, so counting all review
matches would produce 5,332 instead of 5,124. Grouping replaces only the literal
repository parameter in each reported unrecognized FUNCTION value, preserving
endpoint, filters, quoting and command order. Full installer/updater parameters
were compared separately for disagreements; the grouping alone is not that check. This is syntactic grouping,
not execution or behavioral equivalence. First-match selection is a reporting
convention, not a preferred migration template.

| First template | Unique review recipes |
| --- | ---: |
| R36 AppImage-in-archive | 4,483 |
| R35 AppImage | 374 |
| R36 Archive | 208 |
| R36 AppImage | 58 |
| R36 portable2appimage | 1 |

The following are exact normalized selector groups inside those layouts. Except
where explicitly noted, installer and updater FUNCTION values agree.

| Layout | Recipes | Selector distinction | Examples |
| --- | ---: | --- | --- |
| R36 AppImage-in-archive | 4,437 | `/releases`, generic download extraction, negative architecture filter, then `grep -i "appimage$"` | 20x, 2fac, 4nier-patrimonio |
| R35 AppImage | 186 | `/releases/latest`, `https.*mage$`, positive `amd64\|x86_64\|x64\|x86-64` filter | 12to11, abaddon, aerofoil |
| R35 AppImage | 34 | `/releases`, `https.*download.*mage$`, negative filter including armhf | acestep-cpp-ui, altersend, amule |
| R36 AppImage-in-archive | 30 | generic download extraction, positive architecture filter, then `appimage$` | c-dogs-sdl, cataclysm-tlg, chipass |
| R35 AppImage | 24 | `/releases/latest`, `https.*mage$`, negative filter without armhf | affine, animeko, audiomoth-configuration-app |
| R36 Archive | 22 | generic HTTPS extraction, negative filter without armhf, `linux_amd64.tar.gz` keyword | aptly, aretext, brutespray |
| R36 AppImage | 21 | `/releases`, download AppImage extraction, positive architecture filter | 2ship2harkinian, claws-mail, clonehero |
| R35 AppImage | 18 | same selector as preceding row, historical layout | android-translation-layer, anki, antigravity |

The leading command also occurs in the portable2appimage layout, giving 4,438
recipes across layouts. The two positive-architecture AppImage rows give 39
across layouts. These cross-layout totals must not be treated as identical
installer families.

## What upstream explains

The R36 original `modules/template.am`
Git object, lines 361–375, constructs the GitHub release selector. Its AIA
branch chooses `AM-SAMPLE-AppImage-in-archive` and removes `mage$` from the URL
extraction. Lines 443–448 set the default keyword `appimage$` when
`APPIMAGE_DEFAULT` and AIA are nonempty, then append `grep -i "$response"`
before `head -1`. Together these explain the exact shape of the 4,437 group;
whole-recipe layout matching already establishes its remaining original body.
This is evidence of an ordinary generator path, not evidence of the historical
interactive inputs used for each recipe.

R36 lines 411–430 and R35 lines 235–243 implement the optional `/latest`
endpoint. R36 lines 443–448 and R35 lines 260–265 implement positive keyword
insertion. These support treating endpoint/keyword variants as explicit ordinary
selector dimensions. They do not justify approving arbitrary shell, arbitrary
regular expressions, or every positive architecture rewrite automatically.
The current `functions()` in
[originals.py](../../../../tools/recipe-reconstruction/originals.py) reads direct
FUNCTION assignments and therefore does not account for all later generator
rewrites. Ordinary generator variants remain conservatively in review today.

The R36 `templates/AM-SAMPLE-AppImage-in-archive` Git object has SHA-256
`d1ae5ae71a055af61f174425bfcd84e370ece780bcc50536b7674c76336f5119`.
Its installer/updater tries archive extraction conditionally and also accepts a
direct AppImage. Template naming therefore does not establish that acquisition
needs an archive. Its updater tries `appimageupdatetool -Or` before comparing the
recorded URL. Selection/acquisition behavior is not implied by a layout match.

## Bounded next family and refusal gates

Start with the exact 4,437 selector group, but use only **20x, 2fac and
4nier-patrimonio** for a small offline preparation batch. All three have the same
whole R36 archive layout and identical installer/updater selectors after literal
repository substitution. Their source provenance is:

| Path under `programs/x86_64/` | Repository | Source SHA-256 at R36 |
| --- | --- | --- |
| 20x | peakflo/20x | `f10790639ac193a1ecbcdc81824a8a22d9577906c80f4403d616a990069f7f31` |
| 2fac | jeonjw85/2fac | `745b2c7ccd3dde951452ea86cfa33986b78f458c89b45b85ee0cdd7a82a9b0c5` |
| 4nier-patrimonio | 4nier-app/patrimonio | `36ea29727167c231ac7fc2fb61d770c9a2622eccec258e726a1f26edce89a8ff` |

Verified each candidate's bytes directly with `git show R36:path` and SHA-256.
Independent verification also reconstructed all three candidates and pyuploadtool
byte-for-byte from their extracted template parameters. A fresh full inventory
summary reproduced all 9,234 classifications; executing the grouping snippet
reproduced the table above.
Recommendation: a narrowly enumerated selector recognition extension should
recognize this exact generator-derived command shape with a validated literal
repository, requiring matching installer/updater sites and commands. Preserve
unknown syntax, extra commands, changed ordering, differing endpoints and custom
filters as review. Keep template identity/hash plus original source identity/hash
in any later migration record; do not replace originals with copied templates.

A relevant limit already visible in the corpus: **pyuploadtool** fits the archive
layout but installer excludes `continuous` while updater does not. Current
explicit repeated-FUNCTION disagreement reporting covers simple AppImage/Archive
paths only, so its archive match reports one unrecognized FUNCTION without the
extra disagreement finding. It remains parameter-review today. Any extension
must prevent it becoming an instance by approving its two expressions separately.
Seven first-match review recipes have unequal FUNCTION values: am-gui-beta,
citron-nightly, citron-nightly-v3, dbgate, dbgate-premium, gale, pyuploadtool.
No claim that their differences are bugs; gale even contains a leading extra
parenthesis in its captured updater expression.

Before converting the three candidates, separately establish repository numeric
identity, catalog enrollment policy, release/asset ordering and architecture
selection on retained records, including multiple matching assets, prereleases,
missing assets, empty/no-match responses and versions outside the first page.
The old pipeline chooses the first matching URL from a release response; do not
silently equate this to newest publication or newest stable release. A `/latest`
variant needs its own explicit policy because the catalog deliberately does not
publish GitHub's latest designation (ADR 0001).

Rehearse direct download versus appimageupdatetool, archive/direct staging,
replacement/backups, failure behavior, launcher/icon/remover output and standalone
updater behavior with inert local assets. Check existing fork recipes before
replacement. No runtime equivalence, collection enrollment or readiness to deploy
is established by this research; no conversion was performed.

## Reproduction

Generate fresh full evidence using the documented tool and the exact revision:

```sh
python3 tools/recipe-reconstruction/reconstruct.py inventory \
  --recipes-revision bbffd15c19d01ef9124fbf99b5b9c41d2661ea22 \
  --prefix programs/x86_64/ > /tmp/am-124-inventory.jsonl
sha256sum /tmp/am-124-inventory.jsonl
```

Rank without evaluating source shell:

```python
import collections, json
rows = [json.loads(line) for line in open('/tmp/am-124-inventory.jsonl')]
groups = collections.defaultdict(list)
for row in rows:
    if row['status'] != 'parameter_review':
        continue
    match = row['matches'][0]
    repository = match['parameters'][1]
    expressions = tuple(dict.fromkeys(
        item['value'].replace(repository, 'USER/REPO')
        for item in match['parameter_review']
        if item.get('marker') == 'FUNCTION' and 'value' in item))
    differences = tuple(item['reason'] for item in match['parameter_review']
                        if 'value' not in item)
    groups[(match['template'], expressions, differences)].append(row['recipe'])
for key, paths in sorted(groups.items(), key=lambda item: -len(item[1]))[:15]:
    print(len(paths), key, paths[:5])
```

Use `git show FULL_COMMIT:modules/template.am` and
`git show FULL_COMMIT:templates/AM-SAMPLE-AppImage-in-archive` for the primary
source claims above; local working-tree generator content is not the pin.
This research executed no source recipe and made no live/network queries.
