"""Offline ticket-68 candidate patches; preserves every accepted descriptor/alias."""
import difflib
import json
from pathlib import Path
import re
import shlex
import subprocess
import tempfile

from collector import Descriptor, require
from exception_batch import DIRECTORY, PREVIOUS
from identity_batch import ROOT
from large_evidence import saved
from migration_batch import pipeline, compact_recipe
from storage import canonical, content, digest


def patch(path, before, after):
    return ''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),
        fromfile='a/'+path,tofile='b/'+path))


def prepare():
    queue=json.loads((DIRECTORY/'queue.json').read_bytes())
    batch=json.loads((DIRECTORY/'live/batch.json').read_bytes())
    require(batch['stopped'] is None and len(batch['rows'])==len(queue['rows']) and
        batch['queue_sha256']==digest((DIRECTORY/'queue.json').read_bytes()),'incomplete_evidence')
    prior=json.loads((PREVIOUS/'prepared/migration.json').read_bytes())
    result=dict(migrated=[],exceptions=[x for x in prior['exceptions'] if x['alias'] not in
        {row['alias'] for row in queue['rows']}],sources=[])
    recipes_patch=''
    for row,observed in zip(queue['rows'],batch['rows']):
        require(row['alias']==observed['alias'],'row_order')
        identity=saved(ROOT/observed['identity_evidence'],
            json.loads((ROOT/observed['identity_evidence']/'report.json').read_bytes())['url'])
        require(identity['accepted'] and identity['identity']['id']==row['repository_id'],'identity_evidence')
        if not observed['accepted']:
            result['exceptions'].extend(dict(path=r['path'],alias=row['alias'],reason='new_evidence_refused') for r in row['recipes'])
            continue
        directory=ROOT/observed['release_evidence']
        report=saved(directory,observed['fetch_url']); require(report['accepted'],'release_evidence')
        body=(directory/'body.json').read_bytes()
        releases=content(body,dict(url=observed['fetch_url']))
        if isinstance(releases,dict): releases=[releases]
        assets={a['browser_download_url'] for release in releases for a in release['assets']}
        accepted=[]
        for recipe in row['recipes']:
            original=(ROOT/recipe['path']).read_bytes(); require(digest(original)==recipe['sha256'],'recipe_changed')
            selected=[]
            for key in ('install_selector','update_selector'):
                selector=pipeline(row,recipe[key])
                require(not any(x in selector for x in ('`','$(',';','&&','\n')),'unsafe_selector')
                run=subprocess.run(['sh','-c','APP='+shlex.quote(Path(recipe['path']).name)+'\n'+selector],
                    input=body,capture_output=True,timeout=10)
                require(run.returncode==0,'selector_failed'); selected.append(run.stdout.decode().strip())
            reason=None
            if selected[0]!=selected[1] or selected[0] not in assets: reason='original_selector_missing_actual_asset'
            elif recipe['arch'] in ('aarch64','armv7l') and re.search(r'(?:x86[_-]?64|amd64|x64|i[3-6]86)',selected[0].rsplit('/',1)[-1],re.I): reason='arm_compatibility_unproven'
            if reason:
                result['exceptions'].append(dict(path=recipe['path'],alias=row['alias'],reason=reason,selected=selected)); continue
            candidate=compact_recipe(recipe,row)
            with tempfile.NamedTemporaryFile() as tmp:
                tmp.write(candidate.encode());tmp.flush();subprocess.run(['sh','-n',tmp.name],check=True)
            delta=patch(recipe['path'],original.decode(),candidate)
            # Legacy files without final newline require explicit unified-diff markers.
            recipes_patch+=''.join(line if line.endswith('\n') else line+'\n\\ No newline at end of file\n' for line in delta.splitlines(True))
            result['migrated'].append(dict(path=recipe['path'],alias=row['alias'],source_sha256=recipe['sha256'],
                candidate_sha256=digest(candidate.encode()),selected=selected[0],asset=selected[0],
                evidence=observed['release_evidence'],lines_removed=recipe['lines']-len(candidate.splitlines()),
                bytes_removed=len(original)-len(candidate.encode())))
            accepted.append(recipe['path'])
        if accepted:
            result['sources'].append(dict(url=observed['fetch_url'],repository_id=row['repository_id'],
                request_id=Descriptor(observed['fetch_url']).request_id,aliases=[row['alias']],
                identity_evidence='docs/track/release-catalog/research/appimage-exceptions-next-20261102/findings.md#identity-mappings',
                evidence=observed['release_evidence'],body_bytes=len(body),identity=observed['identity']))
    require(len(result['migrated'])+len(result['exceptions'])==78,'recipe_accounting')
    prepared=DIRECTORY/'prepared';prepared.mkdir(exist_ok=True)
    old_inventory=json.loads((PREVIOUS/'prepared/inventory.json').read_bytes())
    manifests={name:json.loads((ROOT/entry['path']).read_bytes()) for name,entry in old_inventory['shards'].items()}
    before={name:canonical(m) for name,m in manifests.items()}
    existing={source['request_id']:(name,source) for name,m in manifests.items() for source in m['sources']}
    new=[]
    for source in result['sources']:
        clean={k:v for k,v in source.items() if k not in ('evidence','body_bytes','identity')}
        if source['request_id'] in existing:
            name,old=existing[source['request_id']]
            require(old['url']==source['url'] and old['repository_id']==source['repository_id'],'source_conflict')
            old['aliases']=list(dict.fromkeys(old.get('aliases',[])+source['aliases']))
        else: new.append(source)
    current=[]; size=0
    for source in new:
        if len(current)==52 or size+source['body_bytes']>32_000_000:
            manifests[f'{len(manifests):02d}']=dict(schema=2,sources=current);current=[];size=0
        current.append({k:v for k,v in source.items() if k not in ('evidence','body_bytes','identity')});size+=source['body_bytes']
    if current: manifests[f'{len(manifests):02d}']=dict(schema=2,sources=current)
    inv=dict(schema=1,shards={})
    for name,manifest in manifests.items():
        if name in before and canonical(manifest)==before[name]: inv['shards'][name]=old_inventory['shards'][name];continue
        path=prepared/f'manifest-{name}.json';raw=canonical(manifest)+b'\n';path.write_bytes(raw)
        inv['shards'][name]=dict(path=str(path.relative_to(ROOT)),sha256=digest(raw))
    raw=canonical(inv)+b'\n';(prepared/'inventory.json').write_bytes(raw)
    new_descriptors=len(new)
    enrollment=''
    for path in ('.github/workflows/catalog-shards.yml','tools/catalog-collector/scheduled_dispatch.py','tools/catalog-collector/shard_delivery.py','tools/catalog-collector/test_scheduled_dispatch.py'):
        old=(ROOT/path).read_text();new=old
        if path.endswith('catalog-shards.yml') or path.endswith('test_scheduled_dispatch.py'):
            new=new.replace(str((PREVIOUS/'prepared/inventory.json').relative_to(ROOT)),str((prepared/'inventory.json').relative_to(ROOT)))
        elif path.endswith('scheduled_dispatch.py'):
            new=new.replace(digest((PREVIOUS/'prepared/inventory.json').read_bytes()),digest(raw))
        else:
            new=new.replace('appimage-next-large-batch-20261102/prepared/manifest-', '(?:appimage-next-large-batch-20261102|appimage-exceptions-next-20261102)/prepared/manifest-')
        require(new!=old,'enrollment_patch_missing');enrollment+=patch(path,old,new)
    (prepared/'enrollment.patch').write_text(enrollment)
    (prepared/'recipes.patch').write_text(recipes_patch)
    (prepared/'migration.json').write_bytes(canonical(result)+b'\n')
    for name in ('enrollment.patch','recipes.patch'): subprocess.run(['git','apply','--check',str(prepared/name)],cwd=ROOT,check=True)
    print(json.dumps(dict(recipes=len(result['migrated']),exceptions=len(result['exceptions']),sources=len(result['sources']),
        new_descriptors=new_descriptors,shards=len(inv['shards']),inventory_sha256=digest(raw),
        lines_removed=sum(r['lines_removed'] for r in result['migrated']),bytes_removed=sum(r['bytes_removed'] for r in result['migrated'])),indent=2))
    return result


if __name__=='__main__': prepare()
