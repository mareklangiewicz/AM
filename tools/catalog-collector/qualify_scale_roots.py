"""Offline reference-workload root check; no enrollment or remote writes.

Synthetic identities reuse saved evidence shapes. This compares global roots with per-source provenance; it does not measure collection throughput or complete snapshots.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import resource
import time

import contracts as c


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--saved-data',type=Path,required=True)
    parser.add_argument('--count',type=int,default=5000)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if not 1<=args.count<=10000:parser.error('--count must be 1..10000')
    started=time.monotonic()
    metadata=json.loads((args.saved_data/'review.json').read_text())
    folder=args.saved_data/metadata['pin']
    raw=(folder/'provenance.yaml').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=metadata['document_sha256']['provenance.yaml']:
        raise ValueError('saved provenance digest differs')
    saved=c.decode(raw)
    fixture=c.decode((c.ROOT/'tools/catalog-contract/fixtures/provenance.yaml').read_bytes())
    shapes={'saved_unknown':next(iter(saved['apps'].values())),
            'three_evidenced_architectures':fixture['apps']['example']}
    rows=[]
    for label,shape in shapes.items():
        apps={};bindings={}
        for index in range(args.count):
            app=f'scale-{index:05d}';rid=1000000000000+index
            apps[app]='repositories/'+app+'.yaml'
            bindings[app]=copy.deepcopy(shape)
            for arch,binding in bindings[app].items():
                binding['repository_id']=rid
                if 'recipe' in binding:binding['recipe']['path']=f'programs/{arch}/{app}'
        documents={
            'apps.yaml':dict(c.header('apps','a'*40),apps=apps),
            'provenance.yaml':dict(c.header('provenance','a'*40),apps=bindings),
        }
        partitions=c.partition_provenance(apps,bindings,'a'*40)
        largest=max(partitions,key=lambda path:len(partitions[path]))
        # Every generated partition has this same validated evidence shape. Check
        # complete app/source membership and exact byte bounds for all partitions;
        # parse the largest representative without pretending this is a full tree.
        c.provenance_references(apps,{path:1000000000000+index for index,path in enumerate(apps.values())},
            {path:dict(schema=c.header('provenance','a'*40)['schema'],apps={path.removeprefix('provenance/').removesuffix('.yaml'):bindings[path.removeprefix('provenance/').removesuffix('.yaml')]}) for path in partitions},{key:'a'*40 for key in ('schemas','recipes','rules')})
        c.decode(partitions[largest])
        rows.append(dict(scenario=label,path='provenance/<source>.yaml',documents=len(partitions),
            total_bytes=sum(map(len,partitions.values())),largest_bytes=len(partitions[largest]),
            configured_cap=c.FILE_CAP,unused_fraction=1-len(partitions[largest])/c.FILE_CAP,
            result='accepted' if max(map(len,partitions.values()))<=c.FILE_CAP else 'refused'))
        for name,obj in documents.items():
            body=c.encode(obj)
            row=dict(scenario=label,path=name,bytes=len(body),sha256=hashlib.sha256(body).hexdigest(),
                     configured_cap=c.FILE_CAP,unused_fraction=1-len(body)/c.FILE_CAP)
            if len(body)>c.FILE_CAP:
                # Exercise the actual maintained refusal path before YAML parsing.
                try:c.decode(body)
                except ValueError as error:row.update(result='refused',reason=str(error))
                else:raise AssertionError('oversized root unexpectedly accepted')
            else:
                c.decode(body);row['result']='accepted'
            rows.append(row)
    result=dict(synthetic=True,live_acquisition=False,source_count=args.count,app_count=args.count,
        saved_pin=metadata['pin'],saved_baseline=metadata['baseline'],saved_provenance_sha256=hashlib.sha256(raw).hexdigest(),
        shapes='saved unknown per-architecture bindings; independent fixture with shared/template/custom/unknown architecture evidence',
        seconds=time.monotonic()-started,peak_self_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,rows=rows)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
