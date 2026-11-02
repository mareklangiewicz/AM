"""Read-only acceptance of one authorized sharded publication before recipe push.

Downloads exact same-run public artifacts and catalog Git objects. Never dispatches,
pushes, repins, installs or executes app binaries. Run from the reviewed checkout.
"""
import argparse
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import re
import shlex
import subprocess
import tempfile
import zipfile

from collector import require, timestamp
from delivery import (URL, REMOTE_REF, ZIP_CAP, bounded, environment, remote_git,
                      unpack_artifact, verify_artifact)
from identity_batch import ROOT
from large_evidence import DIRECTORY, PAYLOAD_HASH
from migration_batch import pipeline
from publication import REF, blob, git
from shard_delivery import inventory, read_shard
from shards import compose, root_index
from storage import canonical, content, decode, digest


def accept(run_id, revision, parent, output):
    require(re.fullmatch('[1-9][0-9]*', run_id) and re.fullmatch('[0-9a-f]{40}', revision) and
            re.fullmatch('[0-9a-f]{40}', parent), 'acceptance_arguments')
    output = Path(output); output.mkdir(exist_ok=False)
    token = subprocess.run(['gh','auth','token','--hostname','github.com'],check=True,
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,timeout=10).stdout.strip()
    def api(route, cap=1_000_000):
        with tempfile.TemporaryDirectory(prefix='catalog-accept-api-') as scratch:
            return bounded(['gh','api','--hostname','github.com','repos/mareklangiewicz/AM/'+route],
                env=environment(token,scratch,github=True),cap=cap)
    run = decode(api(f'actions/runs/{run_id}'))
    require(run['status']=='completed' and run['conclusion']=='success' and
            run['head_sha']==revision and run['head_branch']=='main-marek' and
            run['path']=='.github/workflows/catalog-shards.yml' and run['event']=='workflow_dispatch' and
            run['run_attempt']==1, 'acceptance_run')
    listing = decode(api(f'actions/runs/{run_id}/artifacts?per_page=100'))
    require(listing['total_count']==len(listing['artifacts']) and len(listing['artifacts'])<=33,
            'acceptance_artifacts')
    (output/'run.json').write_bytes(canonical(run)+b'\n')
    (output/'artifacts.json').write_bytes(canonical(listing)+b'\n')
    (output/'logs.zip').write_bytes(api(f'actions/runs/{run_id}/logs',20_000_000))
    artifacts = {row['name']:row for row in listing['artifacts']}
    require(len(artifacts)==len(listing['artifacts']), 'duplicate_artifacts')
    publication = artifacts[f'catalog-shard-publication-{run_id}-1']
    require(publication['expired'] is False and publication['size_in_bytes'] <= 64_000,
            'publication_artifact_bound')
    packed = api(f'actions/artifacts/{publication["id"]}/zip',64_000)
    require(publication['digest']=='sha256:'+digest(packed), 'publication_artifact_digest')
    (output/'publication.zip').write_bytes(packed)
    with zipfile.ZipFile(io.BytesIO(packed)) as archive:
        require(archive.namelist()==['publication.json'] and
                archive.getinfo('publication.json').file_size <= 64_000, 'publication_artifact_files')
        published = decode(archive.read('publication.json'))
    require(published['source_revision']==revision and published['parent']==parent and
            published['run_id']==run_id and published['run_attempt']=='1', 'publication_provenance')
    context = dict(repository='mareklangiewicz/AM',repository_id='1291019762',
        event='workflow_dispatch',ref='refs/heads/main-marek',sha=revision,workflow_sha=revision,
        approved_revision=revision,run_id=run_id,run_attempt='1',previous_publication=parent,
        inventory_sha256=published['inventory_sha256'])
    raw = (DIRECTORY/'prepared/inventory.json').read_bytes()
    for path in ('payload.json','prepared/inventory.json','prepared/migration.json'):
        relative = str((DIRECTORY/path).relative_to(ROOT))
        require(git(ROOT,'show',revision+':'+relative)==(DIRECTORY/path).read_bytes(),
                'acceptance_source_data_changed')
    manifests = inventory(context,raw,revision,ROOT)
    require(set(artifacts)=={f'restricted-catalog-{run_id}-1-{name}' for name in manifests} |
            {f'catalog-shard-publication-{run_id}-1'}, 'unexpected_artifacts')
    repo = output/'git'
    repo.mkdir()
    git(repo,'init','--bare','--quiet','--template=')
    remote = remote_git(repo,token,'ls-remote','--refs',URL,REMOTE_REF).decode().strip()
    require(remote==f'{published["commit"]}\t{REMOTE_REF}', 'acceptance_catalog_moved')
    remote_git(repo,token,'fetch','--quiet','--no-tags','--depth=2',URL,f'{REMOTE_REF}:{REF}')
    commit = git(repo,'rev-parse',REF).decode().strip()
    require(commit==published['commit'] and git(repo,'show','-s','--format=%P',commit).decode().strip()==parent,
            'acceptance_git_parent')
    trees = {}
    for name, manifest in manifests.items():
        prior = read_shard(repo,parent,name)
        ctx = dict(context,manifest_sha256=digest(manifest))
        if prior is None: ctx['previous_publication']=''
        row = artifacts[f'restricted-catalog-{run_id}-1-{name}']
        meta = decode(api(f'actions/artifacts/{row["id"]}'))
        observed_run = meta['workflow_run']
        require(meta['name']==row['name'] and meta['expired'] is False and
                meta['digest']==row['digest'] and meta['size_in_bytes']<=ZIP_CAP and
                observed_run['id']==int(run_id) and observed_run['head_sha']==revision and
                observed_run['repository_id']==observed_run['head_repository_id']==1291019762 and
                observed_run['head_branch']=='main-marek', 'acceptance_artifact_origin')
        packed = api(f'actions/artifacts/{row["id"]}/zip',ZIP_CAP)
        require(meta['digest']=='sha256:'+digest(packed), 'acceptance_artifact_digest')
        (output/f'shard-{name}.zip').write_bytes(packed)
        (output/f'shard-{name}-metadata.json').write_bytes(canonical(meta)+b'\n')
        files = unpack_artifact(packed)
        trees[name] = verify_artifact(files,ctx,manifest,revision,prior)
    root_raw = blob(repo,commit,'index.json',2_000_000)
    root = root_index(root_raw)
    require(root['collector_revision']==revision and root['run']=={'id':run_id,'attempt':'1'},
            'acceptance_root_context')
    require(timestamp(root['generated_at']) <= datetime.now(timezone.utc), 'future_publication')
    tree = compose(trees,generated_at=root['generated_at'],revision=revision,run=root['run'])
    require(tree['index.json']==root_raw and digest(root_raw)==published['index_sha256'], 'acceptance_root')
    listing_raw = git(repo,'ls-tree','-rz',commit)
    (output/'git-tree.z').write_bytes(listing_raw)
    records = listing_raw.split(b'\0')
    observed = {}
    for record in records:
        if not record: continue
        metadata,path = record.split(b'\t',1)
        mode,kind,oid = metadata.split(b' ')
        require(mode==b'100644' and kind==b'blob', 'acceptance_git_mode')
        observed[path.decode()] = oid.decode()
    require(set(observed)==set(tree), 'acceptance_git_paths')
    for path,body in tree.items():
        require(git(repo,'hash-object','--stdin',data=body).decode().strip()==observed[path], 'acceptance_git_blob')
    entries, aliases = {}, {}
    for candidate in trees.values():
        index = decode(candidate['index.json']); entries.update(index['entries']); aliases.update(index['aliases'])
    payload_raw = (DIRECTORY/'payload.json').read_bytes()
    require(digest(payload_raw)==PAYLOAD_HASH, 'acceptance_payload_digest')
    payload = decode(payload_raw)
    frozen = {r['path']:(row,r) for row in payload['rows'] for r in row['recipes']}
    migration = decode((DIRECTORY/'prepared/migration.json').read_bytes())
    for item in migration['migrated']:
        require(digest((ROOT/item['path']).read_bytes())==item['candidate_sha256'], 'acceptance_recipe_changed')
        row,recipe = frozen[item['path']]
        entry = entries[aliases[row['alias']]['request_id']]
        body = tree[entry['observation']['path']]
        value = content(body,entry['descriptor'])
        releases = value if isinstance(value,list) else [value]
        assets = {a['browser_download_url'] for release in releases for a in release['assets']}
        selections = [subprocess.run(['sh','-c','APP='+shlex.quote(Path(item['path']).name)+'\n'+pipeline(row,recipe[key])],
            input=body,capture_output=True,check=True,timeout=10).stdout.decode().strip()
            for key in ('install_selector','update_selector')]
        require(selections[0]==selections[1] and selections[0] in assets, 'acceptance_actual_selector')
    from consumer import lookup
    representatives = {}
    for item in migration['migrated']:
        representatives.setdefault(Path(item['path']).parent.name,item['alias'])
    reader_checks = []
    for alias in dict.fromkeys(representatives.values()):
        entry = entries[aliases[alias]['request_id']]
        expected = tree[entry['observation']['path']]
        body, _ = lookup(alias,commit=commit)
        require(body==expected, 'acceptance_python_reader')
        shell = subprocess.run(['sh',str(ROOT/'modules/catalog.am'),alias,'--commit',commit],
            env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8',
                 'AMREPO':'https://raw.githubusercontent.com/mareklangiewicz/AM/main-marek'},
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=95)
        require(shell.returncode==0 and shell.stdout==expected, 'acceptance_shell_reader')
        reader_checks.append(dict(alias=alias,sha256=digest(expected),both_readers=True))
    result = dict(outcome='accepted',commit=commit,parent=parent,source_revision=revision,
        run_id=run_id,shards=len(trees),recipes=len(migration['migrated']),
        original_selectors=2*len(migration['migrated']),tree_bytes=sum(map(len,tree.values())),
        index_sha256=digest(root_raw),pinned_readers=reader_checks,
        verified_at=datetime.now(timezone.utc).isoformat())
    (output/'acceptance.json').write_bytes(canonical(result)+b'\n')
    print(json.dumps(result,indent=2))
    token=b''
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id',required=True)
    parser.add_argument('--revision',required=True)
    parser.add_argument('--parent',required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    accept(args.run_id,args.revision,args.parent,args.output)
