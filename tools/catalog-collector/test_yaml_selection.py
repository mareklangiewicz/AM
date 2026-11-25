"""Selection is a client decision; collection/publication cannot refresh old facts."""
import copy
from datetime import datetime, timezone
import unittest

from reference_selection import select


def sample_release():
    """One normalized release fact with awkward text, as normalize returns it."""
    return dict(tag='v2.0.0', title='Quotes " and \\; caf\u00e9 \u4e2d\u6587 \U0001f427\n\r\t\n',
                url='https://github.com/example/app/releases/tag/v2.0.0',
                published_at='2026-11-02T12:00:00Z', prerelease=False,
                assets={'789': dict(name="John's app #1.AppImage",
                                    url='https://github.com/example/app/releases/download/v2.0.0/app?x=a:b#part',
                                    size=0, content_type='')})


NOW = datetime(2026,11,4,13,tzinfo=timezone.utc)
RULE = dict(release_order='published_desc',stable_only=False,asset_suffix='.AppImage',
            include=['x86_64'],exclude=['.zsync'],ignore_case=False)


class Selection(unittest.TestCase):
    def setUp(self):
        self.repo = dict(repository_id=123, repository='example/app',
                         observed_at='2026-11-04T12:00:00Z', releases={'456':sample_release()})
        release = self.repo['releases']['456']
        release['published_at'] = '2026-11-01T00:00:00Z'
        release['prerelease'] = False
        release['assets']['789'].update(name='app-x86_64.AppImage',url='https://example.com/stable')
        self.apps = {'app':self.repo['repository_id']}
        self.repositories = {str(self.repo['repository_id']):self.repo}

    def choose(self,rule=None,**kwargs):
        return select(self.apps,self.repositories,'app',rule or RULE,now=NOW,**kwargs)

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

    def test_an_old_selected_record_stays_the_winner_and_is_marked_stale(self):
        release = self.repo['releases']['456']
        release['observed_at'] = '2026-10-20T00:00:00Z'
        self.assertTrue(self.choose()['stale'])
        # Another fresher matching release cannot silently replace the policy's winner.
        older = copy.deepcopy(release);older.pop('observed_at')
        older['published_at'] = '2026-10-01T00:00:00Z'
        self.repo['releases']['455'] = older
        selected = self.choose()
        self.assertEqual(selected['release_id'],'456');self.assertTrue(selected['stale'])

    def test_freshness_boundary_and_future_observation(self):
        self.repo['observed_at'] = '2026-10-21T13:00:00Z'  # exactly 14 days before NOW
        self.assertFalse(self.choose()['stale'])
        self.repo['observed_at'] = '2026-10-21T12:59:59Z'
        self.assertTrue(self.choose()['stale'])
        self.repo['observed_at'] = '2026-11-04T13:00:01Z'
        with self.assertRaisesRegex(ValueError,'future_release_observation'): self.choose()

    def test_policy_refuses_implicit_latest_and_missing_app_or_asset(self):
        for rule in (dict(RULE,release_order='github_latest'),dict(RULE,stable_only=1),
                     dict(RULE,include='x86_64')):
            with self.assertRaises(ValueError):self.choose(rule)
        with self.assertRaisesRegex(ValueError,'unknown_app'):
            select(self.apps,self.repositories,'missing',RULE,now=NOW)
        with self.assertRaisesRegex(ValueError,'no_matching_asset'):
            self.choose(dict(RULE,include=['not-present']))


if __name__ == '__main__':unittest.main()
