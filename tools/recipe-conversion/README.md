# Recipe conversion

One entry point that turns an original recipe into a recipe declaration or a
long recipe (terms: root `GLOSSARY.md`, Recipes). It reads the original as
text. It never runs recipe shell and never touches the network; the verified
catalog source identity is an input.

```sh
python3 tools/recipe-conversion/convert.py ORIGINAL --recipe x86_64/0xfx \
  --form declaration --repository-id 1186679146 \
  --repository averagenative/0xFX --requested-repository averagenative/0xfx
```

The converted recipe goes to stdout. A refusal prints `refused: <reason>` on
stderr and exits 2 with nothing on stdout. `--form long` also needs
`--policies FILE` for the selection policies that belong in
`tools/catalog-collector/recipe-url-policies.json`. A recipe that selects from
several repositories takes `--identities FILE` (a JSON list) instead of the
single-source options.

From Python: `convert.convert(source, recipe, form, identities)` returns
`form`, `text` and `policies`, or raises `convert.Refusal`.
`declaration_identities(text)` and `policy_identities(rows)` read the
identities back out of an already converted recipe, for re-conversion.

## What each form accepts

| Form | Accepts | Refuses |
| --- | --- | --- |
| `declaration` | An original that is, line for line, an instance of a reviewed upstream AppImage template, with the same literal `SITE` and release selection in installer and updater, and a selector that is a literal filter pipeline ending in a direct AppImage URL. | Any added, removed or edited line; a non-GitHub or second release read; a selector with shell beyond `sed`/`grep`/`head`; an identity for another repository. |
| `long` | An original whose release selections are literal GitHub release reads the catalog can answer. Its install steps are kept as written. | A dynamic selector, an auxiliary GitHub API read, a custom native-update bypass, a selection from a repository with no identity. |

A selector may use one variable, a literal `$APP`, which is written out; any
other expansion refuses. Single-quoted `APP='x'` / `SITE='x'` and extra spaces after `curl -Ls` count
as the same literals.

## Reviewed layouts

`layouts.json` names the upstream template bodies a declaration may come from,
each as a Git commit, path and SHA-256. The body is read from that Git object
and refused if its hash differs. A new upstream template version is not
accepted until someone has compared its install steps with
`modules/appimage.am` and added it here; until then its recipes refuse the
declaration form and convert to long recipes.

A layout may carry `settings`: declaration settings that reproduce what its
install steps do beyond the shared installer's defaults. Template 3.6's and
`bb53f3180`'s desktop `sed` removes `--no-sandbox`, so their rows set
`DESKTOP_STRIP_NO_SANDBOX=true` (ticket 32).

The first row (`b7c72a974`, 3.5) is the base. Every other row lists its
`differences`: each line its body removes (`-`) or adds (`+`) against the
base, with exactly one of `setting` (a key in the row's `settings`), `neutral`
(a reason the line makes no difference to what a declaration installs) or
`dropped` (a reason, plus the `ticket` that tracks the behavior declarations
do not reproduce). `convert.layouts()` refuses to load a layout with an
unmapped differing line, an entry for a line that no longer differs, or a
setting no line maps to (ticket 36). Template 3.6's multiple-launcher lines
are `neutral`: since ticket 37 the shared installer installs every launcher
for every declaration. Adding a layout: list its lines with
`convert.differences(base, body)` and classify each one against
`modules/appimage.am`.

The AppImage-in-archive template at `cf50304fc` (ticket 43) is a layout for
selections that name a direct AppImage only. Its download step unpacks a
`7z`, `tar.*` or `zip` download; its lines are `neutral` because a
declaration's selector always has an include rule ending in `mage$`
(`bulk_recipes.url_rules` refuses any other: "selector does not establish a
direct AppImage suffix"), so the one downloaded file is the AppImage itself.
Its instances that select any asset refuse the declaration and stay long
recipes.

## Tests

```sh
python3 -B -m unittest discover -s tools/recipe-conversion -p 'test_*.py'
```

They need the upstream merge base `7b4f831e6` and fork commit `6277377ae` as
local Git objects. The corpus tests convert every original behind the bulk
conversion published at `6277377ae` and require byte-identical results: 984
recipe declarations and 8,770 long recipes with their policies. Since ticket
32 the 586 declarations from template 3.6 must differ from the published text
by exactly one added `DESKTOP_STRIP_NO_SANDBOX=true` line; the 398 from 3.5
stay identical. One
declaration (`odicto`) and 103 long recipes refuse; those were adapted by hand
and are pinned as refusals. One declaration (`pdf4qt`) is pinned as a
deliberate difference: it was published with a selector's `$APP` kept as
pattern text, which matches nothing, and the conversion writes the name out.
