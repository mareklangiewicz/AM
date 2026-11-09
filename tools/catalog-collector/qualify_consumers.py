"""Inventory maintained source consumers of format 3 without executing recipes or touching hosts."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

import host_catalog as host


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    recipes=[]
    for arch in ('x86_64','aarch64','i686','armv7l'):
        for path in sorted((host.ROOT/'programs'/arch).iterdir()):
            if not path.is_file():continue
            raw=path.read_bytes();source=raw.decode()
            if not re.search(r'^CATALOG_FORMAT=(?:3|"3"|\x273\x27)$',source,re.M):continue
            recipes.append(dict(path=path.relative_to(host.ROOT).as_posix(),sha256=hashlib.sha256(raw).hexdigest(),
                declaration='# AM-RECIPE-DECLARATION 1\n' in source,arch=arch))
    modules=['modules/catalog-yaml.am','modules/catalog-contract-reader.am','modules/catalog-contract-parser.am','modules/catalog-contract-tables.am',
        'modules/catalog-yaml-policy.am','modules/appimage.am','modules/install.am']
    rows,sources=host.configuration()
    result=dict(installed_host_inspected=False,external_consumers=False,
        format_3_recipe_count=len(recipes),declaration_recipe_count=sum(r['declaration'] for r in recipes),
        transitional_recipe_count=sum(not r['declaration'] for r in recipes),
        architectures=dict(Counter(r['arch'] for r in recipes)),collection_app_identities=len(rows),collection_sources=len(sources),
        modules={p:hashlib.sha256((host.ROOT/p).read_bytes()).hexdigest() for p in modules},recipes=recipes)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('recipes','modules')},indent=2))


if __name__=='__main__':main()
