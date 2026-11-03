#!/usr/bin/env python3
"""THROWAWAY offline transition model. Responses are fixtures, never network I/O."""
import copy
import datetime
from experiment import document


class CollectionFailure(Exception):
    pass


class RunBudget:
    """Shared fixture accounting, not an OS deadline or transport byte limiter."""
    def __init__(self,requests=900,bytes=1024*1024*1024,seconds=1200):
        self.limits=(requests,bytes,seconds)
        self.used=[0,0,0]

    def exhausted(self):
        return any(used>=limit for used,limit in zip(self.used,self.limits))

    def account(self,response):
        if self.exhausted():
            raise CollectionFailure('collection_limit')
        self.used=[self.used[0]+1,self.used[1]+response.get('bytes',0),self.used[2]+response.get('seconds',0)]
        if any(used>limit for used,limit in zip(self.used,self.limits)):
            raise CollectionFailure('collection_limit')


def parameters(page_size=100, page_limit=1):
    if type(page_size) is not int or not 1 <= page_size <= 100:
        raise ValueError('page size')
    if page_limit != 'all' and (type(page_limit) is not int or page_limit < 1 or page_limit > 9223372036854775807):
        raise ValueError('page limit')
    return page_size, page_limit


def fresh(release, now, hours=48):
    parse=lambda s: datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ')
    age=(parse(now)-parse(release['observed_at'])).total_seconds()
    return 0 <= age <= hours*3600


def refresh(previous, responses, *, attempted_at, page_size=100, page_limit=1,
            max_requests=64, max_response_bytes=16*1024*1024,
            max_bytes=96*1024*1024, max_seconds=120,
            max_catalog_bytes=16*1024*1024, max_line_bytes=65536,
            reconcile=False, run_budget=None):
    """Atomic per-source fixture transition; all bounds are trial inputs.

    Each response has received_at, releases (normalized facts keyed by ID),
    has_next, bytes, seconds and optional error. Reconciliation is a candidate
    explicit policy, allowed only with page_limit=all and successful EOF.
    """
    parameters(page_size,page_limit)
    if reconcile and page_limit != 'all':
        raise ValueError('reconciliation requires explicit all scope')
    run_budget=run_budget or RunBudget()
    result=copy.deepcopy(previous)
    attempt=dict(attempted_at=attempted_at,page_size=page_size,page_limit=page_limit,reconcile=reconcile,status='ok')
    result['collection']=attempt
    fetched={}; total_bytes=0; seconds=0; pages=0; complete=False
    try:
        for response in responses:
            if pages >= max_requests:
                raise CollectionFailure('collection_limit')
            run_budget.account(response)
            pages+=1
            if response.get('error'):
                raise CollectionFailure(response['error'])
            total_bytes+=response['bytes']; seconds+=response['seconds']
            if response['bytes']>max_response_bytes or total_bytes>max_bytes or seconds>max_seconds:
                raise CollectionFailure('collection_limit')
            if len(response['releases'])>page_size:
                raise CollectionFailure('invalid_response')
            if response['received_at']<attempted_at or (pages>1 and response['received_at']<completed):
                raise CollectionFailure('invalid_response')
            completed=response['received_at']
            for rid, facts in response['releases'].items():
                if rid in fetched:
                    raise CollectionFailure('invalid_response')
                fetched[rid]=dict(observed_at=completed,**{k:v for k,v in copy.deepcopy(facts).items() if k!='observed_at'})
            complete=not response['has_next']
            if complete or (page_limit!='all' and pages==page_limit):
                break
        else:
            raise CollectionFailure('transport')
        retained={} if reconcile else copy.deepcopy(previous.get('releases',{}))
        retained.update(fetched)
        result['last_success']=dict(completed_at=completed,page_size=page_size,
                                    page_limit=page_limit,reconcile=reconcile,pages_fetched=pages,history_complete=complete)
        result['releases']={rid:retained[rid] for rid in sorted(retained,key=int)}
        if any(r['observed_at']>completed for r in retained.values()):
            raise CollectionFailure('invalid_response')
        # Canonical root order; preserve the identity, not former attempt metadata.
        result={k:result[k] for k in ('format','schema','repository_id','repository','collection','last_success','releases')}
        encoded=document(result).encode()
        if len(encoded)>max_catalog_bytes or any(len(line)>max_line_bytes for line in encoded.splitlines()):
            raise CollectionFailure('collection_limit')
        return result
    except CollectionFailure as exc:
        result=copy.deepcopy(previous)
        attempt.update(status='failed',reason=str(exc))
        result['collection']=attempt
        return {k:result[k] for k in ('format','schema','repository_id','repository','collection','last_success','releases') if k in result}


def collect(configured, fixtures, *, sources=None, run_budget=None, report=None, **options):
    """Source subset selection; unselected repositories remain byte-for-byte facts.

    Shared fixture request/byte/time budgets apply across selected sources;
    actual transport limits, deadlines and runner scheduling are not implemented.
    """
    selected=list(configured) if sources is None else list(sources)
    if len(set(selected))!=len(selected) or any(rid not in configured for rid in selected):
        raise ValueError('source subset')
    parameters(options.get('page_size',100),options.get('page_limit',1))
    result=copy.deepcopy(configured)
    run_budget=run_budget or RunBudget()
    report=report if report is not None else {}
    for rid in selected:
        if run_budget.exhausted():
            report[rid]='unattempted_collection_limit'
            continue
        result[rid]=refresh(configured[rid],fixtures[rid],run_budget=run_budget,**options)
        report[rid]=result[rid]['collection']['status']
    return result
