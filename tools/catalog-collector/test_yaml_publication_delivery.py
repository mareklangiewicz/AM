"""Offline remote-prior and exact-lease publication; local file Git only."""
import hashlib
from pathlib import Path
import shutil
import unittest
from unittest.mock import patch

from publication import git, REF
from delivery import YAML_REMOTE_REF as REMOTE_REF
import delivery as shared
from storage import canonical
from test_yaml_staging import REV, POLICY
import test_yaml_staging as staging_tests
from test_yaml_delivery import zipped
import yaml_delivery as delivery
import yaml_staging as staging


class Publication(unittest.TestCase):
    setUpClass = classmethod(staging_tests.Staging.setUpClass.__func__)
    produce = staging_tests.Staging.produce

    def setUp(self):
        staging_tests.Staging.setUp(self)
        self.remote = Path(self.directory.name)/'remote.git'
        self.remote.mkdir()
        git(self.remote,'init','--bare','--quiet','--template=')
        self.counter = 0
        self.url_patch = patch('delivery.URL',str(self.remote))
        self.url_patch.start()
        self.addCleanup(self.url_patch.stop)
        self.produce()
        self.capture()

    def capture(self):
        self.tree,self.receipt = staging.read_staged(self.output,self.limits)
        self.zip = zipped([('receipt.json',self.receipt),
                           *[('candidate/'+p,b) for p,b in self.tree.items()]])
        self.digest = hashlib.sha256(self.zip).hexdigest()

    def publish(self, **kwargs):
        self.counter += 1
        directory = Path(self.directory.name)/f'publication-{self.counter}'
        metadata = dict(id=42,expired=False,name='yaml-bootstrap-10-1',
            size_in_bytes=len(self.zip),digest='sha256:'+self.digest,
            workflow_run=dict(id=10,head_sha=REV,repository_id=1,
                              head_repository_id=1,head_branch='main-marek'))
        bounded = shared.bounded
        def io(command, **options):
            if command[0] == 'gh':
                return self.zip if command[-1].endswith('/zip') else canonical(metadata)
            return bounded(command,**options)
        with patch('delivery.bounded',side_effect=io):
            result = delivery.publish(self.context,self.raw,REV,POLICY,self.recipes,
                '42',self.digest,b'fixture-token',directory,**kwargs)
        return result

    def current(self):
        return git(self.remote,'for-each-ref','--format=%(objectname)',REMOTE_REF).decode().strip()

    def refresh(self, pin):
        git(self.repo,'fetch','--quiet','--no-tags',str(self.remote),f'{REMOTE_REF}:{REF}')
        self.context['previous_publication'] = pin
        shutil.rmtree(self.output)
        self.produce()
        self.capture()

    def other_commit(self, parent=None):
        tree = git(self.remote,'mktree',data=b'').decode().strip()
        return git(self.remote,'commit-tree',tree,*(['-p',parent] if parent else []),
                   data=b'Competing publication\n').decode().strip()

    def test_yaml_publication_does_not_touch_format1_ref(self):
        legacy=self.other_commit()
        git(self.remote,'update-ref',shared.REMOTE_REF,legacy)
        result=self.publish()
        self.assertEqual(result['ref'],REMOTE_REF)
        self.assertNotEqual(REMOTE_REF,shared.REMOTE_REF)
        self.assertEqual(git(self.remote,'rev-parse',shared.REMOTE_REF).decode().strip(),legacy)
        self.assertEqual(self.current(),result['commit'])

    def test_bootstrap_refresh_exact_pin_and_yaml_only_history(self):
        first = self.publish()
        pin = first['commit']
        self.assertEqual(self.current(),pin)
        self.assertEqual(delivery.read_prior(self.remote,pin,self.limits),self.tree)
        self.assertEqual(git(self.remote,'rev-list','--parents','-n','1',pin).decode().split(),[pin])
        self.refresh(pin)
        expected = self.tree
        second = self.publish()
        self.assertEqual(second['parent'],pin)
        self.assertEqual(self.current(),second['commit'])
        self.assertEqual(delivery.read_prior(self.remote,second['commit'],self.limits),expected)
        self.assertEqual(git(self.remote,'rev-list','--parents','-n','1',second['commit']).decode().split(),
                         [second['commit'],pin])
        names = git(self.remote,'ls-tree','-r','--name-only',second['commit']).decode().splitlines()
        self.assertEqual(set(names),set(expected))
        self.assertNotIn('receipt.json',names)
        with patch('yaml_delivery.acquire') as artifact:
            with self.assertRaisesRegex(ValueError,'publication_parent_changed'):
                self.publish()
            artifact.assert_not_called()

    def test_preflight_and_existing_output_refuse_before_remote(self):
        self.context['yaml_policy_sha256'] = 'a'*64
        with patch('delivery.remote_git') as remote, self.assertRaises(ValueError):
            self.publish()
        remote.assert_not_called()
        self.context['yaml_policy_sha256'] = hashlib.sha256(POLICY).hexdigest()
        # The refused preflight did not create its destination.
        self.assertFalse((Path(self.directory.name)/'publication-1').exists())
        target = Path(self.directory.name)/'publication-2'
        target.mkdir()
        (target/'keep').write_bytes(b'keep')
        with patch('delivery.remote_git') as remote, self.assertRaises(FileExistsError):
            self.publish()
        remote.assert_not_called()
        self.assertEqual((target/'keep').read_bytes(),b'keep')

    def test_absence_stale_pin_and_fetch_race_refuse(self):
        with self.assertRaises(ValueError):
            delivery.fetch_prior(dict(self.context,previous_publication='a'*40),
                self.raw,REV,POLICY,b'fixture-token',Path(self.directory.name)/'missing')
        pin = self.publish()['commit']
        with self.assertRaises(ValueError):
            delivery.fetch_prior(self.context,self.raw,REV,POLICY,b'fixture-token',
                                 Path(self.directory.name)/'not-absent')
        self.context['previous_publication'] = pin
        original = shared.remote_git
        competitor = self.other_commit(pin)
        def raced(repo,token,*args):
            if args[0] == 'fetch':
                git(self.remote,'update-ref',REMOTE_REF,competitor,pin)
            return original(repo,token,*args)
        with patch('delivery.remote_git',side_effect=raced), self.assertRaisesRegex(
                ValueError,'publication_parent_changed'):
            delivery.fetch_prior(self.context,self.raw,REV,POLICY,b'fixture-token',
                                 Path(self.directory.name)/'fetch-race')
        self.assertEqual(self.current(),competitor)

    def race_push(self, parent, replacement):
        original = shared.remote_git
        def raced(repo,token,*args):
            if args[0] == 'push':
                self.assertIn(f'--force-with-lease={REMOTE_REF}:{parent or ""}',args)
                if replacement:
                    git(self.remote,'update-ref',REMOTE_REF,replacement,parent or '0'*40)
                else:
                    git(self.remote,'update-ref','-d',REMOTE_REF,parent)
            return original(repo,token,*args)
        with patch('delivery.remote_git',side_effect=raced), self.assertRaises(ValueError):
            self.publish()
        self.assertEqual(self.current(),replacement or '')

    def test_bootstrap_racing_creation_refuses(self):
        self.race_push(None,self.other_commit())

    def test_refresh_racing_descendant_refuses(self):
        parent = self.publish()['commit']
        self.refresh(parent)
        self.race_push(parent,self.other_commit(parent))

    def test_refresh_racing_deletion_refuses(self):
        parent = self.publish()['commit']
        self.refresh(parent)
        self.race_push(parent,None)

    def test_refresh_racing_backward_reset_refuses(self):
        first = self.publish()['commit']
        self.refresh(first)
        second = self.publish()['commit']
        self.refresh(second)
        self.race_push(second,first)

    def raw_commit(self, files, mode='100644'):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            index = Path(directory)/'index'
            git(self.remote,'read-tree','--empty',index=index)
            for path,body in files.items():
                oid = git(self.remote,'hash-object','-w','--stdin',data=body).decode().strip()
                git(self.remote,'update-index','--add','--cacheinfo',mode,oid,path,index=index)
            tree = git(self.remote,'write-tree',index=index).decode().strip()
        return git(self.remote,'commit-tree',tree,data=b'Fixture\n').decode().strip()

    def test_prior_format_layout_modes_and_limits_refuse(self):
        for files,mode in (({'index.json':b'{}'},'100644'),
                           (dict(self.tree,**{'receipt.json':b'{}'}),'100644'),
                           (self.tree,'100755'),(self.tree,'120000'),
                           (dict(self.tree,**{'apps.yaml':b'bad'}),'100644')):
            pin = self.raw_commit(files,mode)
            with self.subTest(mode=mode),self.assertRaises(ValueError):
                delivery.read_prior(self.remote,pin,self.limits)
        pin = self.raw_commit(self.tree)
        for key in ('max_files','max_file_bytes','max_tree_bytes'):
            with self.subTest(key=key),self.assertRaises(ValueError):
                delivery.read_prior(self.remote,pin,dict(self.limits,**{key:1}))
        for pin in (None,'HEAD','refs/heads/catalog','a'*39):
            with self.assertRaises(ValueError):
                delivery.read_prior(self.remote,pin,self.limits)

    def test_bad_artifact_and_history_limit_do_not_push(self):
        self.receipt = b'{}'
        self.zip = zipped([('receipt.json',self.receipt),
                           *[('candidate/'+p,b) for p,b in self.tree.items()]])
        self.digest = hashlib.sha256(self.zip).hexdigest()
        with self.assertRaises((ValueError,KeyError)):
            self.publish()
        self.assertEqual(self.current(),'')
        self.capture()
        with patch('publication.HISTORY_CAP',1),self.assertRaisesRegex(
                ValueError,'yaml_publication_history_bound'):
            self.publish()
        self.assertEqual(self.current(),'')


if __name__ == '__main__':
    unittest.main()
