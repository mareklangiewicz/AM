#!/usr/bin/env python3
"""Static migration inventory; never execute recipes or legacy selector bodies."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'catalog-collector'))
from collections import Counter
import hashlib,json,re,subprocess
from yaml_enrollment import enroll,shared_recipes

ROOT = Path(__file__).resolve().parents[2]


def inventory():
    revision = subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
    raw = (ROOT/'docs/track/release-catalog/design/staged-manifest.json').read_bytes()
    recipes = list(shared_recipes(ROOT))
    apps,identities,enrollment = enroll(raw,1,recipes,source_revision=revision)
    included = {row['path'] for row in enrollment['recipes']}
    rows = []
    for path,body in recipes:
        text = body.decode('utf-8')
        if '# AM-CATALOG-RECIPE 1' not in text.splitlines():continue
        variables = {key:value for key,value in re.findall(
            r'^(ASSET_[A-Z_]+|PACKAGE_KIND|REFRESH_ALWAYS)=(.*)$',text,re.M)}
        custom = bool(re.search(r'^select_asset\(\)',text,re.M))
        alias = re.search(r'^CATALOG_ALIAS="([^"\n]+)"$',text,re.M)[1]
        rows.append(dict(path=path,in_current_manifest=path in included,
            selector='custom_shell' if custom else 'generic_url_filter',
            kind=variables.get('PACKAGE_KIND','appimage'),
            endpoint='latest' if alias.endswith('/latest') else 'list',alias=alias,variables=variables,
            sha256=hashlib.sha256(body).hexdigest()))
    selected = [r for r in rows if r['in_current_manifest']]
    return dict(source_revision=revision,manifest_sha256=hashlib.sha256(raw).hexdigest(),
        enrolled_apps=len(apps),enrolled_repositories=len(identities),enrolled_recipe_paths=len(selected),
        excluded_marked_paths=len(rows)-len(selected),
        selected_selector_counts=dict(Counter(r['selector'] for r in selected)),
        selected_kind_counts=dict(Counter(r['kind'] for r in selected)),
        selected_endpoint_counts=dict(Counter(r['endpoint'] for r in selected)),
        selected_ignore_case_counts=dict(Counter(r['variables'].get('ASSET_IGNORE_CASE','false') for r in selected)),
        selected_refresh_always_counts=dict(Counter(r['variables'].get('REFRESH_ALWAYS','false') for r in selected)),
        recipes=selected)


if __name__ == '__main__':
    result = inventory()
    records = result.pop('recipes')
    # One recipe per line keeps the generated audit map reviewable.
    header = json.dumps(result,indent=2,sort_keys=True)
    print(header[:-2]+',\n  "recipes": [\n'+',\n'.join(
        '    '+json.dumps(row,sort_keys=True,separators=(',',':')) for row in records)+'\n  ]\n}')
