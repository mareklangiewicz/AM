"""Prepare labelled wire-limit browser fixtures, not real upstream observations."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/catalog-collector'))
import contracts as c


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True,help='Qualified title-boundary YAML')
    parser.add_argument('--work',type=Path,required=True)
    args=parser.parse_args();args.work.mkdir(parents=True,exist_ok=False)
    title=c.decode(args.source.read_bytes());revision=title['schema'].split('/')[-3]
    title.update(repository_id=123,repository='synthetic/boundary-title')
    target=c.FILE_CAP-128
    record=next(iter(title['releases'].values()));record['title']+='x'*(target-len(c.encode(title)))
    dense=copy.deepcopy(title);dense.update(repository='synthetic/boundary-density')
    release=copy.deepcopy(record);release.update(tag='synthetic-density',title='',prerelease=False,
        url='https://example.invalid/release',download_base='https://example.invalid/download/',assets={})
    dense['releases']={'1':release}
    def fill(count):
        release['assets']={str(i):dict(name=f'asset-{i:05d}-x86_64.AppImage',url_suffix=f'{i}.AppImage',size=1)
                           for i in range(1,count+1)}
        return c.encode(dense)
    low,high=1,32768;count=0
    while low<=high:
        mid=(low+high)//2
        if len(fill(mid))<=target:count=mid;low=mid+1
        else:high=mid-1
    body=fill(count);release['title']='x'*(target-len(body))
    cases={}
    for name,source in (('title',title),('density',dense)):
        raw=c.encode(source);c.decode(raw)
        if len(raw)!=target:raise AssertionError('boundary size')
        apps={'boundary':'repositories/boundary.yaml'}
        inputs={key:revision for key in ('source','policy','recipes','rules','schemas')}
        tree={'catalog.yaml':c.encode(dict(c.header('catalog',revision),inputs=inputs,
              producer=dict(id=1,attempt=1),retention='32-plus-stable-exact-tag-v1')),
              'apps.yaml':c.encode(dict(c.header('apps',revision),apps=apps)),
              'repositories/boundary.yaml':raw}
        tree.update(c.partition_provenance(apps,{'boundary':{arch:dict(repository_id=123,availability='unknown',classification='unknown')
            for arch in ('x86_64','aarch64','i686','armv7l')}},revision))
        c.validate_tree(tree)
        hashes={path:hashlib.sha256(body).hexdigest() for path,body in sorted(tree.items())}
        pin=hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest()[:40]
        folder=args.work/name
        for path,body in tree.items():
            out=folder/path;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(body)
        cases[name]=dict(pin=pin,folder=name,bytes=len(raw),releases=len(source['releases']),
            assets=sum(len(value['assets']) for value in source['releases'].values()),hashes=hashes,
            delivery=dict(pin=pin,source=revision,baseline=revision,sources=1,apps=1,refused=[],
                          label='Synthetic wire-limit fixture · not upstream observations'))
    (args.work/'cases.json').write_text(json.dumps(dict(synthetic=True,cases=cases),indent=2)+'\n')
    print(json.dumps({name:{key:value for key,value in row.items() if key not in ('hashes','delivery')} for name,row in cases.items()},indent=2))


if __name__=='__main__':main()
