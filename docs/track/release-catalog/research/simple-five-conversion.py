"""Convert only the five-candidate preparation's fully passing source recipes."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[4]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--prepared', type=Path, required=True)
args = parser.parse_args()
stage = args.prepared/'evidence'
research = ROOT/'docs/track/release-catalog/research'
archive = research/'simple-five-evidence.tar.gz'
assert not archive.exists()
rows = json.loads((stage/'selection.json').read_text())
ready, exclusions = [], []
for row in rows:
    d = stage/row['app']
    failures = []
    for filename, status in (('payload-receipt.json','verified'),('static.json','compatible'),('policy.json','verified')):
        receipt = json.loads((d/filename).read_text())
        if receipt['status'] != status:
            failures.append(receipt.get('reason', filename))
    if failures:
        exclusions.append(dict(app=row['app'], reasons=failures))
    else:
        ready.append(row)
assert len(rows)==5 and len(ready)==4
assert {row['app'] for row in exclusions} == {'agent-skills'}
# Bind every passing before-image before changing any recipe or enrollment.
for row in ready:
    assert hashlib.sha256((ROOT/row['provenance']['recipe']).read_bytes()).hexdigest() == row['provenance']['source_sha256']
    assert row['strip_no_sandbox']
enrollment = ROOT/'tools/catalog-collector/collection-apps.json'
extra = json.loads(enrollment.read_text())
for row in ready:
    assert next(item for item in extra if item['app']==row['app']) == dict(
        app=row['app'],repository_id=row['repository_id'],repository=row['repository'])
for row in ready:
    app = row['app']
    settings = dict(APP=app,CATALOG_FORMAT='2',CATALOG_RECIPE='x86_64/'+app,
        CATALOG_ALIAS='https://api.github.com/repos/'+row['requested_repository']+'/releases',
        CATALOG_REPOSITORY_ID=str(row['repository_id']),CATALOG_REPOSITORY=row['repository'],
        CATALOG_CHANNEL='any',CATALOG_ASSET_PATTERN=row['pattern'],PACKAGE_KIND='appimage',
        PACKAGE_LAYOUT='raw',DESKTOP_EXEC='command',DESKTOP_STRIP_NO_SANDBOX='true')
    text = ('#!/bin/sh\n# AM INSTALL SCRIPT VERSION 3.5\n# AM-CATALOG-RECIPE 1\n'
        '# AM-RECIPE-DECLARATION 1\nset -eu\n'+
        ''.join(key+'='+shlex.quote(value)+'\n' for key,value in settings.items())+
        '\n# shellcheck source=modules/appimage.am\n. "/opt/am/modules/appimage.am"\nam_appimage "$0" "$@"\n')
    (ROOT/row['provenance']['recipe']).write_text(text)
converted = {row['app'] for row in ready}
enrollment.write_text(json.dumps([row for row in extra if row['app'] not in converted],indent=2)+'\n')
recipes = ROOT/'tools/catalog-collector/collection-recipes.txt'
lines = recipes.read_text().splitlines()
comments = [line for line in lines if line.startswith('#')]
names = [line for line in lines if line and not line.startswith('#')]
assert not converted.intersection(path.split('/',1)[1] for path in names)
recipes.write_text('\n'.join(comments+sorted(names+['x86_64/'+app for app in converted]))+'\n')
subprocess.run(['python3','tools/catalog-collector/recipe_policy_source.py'],cwd=ROOT,check=True)
manifest = {}
with tarfile.open(archive,'w:gz',dereference=False) as saved:
    for row in rows:
        for path in sorted((stage/row['app']).rglob('*')):
            if path.is_dir():
                continue
            name = path.relative_to(stage).as_posix()
            manifest[name] = ({'symlink':str(path.readlink())} if path.is_symlink() else
                dict(bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
            saved.add(path,arcname=name,recursive=False)
    for name in ('metadata.json','selection.json','prepare.py','acquire.py','static_payload.py','policies.py'):
        path = stage/name
        saved.add(path,arcname='scripts/'+name,recursive=False)
        manifest['scripts/'+name]=dict(bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
receipt = dict(source_before=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),
    observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    evidence_archive=archive.name,evidence_archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
    converted=sorted(converted),candidates=rows,exclusions=exclusions,manifest=manifest,
    total_verified_payload_bytes=sum(json.loads((stage/row['app']/'payload-receipt.json').read_text())['bytes'] for row in rows),
    collection_identity_change=False,installed_host_changed=False,
    note='Four reviewed recipe-source migrations. Agent Skills remains catalog-only; payloads were not executed.')
(research/'simple-five-evidence.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({key:value for key,value in receipt.items() if key not in ('candidates','manifest')},indent=2))
