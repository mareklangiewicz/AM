"""Release facts as GitHub lists them: twins under one tag, recreated tags and proven-gone
releases (catalog-simplification ticket 18, decided in ticket 07)."""
import os
import subprocess
import tempfile
import unittest

from bounded import normalize
import contracts as c
from fixture_v3 import repository

PIN = 'a'*40
OLD = '2026-11-03T01:00:00Z'
NEW = '2026-11-08T01:00:00Z'


def github_release(rid, tag, published_at, *assets, prerelease=False):
    """One release as GitHub's releases API returns it, with (asset id, name) pairs."""
    return dict(id=rid, tag_name=tag, name=tag, draft=False, prerelease=prerelease,
                html_url=f'https://github.com/example/app/releases/tag/{tag}',
                created_at=published_at, published_at=published_at,
                assets=[dict(id=aid, name=name, size=1, content_type='application/octet-stream',
                             browser_download_url=f'https://github.com/example/app/releases/download/{tag}/{name}')
                        for aid, name in assets])


def recollect(previous, releases, received_at, *, complete):
    """The next successful collection of the same repository, from GitHub's response list."""
    acquired = dict(received_at=received_at, releases=normalize(releases, 100), history_complete=complete)
    return c.source(previous, acquired, rid='123', repository='example/app', revision=PIN)


class Twins(unittest.TestCase):
    def test_two_releases_sharing_a_tag_are_both_recorded(self):
        # The shape of all 14 same_tag_conflict sources (ticket 07): two IDs created in the
        # same second under one tag, the Linux build on one twin and the rest on the other.
        twins = [github_release(397747229, 'v2.1.8', '2026-09-27T17:42:53Z', (1, 'app-setup.exe')),
                 github_release(397747228, 'v2.1.8', '2026-09-27T17:42:53Z', (2, 'app.AppImage'))]
        doc = repository('123', 'example/app', twins, NEW, PIN)
        self.assertEqual(sorted(doc['releases']), ['397747228', '397747229'])
        self.assertEqual({r['tag'] for r in doc['releases'].values()}, {'v2.1.8'})


class RecreatedTags(unittest.TestCase):
    def test_a_new_release_id_under_an_old_tag_does_not_replace_the_old_one(self):
        before = repository('123', 'example/app',
                            [github_release(100, 'nightly', '2026-11-01T00:00:00Z', (1, 'a.AppImage'))],
                            OLD, PIN, complete=False)
        after = recollect(before, [github_release(200, 'nightly', '2026-11-07T00:00:00Z', (2, 'b.AppImage'))],
                          NEW, complete=False)
        self.assertEqual(sorted(after['releases']), ['100', '200'])
        self.assertEqual(after['releases']['100']['observed_at'], OLD)



class ProvenGone(unittest.TestCase):
    def setUp(self):
        self.before = repository('123', 'example/app', [
            github_release(300, 'v3', '2026-11-02T00:00:00Z', (3, 'c.AppImage')),
            github_release(200, 'v2', '2026-11-01T00:00:00Z', (2, 'b.AppImage')),
            github_release(100, 'v1', '2026-10-31T00:00:00Z', (1, 'a.AppImage'))], OLD, PIN, complete=False)

    def test_a_release_missing_from_a_complete_history_is_removed(self):
        after = recollect(self.before, [github_release(300, 'v3', '2026-11-02T00:00:00Z', (3, 'c.AppImage'))],
                          NEW, complete=True)
        self.assertEqual(sorted(after['releases']), ['300'])

    def test_a_release_missing_between_returned_ones_is_not_proof_on_a_partial_page(self):
        # GitHub's list is not strictly newest-first by any timestamp (ticket 18 comments), so
        # a returned older release proves nothing about a missing newer one.
        after = recollect(self.before, [github_release(300, 'v3', '2026-11-02T00:00:00Z', (3, 'c.AppImage')),
                                        github_release(100, 'v1', '2026-10-31T00:00:00Z', (1, 'a.AppImage'))],
                          NEW, complete=False)
        self.assertEqual(sorted(after['releases']), ['100', '200', '300'])
        self.assertEqual(after['releases']['200']['observed_at'], OLD)

    def test_a_release_the_fetch_did_not_reach_is_kept_with_its_last_seen_time(self):
        after = recollect(self.before, [github_release(300, 'v3', '2026-11-02T00:00:00Z', (3, 'c.AppImage'))],
                          NEW, complete=False)
        self.assertEqual(sorted(after['releases']), ['100', '200', '300'])
        self.assertEqual({rid: r.get('observed_at') for rid, r in after['releases'].items()},
                         {'100': OLD, '200': OLD, '300': None})



class HostSelection(unittest.TestCase):
    def test_the_host_installs_from_whichever_twin_holds_the_appimage(self):
        # kachakaran6/beacon's newest tag on November 24, 2026 (GitHub API): the Windows build
        # on one twin, the Linux build on the other.
        twins = [github_release(397747229, 'v2.1.8', '2026-09-27T17:42:53Z',
                                (593431905, 'Beacon-2.1.8-portable.exe'), (593431906, 'Beacon-Setup-2.1.8.exe'),
                                (593431968, 'latest.yml')),
                 github_release(397747228, 'v2.1.8', '2026-09-27T17:42:53Z',
                                (593434108, 'Beacon-2.1.8.AppImage'), (593436508, 'Beacon-2.1.8.deb'),
                                (593431904, 'Beacon-Setup-2.1.8.exe.blockmap'), (593436630, 'latest-linux.yml'))]
        doc = repository('1380381406', 'kachakaran6/beacon', twins, NEW, PIN)
        with tempfile.NamedTemporaryFile() as f:
            f.write(c.encode(doc)); f.flush()
            facts = subprocess.run(['sh', str(c.ROOT/'modules/catalog-contract-reader.am'), 'asset_facts', f.name],
                                   capture_output=True, text=True)
        self.assertEqual(facts.returncode, 0, facts.stderr)
        selected = subprocess.run(['awk', '-f', str(c.ROOT/'modules/catalog-yaml-policy.am')], input=facts.stdout,
                                  text=True, capture_output=True,
                                  env=dict(os.environ, LC_ALL='C', AM_YAML_RECIPE='x86_64/beacon',
                                           AM_YAML_REPOSITORY='1380381406', AM_YAML_NOW=NEW))
        self.assertEqual(selected.returncode, 0, selected.stderr)
        self.assertIn('Beacon-2.1.8.AppImage', selected.stdout)


if __name__ == '__main__':
    unittest.main()
