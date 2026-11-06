"""Single-user YAML catalog: bounded release-list collection and retained facts.

Collection combines reviewed recipe declarations and catalog-only identities.
One page of 100 releases per attempted source; clients enforce 48-hour selected
record freshness. Batches preserve untouched facts and isolate source failures.
No latest endpoint, consumer version choice or pruning.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import http.client
import json
import os
import re
from pathlib import Path
import subprocess
import time
import urllib.error
import urllib.request

import yaml

from bounded import normalize, unique_object
from retention import refresh
from yaml_publication import schema_url
from yaml_publication import candidate_tree, load_local
from publication import git, publish_tree

from recipe_declarations import recipe_rows

ROOT = Path(__file__).resolve().parents[2]
FILE_CAP = 2097152
RESPONSE_CAP = 16 * 1024 * 1024
TOTAL_CAP = 96 * 1024 * 1024
SOURCE_CAP = 224
REQUEST_CAP = 52


class TransferFailure(OSError):
    """Reserve the complete read allowance when a transfer ends mid-response."""
    def __init__(self, budget_bytes):
        super().__init__('release transfer failed')
        self.budget_bytes = budget_bytes


def utc():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def configuration():
    declarations = {row['recipe']: row for row in recipe_rows(ROOT)}
    enrolled = [line for line in (ROOT/'tools/catalog-collector/collection-recipes.txt').read_text().splitlines()
                if line and not line.startswith('#')]
    if not enrolled or len(set(enrolled)) != len(enrolled):
        raise ValueError('empty or duplicate collection enrollment')
    if any(recipe not in declarations for recipe in enrolled):
        raise ValueError('unknown collection recipe')
    rows = [declarations[recipe] for recipe in enrolled]
    # Catalog facts do not require an installer migration or selection policy.
    # Missing file supports older checkouts and isolated declaration fixtures.
    catalog_only = ROOT/'tools/catalog-collector/collection-apps.json'
    extra = (json.loads(catalog_only.read_text(), object_pairs_hook=unique_object)
             if catalog_only.exists() else [])
    if not isinstance(extra, list):
        raise ValueError('catalog-only enrollment must be a list')
    for row in extra:
        if (not isinstance(row, dict) or set(row) != {'app', 'repository_id', 'repository'}
                or not isinstance(row['app'], str)
                or not re.fullmatch(r'[a-z0-9][a-z0-9_.+-]*', row['app'])
                or type(row['repository_id']) is not int or row['repository_id'] <= 0
                or not isinstance(row['repository'], str)
                or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', row['repository'])):
            raise ValueError('invalid catalog-only enrollment')
    rows = rows + extra
    sources = {}
    for row in rows:
        rid = str(row['repository_id'])
        if rid in sources and sources[rid] != row['repository']:
            raise ValueError('conflicting repository identity')
        sources[rid] = row['repository']
    if len(sources) > SOURCE_CAP or len({r['app'] for r in rows}) != len(rows):
        raise ValueError('manifest scope')
    return rows, sources


def installation_configuration():
    """Only enrolled recipes with reviewed installation/selection declarations."""
    rows, _ = configuration()
    rows = [row for row in rows if 'recipe' in row]
    return rows, {str(row['repository_id']): row['repository'] for row in rows}


def _response(rid, evidence, allowance):
    """Bound response bytes at the transport seam; return inert text and receipt."""
    if evidence:
        path = Path(evidence)/(rid+'-releases.json')
        with path.open('rb') as stream:
            body = stream.read(allowance+1)
        received = (Path(evidence)/(rid+'-receipt.txt')).read_text().strip()
        return body, received
    url = f'https://api.github.com/repositories/{rid}/releases?per_page=100&page=1'
    headers = {'Accept':'application/vnd.github+json', 'User-Agent':'AM-YAML-catalog',
               'X-GitHub-Api-Version':'2022-11-28'}
    token = os.environ.get('GH_TOKEN')
    if token:
        headers['Authorization'] = 'Bearer '+token
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
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


def collect(revision, previous, evidence=None, *, batch_size=None):
    """Refresh all (strict) or a bounded oldest-attempt-first batch.

    Strict mode retains the existing all-or-nothing command. Batch mode reports
    failures, preserves old observations and publishes only successfully observed
    new app identities. Unattempted documents retain their original schema too.
    """
    rows, sources = configuration()
    if batch_size is not None and (type(batch_size) is not int or not 1 <= batch_size <= REQUEST_CAP):
        raise ValueError('batch size')
    if batch_size is None and len(sources) > REQUEST_CAP:
        raise ValueError('use bounded batch collection')
    if batch_size is not None and not set(previous) <= set(sources):
        raise ValueError('batch would discard retained sources')
    for rid, before in previous.items():
        if rid in sources and (before['repository_id'] != int(rid) or
                               before['repository'].lower() != sources[rid].lower()):
            raise ValueError('retained repository identity mismatch')
    selected = list(sources)
    if batch_size is not None:
        selected.sort(key=lambda rid: (previous.get(rid, {}).get('collection', {}).get('attempted_at', ''), int(rid)))
        selected = selected[:batch_size]
    schema = schema_url(revision)
    repositories = dict(previous) if batch_size is not None else {}
    used = 0
    report = []
    started = time.monotonic()
    for rid in selected:
        name = sources[rid]
        if time.monotonic()-started > 300 or used >= TOTAL_CAP:
            if batch_size is not None:
                break
            raise ValueError('collection elapsed budget')
        attempted = utc()
        before = previous.get(rid, dict(format=2, schema=schema,
            repository_id=int(rid), repository=name))
        stop = False
        reason = 'transport'
        try:
            allowance = min(RESPONSE_CAP, TOTAL_CAP-used)
            body, received = _response(rid, evidence, allowance)
            used += len(body)
            if evidence:
                attempted = received
            reason = 'collection_limit'
            if len(body) > allowance:
                raise ValueError('collection byte budget')
            reason = 'invalid_response'
            raw = json.loads(body, object_pairs_hook=unique_object)
            records = normalize(raw, 100)
            response = dict(received_at=received, releases=records, has_next=len(raw)==100,
                            bytes=len(body), seconds=0)
            result = refresh(before, [response], attempted_at=attempted,
                page_size=100, page_limit=1, max_catalog_bytes=FILE_CAP)
            reason = result['collection'].get('reason', 'invalid_response')
            if result['collection']['status'] != 'ok':
                raise ValueError('source refused: '+rid)
        except (OSError, http.client.HTTPException, ValueError, KeyError, TypeError) as error:
            if batch_size is None:
                raise
            # Do not repeat requests after rate/auth failures. Diagnostics never
            # interpolate exceptions, request headers or credential-bearing URLs.
            if isinstance(error, urllib.error.HTTPError):
                stop = error.code in (401, 403, 429)
                reason = 'transport'
                error.close()
            if isinstance(error, TransferFailure):
                used += error.budget_bytes
            result = refresh(before, [dict(error=reason, releases={}, bytes=0,
                seconds=0, received_at=attempted, has_next=False)],
                attempted_at=attempted, page_size=100, page_limit=1,
                max_catalog_bytes=FILE_CAP)
            repositories[rid] = result
            failure = dict(repository_id=int(rid), repository=name, status='failed', reason=reason)
            if isinstance(error, urllib.error.HTTPError):
                failure['http_status'] = error.code
            if isinstance(error, TransferFailure):
                failure['response_budget_charge'] = error.budget_bytes
            report.append(failure)
            status = ' HTTP '+str(error.code) if isinstance(error, urllib.error.HTTPError) else ''
            print(name+': failed ('+reason+status+')', flush=True)
            if stop:
                break
            continue
        result['schema'] = schema
        result['repository'] = name
        repositories[rid] = result
        report.append(dict(repository_id=int(rid), repository=name, status='ok', observed_at=received,
                           response_sha256=hashlib.sha256(body).hexdigest()))
        print(name+': '+str(len(records))+' releases', flush=True)
    apps = {row['app']:row['repository_id'] for row in rows
            if str(row['repository_id']) in repositories and
            (batch_size is None or 'last_success' in repositories[str(row['repository_id'])])}
    tree = candidate_tree(apps, repositories, schema=schema, max_file_bytes=FILE_CAP)
    return tree, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True, type=Path, help='Remote-free bare publication repository')
    parser.add_argument('--parent', required=True, help='Existing release-catalog commit')
    parser.add_argument('--evidence', type=Path, help='Saved live responses; no requests')
    parser.add_argument('--report', required=True, type=Path)
    parser.add_argument('--batch-size', type=int, help='Oldest-attempt-first subset, at most 52 requests')
    args = parser.parse_args()
    revision = subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
    previous = load_local(args.repo,args.parent,max_file_bytes=FILE_CAP)[1]
    tree, report = collect(revision, previous, args.evidence, batch_size=args.batch_size)
    pin = publish_tree(args.repo, tree, args.parent)
    rows, sources = configuration()
    apps = yaml.safe_load(tree['apps.yaml'])['apps']
    pending = sorted({row['app'] for row in rows}-set(apps))
    args.report.write_text(json.dumps(dict(pin=pin,parent=args.parent,source=revision,
        batch_size=args.batch_size,enrolled_apps=len(rows),enrolled_sources=len(sources),
        published_apps=len(apps),pending_apps=pending,sources=report),indent=2)+'\n')
    failures = sum(row['status']=='failed' for row in report)
    print(f'Catalog apps: {len(apps)} / {len(rows)} enrolled; {len(report)} sources attempted; '
          f'{failures} failed; {len(pending)} apps pending', flush=True)
    print('Catalog commit: '+pin)


if __name__=='__main__': main()
