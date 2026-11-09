"""Prepare one v3 enrollment from public identities and exact recipe bindings.

Different upstreams for the same app receive stable catalog aliases. Installed
APP names are not changed. Acquisition/publication remain separate operations.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

import host_catalog as host


def identities(directories):
    result={};source=None
    for directory in directories:
        report=json.loads((directory/'identities.json').read_text())
        if source is not None and report['source']!=source:raise ValueError('identity source pins differ')
        source=report['source']
        checked={}
        for row in report['repositories']:
            name=row['evidence']
            if not re.fullmatch(r'[0-9]{4}[.]json',name):raise ValueError('identity evidence path')
            if name not in checked:checked[name]=hashlib.sha256((directory/name).read_bytes()).hexdigest()
            if checked[name]!=row['evidence_sha256']:raise ValueError('identity evidence changed')
            row=dict(row,evidence=directory.name+'/'+row['evidence'])
            old=result.get(row['requested_repository'].lower())
            if old and old.get('repository_id')!=row.get('repository_id'):
                raise ValueError('identity changed between probes')
            if old and old['observed_at']>row['observed_at']:continue
            result[row['requested_repository'].lower()]=row
    return source,result


def allocate_name(repository,rid,used):
    name=re.sub('[^a-z0-9_.+-]','-',repository.split('/')[-1].lower())[:64]
    if not name or not re.match('[a-z0-9]',name):name='repo-'+str(rid)
    if name in used:name='repo-'+str(rid)
    if name in used:raise ValueError('source-name collision')
    return name


def plan(scan,directories):
    source,known=identities(directories)
    if scan['source']!=source:raise ValueError('scan source differs from identity evidence')
    current,sources=host.configuration()
    byapp={row['app']:dict(app=row['app'],repository_id=row['repository_id'],repository=row['repository']) for row in current}
    reserved=set(byapp)|{row['app'] for row in scan['candidates']+scan['ambiguous']}
    bindings=[];exceptions=[];aliases=[]
    for candidate in scan['candidates']+scan['ambiguous']:
        app=candidate['app'];groups={}
        for proof in candidate['bindings']:
            raw=(host.ROOT/proof['recipe']).read_bytes()
            if hashlib.sha256(raw).hexdigest()!=proof['sha256']:raise ValueError('recipe changed: '+proof['recipe'])
            identity=known.get(proof['repository'].lower())
            if identity is None:raise ValueError('missing identity evidence: '+proof['repository'])
            if identity['status'] not in ('verified','no_public_release'):
                retained=[rid for rid,name in sources.items() if name.lower()==proof['repository'].lower()]
                if len(retained)==1:
                    identity=dict(identity,repository_id=int(retained[0]),repository=sources[retained[0]],
                        status='retained_identity',retained_identity_source=source)
                else:
                    exceptions.append(dict(app=app,recipe=proof['recipe'],repository=proof['repository'],reason=identity['status']))
                    continue
            rid=identity['repository_id'];groups.setdefault(rid,[]).append((proof,identity))
        if not groups:continue
        # Keep published names stable. Prefer x86_64 for a new multi-source app;
        # other source variants get an explicit numeric suffix, never overwrite it.
        preferred=byapp.get(app,{}).get('repository_id')
        if preferred not in groups:
            if app in byapp:raise ValueError('published app source no longer matches reviewed recipes: '+app)
            preferred=min(groups,key=lambda rid:(not any(p['recipe'].startswith('programs/x86_64/') for p,_ in groups[rid]),rid))
        for rid,proofs in groups.items():
            catalog_app=app
            if rid!=preferred:
                suffix='.src-'+str(rid);catalog_app=app[:64-len(suffix)]+suffix
                if catalog_app in reserved and byapp.get(catalog_app,{}).get('repository_id')!=rid:
                    raise ValueError('catalog alias collision')
                reserved.add(catalog_app)
                aliases.append(dict(app=app,catalog_app=catalog_app,repository_id=rid))
            spelling={identity['repository'] for _,identity in proofs}
            if len({name.lower() for name in spelling})!=1:raise ValueError('source canonical identity conflict')
            canonical=proofs[0][1]['repository']
            byapp[catalog_app]=dict(app=catalog_app,repository_id=rid,repository=canonical)
            for proof,identity in proofs:
                bindings.append(dict(proof,app=app,catalog_app=catalog_app,
                    requested_repository=proof['repository'],
                    repository_id=rid,repository=canonical,source_status=identity['status'],
                    identity_evidence=identity['evidence'],identity_evidence_sha256=identity['evidence_sha256']))
                if identity['status']=='retained_identity':bindings[-1]['retained_identity_source']=source
    # One canonical spelling per numeric source, including already-enrolled apps.
    canonical={}
    for row in known.values():
        if 'repository_id' in row:
            rid=row['repository_id']
            if rid in canonical and canonical[rid].lower()!=row['repository'].lower():raise ValueError('canonical source disagreement')
            canonical[rid]=row['repository']
    for row in byapp.values():row['repository']=canonical.get(row['repository_id'],row['repository'])
    registry=json.loads((host.ROOT/'tools/catalog-collector/source-names.json').read_text())
    used=set(registry['active'].values())|set(registry['retired'])
    for row in sorted(byapp.values(),key=lambda row:row['repository_id']):
        rid=str(row['repository_id'])
        if rid not in registry['active']:
            name=allocate_name(row['repository'],row['repository_id'],used)
            registry['active'][rid]=name;used.add(name)
    recipes={row['app'] for row in current if 'recipe' in row}
    extra=[row for app,row in sorted(byapp.items()) if app not in recipes]
    return dict(source=source,observed_at=host.utc(),enrollment=extra,registry=registry,
        bindings=bindings,aliases=aliases,exceptions=exceptions,
        app_count=len(byapp),source_count=len({row['repository_id'] for row in byapp.values()}),
        unresolved=scan['unresolved'],
        note='One catalog; aliases distinguish different upstreams. Empty-release sources are not usable selections. No acquisition/publication or host writes.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scan',type=Path,required=True)
    parser.add_argument('--identities',type=Path,nargs='+',required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    result=plan(json.loads(args.scan.read_text()),args.identities)
    if args.out.exists():raise ValueError('receipt already exists')
    if result['source_count']>host.SOURCE_CAP:raise ValueError('enrollment exceeds configured source allowance')
    if args.apply:
        folder=host.ROOT/'tools/catalog-collector'
        (folder/'collection-apps.json').write_text(json.dumps(result['enrollment'],indent=2)+'\n')
        (folder/'source-names.json').write_text(json.dumps(result['registry'],indent=2)+'\n')
        host.configuration()
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ('app_count','source_count')}))


if __name__=='__main__':main()
