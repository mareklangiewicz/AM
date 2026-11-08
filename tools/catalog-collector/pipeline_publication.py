"""Explicit publication and independent best-effort status finalization.

Only this module initiates remote writes. Tests use disposable local bare remotes.
Artifacts supply inert bounded data, never code, targets, credentials or authority.
"""
import argparse
import base64
import os
from datetime import datetime,timezone
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import tempfile
import time

import contracts as c
from bounded import unique_object
from publication import git,environment,bounded,publish_tree,REF
from incremental import Snapshot,Candidate,decode as decode_fact
from yaml_publication import tree_documents

REFS={'format-2':'refs/heads/release-catalog','format-3':'refs/heads/release-catalog-v3','status-1':'refs/heads/catalog-status-v1'}


def utc(): return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
def unknown(): return dict(state='unknown')
def known(value): return dict(state='known',value=value)


class Transport:
    """Fixed trusted target and counted, bounded Git operations; never retry writes."""
    def __init__(self,url): self.url=url
    def call(self,repo,*args):
        # Remote credentials (if configured) come from the invoking trusted job,
        # never a URL/header/environment dump in the transferred artifact.
        env=environment()
        token=os.environ.get('GH_TOKEN')
        if token and self.url=='https://github.com/mareklangiewicz/AM.git':
            auth=base64.b64encode(('x-access-token:'+token).encode()).decode()
            env.update(GIT_CONFIG_COUNT='2',GIT_CONFIG_KEY_0='http.https://github.com/mareklangiewicz/AM.git.extraHeader',
                       GIT_CONFIG_VALUE_0='Authorization: Basic '+auth,GIT_CONFIG_KEY_1='http.followRedirects',GIT_CONFIG_VALUE_1='false')
        return subprocess.run(['git','-C',str(repo),'-c','core.hooksPath=/dev/null',*args],
                              env=env,capture_output=True,timeout=120)
    def head(self,repo,ref):
        result=self.call(repo,'ls-remote','--refs',self.url,ref)
        if result.returncode or len(result.stdout)>256: raise ValueError('remote head unavailable')
        rows=result.stdout.decode('ascii').splitlines()
        if not rows: return None
        if len(rows)!=1: raise ValueError('remote head ambiguous')
        commit,name=rows[0].split('\t')
        if name!=ref: raise ValueError('remote head identity')
        return c.pin(commit)
    def fetch(self,repo,ref):
        commit=self.head(repo,ref)
        if commit is not None:
            result=self.call(repo,'fetch','--no-tags',self.url,commit)
            if result.returncode: raise ValueError('remote parent unavailable')
        return commit
    def push(self,repo,ref,parent,commit):
        return self.call(repo,'push','--porcelain','--force-with-lease='+ref+':'+(parent or ''),self.url,commit+':'+ref)


def publish(repo,tree,parent,transport,ref,*,metrics=None):
    """No merge/retry. Local creation and ambiguous writes never imply success."""
    try:
        if transport.head(repo,ref)!=parent: return dict(state='conflict')
        git(repo,'update-ref',REF,parent) if parent else None
        commit=publish_tree(repo,tree,parent,metrics=metrics)
    except (ValueError,OSError,subprocess.SubprocessError): return dict(state='failed')
    try:
        result=transport.push(repo,ref,parent,commit)
    except (ValueError,OSError,subprocess.SubprocessError): return dict(state='unknown')
    try:
        if transport.head(repo,ref)==commit: return dict(state='confirmed',commit=commit)
    except (ValueError,OSError,subprocess.SubprocessError): return dict(state='unknown')
    if result.returncode and b'(stale info)' in result.stdout: return dict(state='conflict')
    return dict(state='unknown')


