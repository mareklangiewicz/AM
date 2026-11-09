"""Actual shell reads of saved live file observations, without network or payloads."""
import json
import os
import shutil
import subprocess
import tarfile
import unittest

import contracts as c
from publication import git,publish_tree
import test_git_consumers as integration


class FileConsumers(unittest.TestCase):
    script=integration.GitConsumers.script
    env=integration.GitConsumers.env
    calls=integration.GitConsumers.calls
    read=integration.GitConsumers.read

    def setUp(self):
        integration.GitConsumers.setUp(self)
        archive=c.ROOT/'docs/track/catalog-system/git-file-acquisition-16.tar.gz'
        self.documents={}
        with tarfile.open(archive) as saved:
            replay=json.load(saved.extractfile('replay.json'));revision=replay['reviewed_source_revision']
            for app,rid in [('anything-llm',649170660),('cursor',903233225)]:
                raw=saved.extractfile(str(rid)+'.yaml').read(c.FILE_CAP+1)
                self.documents[app]=c.decode(raw)
        apps={app:'repositories/'+app+'.yaml' for app in self.documents}
        tree={apps[app]:c.encode(doc) for app,doc in self.documents.items()}
        tree['apps.yaml']=c.encode(dict(c.header('apps',revision),apps=apps))
        tree['catalog.yaml']=c.encode(dict(c.header('catalog',revision),
            inputs={k:revision for k in ('source','policy','recipes','rules','schemas')},
            producer=dict(id=1,attempt=1),retention='32-plus-stable-exact-tag-v1'))
        tree.update(c.partition_provenance(apps,{app:{'x86_64':dict(repository_id=doc['repository_id'],
            availability='unknown',classification='unknown')} for app,doc in self.documents.items()},revision))
        c.validate_tree(tree)
        self.repo=self.path/'remote.git';self.repo.mkdir();git(self.repo,'init','--bare','--quiet','--template=')
        self.pin=publish_tree(self.repo,tree,None)
        self.clock=max(doc['collected_at'] for doc in self.documents.values())

    def test_exact_live_files_through_shell_under_all_three_awks(self):
        for awk in ['mawk','gawk','busybox']:
            executable=self.bin/'awk';executable.unlink(missing_ok=True)
            executable.symlink_to(shutil.which(awk))
            for app,recipe in [('cursor','cursor'),('anything-llm','anything-llm.select-2')]:
                with self.subTest(awk=awk,app=app):
                    ref=next(r for r in self.documents[app]['git_refs'].values() if 'files' in r)
                    expected=next(iter(ref['files'].values()))['content']
                    result=self.read(recipe,'--git-file')
                    self.assertEqual(result.returncode,0,result.stderr)
                    self.assertEqual(result.stdout,expected)
        self.assertFalse((self.path/'downloads').exists())


if __name__=='__main__':unittest.main()
