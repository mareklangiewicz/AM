"""Explicit candidate creation and offline validation; publication is ticket 12."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

import host_catalog as host
import contracts
from yaml_publication import load_local, tree_documents
from bounded import unique_object
from provenance import Evaluator

LIMITS=dict(max_file_bytes=host.FILE_CAP,max_files=1024,max_tree_bytes=1024*1024*1024)


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
        'schemas':['schemas/catalog','tools/catalog-contract','modules/catalog-contract-parser.am','modules/catalog-contract-tables.am'],
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
    revision=subprocess.check_output(['git','-C',str(host.ROOT),'rev-parse','HEAD'],text=True).strip()
    inputs={key:contracts.pin(getattr(args,key+'_revision') or revision)
            for key in ('source','policy','recipes','rules','schemas')}
    verify_checkout_inputs(inputs,args.registry)
    if args.output.exists(): raise ValueError('output must not exist')
    previous=load_local(args.repo,args.parent,max_file_bytes=host.FILE_CAP)[1]
    if bool(args.v3_repo)!=bool(args.v3_parent): raise ValueError('v3 parent needs repository and exact pin')
    prior=contracts.read_local(args.v3_repo,args.v3_parent) if args.v3_parent else {}
    prior_docs=contracts.validate_tree(prior) if prior else {}
    rows,sources=host.configuration()
    names=registry_names(rows,args.registry)
    for path,obj in prior_docs.items():
        if obj['kind']=='repository' and names.get(str(obj['repository_id']))+'.yaml'!=path.removeprefix('repositories/'):
            raise ValueError('source registry changed identity')
    acquired={}; metrics={}
    legacy,legacy_report=host.collect(revision,previous,args.evidence,batch_size=args.batch_size,
                                      metrics=metrics,acquisitions=acquired)
    tree={path:raw for path,raw in prior.items() if path.startswith('repositories/')}
    report=[]
    for rid,acquisition in acquired.items():
        path='repositories/'+names[rid]+'.yaml'
        try:
            obj=contracts.source(prior_docs.get(path),acquisition,rid=rid,repository=sources[rid],revision=inputs['schemas'])
            tree[path]=contracts.encode(obj)
            report.append(dict(repository_id=int(rid),status='ok'))
        except (ValueError,KeyError,TypeError) as error:
            reason='document_overflow' if str(error)=='document_overflow' else 'source_validation'
            report.append(dict(repository_id=int(rid),status='failed',reason=reason))
    recorded={row['repository_id'] for row in report}
    for row in legacy_report:
        if row['repository_id'] not in recorded:
            reason={'invalid_response':'source_validation','transport':'transport','collection_limit':'byte_budget'}.get(row.get('reason'),'unknown')
            if row.get('http_status')==401: reason='authentication'
            elif row.get('http_status') in (403,429): reason='quota'
            report.append(dict(repository_id=row['repository_id'],status='failed',reason=reason))
    apps={row['app']:'repositories/'+names[str(row['repository_id'])]+'.yaml' for row in rows
          if 'repositories/'+names[str(row['repository_id'])]+'.yaml' in tree}
    tree['catalog.yaml']=contracts.encode(dict(contracts.header('catalog',inputs['schemas']),inputs=inputs,
                                               producer=dict(id=args.run_id,attempt=args.attempt),retention='32-plus-stable-exact-tag-v1'))
    tree['apps.yaml']=contracts.encode(dict(contracts.header('apps',inputs['schemas']),apps=apps))
    evaluator=Evaluator(host.ROOT,inputs,host.utc())
    reviews=json.loads(args.reviews.read_text(),object_pairs_hook=unique_object) if args.reviews else {}
    old_bindings=prior_docs.get('provenance.yaml',{}).get('apps',{})
    provenance={row['app']:{arch:evaluator.classify(row['app'],arch,row['repository_id'],
                           prior=old_bindings.get(row['app'],{}).get(arch),
                           review=reviews.get(row['app'],{}).get(arch))
                           for arch in ('x86_64','aarch64','i686','armv7l')} for row in rows if row['app'] in apps}
    tree['provenance.yaml']=contracts.encode(dict(contracts.header('provenance',inputs['schemas']),apps=provenance))
    contracts.validate_tree(tree)
    write_tree(args.output/'format-2',legacy)
    write_tree(args.output/'format-3',tree)
    evidence=dict(version=1,run=dict(id=args.run_id,attempt=args.attempt),inputs=inputs,
                  parents=dict(format_2=args.parent,format_3=args.v3_parent),
                  collection_mode='saved' if args.evidence else 'live',sources=report,
                  target_counts=dict(enrolled=len(sources),selected=metrics['selected_sources'],attempted=len(report),
                                     successful=sum(row['status']=='ok' for row in report),
                                     failed=sum(row['status']=='failed' for row in report),unknown=0,
                                     unattempted=metrics['selected_sources']-len(report)),
                  compatibility_sources=legacy_report,compatibility_metrics=metrics,
                  acquisition=dict(http_attempts=metrics['requests'],charged_response_bytes=metrics['response_bytes'],
                                   received_response_bytes_state='unknown',seconds=metrics['acquisition_seconds']),
                  hashes={channel:{name:hashlib.sha256(raw).hexdigest() for name,raw in content.items()}
                          for channel,content in (('format-2',legacy),('format-3',tree))})
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
        tree_documents(tree,LIMITS)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='operation',required=True)
    c=sub.add_parser('collect')
    c.add_argument('--repo',type=Path,required=True)
    c.add_argument('--parent',type=contracts.pin,required=True)
    c.add_argument('--v3-repo',type=Path)
    c.add_argument('--v3-parent',type=contracts.pin)
    c.add_argument('--evidence',type=Path)
    c.add_argument('--reviews',type=Path,help='Explicit exact-input custom classification reviews')
    c.add_argument('--output',type=Path,required=True)
    c.add_argument('--registry',type=Path,default=host.ROOT/'tools/catalog-collector/source-names.json')
    c.add_argument('--batch-size',type=int,default=host.REQUEST_CAP)
    c.add_argument('--run-id',type=int,required=True)
    c.add_argument('--attempt',type=int,default=1)
    for key in ('source','policy','recipes','rules','schemas'):
        c.add_argument('--'+key+'-revision',type=contracts.pin)
    v=sub.add_parser('validate')
    v.add_argument('--candidate',type=Path,required=True)
    v.add_argument('--channel',choices=('format-2','format-3','status-1'),default='format-3')
    for key in ('source','policy','recipes','rules','schemas'):
        v.add_argument('--expected-'+key,type=contracts.pin)
    sub.add_parser('publish',help='Reserved explicit publication interface (ticket 12)')
    args=parser.parse_args(argv)
    if args.operation=='publish': parser.error('publication/finalization is not implemented yet (ticket 12)')
    if args.operation=='collect': collect(args)
    else: validate(args)
