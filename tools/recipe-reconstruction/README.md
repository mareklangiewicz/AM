# Upstream recipe recognition and reconstruction

Read original templates directly from pinned Git revisions, recognize whole
recipe instances, expose custom parameters and prepare migration inventories.
Python 3.10+ and Git are required. No copied templates, generator excerpts or
recipe fixtures are maintained here. No source shell is evaluated.

## Classify against all original templates

```sh
python3 tools/recipe-reconstruction/reconstruct.py classify /path/to/recipe
python3 tools/recipe-reconstruction/reconstruct.py templates
```

The tool discovers every file under `templates/` at the two recorded revisions:
`bbffd15c19d01ef9124fbf99b5b9c41d2661ea22` and
`bb53f3180ec92f862020f8bdccef0f6614015bae`. This covers all 15 templates at the
first revision plus 10 historical originals, including the legacy AppImage
layout. These are pinned local Git objects, not a claim about latest upstream.
Use `--repo /path/to/AM --revision COMMIT` to select another source; repeat
`--revision` to compare multiple revisions. Refs resolve to full commit IDs before
use. Missing objects fail with an actionable Git error; no fetch or fallback copy.

| Status | Meaning |
| --- | --- |
| `instance` | Whole text fits a template; parameters are conservative literal values or recognized upstream generator defaults |
| `parameter_review` | Whole layout fits, but some parameter contains unresolved/custom/unrecognized logic or repeated standard parameters disagree |
| `unmatched` | No whole-layout match; may be a custom recipe, unhandled edit form or another historical revision |

A structural instance can contain custom logic in upstream's FUNCTION slot. The
tool explicitly reports every such unrecognized expression in `parameter_review`.
It does not bless arbitrary shell just because a placeholder accepts it. An
unmatched recipe is not proof of custom logic. `classify` includes a nearest
original-template diff for investigation; that preview is unexpanded and is not
a verified extraction. All results leave runtime compatibility unassessed.

Matching accounts for the complete file with exact line endings and no comment
or whitespace stripping. Captures cannot span physical lines; extra commands
outside slots fail the layout match. SAMPLE captures must agree across the file.
Standard AppImage/Archive installer/updater site and FUNCTION values must agree.
This also applies to the archive-capable AppImage layout. The inspected 3.6
archive layout additionally recognizes the generator's exact AIA/default-keyword
rewrite: its generic GitHub download selector followed by `grep -i "appimage$"`
before `head -1`. This extension requires the inspected template and generator
SHA-256 values in `originals.py`; a changed original must be reviewed again.
Other endpoints, filters, ordering and extra shell remain parameter review.
See [selector research](../../docs/track/release-catalog/research/selector-review-groups.md)
for original generator locations and the bounded migration candidates.
Captures resembling shell or unresolved markers require review. Inputs are
limited to 1 MiB; layout matching refuses lines over 8 KiB. New upstream marker
syntaxes require extending the explicit marker vocabulary and focused checks;
arbitrary uppercase shell variables are never treated as editable placeholders.
The current marker vocabulary covers the inspected pinned template set. This
is conservative syntactic accounting, not shell semantic equivalence.

Exact extracted parameters can be rendered without storing the body:

```sh
# Save one match object from classify's matches list to declaration.json.
python3 tools/recipe-reconstruction/reconstruct.py expand declaration.json > /tmp/reconstructed
```

A match records `template: FULL_COMMIT:templates/NAME`, its source hash and an
ordered `parameters` list. `expand` requires that identity in the selected source
revisions, substitutes each original marker once, and writes only recipe bytes.
Expansion also permits review candidates for inspection; it is not approval to
execute or convert the resulting recipe. A single-line shell parameter remains
inert text throughout. Keep output separate from inputs when using redirection.

## Migration planning

```sh
python3 tools/recipe-reconstruction/reconstruct.py inventory \
  --recipes-revision bbffd15c19d01ef9124fbf99b5b9c41d2661ea22 --summary

# Full JSONL evidence with source hashes, exact parameters and review findings:
python3 tools/recipe-reconstruction/reconstruct.py inventory \
  --recipes-revision COMMIT --prefix programs/x86_64/ > /tmp/recipe-inventory.jsonl
```