def artifact(directory,*,run,inputs,parents):
    """Bounded transferred tree, exact trusted run/input/parent and content bindings."""
    directory=Path(directory)
    if directory.is_symlink() or not directory.is_dir(): raise ValueError('missing candidate')
    files={};total=0
    for path in directory.rglob('*'):
        name=path.relative_to(directory).as_posix()
        if path.is_symlink() or not (path.is_file() or path.is_dir()): raise ValueError('artifact file type')
        if path.is_dir():
            if name not in ('format-2','format-3','format-2/repositories','format-3/repositories','format-3/provenance'): raise ValueError('artifact directory')
            continue
        size=path.stat().st_size;total+=size
        cap=16*1024*1024 if name=='report.json' else c.FILE_CAP
        if size>cap or total>2*c.TREE_CAP or len(files)>=40001: raise ValueError('artifact bound')
        if name!='report.json' and not re.fullmatch(r'(?:format-2/(?:apps\.yaml|repositories/[1-9][0-9]*\.yaml)|format-3/(?:catalog\.yaml|apps\.yaml|(?:repositories|provenance)/'+c.NAME+r'\.yaml))',name): raise ValueError('artifact path')
        files[name]=path.read_bytes()
    report=json.loads(files.pop('report.json'),object_pairs_hook=unique_object)
    allowed_report={'version','started_at','reported_at','run','inputs','parents','collection_mode','sources','selected_sources','target_counts','compatibility_sources','compatibility_metrics','validation','acquisition','hashes'}
    if set(report)-allowed_report: raise ValueError('unexpected report fields')
    if report['version']!=1 or report['run']!=run or report['inputs']!=inputs or report['parents']!=parents: raise ValueError('artifact binding')
    expected={'format-2':{},'format-3':{}}
    for name,raw in files.items():
        channel,path=name.split('/',1);expected[channel][path]=hashlib.sha256(raw).hexdigest()
    if report['hashes']!=expected: raise ValueError('artifact content hash')
    trees={channel:{name.split('/',1)[1]:raw for name,raw in files.items() if name.startswith(channel+'/')} for channel in expected}
    # Revalidate in the trusted publisher; the artifact's validation receipts are ignored.
    Candidate(None,trees['format-2'],'format-2')
    checked=Candidate(None,trees['format-3'])
    docs={path:(meta['root'] if 'root' in meta else dict(kind='repository',repository_id=meta['repository_id'],
              repository=meta['repository'],collected_at=meta['completed_at'])) for path,meta in checked.metadata.items()}
    if docs['catalog.yaml']['inputs']!=inputs or docs['catalog.yaml']['producer']!=run: raise ValueError('descriptor binding')
    # Do not allow public outcome evidence to smuggle arbitrary exception strings.
    allowed_reasons={'transport','authentication','quota','request_budget','byte_budget','time_budget','source_validation','document_overflow','candidate_validation','parent_conflict','publication_transport','internal','unknown'}
    seen=set()
    for source in report['sources']:
        if set(source)-{'repository_id','status','reason'} or source['status'] not in ('ok','failed') or type(source['repository_id']) is not int or source['repository_id']<=0 or source['repository_id'] in seen: raise ValueError('source evidence')
        if 'reason' in source and source['reason'] not in allowed_reasons: raise ValueError('source reason')
        seen.add(source['repository_id'])
    counts=report['target_counts']
    if set(counts)!=set(('enrolled','selected','attempted','successful','failed','unknown','unattempted')) or any(type(v) is not int or not 0<=v<=9223372036854775807 for v in counts.values()): raise ValueError('count evidence')
    if counts['attempted']!=len(report['sources']) or counts['successful']!=sum(r['status']=='ok' for r in report['sources']) or counts['failed']!=sum(r['status']=='failed' for r in report['sources']) or counts['unknown']!=0 or counts['selected']!=counts['attempted']+counts['unattempted'] or counts['selected']>counts['enrolled']: raise ValueError('count relationship')
    selected=report['selected_sources']
    if not isinstance(selected,list) or any(type(rid) is not int or rid<=0 for rid in selected) or len(set(selected))!=len(selected) or len(selected)!=counts['selected'] or not seen<=set(selected): raise ValueError('selected scope identity')
    acquisition=report['acquisition'];limits=report['compatibility_metrics']
    for value in (acquisition['http_attempts'],acquisition['charged_response_bytes'],limits['request_cap'],limits['response_byte_cap'],limits['acquisition_cap_seconds']):
        if type(value) is not int or not 0<=value<=9223372036854775807: raise ValueError('measurement evidence')
    if type(acquisition['seconds']) not in (int,float) or not math.isfinite(acquisition['seconds']) or not 0<=acquisition['seconds']<86400: raise ValueError('duration evidence')
    # Original stage times also pass the shared final-summary domain validator.
    c.decode(c.encode(summary(run,inputs,parents['format_3'],report,{key:dict(state='not_attempted') for key in REFS},started_at=report['started_at'],validation='ok',reason='complete')))
    return report,trees,docs


