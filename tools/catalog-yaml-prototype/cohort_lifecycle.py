"""Build an offline disposable lifecycle candidate; never edit active modules."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def module_candidate():
    source = (ROOT/'modules/appimage.am').read_text()
    before = '''\t[ -r "$CATALOG_HELPER" ] || { echo 'Missing catalog.am; synchronize AM modules.' >&2; exit 3; }
\tcatalog_body=$(sh "$CATALOG_HELPER" "$CATALOG_ALIAS" "$@") || exit 3
\tversion=$(printf '%s\\n' "$catalog_body" | am_appimage_select_asset) || exit 3'''
    after = '''\t# Offline candidate only: explicit local pin/recipe/time and exact waiver.
\t[ "$#" -eq 0 ] || { echo 'Unsupported offline lifecycle argument' >&2; exit 3; }
\tselection=$(sh "$CATALOG_YAML_HELPER" "$CATALOG_YAML_REPO" "$CATALOG_YAML_COMMIT" "$CATALOG_YAML_RECIPE" "$CATALOG_YAML_NOW" "${CATALOG_YAML_ACCEPT-}") || exit 3
\tversion=$(printf '%s\\n' "$selection" | sed -n '6p') || exit 3'''
    assert source.count(before) == 1
    return source.replace(before, after)


def recipe_candidate(recipe, module, repo, commit, now):
    source = (ROOT/'programs'/recipe).read_text()
    # Trusted test paths are shell quoted; no catalog field enters this source.
    import shlex
    bindings = dict(CATALOG_YAML_HELPER=ROOT/'tools/catalog-collector/yaml_cohort.sh',
        CATALOG_YAML_REPO=repo, CATALOG_YAML_COMMIT=commit,
        CATALOG_YAML_RECIPE=recipe, CATALOG_YAML_NOW=now)
    lines = ''.join(k+'='+shlex.quote(str(v))+'\n' for k, v in bindings.items())
    return source.replace('. "/opt/am/modules/appimage.am"', lines+'. '+shlex.quote(str(module)))