The inventory streams original recipes from a Git tree once. Each row records
source commit/path/hash, template matches and a migration action:
`review_runtime_policy`, `inspect_parameter_logic` or `inspect_unmatched_source`.
Use standard-instance groups as candidate batches; inspect parameter-review
findings and unmatched sources separately. Reuse the same classifier for changed
recipes during an upstream merge. No recipes, collection lists, registries or
installed files are written. Summary counts are evidence, not converted apps.

Template recognition does not infer repository numeric identity, catalog channel
or asset patterns. Conversion must separately review selection/order, direct
acquisition versus appimageupdatetool, replacement/backups, desktop behavior and
host-specific launchers. There is no automatic conversion approval.

## Existing short-recipe expansion

The narrower legacy interface still expands a short declaration through the
original upstream 3.5 GitHub AppImage generator profile:

```sh
python3 tools/recipe-reconstruction/reconstruct.py render \
  --short-recipe programs/x86_64/obsidian --template github-appimage-3.5 > /tmp/upstream-recipe
python3 tools/recipe-reconstruction/reconstruct.py check /tmp/upstream-recipe
python3 tools/recipe-reconstruction/reconstruct.py verify-upstream --repo .
```

`render --declaration FILE --template github-appimage-3.5` accepts exactly
`{"template":"github-appimage-3.5","app":"example","repository":"owner/project"}`.
Only known literal current short-header settings/wrapper and x86_64 AppImage
layout are supported. The literal `DESKTOP_STRIP_NO_SANDBOX` setting is accepted by the short reader.
Other declared selector/launcher settings are not encoded
in upstream output or behaviorally validated. Template/generator/fixture hashes
remain in `provenance.json`; the actual bodies come from Git originals. The
existing short-reader's refusal checks and real round trips remain covered.

`classify` exits 0 for an instance, 1 for review/unmatched. Legacy `check` exits
0 exact, 1 review, 2 unsupported, 3 operational/integrity error. `inventory` and
`templates` exit 0 on completion, even if inventory includes review cases.
Operational errors exit 3; unsupported inputs exit 2. Analysis commands output
JSON (inventory JSONL); render/expand output bytes and send error JSON to stderr.
Invalid command syntax uses normal argparse usage text and exit 2.

## Tests and updating source revisions

```sh
python3 -B -m unittest discover -s tools/recipe-reconstruction -p 'test_*.py' -v
```

Tests read the originals too: one parametrized contract generates examples for
**every discovered original**, round-trips extracted parameters and refuses added
steps. Shared tests exercise custom FUNCTION expressions, nonliteral parameters,
repeated identities, real upstream recipes, CLI and inventory contracts. No
per-app template copies or handwritten parallel installer bodies are needed.
The candidate runtime assessment also compares the extracted, hash-checked
upstream selector against the maintained awk policy using local facts, and
exercises the shared installer with inert assets in disposable directories.
It records known behavioral differences, not migration approval; see
[assessment](../../docs/track/release-catalog/research/three-candidate-runtime-assessment.md).
The tests intentionally require the recorded Git objects; source-only archives
and shallow clones without them must first obtain those originals explicitly.

Upstream remains authoritative. Review a new template/generator revision with
`--revision`, inspect inventory changes, extend marker/default-expression support
only with tests, and then update the pinned metadata deliberately. New template
layouts never silently replace an old family's meaning. Upstream's interactive
`am -t` is documented in `docs/guides-and-tutorials/template.md`; it is not run.


## Twenty-recipe retained batch evidence

Ticket [133](../../docs/track/release-catalog/issues/133-prepare-large-existing-recipe-batch.md)
adds twenty source conversions with static payload gates and a portable evidence
archive. `test_large_batch.py` replays exact originals, full saved release-page
selectors on three awk implementations and actual converted recipes with authored
inert extractors plus saved desktop/icon data. It never executes downloaded
AppImage/AppRun bytes. The evidence and source declarations do not enroll these
apps for collection; production catalog availability is a separate gate. See the
[batch report](../../docs/track/release-catalog/research/large-batch-conversion.md)
for policy changes, exclusions and verification limits.


The [next ten-recipe batch](../../docs/track/release-catalog/research/next-ten-conversion.md)
reuses that verification through `LargeBatch.receipt_path` and a small subclass;
there is one lifecycle/selector implementation for both evidence receipts. Its
local collection preparation is separate from the prior published 43/41 result.
