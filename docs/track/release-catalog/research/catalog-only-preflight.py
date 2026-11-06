"""Fresh bounded acquisition and remote-free replay; never push or deploy."""
import argparse
import contextlib
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import time
import urllib.request

root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(root/'tools/catalog-collector'))
import host_catalog
from publication import git, publish_tree
from yaml_publication import load_local

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out', type=Path, required=True)
parser.add_argument('--parent', required=True)
args = parser.parse_args()
args.out.mkdir(parents=True, exist_ok=False)
evidence = args.out/'responses'; evidence.mkdir()
rows, sources = host_catalog.configuration()
token = subprocess.check_output(['gh', 'auth', 'token'], text=True).strip()
started = time.monotonic()
used = 0
responses = []
for rid, name in sources.items():
    if time.monotonic()-started > 300:
        raise ValueError('collection elapsed budget')
    url = f'https://api.github.com/repositories/{rid}/releases?per_page=100&page=1'
    request = urllib.request.Request(url, headers={
        'Authorization': 'Bearer '+token, 'Accept': 'application/vnd.github+json',
        'User-Agent': 'AM-catalog-preflight', 'X-GitHub-Api-Version': '2022-11-28'})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200 or response.url != url:
            raise ValueError('release response identity')
        body = response.read(host_catalog.RESPONSE_CAP+1)
    used += len(body)
    if len(body) > host_catalog.RESPONSE_CAP or used > host_catalog.TOTAL_CAP:
        raise ValueError('collection byte budget')
    observed = host_catalog.utc()
    (evidence/(rid+'-releases.json')).write_bytes(body)
    (evidence/(rid+'-receipt.txt')).write_text(observed+'\n')
    responses.append(dict(repository_id=rid, repository=name, bytes=len(body),
        observed_at=observed, sha256=hashlib.sha256(body).hexdigest()))
    print(name, flush=True)
elapsed = time.monotonic()-started
del token
repo = args.out/'catalog.git'; repo.mkdir()
git(repo, 'init', '--bare', '--quiet', '--template=')
subprocess.run(['git', '-C', str(root), 'push', str(repo),
    args.parent+':refs/heads/catalog'], check=True, capture_output=True)
apps_before, prior = load_local(repo, args.parent, max_file_bytes=host_catalog.FILE_CAP)
revision = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
started = time.monotonic()
with contextlib.redirect_stdout(io.StringIO()):
    tree, report = host_catalog.collect(revision, prior, evidence)
pin = publish_tree(repo, tree, args.parent)
apps, documents = load_local(repo, pin, max_file_bytes=host_catalog.FILE_CAP)
assert all(apps.get(app) == rid for app, rid in apps_before.items())
assert len(documents) == len(sources)
result = dict(parent=args.parent, candidate=pin, source=revision,
    note='Local working-tree rehearsal; candidate is not published and pending source edits are not claimed committed.',
    apps=len(apps), repositories=len(documents), response_bytes=used,
    acquisition_seconds=elapsed, replay_seconds=time.monotonic()-started,
    yaml_bytes=sum(map(len, tree.values())), largest_yaml_bytes=max(map(len, tree.values())),
    previous_app_identities_preserved=True, responses=responses)
(args.out/'receipt.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({key:value for key,value in result.items() if key!='responses'}, indent=2))
