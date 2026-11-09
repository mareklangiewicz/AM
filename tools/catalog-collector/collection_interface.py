"""Explicit candidate creation and offline validation; publication is ticket 12."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time

import host_catalog as host
import contracts
from bounded import unique_object
from provenance import Evaluator
from incremental import Snapshot,Records,Candidate

def verify_checkout_inputs(inputs, registry):
    """Pins describe actual maintained bytes, including independently pinned inputs."""
    from publication import git
    if Path(registry).read_bytes()!=git(host.ROOT,'show',inputs['policy']+':tools/catalog-collector/source-names.json'):
        raise ValueError('source registry differs from policy pin')
    scopes={
        'source':['tools/catalog-collector','tools/catalog-contract','modules/catalog-contract-reader.am','modules/catalog-contract-parser.am','modules/catalog-contract-tables.am'],
        'policy':['tools/catalog-collector/collection-recipes.txt','tools/catalog-collector/collection-apps.json','tools/catalog-collector/source-names.json'],
        'recipes':['programs'],
        'rules':['tools/catalog-collector/provenance.py','tools/recipe-reconstruction'],
        'schemas':['docs/catalog-format-v3.md','schemas/catalog','tools/catalog-contract','modules/catalog-contract-parser.am','modules/catalog-contract-tables.am'],
    }
    for key,paths in scopes.items():
        changed=subprocess.run(['git','-C',str(host.ROOT),'diff','--quiet',inputs[key],'--',*paths]).returncode
        untracked=subprocess.check_output(['git','-C',str(host.ROOT),'ls-files','--others','--exclude-standard','--',*paths])
        if changed or untracked: raise ValueError('checkout differs from '+key+' input pin')


def registry_names(rows, path):
    registry=json.loads(Path(path).read_text(),object_pairs_hook=unique_object)
    if set(registry)!= {'active','retired'} or not isinstance(registry['retired'],list):
        raise ValueError('source registry')
    names=registry['active']
    if len(set(names.values()))!=len(names) or len(set(registry['retired']))!=len(registry['retired']):
        raise ValueError('duplicate source name')
    if set(names.values()) & set(registry['retired']): raise ValueError('retired source name')
    for rid,name in names.items():
        if not re.fullmatch('[1-9][0-9]*',rid) or not re.fullmatch(contracts.NAME,name) or name in ('.','..'):
            raise ValueError('source name spelling')
    if any(str(row['repository_id']) not in names for row in rows): raise ValueError('unallocated source')
    return names


def write_tree(directory, tree):
    directory.mkdir(parents=True,exist_ok=False)
    for name,body in tree.items():
        path=directory/name; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(body)


def collect(args):
    command_started=time.monotonic()
    revision=subprocess.check_output(['git','-C',str(host.ROOT),'rev-parse','HEAD'],text=True).strip()
    inputs={key:contracts.pin(getattr(args,key+'_revision') or revision)
            for key in ('source','policy','recipes','rules','schemas')}
    if args.output.exists(): raise ValueError('output must not exist')
    started_at=host.utc()
    if args.parent and not args.repo: raise ValueError('parent requires local repository')
    prior=Snapshot(args.repo,args.parent) if args.parent else None
    previous=Records(prior) if prior else {}
    # A collector-only revision must not rebind unchanged source documents.
    # Verification below refuses reuse if the schema checkout actually changed.
    if prior and args.schemas_revision is None:
        inputs['schemas']=prior.metadata['catalog.yaml']['root']['inputs']['schemas']
    verify_checkout_inputs(inputs,args.registry)
    prior_docs={path:meta['root'] for path,meta in prior.metadata.items() if 'root' in meta} if prior else {}
    profile=dict(source_cap=args.source_cap,request_cap=args.request_cap,total_cap=args.total_bytes,
                 seconds_cap=args.acquisition_seconds,reserve=args.rate_reserve,response_cap=args.response_bytes)
    if any(type(value) is not int or value<1 for value in profile.values()): raise ValueError('collection profile')
    rows,sources=host.configuration(source_cap=args.source_cap)
    names=registry_names(rows,args.registry)
    for path,obj in (prior.metadata.items() if prior else ()):
        if path.startswith('repositories/') and names.get(str(obj['repository_id']))+'.yaml'!=path.removeprefix('repositories/'):
            raise ValueError('source registry changed identity')
    acquired={}; metrics={}
    _,acquisition_report=host.collect(revision,previous,args.evidence,batch_size=args.batch_size,
                                      metrics=metrics,acquisitions=acquired,incremental=True,profile=profile,native_v3=True)
    tree={}
    report=[]
    for rid,acquisition in acquired.items():
        path='repositories/'+names[rid]+'.yaml'
        try:
            obj=contracts.source(contracts.decode(prior[path]) if prior and path in prior else None,acquisition,rid=rid,repository=sources[rid],revision=inputs['schemas'])
            tree[path]=contracts.encode(obj)
            report.append(dict(repository_id=int(rid),status='ok'))
        except (ValueError,KeyError,TypeError) as error:
            reason='document_overflow' if str(error)=='document_overflow' else 'source_validation'
            report.append(dict(repository_id=int(rid),status='failed',reason=reason))
    recorded={row['repository_id'] for row in report}
    for row in acquisition_report:
        if row['repository_id'] not in recorded:
            reason={'invalid_response':'source_validation','transport':'transport','collection_limit':'byte_budget'}.get(row.get('reason'),'unknown')
            if row.get('http_status')==401: reason='authentication'
            elif row.get('http_status') in (403,429): reason='quota'
            report.append(dict(repository_id=row['repository_id'],status='failed',reason=reason))
    apps={row['app']:'repositories/'+names[str(row['repository_id'])]+'.yaml' for row in rows
          if 'repositories/'+names[str(row['repository_id'])]+'.yaml' in tree or prior and 'repositories/'+names[str(row['repository_id'])]+'.yaml' in prior}
    tree['catalog.yaml']=contracts.encode(dict(contracts.header('catalog',inputs['schemas']),inputs=inputs,
                                               producer=dict(id=args.run_id,attempt=args.attempt),retention='32-plus-stable-exact-tag-v1'))
    tree['apps.yaml']=contracts.encode(dict(contracts.header('apps',inputs['schemas']),apps=apps))
    evaluator=Evaluator(host.ROOT,inputs,host.utc())
    reviews=json.loads(args.reviews.read_text(),object_pairs_hook=unique_object) if args.reviews else {}
    old_bindings={app:arches for path,doc in prior_docs.items() if path.startswith('provenance/') for app,arches in doc['apps'].items()}
    provenance={row['app']:{arch:evaluator.classify(row['app'],arch,row['repository_id'],
                           prior=old_bindings.get(row['app'],{}).get(arch),
                           review=reviews.get(row['app'],{}).get(arch))
                           for arch in ('x86_64','aarch64','i686','armv7l')} for row in rows if row['app'] in apps}
    tree.update(contracts.partition_provenance(apps,provenance,inputs['schemas']))
    tree=Candidate(prior,tree)
    write_tree(args.output/'format-3',tree)
    evidence=dict(version=1,started_at=started_at,reported_at=host.utc(),run=dict(id=args.run_id,attempt=args.attempt),inputs=inputs,
                  parents=dict(format_3=args.parent),
                  collection_mode='saved' if args.evidence else 'live',sources=report,
                  selected_sources=metrics['selected_repository_ids'],
                  target_counts=dict(enrolled=len(sources),selected=metrics['selected_sources'],attempted=len(report),
                                     successful=sum(row['status']=='ok' for row in report),
                                     failed=sum(row['status']=='failed' for row in report),unknown=0,
                                     unattempted=metrics['selected_sources']-len(report)),
                  collection_metrics=metrics,
                  validation=dict(format_3=tree.validation,format_3_parent=prior.validation if prior else None),
                  acquisition=dict(http_attempts=metrics['requests'],charged_response_bytes=metrics['response_bytes'],
                                   received_response_bytes_state='unknown',seconds=metrics['acquisition_seconds'],
                                   command_seconds=time.monotonic()-command_started),
                  hashes={channel:{name:hashlib.sha256(raw).hexdigest() for name,raw in content.items()}
                          for channel,content in (('format-3',tree),)})
    (args.output/'report.json').write_text(json.dumps(evidence,indent=2)+'\n')


def validate(args):
    if args.channel=='format-3':
        tree=contracts.read_directory(args.candidate)
        descriptor=contracts.decode(tree['catalog.yaml'])
        for key in ('source','policy','recipes','rules','schemas'):
            expected=getattr(args,'expected_'+key)
            if expected is not None and descriptor['inputs'][key]!=expected:
                raise ValueError('candidate input binding')
    elif args.channel=='status-1': contracts.read_directory(args.candidate,'status')
    else:
        tree={}
        for path in args.candidate.rglob('*'):
            if path.is_symlink(): raise ValueError('candidate symlink')
            if path.is_file():
                if path.stat().st_size>host.FILE_CAP: raise ValueError('document bound')
                tree[path.relative_to(args.candidate).as_posix()]=path.read_bytes()
        # Use the same bounded validator as collection and trusted publication;
        # the older materializing helper's 1,024-file profile cannot fit 5,000 sources.
        Candidate(None,tree,'format-2')


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='operation',required=True)
    c=sub.add_parser('collect')
    c.add_argument('--repo',type=Path,help='Local format-3 parent object repository')
    c.add_argument('--parent',type=contracts.pin,help='Exact v3 parent; omit for empty-channel bootstrap')
    c.add_argument('--evidence',type=Path)
    c.add_argument('--reviews',type=Path,help='Explicit exact-input custom classification reviews')
    c.add_argument('--output',type=Path,required=True)
    c.add_argument('--registry',type=Path,default=host.ROOT/'tools/catalog-collector/source-names.json')
    c.add_argument('--batch-size',type=int,default=500)
    c.add_argument('--source-cap',type=int,default=10000)
    c.add_argument('--request-cap',type=int,default=750)
    c.add_argument('--total-bytes',type=int,default=host.TOTAL_CAP)
    c.add_argument('--response-bytes',type=int,default=host.RESPONSE_CAP)
    c.add_argument('--acquisition-seconds',type=int,default=host.ACQUISITION_SECONDS)
    c.add_argument('--rate-reserve',type=int,default=host.RATE_RESERVE)
    c.add_argument('--run-id',type=int,required=True)
    c.add_argument('--attempt',type=int,default=1)
    for key in ('source','policy','recipes','rules','schemas'):
        c.add_argument('--'+key+'-revision',type=contracts.pin)
    v=sub.add_parser('validate')
    v.add_argument('--candidate',type=Path,required=True)
    v.add_argument('--channel',choices=('format-2','format-3','status-1'),default='format-3')
    schema=sub.add_parser('schema-revision',help='Read the schema pin from one exact bounded catalog descriptor; no network')
    schema.add_argument('--repo',type=Path,required=True)
    schema.add_argument('--parent',type=contracts.pin,required=True)
    for key in ('source','policy','recipes','rules','schemas'):
        v.add_argument('--expected-'+key,type=contracts.pin)
    from pipeline_publication import add_arguments
    add_arguments(sub)
    args=parser.parse_args(argv)
    if args.operation=='schema-revision':
        print(contracts.schema_revision(args.repo,args.parent));return
    if args.operation=='publish':
        from pipeline_publication import run
        result=run(args)
        active=('format-3','status-1')
        if result['validation']!='ok' or any(result['outcomes'][key]['state']!='confirmed' for key in active):
            raise SystemExit(1)
        return result
    if args.operation=='collect': collect(args)
    else: validate(args)
