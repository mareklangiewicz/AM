"""Single-user YAML catalog: bounded release-list collection and retained facts.

The explicit collection list resolves reviewed recipe declarations. One page of 100 releases per source, with
48-hour selected-record freshness enforced by clients. Failures preserve the
previous published tree. No latest endpoint, consumer version choice or pruning.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.request

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
    sources = {}
    for row in rows:
        rid = str(row['repository_id'])
        if rid in sources and sources[rid] != row['repository']:
            raise ValueError('conflicting repository identity')
        sources[rid] = row['repository']
    if len(sources) > 52 or len({r['app'] for r in rows}) != len(rows):
        raise ValueError('manifest scope')
    return rows, sources


def collect(revision, previous, evidence=None):
    rows, sources = configuration()
    schema = schema_url(revision)
    repositories = {}
    used = 0
    report = []
    started = time.monotonic()
    for rid, name in sources.items():
        if time.monotonic()-started > 300:
            raise ValueError('collection elapsed budget')
        attempted = utc()
        before = previous.get(rid, dict(format=2, schema=schema,
            repository_id=int(rid), repository=name))
        if evidence:
            path = Path(evidence)/(rid+'-releases.json')
            if path.stat().st_size > RESPONSE_CAP:
                raise ValueError('response byte budget')
            body = path.read_bytes()
            received = (Path(evidence)/(rid+'-receipt.txt')).read_text().strip()
            attempted = received
        else:
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
                body = response.read(RESPONSE_CAP+1)
            received = utc()
        used += len(body)
        if len(body)>RESPONSE_CAP or used>TOTAL_CAP:
            raise ValueError('collection byte budget')
        raw = json.loads(body, object_pairs_hook=unique_object)
        records = normalize(raw, 100)
        # A full page may have more history. Never claim EOF based on the cap.
        response = dict(received_at=received, releases=records, has_next=len(raw)==100,
                        bytes=len(body), seconds=0)
        result = refresh(before, [response], attempted_at=attempted,
            page_size=100, page_limit=1, max_catalog_bytes=FILE_CAP)
        if result['collection']['status'] != 'ok':
            raise ValueError('source refused: '+rid)
        result['schema'] = schema
        result['repository'] = name
        repositories[rid] = result
        report.append(dict(repository_id=int(rid), repository=name, observed_at=received,
                           response_sha256=hashlib.sha256(body).hexdigest()))
        print(name+': '+str(len(records))+' releases', flush=True)
    apps = {row['app']:row['repository_id'] for row in rows}
    tree = candidate_tree(apps, repositories, schema=schema, max_file_bytes=FILE_CAP)
    return tree, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True, type=Path, help='Remote-free bare publication repository')
    parser.add_argument('--parent', required=True, help='Existing release-catalog commit')
    parser.add_argument('--evidence', type=Path, help='Saved live responses; no requests')
    parser.add_argument('--report', required=True, type=Path)
    args = parser.parse_args()
    revision = subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
    previous = load_local(args.repo,args.parent,max_file_bytes=FILE_CAP)[1]
    tree, report = collect(revision, previous, args.evidence)
    pin = publish_tree(args.repo, tree, args.parent)
    args.report.write_text(json.dumps(dict(pin=pin,parent=args.parent,source=revision,sources=report),indent=2)+'\n')
    print('Catalog commit: '+pin)


if __name__=='__main__': main()
