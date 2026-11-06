"""Prepare five existing recipes with saved facts and static AppImage inspection.

Reuses the reviewed 135 acquisition/inspection scripts after binding their
archive digest. Never installs or executes application payloads or AppRun.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'tools/recipe-reconstruction'))
from originals import Originals, Catalogue

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
resource.setrlimit(resource.RLIMIT_AS, (1024**3, 1024**3))
base = args.out
base.mkdir(parents=True, exist_ok=False)
stage = base/'evidence';stage.mkdir()
payloads = base/'payloads';payloads.mkdir()
research = ROOT/'docs/track/release-catalog/research'
prior = json.loads((research/'next-ten-evidence.json').read_text())
archive = research/prior['evidence_archive']
assert hashlib.sha256(archive.read_bytes()).hexdigest() == prior['evidence_archive_sha256']
originals = Originals(ROOT)
revision = 'bbffd15c19d01ef9124fbf99b5b9c41d2661ea22'
catalogue = Catalogue(originals,[revision,'bb53f3180ec92f862020f8bdccef0f6614015bae'])
apps = ('agent-skills','agent-smith','agent-switchboard','agent-teams-ai','agent-toolkit')
rows = []
def fetch(path, target):
    headers = {'Accept':'application/vnd.github+json','User-Agent':'AM-recipe-preparation',
               'X-GitHub-Api-Version':'2022-11-28'}
    if os.environ.get('GH_TOKEN'):
        headers['Authorization'] = 'Bearer '+os.environ['GH_TOKEN']
    with urllib.request.urlopen(urllib.request.Request('https://api.github.com/'+path,
            headers=headers), timeout=30) as response:
        body = response.read(16*1024*1024+1)
        assert len(body) <= 16*1024*1024
    target.write_bytes(body)
    return json.loads(body), hashlib.sha256(body).hexdigest()
for app in apps:
    source = (ROOT/'programs/x86_64'/app).read_text()
    assert source == originals.read(revision,'programs/x86_64/'+app)
    checked = catalogue.check(source)
    assert checked['status'] == 'instance'
    match = next(match for match in checked['matches'] if match['status']=='instance')
    assert catalogue.render(match['template'],match['parameters']) == source
    assert match['parameters'][:3] == match['parameters'][3:]
    repository = match['parameters'][1]
    d = stage/app;d.mkdir()
    metadata, metadata_hash = fetch('repos/'+repository,d/'repository.json')
    assert metadata['private'] is False and metadata['full_name'].lower()==repository.lower()
    releases, releases_hash = fetch('repositories/'+str(metadata['id'])+'/releases?per_page=100&page=1',d/'releases.json')
    assert isinstance(releases,list) and 0<len(releases)<=100 and not any(r.get('draft') for r in releases)
    import datetime
    observed = datetime.datetime.now(datetime.timezone.utc).isoformat()
    rows.append(dict(app=app,requested_repository=repository,repository=metadata['full_name'],
        repository_id=metadata['id'],observed_at=observed,repository_sha256=metadata_hash,
        releases_sha256=releases_hash,release_count=len(releases),status='metadata-ready',
        provenance=dict(recipe='programs/x86_64/'+app,source_commit=revision,
            source_sha256=hashlib.sha256(source.encode()).hexdigest(),**checked)))
(stage/'metadata.json').write_text(json.dumps(rows,indent=2)+'\n')
with tarfile.open(archive) as saved:
    for name in ('prepare.py','acquire.py','static_payload.py','policies.py'):
        text = saved.extractfile('scripts/'+name).read().decode()
        text = text.replace('/tmp/am-135',str(stage))
        text = text.replace('/home/marek/Documents/Codex/am-next-ten-20261106',str(payloads))
        text = text.replace('if len(chosen)==12:break','if len(chosen)==5:break')
        (stage/name).write_text(text)
for name in ('prepare.py','acquire.py','static_payload.py','policies.py'):
    subprocess.run([sys.executable,str(stage/name)],check=True,cwd=ROOT)
print('Local static evidence:',stage)
