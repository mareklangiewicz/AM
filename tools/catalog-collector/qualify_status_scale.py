"""Synthetic 5,000-source health population with real 64/8/90 retention.

Normal hourly scope defaults to 500 sources, independently of population. Uses
the maintained writer/validators/publisher and a disposable local Git repository.
"""
import argparse
from datetime import datetime,timedelta,timezone
import json
from pathlib import Path
import resource
import time

import contracts as c
from incremental import Candidate,Snapshot
import pipeline_publication as p
from publication import git,publish_tree


def stamp(value):return value.strftime('%Y-%m-%dT%H:%M:%SZ')


def packed(repo):
    git(repo,'-c','pack.threads=1','-c','pack.compression=6','repack','-ad','--window=10','--depth=50')
    return sum(path.stat().st_size for path in (repo/'objects/pack').glob('*.pack'))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--scope',type=int,default=500)
    args=parser.parse_args()
    if not 1<=args.scope<=5000:raise ValueError('scope')
    args.work.mkdir(parents=True,exist_ok=False)
    resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
    started=time.monotonic();revision=git(c.ROOT,'rev-parse','HEAD').decode().strip()
    inputs={key:revision for key in ('source','policy','recipes','rules','schemas')}
    pin='a'*40;base=datetime(2026,11,1,tzinfo=timezone.utc)
    identities={1000000000000+i:(f'scale-{i:05d}',f'synthetic/scale-{i:05d}') for i in range(5000)}
    docs={'repositories/'+label+'.yaml':dict(kind='repository',repository_id=rid,repository=repository,collected_at=stamp(base))
          for rid,(label,repository) in identities.items()}
    def selected(run):
        return [1000000000000+((run-1)*args.scope+index)%5000 for index in range(args.scope)]
    def evidence(run):
        ids=selected(run)
        return dict(selected_sources=ids,sources=[dict(repository_id=rid,status='ok') for rid in ids],
            target_counts=dict(enrolled=5000,selected=args.scope,attempted=args.scope,successful=args.scope,failed=0,unknown=0,unattempted=0),
            acquisition=dict(http_attempts=0,charged_response_bytes=0,seconds=0),
            compatibility_metrics=dict(request_cap=750,response_byte_cap=536870912,acquisition_cap_seconds=900))
    def summary(run,at):
        value=p.summary(dict(id=run,attempt=1),inputs,pin,evidence(run),
            {'format-2':dict(state='not_attempted'),'format-3':dict(state='confirmed',commit=pin)},
            started_at=stamp(at-timedelta(minutes=1)),validation='ok',reason='complete')
        value['reported_at']=stamp(at)
        return value
    tree={};summaries={};details={};last=base+timedelta(hours=64)
    for run in range(1,65):
        at=base+timedelta(hours=run);key=f'{run}-1';path=f'runs/{key}/summary.yaml'
        record=summary(run,at);tree[path]=c.encode(record);summaries[key]=path
        for rid in selected(run):
            label,repository=identities[rid]
            docs['repositories/'+label+'.yaml']['collected_at']=stamp(at-timedelta(seconds=30))
            if run>=57:
                tree[f'runs/{key}/sources/{label}.yaml']=c.encode(dict(c.header('source',revision),run=record['run'],
                    input_catalog_state='known',input_catalog=pin,repository_id=rid,repository=repository,
                    outcome='ok',completed_at=stamp(at-timedelta(seconds=30)),output_catalog=pin))
        if run>=57:details[key]=stamp(at)
    tree['status.yaml']=c.encode(dict(c.header('status',revision),schemas=revision,last_report='runs/64-1/summary.yaml',
        reported_at=stamp(last),last_confirmed_publication=dict(state='confirmed',commit=pin),summaries=summaries,details=details))
    days={}
    for age in range(89,-1,-1):
        at=(last-timedelta(days=age)).replace(hour=0,minute=0,second=0)
        days[stamp(at)[:10]]=dict(reported_attempts=1,unknown_source_count_attempts=0,successful_sources=args.scope,
            failed_sources=0,first_report=stamp(at),last_report=stamp(at))
    # Older fixture aggregates represent earlier reports outside the retained 64.
    # For retained-summary dates, derive the counters from those actual fixtures.
    for date in [day for day in days if day>=stamp(base)[:10]]:
        reports=[base+timedelta(hours=run) for run in range(1,65) if stamp(base+timedelta(hours=run))[:10]==date]
        days[date]=dict(reported_attempts=len(reports),unknown_source_count_attempts=0,
            successful_sources=len(reports)*args.scope,failed_sources=0,
            first_report=stamp(min(reports)),last_report=stamp(max(reports)))
    unknown={name:dict(state='unknown') for name in ('under_24h','from_24_to_48h','at_least_48h','no_success','unknown')}
    tree['statistics.yaml']=c.encode(dict(c.header('statistics',revision),measured_at=stamp(last),
        freshness=dict(catalog=pin,evaluated_at=stamp(last),**unknown),days=days))
    candidate=Candidate(None,tree,'status-1')
    repo=args.work/'status.git';git(args.work,'init','--bare','--quiet','--template=',str(repo))
    parent=publish_tree(repo,candidate,None);before=packed(repo)
    snapshot=Snapshot(repo,parent,'status-1')
    at=last+timedelta(days=1);current=summary(65,at)
    for rid in selected(65):
        label,_=identities[rid];docs['repositories/'+label+'.yaml']['collected_at']=stamp(at-timedelta(seconds=30))
    begin=time.monotonic();updated=p.status_tree(snapshot,current,evidence(65),docs,identities)
    retention_seconds=time.monotonic()-begin
    root=updated.metadata['status.yaml']['root'];statistics=updated.metadata['statistics.yaml']['root']
    per_report={key:sum(path.startswith('runs/'+key+'/sources/') for path in updated) for key in root['details']}
    if (len(root['summaries']),len(root['details']),len(statistics['days']))!=(64,8,90):raise AssertionError('64/8/90 retention')
    if set(per_report.values())!={args.scope}:raise AssertionError('source scope truncation')
    if '1-1' in root['summaries'] or '57-1' in root['details'] or min(days) in statistics['days']:raise AssertionError('old record retention')
    if sum(day['reported_attempts'] for date,day in statistics['days'].items() if date>=stamp(base)[:10])!=65:
        raise AssertionError('daily counters lost an evicted summary or invented a report')
    metrics={};commit=publish_tree(repo,updated,parent,metrics=metrics);after=packed(repo)
    result=dict(synthetic=True,live_acquisition=False,population=5000,selected_per_report=args.scope,
        source_revision=revision,parent=parent,commit=commit,old_pin_preserved=git(repo,'rev-parse',commit+'^').decode().strip()==parent,
        before_validation=candidate.validation,parent_validation=snapshot.validation,after_validation=updated.validation,
        summaries=len(root['summaries']),detail_reports=len(root['details']),daily_records=len(statistics['days']),
        source_rows_per_detail=per_report,retention_seconds=retention_seconds,publication_metrics=metrics,
        packed_before_bytes=before,packed_after_bytes=after,packed_added_bytes=after-before,
        seconds=time.monotonic()-started,peak_self_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        peak_largest_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
        limits='Synthetic summaries/details/daily fixture, one retained-tree update with a day gap. Dummy confirmed catalog pin; not real health, missing-run interpolation, live quota or a year of Git history.')
    (args.work/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
