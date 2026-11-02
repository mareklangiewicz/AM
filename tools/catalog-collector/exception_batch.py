"""Explicit redirect evidence for ticket 68; no enrollment, retries or app downloads."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import time

from collector import require
from identity_batch import ROOT, OWN_REPOSITORY_ID, fetch
from large_evidence import DIRECTORY as PREVIOUS, PAYLOAD_HASH, saved, quota_stop
from migration_evidence import release_request
from storage import canonical, digest

DIRECTORY = ROOT/'docs/track/release-catalog/research/appimage-exceptions-next-20261102'


def numeric_identity(url, repository_id, out, deadline, *, token=None, curl='/usr/bin/curl'):
    require(url == f'https://api.github.com/repositories/{repository_id}' and
            type(repository_id) is int and repository_id > 0 and repository_id != OWN_REPOSITORY_ID,
            'numeric_identity_url')
    def validate(value, body):
        require(type(value) is dict and value.get('id') == repository_id and
                type(value.get('id')) is int and value.get('private') is False and
                value.get('visibility') == 'public' and
                type(value.get('full_name')) is str and
                re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',value['full_name']) and
                value['full_name'].lower() != 'mareklangiewicz/am', 'numeric_identity_mismatch')
        return dict(identity={k:value[k] for k in ('id','full_name','private','visibility')})
    return fetch(url,out,deadline,validate_value=validate,token=token,curl=curl)


def freeze():
    payload_raw=(PREVIOUS/'payload.json').read_bytes()
    require(digest(payload_raw)==PAYLOAD_HASH,'payload_changed')
    payload=json.loads(payload_raw)
    migration=json.loads((PREVIOUS/'prepared/migration.json').read_bytes())
    batch=json.loads((PREVIOUS/'live/batch.json').read_bytes())
    paths={item['path'] for item in migration['exceptions']}
    require(len(paths)==78,'exception_scope')
    rows=[]
    for row in payload['rows']:
        recipes=[recipe for recipe in row['recipes'] if recipe['path'] in paths]
        if not recipes: continue
        for recipe in recipes:
            require(digest((ROOT/recipe['path']).read_bytes())==recipe['sha256'],'recipe_changed')
        old=ROOT/batch['identities'][row['identity_request']]['evidence']
        identity=saved(old,row['identity_request'])
        if identity.get('status') != 301: continue
        target=identity['public_headers'].get('location','')
        require(re.fullmatch(r'https://api.github.com/repositories/[1-9][0-9]*',target),'redirect_target')
        rid=int(target.rsplit('/',1)[1])
        # Reuse an independently accepted canonical identity/body when available.
        reusable=next((r for r in batch['releases'] if r['repository_id']==rid and r['accepted'] and
                       r['fetch_url']==target+row['alias'][len(row['identity_request']):]),None)
        rows.append(dict(row,recipes=recipes,identity_target=target,repository_id=rid,
            original_identity_evidence=str(old.relative_to(ROOT)),
            original_identity_report_sha256=digest((old/'report.json').read_bytes()),reuse=reusable))
    require(len(rows)==59 and sum(len(r['recipes']) for r in rows)==65,'redirect_scope')
    DIRECTORY.mkdir(exist_ok=True)
    raw=canonical(dict(source_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
        original_payload_sha256=PAYLOAD_HASH,rows=rows))+b'\n'
    path=DIRECTORY/'queue.json'
    require(not path.exists() or path.read_bytes()==raw,'queue_already_frozen')
    path.write_bytes(raw)
    (DIRECTORY/'.gitattributes').write_text('**/headers.txt -text\n')
    print('Frozen',len(rows),'explicit redirect identities;',sum(r['reuse'] is None for r in rows),'new identity/release pairs')


def collect():
    queue=json.loads((DIRECTORY/'queue.json').read_bytes())
    out=DIRECTORY/'live'; out.mkdir(exist_ok=True)
    token=subprocess.run(['gh','auth','token','--hostname','github.com'],check=True,
        stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,timeout=10).stdout.strip()
    end=time.monotonic()+2400
    summary=dict(queue_sha256=digest((DIRECTORY/'queue.json').read_bytes()),
        policy='explicit-numeric-targets-no-redirects-no-retries',rows=[],stopped=None)
    def save(): (out/'batch.json').write_bytes(canonical(summary)+b'\n')
    def obtain(directory,url,send):
        prior=saved(directory,url)
        return prior if prior is not None else send()
    try:
        for index,row in enumerate(queue['rows']):
            if time.monotonic()>=end: summary['stopped']='deadline'; break
            rid=row['repository_id']; identity_url=row['identity_target']
            if row['reuse']:
                prior=row['reuse']
                original=json.loads((PREVIOUS/'live/batch.json').read_bytes())
                known=original['identities'][prior['alias'].split('/releases')[0]]
                report=saved(ROOT/known['evidence'],prior['alias'].split('/releases')[0])
                require(report['accepted'] and report['identity']['id']==rid,'reuse_identity')
                release=saved(ROOT/prior['evidence'],prior['fetch_url'])
                require(release['accepted'],'reuse_release')
                summary['rows'].append(dict(alias=row['alias'],repository_id=rid,
                    identity=report['identity'],identity_evidence=known['evidence'],
                    release_evidence=prior['evidence'],fetch_url=prior['fetch_url'],accepted=True,reused=True))
                save(); continue
            directory=out/f'identity-{index:02d}'
            report=obtain(directory,identity_url,lambda:numeric_identity(identity_url,rid,directory,
                min(end,time.monotonic()+30),token=token))
            result=dict(alias=row['alias'],repository_id=rid,accepted=False,
                identity_evidence=str(directory.relative_to(ROOT)),identity=report.get('identity'))
            summary['rows'].append(result); save()
            if quota_stop(report,(directory/'headers.txt').read_bytes()):
                summary['stopped']='quota_or_missing_quota'; break
            if not report['accepted']: continue
            url=identity_url+row['alias'][len(row['identity_request']):]
            directory=out/f'release-{index:02d}'
            report=obtain(directory,url,lambda:release_request(url,rid,directory,
                min(end,time.monotonic()+30),token=token))
            result.update(fetch_url=url,release_evidence=str(directory.relative_to(ROOT)),accepted=report['accepted'])
            save()
            print(json.dumps(dict(completed=index+1,total=len(queue['rows']),alias=row['alias'],accepted=report['accepted'])),flush=True)
            if quota_stop(report,(directory/'headers.txt').read_bytes()):
                summary['stopped']='quota_or_missing_quota'; break
    finally:
        token=b''; summary['completed_at']=datetime.now(timezone.utc).isoformat(); save()
    require(summary['stopped'] is None,'evidence_stopped')
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('freeze','collect'))
    args=parser.parse_args()
    freeze() if args.action=='freeze' else collect()
