"""Actual ZIP -> publisher -> bare Git -> pinned shell roundtrips, without HTTP."""
import io
import json
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
from unittest.mock import patch
import zipfile

import test_delivery as delivery_tests
from test_shell_consumer import ShellFixture, HELPER, ALIAS
from test_storage import GEN, LATER, REV
from delivery import publish, unpack_artifact, REMOTE_REF
from publication import git
from shell_lookup import epoch
from storage import validate


class ShellDelivery(ShellFixture):
    def setUp(self):
        super().setUp()
        self.producer=delivery_tests.DeliveryContract()
        self.producer.setUpClass()
        self.remote=self.path/'remote.git'
        subprocess.run(['git','init','--bare','--quiet','--template=',str(self.remote)],check=True)
        self.script('curl', '''import json, os, pathlib, re, subprocess, sys
p=pathlib.Path(os.environ['FIXTURE']); repo=p/'remote.git'
a=sys.argv[1:]; url=a[-1]
with (p/'calls').open('a') as f: f.write(json.dumps(a)+'\\n')
def git(*args):
    return subprocess.run(['/usr/bin/git','--git-dir='+str(repo),*args],check=True,capture_output=True).stdout
if url=='https://api.github.com/repos/mareklangiewicz/AM/commits/heads/release-catalog':
    raw=git('rev-parse','refs/heads/release-catalog')
else:
    match=re.fullmatch(r'https://raw.githubusercontent.com/mareklangiewicz/AM/([0-9a-f]{40})/(lookup\\.tsv|bodies/[0-9a-f]{64}\\.json)',url)
    assert match, url
    commit, name=match.groups(); raw=git('show',commit+':'+name)
    # Move the branch after its first pinned metadata read, before body fetch.
    move=p/'move-to'
    if name=='lookup.tsv' and move.exists():
        git('update-ref','refs/heads/release-catalog',move.read_text().strip());move.unlink()
pathlib.Path(a[a.index('--output')+1]).write_bytes(raw)
print('200',end='')
''')

    def publish(self, context=None, prior=None, attempts=None, generated=GEN, directory='publication'):
        context=context or self.producer.context()
        files,tree=self.producer.files(context,prior,attempts,generated)
        archive=io.BytesIO()
        with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
            for name,raw in files.items():z.writestr(name,raw)
        # The download boundary is the only injected publisher operation. ZIP,
        # candidate recomputation, Git objects, parent checks and push are real.
        artifact=unpack_artifact(archive.getvalue())
        with patch('delivery.URL',str(self.remote)),patch('delivery.download_artifact',return_value=artifact):
            result=publish(context,self.producer.raw,REV,'1','a'*64,b'FIXTURE',self.path/directory)
        return result['commit'],tree

    def repeat(self, first, tree):
        context=self.producer.context();context['previous_publication']=first
        entries=validate(tree)['entries']
        attempts=[{**a,'status':304,'body':b'','headers':{},'condition':entries[a['request_id']]['validators'],
                   'request_started_at':LATER,'response_completed_at':LATER,'attempt_finished_at':LATER}
                  for a in self.producer.attempts]
        return self.publish(context,tree,attempts,LATER,'repeat')

    def test_real_published_artifact_and_ref_movement_keep_one_snapshot(self):
        first,tree=self.publish()
        second,tree2=self.repeat(first,tree)
        self.assertNotEqual(first,second)
        self.assertEqual(git(self.remote,'rev-parse',second+'^').decode().strip(),first)
        self.assertEqual(tree['bodies/'+self.rid+'.json'],tree2['bodies/'+self.rid+'.json'])
        self.assertNotEqual(tree['lookup.tsv'],tree2['lookup.tsv'])
        # Resolve first, then move the branch to second while the reader runs.
        git(self.remote,'update-ref',REMOTE_REF,first)
        (self.path/'move-to').write_text(second)
        r=self.invoke(args=[])
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(r.stdout,tree['bodies/'+self.rid+'.json'])
        calls=self.calls();self.assertEqual(len(calls),3)
        self.assertTrue(all('/'+first+'/' in c[-1] for c in calls[1:]))
        self.assertEqual(git(self.remote,'rev-parse',REMOTE_REF).decode().strip(),second)
        self.now=[epoch(LATER)]*3
        r=self.invoke(args=['--commit',second])
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(len(self.calls()),2)
        self.assertTrue(all('/'+second+'/' in c[-1] for c in self.calls()))

    def test_stale_acceptance_binds_actual_publication_even_for_same_body(self):
        first,tree=self.publish();second,tree2=self.repeat(first,tree)
        newest=max(datetime.fromisoformat(validate(t)['entries'][self.rid]['observation']['validated_at'])
                   for t in (tree,tree2))
        self.now=[epoch((newest+timedelta(hours=48,microseconds=1)).isoformat())]*3
        obs=validate(tree)['entries'][self.rid]['observation']
        exact=['--commit',first,'--accept-stale',first,self.rid,obs['sha256']]
        r=self.invoke(args=['--commit',first]);self.assertNotEqual(r.returncode,0)
        self.assertEqual(len(self.calls()),1);self.assertEqual(r.stdout,b'')
        r=self.invoke(args=exact);self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(r.stdout,tree['bodies/'+self.rid+'.json'])
        # The unchanged response hash is not consent to a different publication.
        wrong=list(exact);wrong[1]=second
        r=self.invoke(args=wrong);self.assertNotEqual(r.returncode,0)
        self.assertEqual(len(self.calls()),1);self.assertEqual(r.stdout,b'')
        wrong[3]=second
        r=self.invoke(args=wrong);self.assertEqual(r.returncode,0,r.stderr)