def summary(run,inputs,parent,report,outcomes,*,started_at,validation,reason,publication_metrics=None):
    fields=c.DEFINITIONS['metrics']['properties']
    measurements={name:unknown() for name in fields}
    counts={name:unknown() for name in c.DEFINITIONS['counts']['properties']}
    budgets=dict(requests=0,bytes=0,acquisition_milliseconds=0,document_bytes=c.FILE_CAP)
    collection='unknown'
    if report is not None:
        raw=report['target_counts']
        counts={name:known(raw[name]) for name in raw}
        counts['deferred']=known(raw['unattempted'])
        collection='ok' if raw['successful']==raw['selected'] else 'partial' if raw['successful'] else 'failed'
        acquisition=report['acquisition'];metrics=report['compatibility_metrics']
        measurements['http_attempts']=known(acquisition['http_attempts'])
        measurements['charged_bytes']=known(acquisition['charged_response_bytes'])
        measurements['acquisition_milliseconds']=known(int(acquisition['seconds']*1000))
        if 'command_seconds' in acquisition:measurements['command_milliseconds']=known(int(acquisition['command_seconds']*1000))
        budgets.update(requests=metrics['request_cap'],bytes=metrics['response_byte_cap'],acquisition_milliseconds=metrics['acquisition_cap_seconds']*1000)
    if outcomes['format-3']['state']=='confirmed' and publication_metrics:
        values=publication_metrics.get('format-3',{})
        if 'snapshot_yaml_bytes' in values:measurements['tree_bytes']=known(values['snapshot_yaml_bytes'])
        if 'history_object_bytes_after' in values:measurements['local_object_bytes']=known(values['history_object_bytes_after'])
        if 'largest_document_bytes' in values:measurements['largest_document_bytes']=known(values['largest_document_bytes'])
    result=dict(c.header('summary',inputs['schemas']),run=run,inputs=inputs,
                input_catalog_state='known' if parent else 'absent',started_at=started_at,reported_at=utc(),
                collection=collection,validation=validation,publication=outcomes['format-3'],compatibility_publication=outcomes['format-2'],
                counts=counts,stop_reason=reason,metrics=measurements,budgets=budgets,
                actions_url=f"https://github.com/mareklangiewicz/AM/actions/runs/{run['id']}",
                recent_runs_url='https://github.com/mareklangiewicz/AM/actions/workflows/catalog.yml')
    if parent: result['input_catalog']=parent
    return c.decode(c.encode(result))


