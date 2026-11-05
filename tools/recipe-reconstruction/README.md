# Upstream recipe reconstruction

Compare complete upstream recipes with one pinned GitHub AppImage template, or
expand a short declaration into that template's original form. Python 3.10+;
standard library only. Incoming recipes are read as inert text and never run.

Supported template: `github-appimage-3.5-obsidian`, x86_64 AppImage version 3.5.
`provenance.json` records its upstream commit/path, original fixture hashes and
template hash. The source is a cached upstream revision, not automatically latest.
Loading verifies both the template hash and reconstruction of the pinned source.

## Commands

From the repository root:

```sh
# Recognize a complete incoming upstream recipe.
python3 tools/recipe-reconstruction/reconstruct.py check /path/to/upstream/obsidian

# Expand our current short recipe into the explicitly selected upstream template.
python3 tools/recipe-reconstruction/reconstruct.py render \
  --short-recipe programs/x86_64/obsidian \
  --template github-appimage-3.5-obsidian > /tmp/upstream-obsidian

# Check the pinned original for comparison.
python3 tools/recipe-reconstruction/reconstruct.py check \
  tools/recipe-reconstruction/fixtures/obsidian
```

`render --declaration /path/to/declaration.json --template TEMPLATE` also accepts
exactly these JSON fields (including template identity):

```json
{
  "template": "github-appimage-3.5-obsidian",
  "app": "obsidian",
  "repository": "obsidianmd/obsidian-releases"
}
```

An exact check result contains this object as `declaration`. A review result
contains only a `candidate`, which must not be treated as verified extraction.
Template identity is maintenance metadata, explicitly selected rather than
inferred from our installer. A recipe's APP and CATALOG_REPOSITORY provide its
rendered values. The short reader accepts known literal header settings and the
current shared-installer wrapper; it rejects unknown assignments, duplicate
settings, shell expressions, extra commands, non-x86_64 identity and other package
layouts. Other supported literal settings (including asset pattern and launcher
choices) are not encoded in upstream output and are not behaviorally validated
by this tool. Rendering emits the selected template regardless of those choices.

Inputs are limited to 1 MiB of UTF-8 without NUL. Text is not normalized: comments,
whitespace, repeated updater parameters, CRLF and final-newline differences all
matter. Unknown content remains unconverted. The tool writes only stdout/stderr;
use a separate output path when rendering, since shell redirection can truncate
an existing file before the tool runs.

## Results and exit codes

| Exit | Check status | Meaning |
| --- | --- | --- |
| 0 | `exact` | Every input byte is reconstructed; declaration and pinned provenance included |
| 1 | `review` | Literal candidates exist but the complete text differs; unified diff included |
| 2 | `unsupported` | Unknown template, unsupported encoding/size or missing supported literal parameters |
| 3 | `error` | File access, malformed JSON or template integrity failure |

`check` writes one JSON object to stdout for these outcomes. `render` writes only
recipe bytes on success; failures write a JSON object on stderr and no recipe
bytes. Invalid command-line syntax uses argparse's normal usage text and exit 2.
All recognized/candidate check results include `compatibility: "unassessed"`.
An inconsistent installer/updater parameter yields `review`, never `exact`.

## Reviewing an incoming update

Suppose upstream changes every occurrence of Obsidian's repository from
`obsidianmd/obsidian-releases` to `example-owner/example-releases`, leaving the
recipe template untouched. Checking that incoming file returns `exact`, with the
new repository in `declaration`. Compare that declaration with the old result;
review the upstream move and repository numeric identity before proposing edits
in our short recipe. It does not enroll a repository or update catalog policy.

If upstream instead inserts a command into AM-updater or updates shared template
code/comments, the result is `review`; inspect the diff. Retain the original
incoming recipe until its extra behavior is accounted for. A common change
across a family calls for a reviewed template revision and new provenance,
fixtures and checks. Do not add arbitrary updater snippets as parameters or
silently normalize the change away. The new template's runtime compatibility
requires its own review.

## Compatibility policy

This tool approves complete source reconstruction only. It neither approves
conversion nor establishes runtime equivalence. No recipe family currently has
an automatic conversion approval through this tool.

| Behavior | Current decision for conversion |
| --- | --- |
| Upstream response-text filtering and first URL vs our explicit catalog selection | Separate selection review required; recognition does not translate filters or infer repository IDs, channel or asset patterns |
| Upstream appimageupdatetool branch vs our direct acquisition | A conversion must explicitly accept the existing fork update behavior |
| tmp/move/backup behavior vs our shared staging lifecycle | A conversion must explicitly accept existing fork replacement behavior |
| Desktop extraction, --no-sandbox handling and custom launcher preservation | Review the application's requirements against the shared installer |
| Host extras such as obsidian-gui and installed-path desktop Exec | Preserve and review our explicit declarations independently of upstream reconstruction |

These gates preserve the deployed runtime; the tool changes none of those
behaviors. The [experiment report](../../docs/track/release-catalog/research/upstream-recipe-reconstruction.md)
records the inspected differences. Collection enrollment is independent of both
recognition and recipe conversion. No network calls, publication or installed
recipe changes occur here.

## Verification

```sh
python3 -B -m unittest discover -s tools/recipe-reconstruction -p 'test_*.py' -v
```

Checks cover pinned fixture hashes, five byte-exact round trips, source changes
inside/outside the updater, parameter drift, template and newline changes,
nonliteral inputs, current short-recipe rendering, refusal of unsupported short
recipes, integrity checks and CLI status/output contracts. The throwaway HTML
remains on `prototype/120-upstream-reconstruction`; it is not a dependency.
