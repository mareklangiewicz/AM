"""Offline maintained-policy parity on actual saved v2/v3 facts.

Does not implement an installed v3 transport or execute recipes. Retention/tag
differences are reported separately from shared-record fact/selection parity.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

import contracts as c
import host_catalog as host
from incremental import decode
from publication import git


def facts(doc):
    rows=[]
    for rid,record in doc['releases'].items():
        release=c.expand_release(record,doc['observed_at'])
        for aid,asset in release['assets'].items():
            rows.append('\t'.join([rid,aid,*[json.dumps(value,ensure_ascii=False) for value in
                (release['observed_at'],release.get('published_at',release.get('created_at')),
                 release['tag'],asset['name'],asset['url'],release['prerelease'])]]))
    return '\n'.join(rows)+('\n' if rows else '')


def run_policy(text,row,now):
    result=subprocess.run(['awk','-f',str(c.ROOT/'modules/catalog-yaml-policy.am')],
        input=text,text=True,capture_output=True,timeout=15,
        env={**os.environ,'LC_ALL':'C','AM_YAML_RECIPE':row['recipe'],
             'AM_YAML_REPOSITORY':str(row['repository_id']),'AM_YAML_NOW':now,
             'AM_YAML_PIN':'a'*40,'AM_YAML_STALE_OPTION':'release',
             'AM_YAML_INCLUDE_PUBLICATION':'1','AM_YAML_ACCEPT':'','AM_YAML_TOOL':''})
    return dict(code=result.returncode,output=result.stdout,diagnostic=result.stderr)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--saved-data',type=Path,required=True)
    parser.add_argument('--legacy-repo',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();started=time.monotonic()
    metadata=json.loads((args.saved_data/'review.json').read_text())
    names=json.loads((c.ROOT/'tools/catalog-collector/source-names.json').read_text())['active']
    rows,_=host.installation_configuration();cached={};results=[]
    for row in rows:
        rid=str(row['repository_id']);path='repositories/'+names[rid]+'.yaml'
        if path not in metadata['document_sha256']:
            results.append(dict(recipe=row['recipe'],state='saved_v3_source_unavailable'));continue
        if rid not in cached:
            raw=(args.saved_data/metadata['pin']/path).read_bytes()
            if hashlib.sha256(raw).hexdigest()!=metadata['document_sha256'][path]:raise ValueError('saved hash mismatch')
            target=c.decode(raw)
            original=git(args.legacy_repo,'show',metadata['baseline']+':repositories/'+rid+'.yaml')
            legacy=decode('repositories/'+rid+'.yaml',original,'format-2')[0]
            common=set(legacy['releases'])&set(target['releases'])
            for release_id in common:
                before=dict(legacy['releases'][release_id])
                before.setdefault('observed_at',legacy['observed_at'])
                if before!=c.expand_release(target['releases'][release_id],target['observed_at']):
                    raise AssertionError('common facts differ: '+rid+'/'+release_id)
            with tempfile.NamedTemporaryFile() as saved:
                saved.write(original);saved.flush()
                old_facts=subprocess.run(['sh',str(c.ROOT/'modules/catalog-yaml-reader.am'),'asset_facts',saved.name],
                    capture_output=True,text=True,check=True).stdout
            cached[rid]=(target,old_facts,facts(target),len(legacy['releases'])-len(common))
        target,old_facts,new_facts,removed=cached[rid]
        now=target['collected_at']
        old=run_policy(old_facts,row,now);new=run_policy(new_facts,row,now)
        parity=old==new
        if not parity and not removed:raise AssertionError('unexplained selection difference: '+row['recipe'])
        results.append(dict(recipe=row['recipe'],repository_id=int(rid),channel=row['channel'],
            compared_at=now,removed_legacy_release_records=removed,selection_equal=parity,
            v2=old,v3_facts=new,state='compared'))
    result=dict(source_revision=git(c.ROOT,'rev-parse','HEAD').decode().strip(),
        saved_pin=metadata['pin'],legacy_pin=metadata['baseline'],live_acquisition=False,
        installed_host_inspected=False,installed_v3_transport_qualified=False,
        policy='actual maintained awk; v2 shell asset_facts versus decoded v3 common-fact projection',
        clock='each source original successful collection time; not current freshness acceptance',
        maintained_recipes=len(rows),compared_sources=len(cached),seconds=time.monotonic()-started,
        identical_selections=sum(r.get('selection_equal',False) for r in results),rows=results)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:value for key,value in result.items() if key!='rows'},indent=2))


if __name__=='__main__':main()
