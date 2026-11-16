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

## Tests

```sh
python3 -B -m unittest discover -s tools/recipe-conversion -p 'test_*.py'
```

They need the upstream merge base `7b4f831e6` and fork commit `6277377ae` as
local Git objects. The corpus tests convert every original behind the bulk
conversion published at `6277377ae` and require byte-identical results: 984
recipe declarations and 8,770 long recipes with their policies. One
declaration (`odicto`) and 103 long recipes refuse; those were adapted by hand
and are pinned as refusals. One declaration (`pdf4qt`) is pinned as a
deliberate difference: it was published with a selector's `$APP` kept as
pattern text, which matches nothing, and the conversion writes the name out.
