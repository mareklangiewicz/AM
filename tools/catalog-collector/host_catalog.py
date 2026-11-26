"""Single-user YAML catalog: enrollment and bounded release-list collection (a library; catalog_run.py runs it).

Enrollment is catalog/apps.yaml: each app's identity is in the repository file it points to.
One page of 100 releases (fewer for PAGE_SIZES) per attempted source; clients enforce seven-day selected
record freshness. Batches preserve untouched facts and isolate source failures.
No latest endpoint, consumer version choice or pruning.
"""
from datetime import datetime, timezone
import http.client
import json
import os
import re
from pathlib import Path
import time
import urllib.error
import urllib.request

import yaml

from bounded import normalize, unique_object
import documents

from recipe_declarations import recipe_rows

ROOT = Path(__file__).resolve().parents[2]
FILE_CAP = 2097152
RESPONSE_CAP = 16 * 1024 * 1024
TOTAL_CAP = 512 * 1024 * 1024
SOURCE_CAP = 9000
REQUEST_CAP = 750  # a 500-repository batch plus its Git reads, with room (the v3 workflow's allowance)
ACQUISITION_SECONDS = 900
RATE_RESERVE = 100

# Reviewed against GitHub's numeric repository endpoint on 2026-11-09.
# This permits retaining the old name until a successful new observation;
# it does not authorize arbitrary name drift or alter retained facts/times.
REVIEWED_REPOSITORY_TRANSFERS = {
    '1369127769': ('alex-pokydin/arduloops', 'arduloops/arduloops'),
}

# Releases per page for sources whose 100-release page exceeds RESPONSE_CAP
# (about 300 KB per release, measured 2026-11-23); every other source gets 100.
PAGE_SIZES = {
    '144590939': 30,  # VSCodium/vscodium
    '16089035': 30,   # wekan/wekan
}


def page_size(rid):
    return PAGE_SIZES.get(str(rid), 100)


def failure_cause(error):
    """The source's own failure, or None for a run-wide stop that visits nothing."""
    if isinstance(error, CollectionStop):
        return None
    if isinstance(error, urllib.error.HTTPError):
        return None if error.code in (401, 403, 429) else 'not_found' if error.code == 404 else 'transport'
    if isinstance(error, ResponseLimit):
        return 'too_large'
    if isinstance(error, (OSError, http.client.HTTPException)):
        return 'transport'
    return 'invalid_response'


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """One counted request must not silently forward credentials or add calls."""
    def redirect_request(self, request, response, code, message, headers, url):
        return None


def _open(request):
    return urllib.request.build_opener(NoRedirect()).open(request, timeout=30)


class TransferFailure(OSError):
    """Reserve the complete read allowance when a transfer ends mid-response."""
    def __init__(self, budget_bytes):
        super().__init__('release transfer failed')
        self.budget_bytes = budget_bytes


class ResponseLimit(ValueError):
    """A source response exceeded its own bound while shared bytes remain."""


class CollectionStop(ValueError):
    def __init__(self,reason):
        super().__init__('collection allowance');self.reason=reason


def utc():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


NAME = r'[a-z0-9][a-z0-9_.+-]{0,63}'
RETIRED = 'tools/catalog-collector/retired-names.yaml'
LOADER = getattr(yaml, 'CSafeLoader', yaml.SafeLoader)


def retired_names(root):
    """retired-names.yaml: repository file names never given out again."""
    document = yaml.load((Path(root)/RETIRED).read_text(encoding='utf-8'), Loader=LOADER)
    if (not isinstance(document, dict) or set(document) != {'$schema', 'retired'}
            or document['$schema'] != documents.DEFS['retired_names']['properties']['$schema']['const']
            or not isinstance(document['retired'], dict)
            or any(value is not True or not re.fullmatch(NAME, name) for name, value in document['retired'].items())):
        raise ValueError('retired names')
    return set(document['retired'])