def status_tree(previous,current,report,docs,identities=None):
    """64/8/90 actual reported coverage; aggregates never count absent attempts."""
    tree=dict(previous or {})
    snapshot=previous if isinstance(previous,Snapshot) else None
    old={path:meta['root'] for path,meta in snapshot.metadata.items() if 'root' in meta} if snapshot else c.validate_tree(tree,'status') if tree else {}
    run=current['run'];key=f"{run['id']}-{run['attempt']}";path=f'runs/{key}/summary.yaml'
    # A reported rerun attempt is immutable; rerun attempts have distinct keys.
    if path in tree: raise ValueError('attempt already reported')
    tree[path]=c.encode(current)
    sources_by_id={obj['repository_id']:(name,obj) for name,obj in docs.items() if obj['kind']=='repository'} if docs else {}
    if report is not None:
        attempted={row['repository_id'] for row in report['sources']}
        source_rows=[*report['sources'],*[dict(repository_id=rid,status='unattempted') for rid in report['selected_sources'] if rid not in attempted]]
        for row in source_rows:
            rid=row['repository_id']
            if rid in sources_by_id:
                name,obj=sources_by_id[rid];label=Path(name).stem
            elif identities and rid in identities:
                label,repository=identities[rid];obj=dict(repository=repository)
            else: raise ValueError('missing attempted source identity')
            source=dict(c.header('source',current['inputs']['schemas']),run=run,
                        input_catalog_state=current['input_catalog_state'],repository_id=rid,repository=obj['repository'],
                        outcome=row['status'])
            if 'input_catalog' in current:source['input_catalog']=current['input_catalog']
            if 'reason' in row:source['reason']=row['reason']
            if row['status']=='ok':source['completed_at']=obj['collected_at']
            if current['publication']['state']=='confirmed':source['output_catalog']=current['publication']['commit']
            tree[f'runs/{key}/sources/{label}.yaml']=c.encode(source)
    summaries={name:c.decode(raw) for name,raw in tree.items() if name.endswith('/summary.yaml')}
    ordered=sorted(summaries,key=lambda name:(summaries[name]['reported_at'],summaries[name]['run']['id'],summaries[name]['run']['attempt']),reverse=True)
    keep=set(ordered[:64]);detail_keys={name.split('/')[1] for name in ordered[:8]}
    for name in list(tree):
        if name.endswith('/summary.yaml') and name not in keep:del tree[name]
        elif '/sources/' in name and name.split('/')[1] not in detail_keys:del tree[name]
    # Accumulate one exact reported attempt into its UTC day. Keep older aggregate
    # coverage even when its detail/summary has aged out of the current tree.
    days=dict(old.get('statistics.yaml',{}).get('days',{}))
    def accumulate(record):
        date=record['reported_at'][:10];count=record['counts']
        all_known=all(count[k]['state']=='known' for k in ('successful','failed'))
        daily=days.setdefault(date,dict(reported_attempts=0,unknown_source_count_attempts=0,successful_sources=0,failed_sources=0,first_report=record['reported_at'],last_report=record['reported_at']))
        daily['reported_attempts']+=1
        daily['first_report']=min(daily['first_report'],record['reported_at']);daily['last_report']=max(daily['last_report'],record['reported_at'])
        if all_known:
            daily['successful_sources']+=count['successful']['value'];daily['failed_sources']+=count['failed']['value']
        else:daily['unknown_source_count_attempts']+=1
    if 'statistics.yaml' not in old:
        for record in old.values():
            if record['kind']=='summary':accumulate(record)
    accumulate(current)
    # Unknown source-count attempts are explicitly counted separately by daily
    # schema fields, rather than silently omitted or forced to zero.
    retained_days={day:days[day] for day in sorted(days)[-90:]}
    confirmed=current['publication'] if current['publication']['state']=='confirmed' else old.get('status.yaml',{}).get('last_confirmed_publication',dict(state='unknown'))
    root=dict(c.header('status',current['inputs']['schemas']),schemas=current['inputs']['schemas'],last_report=path,reported_at=current['reported_at'],
              last_confirmed_publication=confirmed,summaries={name.split('/')[1]:name for name in ordered[:64]},
              details={name.split('/')[1]:summaries[name]['reported_at'] for name in ordered[:8] if any(k.startswith('runs/'+name.split('/')[1]+'/sources/') for k in tree)})
    tree['status.yaml']=c.encode(root)
    # Freshness is attached only to the exact confirmed candidate publication.
    catalog=confirmed.get('commit') or current.get('input_catalog')
    if catalog:
        freshness=dict(catalog=catalog,evaluated_at=current['reported_at'],**{name:unknown() for name in ('under_24h','from_24_to_48h','at_least_48h','no_success','unknown')})
        if docs and current['publication']['state']=='confirmed':
            buckets=dict(under_24h=0,from_24_to_48h=0,at_least_48h=0,no_success=0,unknown=0)
            now=datetime.fromisoformat(current['reported_at'].replace('Z','+00:00'))
            for obj in docs.values():
                if obj['kind']!='repository':continue
                age=(now-datetime.fromisoformat(obj['collected_at'].replace('Z','+00:00'))).total_seconds()
                bucket='unknown' if age<0 else 'under_24h' if age<86400 else 'from_24_to_48h' if age<172800 else 'at_least_48h'
                buckets[bucket]+=1
            enrolled=current['counts']['enrolled']
            if enrolled['state']=='known':buckets['no_success']=max(0,enrolled['value']-sum(buckets.values()))
            freshness.update({name:known(value) for name,value in buckets.items()})
            if enrolled['state']!='known':freshness['no_success']=unknown()
        tree['statistics.yaml']=c.encode(dict(c.header('statistics',current['inputs']['schemas']),measured_at=current['reported_at'],freshness=freshness,days=retained_days))
    if snapshot:
        return Candidate(snapshot,tree,'status-1',removed=set(snapshot)-set(tree))
    c.validate_tree(tree,'status')
    return tree


