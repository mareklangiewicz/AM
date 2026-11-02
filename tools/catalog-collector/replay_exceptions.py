"""Offline ticket-68 artifact/Git replay using actual accepted parent artifacts."""
from datetime import datetime, timezone
import io
import json
import tarfile
import tempfile
import zipfile

from collector import Descriptor, require
from delivery import unpack_artifact, verify_artifact
from exception_batch import DIRECTORY, PREVIOUS
from identity_batch import ROOT
from publication import git
from shard_delivery import publish_root_local
from shards import compose, split
from storage import apply, canonical, digest, validate


def build():
    archive=PREVIOUS/'live-evidence-41471816957.tar.gz'
    require(digest(archive.read_bytes())=='b0984b9547de3f26ee1b6732f806ef2efcee58a2b846ef336bd75edbf67c2401','parent_evidence_digest')
    prior={}
    with tarfile.open(archive) as tar:
        for name in json.loads((PREVIOUS/'prepared/inventory.json').read_bytes())['shards']:
            files=unpack_artifact(tar.extractfile(f'shard-{name}.zip').read())
            tree={p.removeprefix('candidate/'):body for p,body in files.items() if p.startswith('candidate/')}
            validate(tree);prior[name]=tree
    prepared=DIRECTORY/'prepared'
    inv=json.loads((prepared/'inventory.json').read_bytes())
    migration=json.loads((prepared/'migration.json').read_bytes())
    sources={s['request_id']:s for s in migration['sources']}
    gen=datetime.now(timezone.utc).isoformat();rev='a'*40
    ctx=dict(repository='mareklangiewicz/AM',repository_id='1291019762',event='workflow_dispatch',ref='refs/heads/main-marek',
        sha=rev,workflow_sha=rev,approved_revision=rev,run_id='1',run_attempt='1',
        inventory_sha256=digest((prepared/'inventory.json').read_bytes()),previous_publication='6f21b8c1d2bf271f570a0177bc1068bb9ca43d0a')
    trees={}; metrics=[]
    for name,row in inv['shards'].items():
        manifest=(ROOT/row['path']).read_bytes();previous=prior.get(name)
        old=validate(previous) if previous else None
        attempts=[]
        for source in json.loads(manifest)['sources']:
            rid=source['request_id'];descriptor=Descriptor(source['url'])
            if old:
                entry=old['entries'][rid]
                body=b'';report=dict(started_at=gen,completed_at=gen,public_headers={});status=304;condition=entry['validators']
            else:
                directory=ROOT/sources[rid]['evidence'];report=json.loads((directory/'report.json').read_bytes())
                body=(directory/'body.json').read_bytes();require(digest(body)==report['body_sha256'],'body_digest')
                status=200;condition={}
            attempts.append(dict(request_id=rid,descriptor={k:getattr(descriptor,k) for k in ('url','api_version','accept')},
                repository_id=source['repository_id'],request_started_at=report['started_at'],response_completed_at=report['completed_at'],
                attempt_finished_at=report['completed_at'],status=status,headers=report['public_headers'],body=body,condition=condition,outcome='response'))
        tree,transitions=apply(previous,manifest,attempts,workflow_identity=1291019762,generated_at=gen,revision=rev,run={'id':'1','attempt':'1'})
        context=dict(ctx,manifest_sha256=digest(manifest))
        if previous is None: context['previous_publication']=''
        files={'candidate/'+p:b for p,b in tree.items()}
        files.update({a['request_id']+'.body':a['body'] for a in attempts})
        records=[dict(**{k:v for k,v in a.items() if k!='body'},body_bytes=len(a['body']),body_sha256=digest(a['body'])) for a in attempts]
        files['report.json']=canonical(dict(context=context,run={'complete':True},attempts=records))
        files['storage-report.json']=canonical(dict(outcome='validated_candidate',transitions=transitions,files={p:dict(bytes=len(b),sha256=digest(b)) for p,b in tree.items()}))
        buf=io.BytesIO()
        with zipfile.ZipFile(buf,'w',compression=zipfile.ZIP_DEFLATED) as stream:
            for p,b in files.items(): stream.writestr(p,b)
        packed=buf.getvalue(); require(verify_artifact(unpack_artifact(packed),context,manifest,rev,previous)==tree,'artifact_roundtrip')
        trees[name]=tree;metrics.append(dict(shard=name,sources=len(attempts),tree_bytes=sum(map(len,tree.values())),zip_bytes=len(packed)))
    root=compose(trees,generated_at=gen,revision=rev,run={'id':'1','attempt':'1'})
    require(split(root)==trees,'root_roundtrip')
    # Every old alias/descriptor/body survives. Only receipt/provenance timestamps change.
    for name,oldtree in prior.items():
        old,new=validate(oldtree),validate(trees[name])
        require(set(old['aliases'])<=set(new['aliases']) and set(old['entries'])==set(new['entries']),'old_sources_removed')
        for rid,entry in old['entries'].items():
            require(entry['descriptor']==new['entries'][rid]['descriptor'],'old_descriptor_changed')
            require(oldtree[entry['observation']['path']]==trees[name][new['entries'][rid]['observation']['path']],'old_body_changed')
    with tempfile.TemporaryDirectory(prefix='am-exception-git-') as temporary:
        from pathlib import Path
        repo=Path(temporary);git(repo,'init','--bare','--quiet','--template=')
        commit=publish_root_local(repo,root,None,shard_count=len(trees))
        listing=git(repo,'ls-tree','-rz',commit); actual={}
        for record in listing.split(b'\0'):
            if not record:continue
            meta,path=record.split(b'\t');mode,kind,oid=meta.split(b' ')
            require(mode==b'100644' and kind==b'blob','git_modes');actual[path.decode()]=oid.decode()
        require(set(actual)==set(root),'git_paths')
        for path,body in root.items(): require(git(repo,'hash-object','--stdin',data=body).decode().strip()==actual[path],'git_blob')
        try: publish_root_local(repo,root,None,shard_count=len(trees))
        except ValueError as error: require(str(error)=='stale_parent','wrong_parent_refusal')
        else: raise ValueError('stale_parent_accepted')
        object_bytes=sum(p.stat().st_size for p in (repo/'objects').rglob('*') if p.is_file())
    report=dict(interpretation='Offline artifact/Git replay: 719 old conditional responses and workflow context are synthetic; new bodies are actual saved evidence.',
        generated_at=gen,shards=metrics,root_tree_bytes=sum(map(len,root.values())),root_index_bytes=len(root['index.json']),
        lookup_bytes=len(root['lookup.tsv']),git_objects_bytes=object_bytes,all_old_aliases_descriptors_bodies_preserved=True,
        exact_artifact_git_roundtrip=True,stale_parent_refused=True)
    (prepared/'replay.json').write_bytes(canonical(report)+b'\n')
    return root,metrics,gen


if __name__=='__main__':
    tree,metrics,gen=build();print((DIRECTORY/'prepared/replay.json').read_text())
