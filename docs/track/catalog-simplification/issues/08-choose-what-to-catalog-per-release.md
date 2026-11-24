# Choose what to catalog per release and asset

Type: grilling
Label: wayfinder:grilling
Status: resolved
Blocked by: 02

## Question

Given the measured sizes, which fields stay, which become derived defaults
stored only as exceptions (release, archive and download URLs, asset URL equal
to its name), which go (`media_type`?), and how many newest releases each
source keeps? Do all assets stay (the webpage shows all upstream assets) or only
some kinds?

## Answer — November 23, 2026

Marek's decisions, grilled from the measurements in
[Measure where the catalog's bytes go](02-measure-catalog-size.md) and two more
counts below.

Per release: keep the id, `tag`, `prerelease` and `published_at`; `created_at`
only when there is no `published_at`; `title` only when it differs from the tag;
drop `updated_at` (it changes on any edit of the notes; digests capture artifact
changes). The release page URL, source zip/tar URLs and download base are derived
from repository and tag and stored only where they differ (99.4% match; ticket
09 chooses how an exception is written).

Per asset: keep the id, `name` and `size`; derive the URL from download base and
name, stored only where it differs (99.6% match); drop `media_type`; replace
`digest` with `sha256pre`, the first 16 lowercase hex digits of the SHA-256,
quoted, fixed length. Keep every asset, of every platform, checksums and
signatures included: choosing among them is the client's.

`media_type` was dropped rather than derived: an asset's extension predicts its
stored type for only 64.6% of 1,486,460 assets (`.AppImage` octet-stream 63% /
`application/vnd.appimage` 22%; `.sig` labelled `zip` 58%), so a 67-extension
table would still store about 35% as exceptions, mostly uploader noise. The page
shows a type guessed from the extension, labelled a guess.

`sha256pre` is for change detection only, never download verification: a
64-bit prefix makes accidental collisions negligible but is cheap to forge.
Fixed length, not Git-style adaptive, so a record never changes when another
asset arrives. 90 to 38 bytes per line: about 63 MB of today's 448 MB, about a
quarter of the slimmed catalog (and more of packed history, as hex does not
compress; unmeasured).

Retention: each source keeps its 8 newest releases, plus its newest stable one,
plus its newest one with a Linux download, using the same filename rule as the
page's platform guess ([Simplify recipe labels and platform guesses](12-simplify-recipe-labels-and-platform-guesses.md)).
Page sentence: "We keep each app's 8 newest releases, plus its newest stable one
and its newest one with Linux downloads." Count-only retention would break
installs: 55 sources, all with AM recipes (`gaphor`, `doublecmd`, `pinta`,
`wire-desktop`, `qmapshack`, ...), have their newest Linux-looking asset more
than 8 releases back; today's 32 already miss 49 sources this rule keeps.
Counted by [scripts/08/depth.py](../scripts/08/depth.py) and
[scripts/08/mediatype.py](../scripts/08/mediatype.py) on the same extracted
tree as ticket 02.

Estimate, calculated not measured: about 80 MB instead of 448 MB.

Implementation: [Write the slimmer release and asset facts](14-write-slimmer-release-facts.md)
and [Measure the slimmed catalog](15-measure-slimmed-catalog.md), both blocked
by the layout and encoding tickets so the published format changes once.

## Comments

November 24, 2026, from ticket 07: the 8 newest, newest stable and newest with
Linux are counted as tags, with every release ID under a kept tag.
