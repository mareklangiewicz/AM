"""Run from the repository root; writes a cached-ref, offline readiness report."""
import hashlib,json,subprocess,sys,tarfile
from pathlib import Path
sys.path.insert(0,'tools/catalog-collector')
from manifest import load_manifest
from scheduled_dispatch import MANIFEST,CRON
from reader import FRESHNESS_SECONDS

def git(*args):return subprocess.check_output(['git',*args]).decode().strip()
def blob(rev,path):return subprocess.check_output(['git','show',rev+':'+path])
base=git('rev-parse','origin/main-marek');head=git('rev-parse','HEAD')
oper='docs/track/release-catalog/design/staged-manifest.json';candidate='docs/track/release-catalog/design/staged-manifest-am-utils.json'
raw=Path(oper).read_bytes();cand=Path(candidate).read_bytes()
assert raw==blob(base,oper)
assert hashlib.sha256(raw).hexdigest()==MANIFEST
assert len(load_manifest(raw,1291019762).requests)==6
assert len(load_manifest(cand,1291019762).requests)==7
assert json.loads(cand)['sources'][:6]==json.loads(raw)['sources']
workflow=Path('.github/workflows/catalog-collector.yml').read_bytes()
assert workflow==blob(base,'.github/workflows/catalog-collector.yml')
assert workflow.count(oper.encode())==3 and candidate.encode() not in workflow
paths=['.github/workflows/catalog-schedule.yml','tools/catalog-collector/scheduled_dispatch.py']
assert all(Path(p).read_bytes()==blob('9719fdcee',p) for p in paths)
assert CRON=='17 3 * * *'
assert FRESHNESS_SECONDS==172800
assert 'now-checked>172800' in Path('modules/catalog.am').read_text()
for p in ['tools/catalog-collector/collector.py','tools/catalog-collector/delivery.py','tools/catalog-collector/storage.py']:
    # Bound definitions outside source-count changes must remain unchanged.
    def caps(data):return [l for l in data.decode().splitlines() if '_CAP =' in l or 'timeout-minutes:' in l]
    assert [l for l in caps(Path(p).read_bytes()) if not l.startswith('SOURCE_CAP')] == caps(blob(base,p))
changed=git('diff','--name-only',base+'..'+head).splitlines()
history=git('log','--format=','--name-only',base+'..'+head).splitlines()
private=['docs/track/release-catalog/neovim-pilot/','docs/track/release-catalog/research/neovim-delivery-51-','test/e2e/neovim-config-smoke.py','test/e2e/neovim-delivery-rehearsal','test/e2e/neovim_delivery.py']
assert not any(p.startswith(prefix) for p in history for prefix in private)
assert not git('ls-files','-ci','--exclude-standard')
excluded={}
for rev in ['cd3043c27','26f9ff4c0']:
    result=subprocess.run(['git','merge-base','--is-ancestor',rev,head],capture_output=True)
    assert result.returncode==1,(rev,result.returncode)
    excluded[rev]='not_ancestor'
archives=[]
for p in changed:
    if p.endswith('.tar.gz'):
        with tarfile.open(p) as archive:
            members=archive.getmembers()
            assert all(not m.name.startswith('/') and '..' not in Path(m.name).parts for m in members)
            assert not any(any(prefix in m.name for prefix in private) for m in members)
            archives.append({'path':p,'members':len(members),'bytes':Path(p).stat().st_size,'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()})
files=paths+[oper,candidate,'.github/workflows/catalog-collector.yml','tools/catalog-collector/workflow_adapter.py','tools/catalog-collector/collector.py','tools/catalog-collector/manifest.py','tools/catalog-collector/supervised_transport.py','tools/catalog-collector/storage.py','tools/catalog-collector/delivery.py','modules/catalog.am','tools/catalog-collector/reader.py']
result={'reviewed_head':head,'cached_origin_main_marek':base,'queued_commits':int(git('rev-list','--count',base+'..'+head)),'queued_changed_paths':len(changed),'daily_workflow_controller_equal_ticket_40':True,'cron':CRON,'freshness_seconds':FRESHNESS_SECONDS,'operational_manifest_unchanged':True,'operational_sources':6,'candidate_sources':7,'operational_manifest_sha256':MANIFEST,'collector_workflow_unchanged':True,'byte_cap_definitions_unchanged':True,'private_delivery_paths_absent_from_queued_history':True,'tracked_ignored_paths':0,'excluded_commits':excluded,'archive_path_checks':archives,'files':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in files},'limits':['Offline cached-ref comparison; remote state not verified.','Archive member names checked; no full payload privacy/content audit claimed.','Bounded activation review, not full standards/spec review of every queued source change.','Final activation commit must include later closure evidence; recheck source and manifest then.']}
Path('docs/track/release-catalog/research/daily-switch-offline-review.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('files','archive_path_checks','limits')},indent=2))
