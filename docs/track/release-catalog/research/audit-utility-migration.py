"""Source/selector/cost audit of ticket 48; reads Git and recipes, no network."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[4]
BASELINE = 'c787efe3a42fac015f743255006fddd7ea9b3817'


def original(path):
    return subprocess.check_output(['git','show',BASELINE+':'+path],cwd=ROOT)


def size(raw):
    return dict(bytes=len(raw),lines=len(raw.splitlines()))


def main():
    rows=json.loads((ROOT/'docs/track/release-catalog/research/recipe-family-inventory.json').read_bytes())['plain_utility_batch']
    before_lines=before_bytes=after_lines=after_bytes=0
    reports=[]
    for row in rows:
        path=row['path'];before=original(path);after=(ROOT/path).read_bytes()
        old=before.decode();new=after.decode()
        suffixes=re.findall(r'^version=\$\(curl[^|]+\| (.*)\)$',old,re.M)
        assert len(suffixes)==2 and suffixes[0]==suffixes[1]
        expected=('#!/bin/sh\n# AM INSTALL SCRIPT VERSION 3.5\n# AM-CATALOG-RECIPE 1\nset -eu\n'
                  'APP='+Path(path).name+'\nPACKAGE_KIND=executable\n'
                  'CATALOG_ALIAS="https://api.github.com/repos/ivan-hc/am-utils/releases"\n\n'
                  'select_asset() {\n\t'+suffixes[0]+'\n}\n\n'
                  '# shellcheck source=modules/appimage.am\n. "/opt/am/modules/appimage.am"\n'
                  'am_package "$0" "$@"\n')
        assert new==expected,path
        before_lines+=len(before.splitlines());before_bytes+=len(before)
        after_lines+=len(after.splitlines());after_bytes+=len(after)
        updater=old.split("cat >> ./AM-updater << 'EOF'\n",1)[1].split('\nEOF\n',1)[0]+'\n'
        reports.append(dict(path=path,before=size(before),after=size(after),
            original_sha256=hashlib.sha256(before).hexdigest(),recipe_sha256=hashlib.sha256(after).hexdigest(),
            original_generated_updater=size(updater.encode())))
    modules={}
    for name in ('modules/appimage.am','modules/install.am'):
        before=original(name);after=(ROOT/name).read_bytes()
        modules[name]=dict(before=size(before),after=size(after),
            delta_bytes=len(after)-len(before),delta_lines=len(after.splitlines())-len(before.splitlines()))
    report=dict(baseline=BASELINE,recipes=len(rows),identities=len({Path(r['path']).name for r in rows}),
        recipes_before=dict(lines=before_lines,bytes=before_bytes),recipes_after=dict(lines=after_lines,bytes=after_bytes),
        recipe_delta=dict(lines=after_lines-before_lines,bytes=after_bytes-before_bytes),shared_changes=modules,
        production_delta=dict(lines=after_lines-before_lines+sum(m['delta_lines'] for m in modules.values()),
                              bytes=after_bytes-before_bytes+sum(m['delta_bytes'] for m in modules.values())),
        notes='Exact original selector text preserved for every recipe; generated standalone launchers measured by container installed-code.json. Historical audit-executable-lifecycle.py remains a pre-migration baseline audit.',rows=reports)
    path=Path(__file__).with_name('utility-migration-audit.json')
    path.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))


if __name__=='__main__': main()