def add_arguments(sub):
    parser=sub.add_parser('publish',help='Validate transferred candidates, explicitly publish and finalize')
    parser.add_argument('--candidate',type=Path,required=True)
    parser.add_argument('--remote-url',required=True)
    parser.add_argument('--run-id',type=int,required=True)
    parser.add_argument('--attempt',type=int,default=1)
    parser.add_argument('--expected-v2-parent',type=c.pin)
    parser.add_argument('--input-catalog-state',choices=('known','absent','unknown'))
    parser.add_argument('--expected-v3-parent',type=c.pin)
    parser.add_argument('--source-revision',type=c.pin,required=True)
    parser.add_argument('--schemas-revision',type=c.pin,help='Explicit trusted schema transition; otherwise retain the exact expected v3 parent binding')
    parser.add_argument('--enable-targets',action='store_true',help='Explicitly publish v3/status channels; activation needs separate authorization')
    parser.add_argument('--result',type=Path,required=True)


def enrollment():
    import host_catalog as host
    from collection_interface import registry_names
    rows,_=host.configuration(source_cap=10000)
    names=registry_names(rows,host.ROOT/'tools/catalog-collector/source-names.json')
    return rows,names


def check_enrollment(trees,docs,rows,names):
    apps={row['app']:row['repository_id'] for row in rows}
    legacy=decode_fact('apps.yaml',trees['format-2']['apps.yaml'],'format-2')[0]['apps']
    for app,rid in legacy.items():
        if apps.get(app)!=rid: raise ValueError('compatibility enrollment identity')
    for app,path in docs['apps.yaml']['apps'].items():
        if apps.get(app)!=docs[path]['repository_id'] or path!='repositories/'+names[str(apps[app])]+'.yaml': raise ValueError('target enrollment identity')
    for path,obj in docs.items():
        if obj['kind']=='repository' and path!='repositories/'+names[str(obj['repository_id'])]+'.yaml': raise ValueError('registry source identity')


