"""Adversarial policy differences and selected-record acceptance, offline only."""
import copy
from datetime import datetime, timedelta, timezone
import unittest

from reference_policies import matches, select_cohort
from reference_selection import StaleSelection

NOW = datetime(2026, 11, 4, 12, tzinfo=timezone.utc)
PIN = 'b'*40


def release(tag='v1', published='2026-11-01T00:00:00Z', name='nvim-x86_64.AppImage', url=None):
    return dict(tag=tag, published_at=published, prerelease=False,
        assets={'1': dict(name=name, url=url or 'https://github.com/neovim/neovim/releases/download/'+tag+'/'+name)})


class Cohort(unittest.TestCase):
    def setUp(self):
        self.repository = dict(repository_id=1, observed_at='2026-11-04T12:00:00Z',
                               releases={'1': release()})

    def choose(self, recipe='x86_64/nvim', **kw):
        return select_cohort(recipe, self.repository, PIN, now=NOW, **kw)

    def test_published_order_replaces_page_order_and_falls_through(self):
        self.repository['releases'] = {'1': release(published='2026-11-03T00:00:00Z'),
            '2': release(tag='v2', published='2026-11-02T00:00:00Z'),
            '3': release(tag='v3', published='2026-11-04T00:00:00Z', name='nvim-arm64.AppImage')}
        self.assertEqual(self.choose()['release_id'], '1')
        # Dict/page order does not select v2; newest release without this arch falls through.
        self.repository['releases'] = dict(reversed(list(self.repository['releases'].items())))
        self.assertEqual(self.choose()['release_id'], '1')

    def test_tag_and_url_channels_are_both_explicit(self):
        r = release(tag='nightly')
        self.assertTrue(matches('x86_64/nvim-nightly', r, r['assets']['1']))
        self.assertFalse(matches('x86_64/nvim', r, r['assets']['1']))
        r['tag'] = 'nightly-experiment'  # Legacy substring would admit this URL.
        self.assertFalse(matches('x86_64/nvim-nightly', r, r['assets']['1']))
        r = release(tag='v2-rc1'); r['prerelease'] = True
        self.assertTrue(matches('x86_64/nvim', r, r['assets']['1']))
        r = release(tag='v2', url='https://github.com/neovim/neovim/releases/download/NIGHTLY/nvim.AppImage')
        self.assertTrue(matches('x86_64/nvim', r, r['assets']['1']))  # Case-sensitive legacy exclusion.
        self.assertFalse(matches('x86_64/nvim-nightly', r, r['assets']['1']))

    def test_url_matching_not_asset_name_and_arch_exclusions(self):
        r = release(name='misleading-arm64.zsync', url='https://github.com/neovim/neovim/releases/download/v1/nvim-x86_64.AppImage')
        self.assertTrue(matches('x86_64/nvim', r, r['assets']['1']))
        self.assertFalse(matches('aarch64/nvim', r, r['assets']['1']))
        r = release(name='nvim-arm64.AppImage')
        self.assertTrue(matches('aarch64/nvim', r, r['assets']['1']))
        # Like the legacy recipe, negative arch rules admit an unlabelled asset.
        r = release(name='nvim.AppImage')
        self.assertTrue(matches('aarch64/nvim', r, r['assets']['1']))
        self.assertTrue(matches('x86_64/nvim', r, r['assets']['1']))

    def test_obsidian_case_prerelease_and_broad_url_suffix(self):
        r = release(name='Obsidian.APPIMAGE'); r['prerelease'] = True
        self.assertTrue(matches('x86_64/obsidian', r, r['assets']['1']))
        r['assets']['1']['url'] += '.zsync'
        self.assertFalse(matches('x86_64/obsidian', r, r['assets']['1']))
        r['assets']['1']['url'] = 'https://example.org/odd-mage'
        self.assertTrue(matches('x86_64/obsidian', r, r['assets']['1']))

    def test_ties_use_numeric_release_id_then_name_and_numeric_asset_id(self):
        self.repository['releases']['9007199254740993'] = copy.deepcopy(self.repository['releases']['1'])
        r = self.repository['releases']['9007199254740993']
        r['assets'] = {'9007199254740993': dict(name='a', url=r['assets']['1']['url']),
                       '9007199254740992': dict(name='a', url=r['assets']['1']['url'])}
        selected = self.choose()
        self.assertEqual(selected['release_id'], '9007199254740993')
        self.assertEqual(selected['asset_id'], '9007199254740992')

    def test_selected_observation_waiver_no_fresh_substitution(self):
        self.repository['releases']['1']['observed_at'] = '2026-11-01T00:00:00Z'
        self.repository['releases']['2'] = release(published='2026-10-30T00:00:00Z')
        with self.assertRaises(StaleSelection) as caught:
            self.choose()
        acceptance = caught.exception.acceptance
        self.assertTrue(self.choose(accept_stale=acceptance)['stale'])
        with self.assertRaises(StaleSelection):
            self.choose(accept_stale=dict(acceptance, asset_id='2'))
        self.repository['releases']['1']['observed_at'] = '2026-11-02T12:00:00Z'
        self.assertFalse(self.choose()['stale'])
        self.repository['releases']['1']['observed_at'] = '2026-11-04T12:00:01Z'
        with self.assertRaisesRegex(ValueError, 'future_release_observation'):
            self.choose()

    def test_unknown_and_absent_match_refuse(self):
        with self.assertRaisesRegex(ValueError, 'unknown_cohort_recipe'):
            self.choose('x86_64/other')
        self.repository['releases'] = {}
        with self.assertRaisesRegex(ValueError, 'no_matching_asset'):
            self.choose()


if __name__ == '__main__':
    unittest.main()
