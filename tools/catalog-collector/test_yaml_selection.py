"""Selection is a client decision; collection/publication cannot refresh old facts."""
import copy
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest

from test_yaml_reader import repository
from yaml_publication import git,publish_local
from reference_selection import select,select_local,StaleSelection

PIN = 'a'*40
NOW = datetime(2026,11,4,13,tzinfo=timezone.utc)
RULE = dict(release_order='published_desc',stable_only=False,asset_suffix='.AppImage',
            include=['x86_64'],exclude=['.zsync'],ignore_case=False)


class Selection(unittest.TestCase):
    def setUp(self):
        self.repo = repository()
        self.repo['observed_at'] = '2026-11-04T12:00:00Z'
        self.repo['last_success']['completed_at'] = '2026-11-04T12:00:00Z'
        release = self.repo['releases']['456']
        release.pop('observed_at',None)
        release['published_at'] = '2026-11-01T00:00:00Z'
        release['prerelease'] = False
        release['assets']['789'].update(name='app-x86_64.AppImage',url='https://example.com/stable')
        self.apps = {'app':self.repo['repository_id']}
        self.repositories = {str(self.repo['repository_id']):self.repo}

    def choose(self,rule=None,**kwargs):
        return select(self.apps,self.repositories,'app',PIN,rule or RULE,now=NOW,**kwargs)

    def test_selects_structured_asset_and_preserves_digest_optionality(self):
        selected = self.choose()
        self.assertEqual((selected['release_id'],selected['asset_id'],selected['asset']['url']),
                         ('456','789','https://example.com/stable'))
        self.assertFalse(selected['stale'])
        self.repo['releases']['456']['assets']['789'].pop('digest',None)
        self.assertNotIn('digest',self.choose()['asset'])

    def test_stable_and_fallthrough_are_explicit_client_rules(self):
        newer = copy.deepcopy(self.repo['releases']['456'])
        newer.update(published_at='2026-11-02T00:00:00Z',prerelease=True)
        newer['assets']['789']['url'] = 'https://example.com/preview'
        self.repo['releases']['457'] = newer
        self.assertEqual(self.choose()['release_id'],'457')
        self.assertEqual(self.choose(dict(RULE,stable_only=True))['release_id'],'456')
        newer['assets']['789']['name'] = 'app-arm64.AppImage'
        self.assertEqual(self.choose()['release_id'],'456')

    def test_name_order_and_release_tie_break_are_deterministic(self):
        assets = self.repo['releases']['456']['assets']
        assets['790'] = dict(assets['789'],name='aaa-x86_64.AppImage')
        self.assertEqual(self.choose()['asset_id'],'790')
        self.repo['releases']['9007199254740993'] = copy.deepcopy(self.repo['releases']['456'])
        self.assertEqual(self.choose()['release_id'],'9007199254740993')

    def test_stale_selected_record_is_not_rescued_by_recent_collection(self):
        release = self.repo['releases']['456']
        release['observed_at'] = '2026-10-31T00:00:00Z'
        with self.assertRaises(StaleSelection) as caught:
            self.choose()
        acceptance = caught.exception.acceptance
        self.assertTrue(self.choose(accept_stale=acceptance)['stale'])
        for key in acceptance:
            changed = dict(acceptance);changed[key] = 'different'
            with self.subTest(key=key),self.assertRaises(StaleSelection):
                self.choose(accept_stale=changed)
        # Another fresher matching release cannot silently replace the policy's winner.
        older = copy.deepcopy(release);older.pop('observed_at')
        older['published_at'] = '2026-10-01T00:00:00Z'
        self.repo['releases']['455'] = older
        with self.assertRaises(StaleSelection): self.choose()

    def test_freshness_boundary_future_and_failed_collection(self):
        self.repo['observed_at'] = '2026-11-02T13:00:00Z'
        self.assertFalse(self.choose()['stale'])
        self.repo['observed_at'] = '2026-11-02T12:59:59Z'
        with self.assertRaises(StaleSelection): self.choose()
        self.repo['observed_at'] = '2026-11-04T13:00:01Z'
        with self.assertRaisesRegex(ValueError,'future_release_observation'): self.choose()
        self.repo['observed_at'] = '2026-11-04T12:00:00Z'
        self.repo['collection'].update(status='failed',reason='transport')
        self.assertFalse(self.choose()['stale'])

    def test_exact_pinned_snapshot_survives_new_tip(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            git(repo,'init','--bare','--quiet','--template=')
            pin = publish_local(repo,self.apps,self.repositories,schema=self.repo['schema'],
                                max_file_bytes=2097152,expected_parent=None)
            changed = copy.deepcopy(self.repositories)
            changed[str(self.repo['repository_id'])]['releases']['456']['assets']['789']['url'] = 'https://example.com/new'
            tip = publish_local(repo,self.apps,changed,schema=self.repo['schema'],
                                max_file_bytes=2097152,expected_parent=pin)
            self.assertNotEqual(pin,tip)
            selected = select_local(repo,pin,'app',RULE,now=NOW)
            self.assertEqual(selected['asset']['url'],'https://example.com/stable')
            self.assertEqual(selected['commit'],pin)

    def test_policy_refuses_implicit_latest_and_missing_app_or_asset(self):
        for rule in (dict(RULE,release_order='github_latest'),dict(RULE,stable_only=1),
                     dict(RULE,include='x86_64')):
            with self.assertRaises(ValueError):self.choose(rule)
        with self.assertRaisesRegex(ValueError,'unknown_app'):
            select(self.apps,self.repositories,'missing',PIN,RULE,now=NOW)
        with self.assertRaisesRegex(ValueError,'no_matching_asset'):
            self.choose(dict(RULE,include=['not-present']))


if __name__ == '__main__':unittest.main()
