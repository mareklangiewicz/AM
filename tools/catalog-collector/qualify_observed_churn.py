"""Compare retained facts at two original public v2 pins; never freshen data."""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import statistics
import time

from publication import git
from yaml_publication import decode_document


def facts(doc):
    return {rid:{key:value for key,value in record.items() if key!='observed_at'}
            for rid,record in doc['releases'].items()}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',type=Path,required=True)
    parser.add_argument('--before',required=True)
    parser.add_argument('--after',required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();start=time.monotonic()
    apps=[decode_document(git(args.repo,'show',pin+':apps.yaml'),2097152)['apps'] for pin in (args.before,args.after)]
    common=sorted(set(apps[0].values())&set(apps[1].values()));rows=[];excluded=[];intervals=[]
    for index,rid in enumerate(common):
        path=f'repositories/{rid}.yaml';raw=[git(args.repo,'show',pin+':'+path) for pin in (args.before,args.after)]
        old,new=[decode_document(body,2097152) for body in raw]
        if 'last_success' not in old or 'last_success' not in new:
            excluded.append(dict(repository_id=rid,reason='no_successful_pair'));continue
        at=[doc['last_success']['completed_at'] for doc in (old,new)]
        hours=(datetime.fromisoformat(at[1].replace('Z','+00:00'))-datetime.fromisoformat(at[0].replace('Z','+00:00'))).total_seconds()/3600
        if hours<=0:
            excluded.append(dict(repository_id=rid,reason='no_positive_observation_interval'));continue
        before,after=facts(old),facts(new);overlap=set(before)&set(after)
        row=dict(repository_id=rid,repository=new['repository'],hours=hours,before_observation=at[0],after_observation=at[1],
            new_releases=len(set(after)-set(before)),removed_releases=len(set(before)-set(after)),
            edited_releases=sum(before[key]!=after[key] for key in overlap),facts_changed=before!=after,
            renamed_repository=old['repository']!=new['repository'],
            before_sha256=hashlib.sha256(raw[0]).hexdigest(),after_sha256=hashlib.sha256(raw[1]).hexdigest(),
            latest_scope=new['last_success'])
        rows.append(row);intervals.append(hours)
        if (index+1)%100==0:print(json.dumps(dict(stage='original_observation_pairs',sources=index+1)),flush=True)
    changed=sum(row['facts_changed'] for row in rows);exposure=sum(intervals)
    result=dict(live_acquisition=False,synthetic_observations=False,before=args.before,after=args.after,
        before_apps=len(apps[0]),after_apps=len(apps[1]),common_sources=len(common),compared_successful_sources=len(rows),
        newly_enrolled_sources_excluded=len(set(apps[1].values())-set(apps[0].values())),excluded=excluded,
        source_hours=exposure,interval_hours=dict(min=min(intervals),max=max(intervals),median=statistics.median(intervals)),
        sources_with_retained_fact_changes=changed,observed_changed_source_pairs_per_source_hour=changed/exposure,
        new_release_ids=sum(row['new_releases'] for row in rows),edited_release_records=sum(row['edited_releases'] for row in rows),
        removed_release_ids=sum(row['removed_releases'] for row in rows),seconds=time.monotonic()-start,rows=rows,
        limits='Two preserved v2 pins and their original successful observation times; retained-scope differences, not complete upstream history or a stationary release rate. New enrollment is excluded. This does not resolve tied-tag v3 evidence or qualify installed consumers.')
    args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({key:value for key,value in result.items() if key!='rows'},indent=2))


if __name__=='__main__':main()
