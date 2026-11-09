"""Real shell selection keeps metadata identities and validates version-sort winners."""
import json
import subprocess
import unittest

import contracts as c
from publication import git,publish_tree
from test_yaml_reader import repository
import test_git_consumers as integration

AT=integration.AT


class CustomConsumers(unittest.TestCase):
    setUp=integration.GitConsumers.setUp
    script=integration.GitConsumers.script
    env=integration.GitConsumers.env
    calls=integration.GitConsumers.calls
    read=integration.GitConsumers.read

    def prepare(self,app,releases,policy_name=None):
        policies=json.loads((c.ROOT/'tools/catalog-collector/recipe-url-policies.json').read_text())
        policy=next(r for r in policies if r['recipe']==(policy_name or 'x86_64/'+app))
        rid=policy['repository_id'];revision='a'*40
        doc=c.source(None,dict(received_at=AT,releases=releases,history_complete=True),
                     rid=rid,repository=policy['repository'],revision=revision)
        path='repositories/'+app+'.yaml';apps={policy['catalog_app']:path}
        tree={path:c.encode(doc),'apps.yaml':c.encode(dict(c.header('apps',revision),apps=apps)),
            'catalog.yaml':c.encode(dict(c.header('catalog',revision),
                inputs={k:revision for k in ('source','policy','recipes','rules','schemas')},
                producer=dict(id=1,attempt=1),retention='32-plus-stable-exact-tag-v1'))}
        tree.update(c.partition_provenance(apps,{policy['catalog_app']:{'x86_64':dict(repository_id=rid,
            availability='unknown',classification='unknown')}},revision))
        self.repo=self.path/'remote.git';self.repo.mkdir();git(self.repo,'init','--bare','--quiet','--template=')
        self.pin=publish_tree(self.repo,tree,None);self.clock=AT

    def release(self,tag='v1',published=AT,preview=False):
        r=repository()['releases']['456'];r.pop('observed_at',None)
        r.update(tag=tag,published_at=published,prerelease=preview,assets={})
        r['url']='https://github.com/example/app/releases/tag/'+tag
        return r

    def test_release_only_metadata_does_not_require_assets(self):
        old=self.release('v1','2026-11-08T00:00:00Z');preview=self.release('v2',preview=True)
        self.prepare('code',{'1':old,'2':preview})
        result=self.read('code','--tag');self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout,'v1\n')

    def test_release_url_and_update_time_preserve_distinct_scalar_outputs(self):
        r=self.release('v1');self.prepare('doublecmd-gtk',{'1':r})
        result=self.read('doublecmd-gtk','--release-url')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout,r['url']+'\n')

    def test_mutable_release_update_time_is_observed_metadata(self):
        r=self.release('continuous');r['updated_at']='2026-11-09T11:50:00Z'
        self.prepare('vita3k',{'1':r});result=self.read('vita3k','--updated-at')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout,r['updated_at']+'\n')

    def test_version_sorted_url_then_freshness_checks_the_same_winner(self):
        highest=self.release('v10','2026-11-08T00:00:00Z')
        newer=self.release('v9')
        for r,n in [(highest,10),(newer,9)]:
            r['assets']={'1':dict(name=f'python-{n}-x86_64.AppImage',
                url=f'https://example.org/python-{n}-x86_64.AppImage',size=1,content_type='application/octet-stream')}
        self.prepare('python',{'1':highest,'2':newer})
        result=self.read('python','--version-url')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout,highest['assets']['1']['url']+'\n')
        self.clock='2026-11-12T12:00:00Z'
        result=self.read('python','--version-url')
        self.assertNotEqual(result.returncode,0);self.assertEqual(result.stdout,'')
        self.assertIn('stale',result.stderr)

    def test_source_archive_is_release_fact_without_synthetic_asset_identity(self):
        r=self.release();r['source_tar_url']='https://api.github.com/repos/b3nj5m1n/xdg-ninja/tarball/v1'
        self.prepare('xdg-ninja',{'1':r})
        result=self.read('xdg-ninja','--source-tar-url')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout,r['source_tar_url']+'\n')

    def test_runtime_filter_selects_variant_within_trusted_url_predicates(self):
        r=self.release()
        for n in ['avx','sse']:
            r['assets'][str(len(r['assets'])+1)]=dict(name='mercury-linux-'+n+'.zip',
                url='https://example.org/mercury-linux-'+n+'.zip',size=1,content_type='application/zip')
        self.prepare('mercury',{'1':r})
        result=self.read('mercury','--url','--url-filter','i','sse')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout,'https://example.org/mercury-linux-sse.zip\n')

    def test_source_dispatch_and_variant_filter_agree_for_obs(self):
        r=self.release()
        r['assets']={'1':dict(name='obs-full-x86_64.AppImage',
            url='https://example.org/obs-full-x86_64.AppImage',size=1,content_type='application/octet-stream')}
        self.prepare('obs-studio',{'1':r},policy_name='x86_64/obs-studio.select-2')
        result=self.read('obs-studio','--url','--source-repository','ivan-hc/OBS-Studio-appimage','--url-filter','i','full')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout,r['assets']['1']['url']+'\n')
        result=self.read('obs-studio','--url','--source-repository','unknown/project')
        self.assertNotEqual(result.returncode,0)

    def test_url_menu_lists_old_records_but_chosen_url_must_be_fresh(self):
        r=self.release()
        r['assets']={'1':dict(name='wine-x86_64.AppImage',url='https://example.org/wine-x86_64.AppImage',size=1,content_type='application/octet-stream')}
        self.prepare('wine',{'1':r});self.clock='2026-11-12T12:00:00Z'
        result=self.read('wine','--urls');self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout,r['assets']['1']['url']+'\n')
        result=self.read('wine','--url','--selected-url',r['assets']['1']['url'])
        self.assertNotEqual(result.returncode,0);self.assertEqual(result.stdout,'')
        self.assertIn('stale',result.stderr)


if __name__=='__main__':unittest.main()
