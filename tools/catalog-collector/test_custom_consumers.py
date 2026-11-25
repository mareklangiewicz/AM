"""Real shell selection keeps metadata identities and validates version-sort winners."""
import json
import unittest

import documents
import fixture_catalog
import test_git_consumers as integration

AT=integration.AT


class CustomConsumers(unittest.TestCase):
    setUp=integration.GitConsumers.setUp
    script=integration.GitConsumers.script
    env=integration.GitConsumers.env
    calls=integration.GitConsumers.calls
    read=integration.GitConsumers.read

    def prepare(self,app,releases,policy_name=None):
        """releases: records as bounded.normalize returns them."""
        policies=json.loads((integration.ROOT/'tools/catalog-collector/recipe-url-policies.json').read_text())
        policy=next(r for r in policies if r['recipe']==(policy_name or 'x86_64/'+app))
        rid=policy['repository_id']
        doc=documents.repository(None,dict(received_at=AT,releases=releases,history_complete=True),
                                 repository_id=rid,repository=policy['repository'])
        tree={'catalog/repositories/'+app+'.yaml':documents.encode('repository',doc),
              'catalog/apps.yaml':documents.encode('apps',dict(apps={policy['catalog_app']:dict(
                  repository='repositories/'+app+'.yaml',x86_64='declaration')}))}
        self.repo=fixture_catalog.bare(self.path/'remote.git')
        fixture_catalog.publish(self.repo,tree);self.clock=AT

    def release(self,tag='v1',published=AT,preview=False):
        return dict(tag=tag,title=tag,url='https://github.com/example/app/releases/tag/'+tag,
                    published_at=published,prerelease=preview,assets={})

    def test_release_only_metadata_does_not_require_assets(self):
        old=self.release('v1','2026-11-08T00:00:00Z');preview=self.release('v2',preview=True)
        self.prepare('code',{'1':old,'2':preview})
        result=self.read('code','--tag');self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout,'v1\n')

    def test_release_url_is_a_scalar_output(self):
        r=self.release('v1');self.prepare('doublecmd-gtk',{'1':r})
        result=self.read('doublecmd-gtk','--release-url')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout,r['url']+'\n')

    def test_a_rolling_release_recreated_per_build_is_versioned_by_its_publication_time(self):
        # Vita3K recreates its continuous release per build (a new release ID; see the v3 history of
        # repositories/vita3k.yaml), so published_at changes whenever the build does.
        r=self.release('continuous','2026-11-09T11:50:00Z')
        self.prepare('vita3k',{'1':r});result=self.read('vita3k','--published-at')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout,r['published_at']+'\n')

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
        self.clock='2026-11-24T12:00:01Z'  # 15 days after it was seen: the same winner, warned once
        result=self.read('python','--version-url')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout,highest['assets']['1']['url']+'\n')
        self.assertEqual(result.stderr.count('last seen 15 days ago'),1,result.stderr)

    def test_source_archive_is_release_fact_without_synthetic_asset_identity(self):
        r=self.release();r['source_tar_url']='https://api.github.com/repos/b3nj5m1n/xdg-ninja/tarball/v1'
        self.prepare('xdg-ninja',{'1':r})
        result=self.read('xdg-ninja','--source-tar-url')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout,r['source_tar_url']+'\n')

    def test_a_chosen_url_seen_over_two_weeks_ago_warns_and_one_seen_less_does_not(self):
        r=self.release()
        url='https://example.org/wine-x86_64.AppImage'
        r['assets']={'1':dict(name='wine-x86_64.AppImage',url=url,size=1,content_type='application/octet-stream')}
        self.prepare('wine',{'1':r})
        for clock,warnings in [('2026-11-22T12:00:00Z',0),('2026-11-24T12:00:01Z',1)]:  # 13 and 15 days
            with self.subTest(clock=clock):
                self.clock=clock
                result=self.read('wine','--url','--selected-url',url)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertEqual(result.stdout,url+'\n')
                self.assertEqual(result.stderr.count('last seen 15 days ago'),warnings,result.stderr)


if __name__=='__main__':unittest.main()
