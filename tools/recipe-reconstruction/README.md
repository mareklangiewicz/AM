# Upstream recipe reconstruction

Compare complete upstream recipes with one pinned GitHub AppImage template, or
expand a short declaration into that template's original form. Python 3.10+;
standard library only. Incoming recipes are read as inert text and never run.

Supported template: `github-appimage-3.5`, x86_64 AppImage version 3.5.
`provenance.json` records its upstream commit/path, original fixture hashes and
template hash. The source is a cached upstream revision, not automatically latest.
The recipe body is now the unmodified upstream
`templates/AM-SAMPLE-AppImage` at commit
`bb53f3180ec92f862020f8bdccef0f6614015bae`, stored in `upstream/AM-SAMPLE-AppImage`.
There is no independently authored `template.txt` body. The generator's original
FUNCTION assignment is stored verbatim as `upstream/github-appimage-function.txt`,
with its original file hash and line number in provenance. Loading verifies both
snapshot hashes. Rendering substitutes SAMPLE, REPLACETHIS and FUNCTION as the
upstream generator does, using the pinned default GitHub/x86_64 profile.

The FUNCTION assignment is tokenized as inert text and its three known variable
references are substituted; no shell or upstream interactive generator runs.
This is a deliberately narrow adapter for the pinned generator syntax, not a
shell interpreter. Changes to that syntax require an adapter review.

Upstream documents this system in its
[template guide](https://github.com/ivan-hc/AM/blob/main/docs/guides-and-tutorials/template.md).
The historical template is deliberately pinned: cached upstream/main at
`bbffd15c19d01ef9124fbf99b5b9c41d2661ea22` has a version-3.6 AppImage template
with different desktop handling. Advancing to it requires a separately identified
revision and compatibility review, not a silent replacement of the 3.5 family.
The former app-specific identity `github-appimage-3.5-obsidian` is no longer
accepted. Obsidian remains only one real-app example/fixture.

## Commands

From the repository root:

```sh
# Recognize a complete incoming upstream recipe.
python3 tools/recipe-reconstruction/reconstruct.py check /path/to/upstream/obsidian

# Expand our current short recipe into the explicitly selected upstream template.
python3 tools/recipe-reconstruction/reconstruct.py render \
  --short-recipe programs/x86_64/obsidian \
  --template github-appimage-3.5 > /tmp/upstream-obsidian

# Check the pinned original for comparison.
python3 tools/recipe-reconstruction/reconstruct.py check \
  tools/recipe-reconstruction/fixtures/obsidian
```

`render --declaration /path/to/declaration.json --template TEMPLATE` also accepts
exactly these JSON fields (including template identity):

```json
{
  "template": "github-appimage-3.5",
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

## Verifying and updating upstream sources

With Git and a repository containing both recorded source/fixture commits:

```sh
python3 tools/recipe-reconstruction/reconstruct.py verify-upstream --repo /path/to/AM
```

This reads local Git objects only, checks the complete canonical template, the
full generator hash and exact excerpt line, and every fixture against its recorded
upstream path. It emits JSON on stdout using exact/error exit codes. It does not
fetch, execute source, or change files. Normal check/render commands need no Git.

Upstream is authoritative for template body and generator substitutions. Treat the
`upstream/` files as pinned snapshots, not fork templates to edit independently.
For an upstream revision: inspect the template/generator diff, copy the original
bytes and exact FUNCTION line from that commit, update provenance/hashes and the
family identity as needed, then run verification and all focused checks. No silent
fallback to an app-derived body is permitted. Keep older revisions pinned if
existing recipes still need them. Selecting a revision remains explicit; this
tool does not yet manage multiple families or automate template imports.

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