def enrollment(*, root=None, source_cap=None):
    """Every app in catalog/apps.yaml: (rows, sources, names).

    An app's identity is repository_id and repository in the repository file
    its entry points to; that file's name is its source's name. A recipe in
    collection-recipes.txt is ready to install: its row carries its
    declaration, and its app's entry and file must agree with it. Enrolling an
    app is an apps.yaml entry and a never-read repository file.
    """
    root=ROOT if root is None else Path(root)
    source_cap=SOURCE_CAP if source_cap is None else source_cap
    catalog = root/'catalog'
    entries = yaml.load((catalog/'apps.yaml').read_text(encoding='utf-8'), Loader=LOADER)['apps']
    if not entries:
        raise ValueError('empty enrollment')
    retired = retired_names(root)
    declarations = {row['recipe']: row for row in recipe_rows(root)}
    enrolled = [line for line in (root/'tools/catalog-collector/collection-recipes.txt').read_text().splitlines()
                if line and not line.startswith('#')]
    if len(set(enrolled)) != len(enrolled):
        raise ValueError('duplicate collection recipe')
    if any(recipe not in declarations for recipe in enrolled):
        raise ValueError('unknown collection recipe')
    recipes = {}
    for recipe in enrolled:
        row = declarations[recipe]
        if row['app'] in recipes:
            raise ValueError('manifest scope')
        if row['app'] not in entries:
            raise ValueError('unknown collection app: '+row['app'])
        recipes[row['app']] = row
    rows, sources, names, files = [], {}, {}, {}
    for app, entry in entries.items():
        pointer = re.fullmatch('repositories/('+NAME+r')\.yaml', entry.get('repository', ''))
        if not pointer:
            raise ValueError('repository pointer: '+app)
        name = pointer.group(1)
        if name in retired:
            raise ValueError('retired source name: '+name)
        if name not in files:
            path = catalog/'repositories'/f'{name}.yaml'
            if not path.is_file():
                raise ValueError('missing repository file: '+name)
            files[name] = documents.read_top(path)
        top = files[name]
        rid = str(top.get('repository_id', ''))
        if (not re.fullmatch('[1-9][0-9]*', rid) or not isinstance(top.get('repository'), str)
                or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', top['repository'])):
            raise ValueError('repository identity: '+name)
        if names.setdefault(rid, name) != name:
            raise ValueError('conflicting repository identity: '+names[rid]+', '+name)
        sources[rid] = top['repository']
        row = dict(app=app, repository_id=int(rid), repository=top['repository'])
        if app in recipes:
            if (recipes[app]['repository_id'], recipes[app]['repository']) != (row['repository_id'], row['repository']):
                raise ValueError('recipe identity: '+recipes[app]['recipe'])
            row = recipes[app]
        rows.append(row)
    if len(sources) > source_cap:
        raise ValueError('manifest scope')
    return rows, sources, names


def configuration(*, root=None, source_cap=None):
    """enrollment()'s rows and sources."""
    rows, sources, _ = enrollment(root=root, source_cap=source_cap)
    return rows, sources


def installation_configuration(*, root=None):
    """Only enrolled recipes with reviewed installation/selection declarations."""
    rows, _ = configuration(root=root)
    rows = [row for row in rows if 'recipe' in row]
    return rows, {str(row['repository_id']): row['repository'] for row in rows}


def rate_headers(headers):
    """Keep only bounded numeric quota data, never arbitrary upstream headers."""
    headers = headers or {}
    result = {}
    for name in ('limit', 'remaining', 'used', 'reset'):
        value = headers.get('X-RateLimit-'+name.title(), '')
        if isinstance(value, str) and re.fullmatch(r'[0-9]{1,20}', value):
            result[name] = int(value)
    if headers.get('X-RateLimit-Resource') == 'core':
        result['resource'] = 'core'
    value = headers.get('Retry-After', '')
    if isinstance(value, str) and re.fullmatch(r'[0-9]{1,10}', value):
        result['retry_after_seconds'] = int(value)
    return result


def _response(rid, evidence, allowance, *, rate=None, endpoint=None, kind='releases'):
    """Bound response bytes at the transport seam; return inert text and receipt."""
    if evidence:
        path = Path(evidence)/(rid+'-'+kind+'.json')
        with path.open('rb') as stream:
            body = stream.read(allowance+1)
        receipt=rid+('-receipt.txt' if kind=='releases' else '-'+kind+'-receipt.txt')
        received = (Path(evidence)/receipt).read_text().strip()
        return body, received
    url = f'https://api.github.com/repositories/{rid}/'+(endpoint or f'releases?per_page={page_size(rid)}&page=1')
    headers = {'Accept':'application/vnd.github+json', 'User-Agent':'AM-YAML-catalog',
               'X-GitHub-Api-Version':'2022-11-28'}
    token = os.environ.get('GH_TOKEN')
    if token:
        headers['Authorization'] = 'Bearer '+token
    request = urllib.request.Request(url, headers=headers)
    with _open(request) as response:
        if rate is not None:
            rate.update(rate_headers(response.headers))
        if response.status != 200 or response.url != url:
            raise ValueError('release response identity')
        try:
            body = response.read(allowance+1)
        except (OSError, http.client.HTTPException):
            # Partial bytes may be hidden inside a failed HTTP read. Charging
            # its full allowance prevents isolated failures bypassing the run
            # budget. No upstream diagnostic/header is retained in this error.
            raise TransferFailure(allowance+1) from None
    return body, utc()


def collect(retained, evidence=None, *, batch_size=None, metrics=None, acquisitions, profile=None, root=None):
    """Acquire release facts for all (strict) or a bounded oldest-attempt-first batch.

    An attempt is a success or a source's own failure (`failure_cause`), so a
    failing source rotates with the rest instead of sorting first forever.

    `retained` maps each repository id of the parent snapshot to its metadata
    (repository_id, repository, attempted_at). Successful acquisitions go into
    `acquisitions`; documents are built by the caller. Strict mode raises on the
    first failure; batch mode reports failures and stops at a budget.
    """
    rows,sources=configuration(root=root,source_cap=profile['source_cap']) if profile else configuration(root=root)
    request_cap=profile['request_cap'] if profile else REQUEST_CAP
    total_cap=profile['total_cap'] if profile else TOTAL_CAP
    seconds_cap=profile['seconds_cap'] if profile else ACQUISITION_SECONDS
    reserve=profile['reserve'] if profile else RATE_RESERVE
    response_cap=profile['response_cap'] if profile else RESPONSE_CAP
    if batch_size is not None and (type(batch_size) is not int or not 1 <= batch_size <= request_cap):
        raise ValueError('batch size')
    if batch_size is None and len(sources) > request_cap:
        raise ValueError('use bounded batch collection')
    if batch_size is not None and not set(retained) <= set(sources):
        raise ValueError('batch would discard retained sources')
    for rid, before in retained.items():
        names=(before['repository'].lower(), sources[rid].lower()) if rid in sources else None
        if rid in sources and (before['repository_id'] != int(rid) or
                               (names[0] != names[1] and names != REVIEWED_REPOSITORY_TRANSFERS.get(rid))):
            raise ValueError('retained repository identity mismatch')
    selected = list(sources)
    if batch_size is not None:
        selected.sort(key=lambda rid: (retained.get(rid,{}).get('attempted_at',''), int(rid)))
        selected = selected[:batch_size]
    metrics = metrics if metrics is not None else {}
    metrics.clear()
    metrics.update(requests=0, response_bytes=0, selected_sources=len(selected),
                   selected_repository_ids=[int(rid) for rid in selected],
                   stop_reason='request_limit' if len(selected)<len(sources) else 'complete',
                   request_cap=request_cap, response_byte_cap=total_cap,
                   acquisition_cap_seconds=seconds_cap, primary_reserve=reserve)
    latest_rate = {}
    used = 0;logical_requests=0
    from git_observations import configuration as git_configuration,collect as collect_git
    git_scopes=git_configuration(ROOT if root is None else Path(root))
    report = []
    started = time.monotonic()
    for rid in selected:
        name = sources[rid]
        if logical_requests>=request_cap:
            metrics['stop_reason']='request_limit';break
        if (not evidence and latest_rate.get('remaining', reserve+1) <= reserve
                and latest_rate.get('reset', float('inf')) > time.time()):
            metrics['stop_reason'] = 'primary_rate_reserve'
            if batch_size is None:
                raise ValueError('primary rate reserve')
            break
        if time.monotonic()-started > seconds_cap or used >= total_cap:
            metrics['stop_reason'] = 'byte_limit' if used >= total_cap else 'time_limit'
            if batch_size is not None:
                break
            raise ValueError('collection elapsed budget')
        stop = False
        reason = 'transport'
        rate = {}
        def fetch(kind='releases',endpoint=None):
            nonlocal used,logical_requests,latest_rate
            if logical_requests>=request_cap:raise CollectionStop('request_limit')
            if used>=total_cap:raise CollectionStop('byte_limit')
            if kind!='releases' and time.monotonic()-started>seconds_cap:raise CollectionStop('time_limit')
            if (not evidence and latest_rate.get('remaining',reserve+1)<=reserve and
                    latest_rate.get('reset',float('inf'))>time.time()):raise CollectionStop('primary_rate_reserve')
            allowance=min(response_cap,total_cap-used);logical_requests+=1
            if not evidence:metrics['requests']+=1
            if kind=='releases':body,at=_response(rid,evidence,allowance,rate=rate)
            else:body,at=_response(rid,evidence,allowance,rate=rate,endpoint=endpoint,kind=kind)
            used+=len(body)
            if rate:latest_rate=dict(rate)
            if len(body)>allowance:
                if allowance==response_cap and used<total_cap:
                    raise ResponseLimit()
                raise CollectionStop('byte_limit')
            return body,at
        try:
            body, received = fetch()
            reason = 'invalid_response'
            raw = json.loads(body, object_pairs_hook=unique_object)
            records = normalize(raw, page_size(rid), allow_missing_published=True)
            acquired = dict(received_at=received, releases=records,page_size=page_size(rid),
                            history_complete=len(raw)<page_size(rid))
            if rid in git_scopes:acquired.update(collect_git(git_scopes[rid],fetch))
            acquisitions[rid]=acquired
            report.append(dict(repository_id=int(rid), repository=name, status='ok', observed_at=received))
            if rate: report[-1]['rate'] = rate
            latest_rate = rate
        except (OSError, http.client.HTTPException, ValueError, KeyError, TypeError) as error:
            if batch_size is None:
                raise
            # Do not repeat requests after rate/auth failures. Diagnostics never
            # interpolate exceptions, request headers or credential-bearing URLs.
            if isinstance(error, urllib.error.HTTPError):
                stop = error.code in (401, 403, 429)
                reason = 'transport'
                rate.update(rate_headers(error.headers))
                error.close()
            if isinstance(error, TransferFailure):
                used += error.budget_bytes
            if isinstance(error,ResponseLimit):
                reason='invalid_response'
            if isinstance(error,CollectionStop):
                stop=True;metrics['stop_reason']=error.reason
                reason={'request_limit':'request_budget','byte_limit':'byte_budget',
                        'time_limit':'time_budget','primary_rate_reserve':'quota'}[error.reason]
            failure = dict(repository_id=int(rid), repository=name, status='failed', reason=reason)
            if failure_cause(error):
                failure.update(failed_at=utc(), failed_with=failure_cause(error))
            if isinstance(error, urllib.error.HTTPError):
                failure['http_status'] = error.code
            if rate:
                failure['rate'] = rate
            if isinstance(error, TransferFailure):
                failure['response_budget_charge'] = error.budget_bytes
            report.append(failure)
            status = ' HTTP '+str(error.code) if isinstance(error, urllib.error.HTTPError) else ''
            print(name+': failed ('+reason+status+')', flush=True)
            latest_rate = rate
            if stop:
                if isinstance(error,urllib.error.HTTPError):metrics['stop_reason'] = 'http_'+str(error.code)
                break
            continue
    if used > total_cap:
        metrics['stop_reason'] = 'byte_limit'
    metrics.update(response_bytes=used, acquisition_seconds=time.monotonic()-started,
                   attempted_sources=len(report),
                   successful_sources=sum(row['status']=='ok' for row in report),
                   unattempted_sources=len(sources)-len(report))
    rates = [row['rate'] for row in report if row.get('rate')]
    if rates:
        metrics.update(rate_first=rates[0], rate_last=rates[-1])
    return report

