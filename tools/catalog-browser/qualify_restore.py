"""Verify and restore a retained exact Pages artifact locally, without deploying."""
import argparse
import ast
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import zipfile

from stage import ROOT
sys.path.insert(0,str(ROOT/'tools/catalog-collector'))
import contracts as c


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive',type=Path,required=True)
    parser.add_argument('--sha256',required=True)
    parser.add_argument('--source',type=c.pin,required=True)
    parser.add_argument('--work',type=Path,required=True)
    args=parser.parse_args();raw=args.archive.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=args.sha256:raise ValueError('artifact archive digest')
    # Recovery follows the approved manifest at the retained source revision,
    # even when a later website adds or removes an asset. Parse data, never run it.
    stage_source=subprocess.check_output(['git','-C',str(ROOT),'show',args.source+':tools/catalog-browser/stage.py'])
    assignments=[node for node in ast.parse(stage_source).body if isinstance(node,ast.Assign)
                 and any(isinstance(target,ast.Name) and target.id=='FILES' for target in node.targets)]
    if len(assignments)!=1:raise ValueError('retained source manifest')
    files_allowed=ast.literal_eval(assignments[0].value)
    if not isinstance(files_allowed,tuple) or not files_allowed or len(set(files_allowed))!=len(files_allowed):
        raise ValueError('retained manifest structure')
    if any(not isinstance(name,str) or not re.fullmatch(r'(?:web/catalog/[a-z0-9_.-]+\.(?:html|css|mjs)|tools/catalog-contract/[a-z0-9_.-]+\.mjs)',name) for name in files_allowed):
        raise ValueError('retained manifest path')
    args.work.mkdir(parents=True,exist_ok=False)
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        if archive.namelist()!=['artifact.tar']:raise ValueError('unexpected ZIP members')
        if archive.getinfo('artifact.tar').file_size>c.TREE_CAP:raise ValueError('tar bound')
        tar=archive.read('artifact.tar')
    files={};total=0
    with tarfile.open(fileobj=io.BytesIO(tar)) as archive:
        for member in archive:
            name=member.name.removeprefix('./')
            if member.isdir():continue
            if not member.isfile() or name in files:raise ValueError('artifact member type/duplicate')
            if name not in (*files_allowed,'index.html','.nojekyll') and not re.fullmatch(
                r'review-data/[a-f0-9]{40}/(?:(?:catalog|apps)\.yaml|(?:repositories|provenance)/'+c.NAME+r'\.yaml)',name):
                raise ValueError('artifact path allowlist')
            total+=member.size
            if member.size>c.FILE_CAP or total>c.TREE_CAP or len(files)>=20020:raise ValueError('artifact bound')
            files[name]=archive.extractfile(member).read()
    # The exact retained deployment tar omits the optional staging marker.
    if not set((*files_allowed,'index.html'))<=set(files):raise ValueError('missing website files')
    hashes={name:hashlib.sha256(body).hexdigest() for name,body in files.items()}
    for name in files_allowed:
        if name=='web/catalog/delivery.mjs':continue
        source=subprocess.check_output(['git','-C',str(ROOT),'show',args.source+':'+name])
        if source!=files[name]:raise ValueError('artifact source bytes differ')
    delivery=files['web/catalog/delivery.mjs'].decode()
    if not delivery.startswith('export default ') or not delivery.endswith(';\n'):raise ValueError('delivery grammar')
    metadata=json.loads(delivery[len('export default '):-2])
    if metadata['source']!=args.source or not re.fullmatch('[a-f0-9]{40}',metadata['pin']):raise ValueError('delivery binding')
    prefix='review-data/'+metadata['pin']+'/'
    tree={name.removeprefix(prefix):body for name,body in files.items() if name.startswith(prefix)}
    if len(tree)!=sum(name.startswith('review-data/') for name in files):raise ValueError('mixed review pins')
    docs=c.validate_tree(tree)
    if len(docs['apps.yaml']['apps'])!=metadata['apps']:raise ValueError('review app count')
    if sum(name.startswith('repositories/') for name in tree)!=metadata['sources']:raise ValueError('review source count')
    # Keep the verified before-image, simulate a distinct later artifact directory,
    # then restore to a new path. Never overwrite either preserved version.
    for directory in ('before','later','restored'):
        target=args.work/directory;target.mkdir()
        for name,body in files.items():
            path=target/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
        if directory=='later':(target/'index.html').write_text('Synthetic later artifact; not deployed.\n')
    restored={path.relative_to(args.work/'restored').as_posix():hashlib.sha256(path.read_bytes()).hexdigest()
              for path in (args.work/'restored').rglob('*') if path.is_file()}
    if restored!=hashes:raise AssertionError('restored byte identity')
    result=dict(source=args.source,archive_sha256=args.sha256,tar_sha256=hashlib.sha256(tar).hexdigest(),
        artifact_bytes=len(raw),payload_bytes=total,files=len(files),review=metadata,
        staging_nojekyll_in_archive='.nojekyll' in files,
        restored_identical=True,remote_deployment=False,synthetic_later_artifact=True,
        checks='digest, tar allowlist/types, exact source bytes, delivery and full review tree, restored file hashes',
        file_sha256=hashes)
    (args.work/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:value for key,value in result.items() if key!='file_sha256'},indent=2))


if __name__=='__main__':main()
