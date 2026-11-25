"""seed.py on v3 fixtures: what must survive the conversion does, and both readers accept it.

Run once with the seed (python3 -B -m unittest test_seed, from this directory),
while tools/catalog-contract/fixtures/ (v3) still exists; never maintained.
"""
from pathlib import Path
import subprocess
import unittest

import yaml

import seed

ROOT = seed.ROOT
FIXTURES = ROOT/'tools/catalog-contract/fixtures'


def v3(name):
    return yaml.safe_load((FIXTURES/name).read_text())


def accepted(document):
    raw = seed.documents.encode('repository', document)
    awk = subprocess.run(['awk', '-f', str(ROOT/'modules/catalog-tables.am'), '-f', str(ROOT/'modules/catalog-parser.am')],
                         input=raw, capture_output=True)
    js = ("import {parseDocument} from './tools/catalog-contract/parse.mjs';let s='';for await(const b of process.stdin)s+=b;"
          "try{parseDocument(s)}catch(e){console.error(e.message);process.exitCode=2}")
    node = subprocess.run(['node', '--input-type=module', '-e', js], input=raw, capture_output=True, cwd=ROOT)
    return awk.returncode == 0 and node.returncode == 0


class Seed(unittest.TestCase):
    def test_every_v3_repository_fixture_converts_to_a_valid_document(self):
        for path in sorted(FIXTURES.glob('repository*.yaml')):
            with self.subTest(fixture=path.name):
                self.assertTrue(accepted(seed.convert(v3(path.name))))

    def test_facts_times_and_urls_survive(self):
        old = v3('repository.yaml')
        new = seed.convert(old)
        self.assertEqual((new['repository_id'], new['repository'], new['observed_at']),
                         (old['repository_id'], old['repository'], old['observed_at']))
        self.assertEqual(new['history_complete'], old['scope']['history_complete'])
        for rid, release in new['releases'].items():
            before = seed.expanded_release(old['releases'][rid])
            self.assertEqual(release['tag'], before['tag'])
            self.assertEqual(release.get('observed_at'), old['releases'][rid].get('observed_at'))
            for aid, asset in release['assets'].items():
                derived = f"https://github.com/{old['repository']}/releases/download/{release['tag']}/{asset['name']}"
                self.assertEqual(asset.get('url', derived), before['assets'][aid]['url'])

    def test_git_refs_are_rekeyed_by_name_and_path(self):
        # release-catalog-v3 8b6d58033 repositories/junest.yaml, plus one tag.
        at = '2026-11-24T21:20:47Z'
        branch, tag = '49c8f7d5c7458baeb01c297edec96d2886bf083c68c65a3df9c2d60de8879582', 'e'*64
        old = dict(v3('repository.yaml'),
                   git_scope=dict(tags=True, tags_history_complete=True, branches={branch: 'refs/heads/master'}),
                   git_refs={branch: dict(name='refs/heads/master', commit='0037f96e159a143e37db978e537e3fb362ba3a5b',
                                          observed_at=at, files={'7b60b8e3': dict(path='VERSION', observed_at=at,
                                              blob='ef137167c8c107149ca2783787e81cd3d4e71e14', content='7.4.10\n')}),
                             tag: dict(name='refs/tags/v7.4.10', commit='a'*40, observed_at=at, position=0)})
        new = seed.convert(old)
        self.assertEqual(new['git_scope'], dict(tags=True, tags_history_complete=True))
        self.assertEqual(new['git_refs'], {
            'refs/heads/master': dict(commit='0037f96e159a143e37db978e537e3fb362ba3a5b',
                                      files={'VERSION': dict(blob='ef137167c8c107149ca2783787e81cd3d4e71e14', content='7.4.10\n')}),
            'refs/tags/v7.4.10': dict(commit='a'*40, position=0)})
        self.assertTrue(accepted(new))

    def test_failures_stay_and_twins_are_left_out(self):
        old = v3('repository.yaml')
        failed = dict(old, failed_at='2099-01-01T00:00:00Z', failed_with='transport')
        self.assertEqual(seed.convert(failed)['failed_with'], 'transport')
        never = {k: old[k] for k in ('format', 'schema', 'kind', 'repository_id', 'repository')}
        never.update(failed_at='2026-11-01T00:00:00Z', failed_with='not_found', releases={})
        self.assertEqual(seed.convert(never), dict(repository_id=old['repository_id'], repository=old['repository'],
                                                   releases={}, failed_at='2026-11-01T00:00:00Z', failed_with='not_found'))
        self.assertIsNone(seed.convert(dict(never, failed_with='same_tag_conflict')))


if __name__ == '__main__':
    unittest.main()
