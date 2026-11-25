"""Actual shell reads of saved live file observations, without network or payloads."""
from pathlib import Path
import shutil
import unittest

import yaml

import documents
import fixture_catalog
from publication import git
import test_git_consumers as integration

SAVED=Path(__file__).resolve().parent/'test-catalog'


class FileConsumers(unittest.TestCase):
    script=integration.GitConsumers.script
    env=integration.GitConsumers.env
    calls=integration.GitConsumers.calls
    read=integration.GitConsumers.read

    def setUp(self):
        integration.GitConsumers.setUp(self)
        self.documents={app:yaml.safe_load((SAVED/(app+'.yaml')).read_text()) for app in ('anything-llm','cursor')}
        tree={'catalog/repositories/'+app+'.yaml':(SAVED/(app+'.yaml')).read_bytes() for app in self.documents}
        tree['catalog/apps.yaml']=documents.encode('apps',dict(apps={app:dict(repository='repositories/'+app+'.yaml',x86_64='declaration')
                                                                    for app in self.documents}))
        self.repo=self.path/'remote.git';self.repo.mkdir();git(self.repo,'init','--bare','--quiet','--template=')
        fixture_catalog.publish(self.repo,tree)
        self.clock=max(doc['observed_at'] for doc in self.documents.values())

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
