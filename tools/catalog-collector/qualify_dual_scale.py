"""Temporary dual-format artifact resource check; no enrollment or publication.

Separate preparation/validation processes give meaningful phase RSS high-waters.
The trusted artifact gate runs unchanged on synthetic parents/identities; checkout,
live acquisition and actual enrollment authority are explicitly not qualified.
"""
import argparse
import gc
import hashlib
import json
from pathlib import Path
import re
import resource
import subprocess
import sys
import time
import zipfile

import contracts as c
import pipeline_publication as p
from publication import git
from writer import document
from yaml_publication import schema_url


def prepare(args):
    begin=time.monotonic();evidence=json.loads((args.qualified_work/'receipt.json').read_text())
    names=json.loads((c.ROOT/'tools/catalog-collector/source-names.json').read_text())['active']
    ids={label:rid for rid,label in names.items()};templates=[]
    for name in sorted(evidence['seed_sha256']):
        rid=ids[Path(name).stem]
        templates.append(git(args.legacy_repo,'show',evidence['saved_baseline']+':repositories/'+rid+'.yaml'))
    output=args.work/'artifact';(output/'format-2/repositories').mkdir(parents=True)
    hashes={'format-2':{},'format-3':{}};sizes={'format-2':0,'format-3':0};counts={'format-2':0,'format-3':0}
    def write(channel,path,raw):
        target=output/channel/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        hashes[channel][path]=hashlib.sha256(raw).hexdigest();sizes[channel]+=len(raw);counts[channel]+=1
    descriptor=c.decode((args.qualified_work/'tree/catalog.yaml').read_bytes())
    apps={}
    for index in range(evidence['source_count']):
        app=f'scale-{index:05d}';rid=1000000000000+index;apps[app]=rid
        raw=templates[index%len(templates)]
        raw=re.sub(rb'^repository_id: .*$',f'repository_id: {rid}'.encode(),raw,count=1,flags=re.M)
        repository='synthetic/'+app if index!=evidence['source_count']-1 else 'synthetic/scale-boundary'
        raw=re.sub(rb'^repository: .*$',('repository: '+json.dumps(repository)).encode(),raw,count=1,flags=re.M)
        write('format-2',f'repositories/{rid}.yaml',raw)
        if (index+1)%1000==0:print(json.dumps(dict(stage='prepare_compatibility',sources=index+1)),flush=True)
    write('format-2','apps.yaml',document(dict(format=2,schema=schema_url(descriptor['inputs']['schemas']),apps=apps)).encode())
    for path in (args.qualified_work/'tree').rglob('*'):
        if path.is_file():write('format-3',path.relative_to(args.qualified_work/'tree').as_posix(),path.read_bytes())
    report=dict(version=1,run=descriptor['producer'],inputs=descriptor['inputs'],parents=dict(format_2=None,format_3=None),
        started_at=p.utc(),reported_at=p.utc(),collection_mode='saved',sources=[],selected_sources=[],
        target_counts=dict(enrolled=evidence['source_count'],selected=0,attempted=0,successful=0,failed=0,unknown=0,unattempted=0),
        acquisition=dict(http_attempts=0,charged_response_bytes=0,seconds=0),
        compatibility_metrics=dict(request_cap=750,response_byte_cap=536870912,acquisition_cap_seconds=900,stop_reason='complete'),hashes=hashes)
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    result=dict(synthetic=True,source_count=evidence['source_count'],app_count=len(apps),
        channel_bytes=sizes,channel_files=counts,total_bytes=sum(sizes.values()),
        report_bytes=(output/'report.json').stat().st_size,seconds=time.monotonic()-begin,
        peak_self_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    (args.work/'prepare.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)


def validate(args):
    begin=time.monotonic()
    descriptor=c.decode((args.work/'artifact/format-3/catalog.yaml').read_bytes())
    _,trees,docs=p.artifact(args.work/'artifact',run=descriptor['producer'],inputs=descriptor['inputs'],
                          parents=dict(format_2=None,format_3=None))
    result=dict(seconds=time.monotonic()-begin,validated_files={channel:len(tree) for channel,tree in trees.items()},
        validated_v3_sources=sum(obj['kind']=='repository' for obj in docs.values()),
        peak_self_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        peak_largest_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
        scope='Actual bounded artifact gate with full parallel channel validation; no checkout/enrollment authority, acquisition or publication.')
    (args.work/'validate.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qualified-work',type=Path,required=True)
    parser.add_argument('--legacy-repo',type=Path,required=True)
    parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--phase',choices=('all','prepare','validate'),default='all')
    args=parser.parse_args();resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
    if args.phase!='all':return prepare(args) if args.phase=='prepare' else validate(args)
    args.work.mkdir(parents=True,exist_ok=False)
    for phase in ('prepare','validate'):
        subprocess.run([sys.executable,'-B',__file__,'--qualified-work',str(args.qualified_work),
            '--legacy-repo',str(args.legacy_repo),'--work',str(args.work),'--phase',phase],check=True)
    # A local ZIP is a reproducible transfer-size proxy, not Actions wire usage.
    begin=time.monotonic();archive=args.work/'dual.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as output:
        for path in sorted((args.work/'artifact').rglob('*')):
            if path.is_file():output.write(path,path.relative_to(args.work/'artifact').as_posix())
    result=dict(synthetic=True,live_acquisition=False,enrollment_changed=False,remote_publication=False,
        source_head=git(c.ROOT,'rev-parse','HEAD').decode().strip(),
        implementation_files_sha256={name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in ('pipeline_publication.py','incremental.py','contracts.py','wire_validation.py','yaml_publication.py')},
        preparation=json.loads((args.work/'prepare.json').read_text()),validation=json.loads((args.work/'validate.json').read_text()),
        zip_bytes=archive.stat().st_size,zip_seconds=time.monotonic()-begin,
        address_space_cap_bytes=2*1024**3,
        limits='Synthetic repeated saved v2/v3 shapes, one v3 boundary stress source. Zero selected/acquired sources; original observations are not freshened. Separate processes, not an end-to-end collection or installed-host delivery receipt. ZIP-6 is not actual Actions transfer.')
    (args.work/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
