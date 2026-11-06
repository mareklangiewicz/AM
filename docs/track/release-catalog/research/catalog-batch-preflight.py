"""Fresh bounded batch rehearsal; local Git publication only, no remote writes."""
import argparse
import contextlib
import hashlib
import io
import json
from pathlib import Path
import resource
import subprocess
import sys
import time

import yaml

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT/'tools/catalog-collector'))
import host_catalog as collector
from publication import git, publish_tree
from yaml_publication import load_local

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out', type=Path, required=True)
parser.add_argument('--parent', required=True)
args = parser.parse_args()
# Keep a full-tree rehearsal from competing without a bound with desktop apps.
resource.setrlimit(resource.RLIMIT_AS, (1024**3, 1024**3))
args.out.mkdir(parents=True, exist_ok=False)
responses = args.out/'responses'; responses.mkdir()
repo = args.out/'catalog.git'; repo.mkdir()
git(repo, 'init', '--bare', '--quiet', '--template=')
subprocess.run(['git','-C',str(ROOT),'push',str(repo),args.parent+':refs/heads/catalog'],
    check=True, capture_output=True)
baseline, prior = load_local(repo, args.parent, max_file_bytes=collector.FILE_CAP)
revision = subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
rows, sources = collector.configuration()
original = collector._response
captures = []
def capture(rid, evidence, allowance):
    body, received = original(rid, evidence, allowance)
    (responses/(rid+'-releases.json')).write_bytes(body)
    (responses/(rid+'-receipt.txt')).write_text(received+'\n')
    captures.append(dict(repository_id=rid, bytes=len(body), sha256=hashlib.sha256(body).hexdigest(),
        observed_at=received))
    return body, received
collector._response = capture
pin = args.parent
attempted, batches = set(), []
for number in range(1, 4):
    before_captures = len(captures)
    started = time.monotonic()
    with contextlib.redirect_stdout(io.StringIO()):
        tree, report = collector.collect(revision, prior, batch_size=52)
    child = publish_tree(repo, tree, pin)
    apps = yaml.safe_load(tree['apps.yaml'])['apps']
    assert all(apps.get(app) == rid for app,rid in baseline.items())
    prior = {path.split('/')[1][:-5]:yaml.safe_load(body) for path,body in tree.items()
             if path.startswith('repositories/')}
    attempted.update(str(row['repository_id']) for row in report)
    batches.append(dict(number=number, parent=pin, candidate=child,
        seconds=time.monotonic()-started, apps=len(apps), repositories=len(prior),
        response_bytes=sum(row['bytes'] for row in captures[before_captures:]),
        yaml_bytes=sum(map(len,tree.values())), largest_yaml_bytes=max(map(len,tree.values())),
        sources=report))
    pin = child
    (args.out/'batches.json').write_text(json.dumps(batches,indent=2)+'\n')
    print('Batch',number,':',len(apps),'apps;',len(attempted),'sources attempted;',
          round(batches[-1]['seconds'],2),'seconds',flush=True)
    if attempted == set(sources):
        break
apps, validated = load_local(repo,pin,max_file_bytes=collector.FILE_CAP)
assert all(apps.get(app)==rid for app,rid in baseline.items())
result = dict(source=revision,
    note='Pending working-tree rehearsal, not a published source/catalog. Full original responses are local evidence.',
    parent=args.parent, candidate=pin, enrolled_apps=len(rows), enrolled_sources=len(sources),
    published_candidate_apps=len(apps), candidate_repositories=len(validated),
    sources_attempted=len(attempted), all_enrolled_sources_attempted=attempted==set(sources),
    all_previous_app_identities_preserved=True, batches=batches,
    failed_sources={rid:doc['collection']['reason'] for rid,doc in validated.items()
                    if doc['collection']['status']=='failed'},
    peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    transport=captures)
(args.out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({key:value for key,value in result.items() if key not in ('batches','transport')},indent=2))