def run(args,*,transport=None):
    transport=transport or Transport(args.remote_url)
    inputs={name:args.source_revision for name in ('source','policy','recipes','rules','schemas')}
    run_id=dict(id=args.run_id,attempt=args.attempt)
    parents=dict(format_2=args.expected_v2_parent,format_3=args.expected_v3_parent)
    outcomes={key:dict(state='not_attempted') for key in REFS}
    publication_metrics={}
    report=None;trees=None;docs={};identities={};validation='failed';reason='candidate_validation';started=utc()
    try:
        from collection_interface import verify_checkout_inputs
        import host_catalog as host
        schema_revision=getattr(args,'schemas_revision',None)
        if schema_revision is None and args.expected_v3_parent:
            # Derive authority from the caller's exact expected parent, never
            # from an untrusted artifact's requested schema revision.
            with tempfile.TemporaryDirectory(prefix='am-schema-parent-') as scratch:
                repo=Path(scratch);git(repo,'init','--bare','--quiet','--template=')
                fetched=transport.call(repo,'fetch','--no-tags',transport.url,args.expected_v3_parent)
                if fetched.returncode: raise ValueError('schema parent unavailable')
                # Only this exact root supplies the schema authority. Candidate
                # data is fully revalidated below; no parent blob trust is imported.
                descriptor=c.decode(bounded(['git','-C',str(repo),'-c','core.hooksPath=/dev/null',
                    'show',args.expected_v3_parent+':catalog.yaml'],env=environment(),cap=c.FILE_CAP))
                if descriptor['kind']!='catalog':raise ValueError('schema parent descriptor kind')
                schema_revision=descriptor['inputs']['schemas']
        if schema_revision is not None: inputs['schemas']=schema_revision
        verify_checkout_inputs(inputs,host.ROOT/'tools/catalog-collector/source-names.json')
        report,trees,docs=artifact(args.candidate,run=run_id,inputs=inputs,parents=parents)
        rows,names=enrollment()
        check_enrollment(trees,docs,rows,names)
        enrolled={row['repository_id'] for row in rows}
        if report['target_counts']['enrolled']!=len(enrolled) or not set(report['selected_sources'])<=enrolled: raise ValueError('enrollment denominator')
        identities={row['repository_id']:(names[str(row['repository_id'])],row['repository']) for row in rows}
        validation='ok';started=report['started_at']
        stop=report['compatibility_metrics']['stop_reason']
        reason={'byte_limit':'byte_budget','time_limit':'time_budget','primary_rate_reserve':'quota','http_401':'authentication','http_403':'quota','http_429':'quota'}.get(stop,'complete')
        if reason=='complete' and report['target_counts']['failed']:reason='source_validation'
    except (ValueError,KeyError,TypeError,OSError,RecursionError,subprocess.SubprocessError):
        report=None;trees=None;docs={}
    with tempfile.TemporaryDirectory(prefix='am-publisher-') as scratch:
        root=Path(scratch)
        for channel in ('format-2','format-3'):
            if trees is None or (channel=='format-3' and not args.enable_targets):break
            repo=root/channel;git(root,'init','--bare','--quiet','--template=',str(repo))
            parent=parents[channel.replace('-','_')]
            try:
                current=transport.fetch(repo,REFS[channel])
                if current!=parent:outcomes[channel]=dict(state='conflict')
                else:
                    metrics={};publication_metrics[channel]=metrics
                    metrics['largest_document_bytes']=max(map(len,trees[channel].values()))
                    outcomes[channel]=publish(repo,trees[channel],parent,transport,REFS[channel],metrics=metrics)
            except (ValueError,OSError,subprocess.SubprocessError):outcomes[channel]=dict(state='failed')
            if outcomes[channel]['state']!='confirmed':
                reason='parent_conflict' if outcomes[channel]['state']=='conflict' else 'publication_transport';break
        final=summary(run_id,inputs,args.expected_v3_parent,report,outcomes,started_at=started,validation=validation,reason=reason,publication_metrics=publication_metrics)
        state=getattr(args,'input_catalog_state',None)
        if state is not None:
            final['input_catalog_state']=state
            c.decode(c.encode(final))
        if args.enable_targets:
            repo=root/'status-1';git(root,'init','--bare','--quiet','--template=',str(repo))
            try:
                parent=transport.fetch(repo,REFS['status-1'])
                previous=Snapshot(repo,parent,'status-1') if parent else {}
                tree=status_tree(previous,final,report,docs,identities)
                outcomes['status-1']=publish(repo,tree,parent,transport,REFS['status-1'])
            except (ValueError,KeyError,TypeError,OSError,subprocess.SubprocessError):outcomes['status-1']=dict(state='failed')
    result=dict(run=run_id,outcomes=outcomes,validation=validation,publication_metrics=publication_metrics)
    args.result.write_text(json.dumps(result,indent=2)+'\n')
    return result
