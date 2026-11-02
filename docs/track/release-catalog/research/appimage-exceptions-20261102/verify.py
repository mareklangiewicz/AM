import sys,json,zipfile,io,unittest,hashlib,subprocess,tempfile
from pathlib import Path
from datetime import datetime,timezone,timedelta
from unittest.mock import patch
sys.path.insert(0,str(Path.cwd()/'tools/catalog-collector'))
from delivery import unpack_artifact,verify_artifact,read_git_tree
from storage import validate,apply,canonical
from workflow_adapter import prepare
from collector import Descriptor
from publication import publish_local,git
from reader import select,verify_body
import test_delivery as fixture
import test_migration_batch as batch
D=Path('docs/track/release-catalog/research/appimage-exceptions-20261102'); C=json.loads((D/'candidates.json').read_bytes()); raw=(D/'candidate-manifest.json').read_bytes()
base={p.removeprefix('candidate/'):v for p,v in unpack_artifact(Path(sys.argv[1]).read_bytes()).items() if p.startswith('candidate/')}
GEN=datetime.now(timezone.utc).isoformat(); REV='a'*40
ctx=dict(repository='mareklangiewicz/AM',repository_id='1291019762',event='workflow_dispatch',ref='refs/heads/main-marek',sha=REV,workflow_sha=REV,approved_revision=REV,run_id='1',run_attempt='1',manifest_sha256=hashlib.sha256(raw).hexdigest(),previous_publication='b'*40)
attempts=[]
for rid,e in validate(base)['entries'].items():
 attempts.append(dict(request_id=rid,descriptor=e['descriptor'],repository_id=e['repository_id'],request_started_at=GEN,response_completed_at=GEN,attempt_finished_at=GEN,status=304,headers={},body=b'',condition=e['validators'],outcome='response'))
for n in range(1,5):
 r=json.loads((D/f'release-{n}'/'report.json').read_bytes()); body=(D/f'release-{n}'/'body.json').read_bytes()
 assert hashlib.sha256(body).hexdigest()==r['body_sha256'] and hashlib.sha256((D/f'release-{n}'/'headers.txt').read_bytes()).hexdigest()==r['headers_sha256']
 attempts.append(dict(request_id=r['descriptor']['request_id'],descriptor={k:r['descriptor'][k] for k in ('url','api_version','accept')},repository_id=int(r['url'].split('/repositories/')[1].split('/')[0]),request_started_at=r['started_at'],response_completed_at=r['completed_at'],attempt_finished_at=GEN,status=200,headers=r['public_headers'],body=body,condition={},outcome='response'))
helper=fixture.DeliveryContract();helper.raw=raw
class Checks(unittest.TestCase):
 def test_plan_bound_and_preservation(self):
  m=json.loads(raw);self.assertEqual(m['sources'][:52],json.loads(validate(base)['manifest_json'])['sources'])
  p=prepare(ctx,raw,REV,base);self.assertEqual(len(p.requests),56);self.assertTrue(all(r.condition for r in p.requests[:52]));self.assertTrue(all(not r.condition for r in p.requests[52:]))
  row=dict(m['sources'][-1]);row['url']+='?page=2';row['request_id']=Descriptor(row['url']).request_id;row['aliases']=[];m['sources'].append(row);bad=canonical(m)
  with patch('workflow_adapter.SupervisedTransport') as t,patch('workflow_adapter.Token') as token:
   with self.assertRaises(ValueError):prepare(dict(ctx,manifest_sha256=hashlib.sha256(bad).hexdigest()),bad,REV,base)
   t.assert_not_called();token.assert_not_called()
 def test_recompute_readers_capacity_parent_and_failure(self):
  files,tree=helper.files(ctx,base,attempts,GEN)
  self.assertEqual(verify_artifact(files,ctx,raw,REV,base),tree)
  index=validate(tree)
  for alias in index['aliases']:
   e,_=select(tree['index.json'],alias,'c'*40,now=GEN);self.assertEqual(verify_body(tree[e['observation']['path']],e),tree[e['observation']['path']])
  zipraw=io.BytesIO()
  with zipfile.ZipFile(zipraw,'w',compression=zipfile.ZIP_DEFLATED) as z:
   for p,b in files.items():z.writestr(p,b)
  self.assertEqual(unpack_artifact(zipraw.getvalue()),files)
  with tempfile.TemporaryDirectory() as d:
   repo=Path(d)/'git';repo.mkdir();subprocess.run(['git','init','--bare','--quiet',str(repo)],check=True)
   parent=publish_local(repo,base,None);child=publish_local(repo,tree,parent);self.assertEqual(read_git_tree(repo,child),tree);self.assertEqual(git(repo,'show','-s','--format=%P',child).decode().strip(),parent)
   metrics=dict(tree_bytes=sum(map(len,tree.values())),zip_bytes=len(zipraw.getvalue()),sources=56,existing_304_events='52 synthetic, not live observations',new_sources=4,request_caps_unchanged=True)
  (D/'capacity.json').write_text(json.dumps(metrics,indent=2)+'\n')
  failed=[dict(a) for a in attempts];failed[-1].update(status=None,outcome='timeout',response_completed_at=None,body=b'',headers={})
  files,_=helper.files(ctx,base,failed,GEN);files.pop(failed[-1]['request_id']+'.body',None)
  with self.assertRaises(ValueError):verify_artifact(files,ctx,raw,REV,base)
  bad=[dict(a) for a in attempts];bad[-1].update(status=304,body=b'',headers={})
  with self.assertRaises(ValueError):
   badfiles,_=helper.files(ctx,base,bad,GEN)
   verify_artifact(badfiles,ctx,raw,REV,base)
# Exercise every candidate through the existing inert install/generated-updater
# lifecycle cases, with actual retained metadata and synthetic publications.
import inspect,textwrap
method='test_each_architecture_failure_retry_integrity_stale_and_exact_consent'
source=textwrap.dedent(inspect.getsource(getattr(batch.BatchLifecycle,method))).replace("{'x86_64','aarch64','i686','armv7l'}","{'x86_64','aarch64'}")
exec(source,batch.__dict__)
setattr(batch.BatchLifecycle,method,batch.__dict__[method])
batch.GEN=GEN
batch.migration_rows=lambda:C['recipes']
suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(Checks),unittest.defaultTestLoader.loadTestsFromTestCase(batch.BatchLifecycle)])
r=unittest.TextTestRunner(verbosity=2).run(suite);raise SystemExit(not r.wasSuccessful())
