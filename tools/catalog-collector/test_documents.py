"""The collector's catalog documents: what a GitHub read becomes in catalog/.

Worked examples: inputs as the acquisition hands them over (bounded.normalize
release records, git_observations results), expected documents as literal
bytes, every one of which both readers must accept.
"""
import subprocess
import unittest
from pathlib import Path

import documents as d

ROOT = Path(__file__).resolve().parents[2]
NOW = '2026-11-25T10:00:00Z'


def release(tag, published, *, prerelease=False, assets=(), **extra):
    """A record as bounded.normalize returns it, with GitHub's derived URLs."""
    record = dict(tag=tag, title=tag, url=f'https://github.com/example/app/releases/tag/{tag}',
                  created_at=published, published_at=published, updated_at=published, prerelease=prerelease,
                  source_zip_url=f'https://api.github.com/repos/example/app/zipball/{tag}',
                  source_tar_url=f'https://api.github.com/repos/example/app/tarball/{tag}',
                  assets={})
    for aid, name in assets:
        record['assets'][aid] = dict(name=name, url=f'https://github.com/example/app/releases/download/{tag}/{name}',
                                     size=10, content_type='application/octet-stream')
    record.update(extra)
    return record


def readers_accept(raw):
    """Both readers, as test_examples runs them."""
    awk = subprocess.run(['awk', '-f', str(ROOT/'modules/catalog-tables.am'), '-f', str(ROOT/'modules/catalog-parser.am')],
                         input=raw, capture_output=True)
    js = ("import {parseDocument} from './tools/catalog-contract/parse.mjs';let s='';for await(const b of process.stdin)s+=b;"
          "try{parseDocument(s)}catch(e){console.error(e.message);process.exitCode=2}")
    node = subprocess.run(['node', '--input-type=module', '-e', js], input=raw, capture_output=True, cwd=ROOT)
    return (awk.returncode, awk.stderr, node.returncode, node.stderr)


class Repository(unittest.TestCase):
    def assertDocument(self, document, expected):
        raw = d.encode('repository', document)
        self.assertEqual(raw.decode(), expected)
        self.assertEqual(readers_accept(raw), (0, b'', 0, b''))

    def test_first_read_keeps_only_what_differs_from_the_derived_values(self):
        records = {
            '7': release('v1.0', '2026-10-01T00:00:00Z', assets=[('70', 'app-x86_64.AppImage')]),
            '8': release('v1.1', '2026-11-01T00:00:00Z', title='Big release',
                         assets=[('80', 'app.tar.gz'), ('81', 'app setup.exe')]),
        }
        records['8']['assets']['80']['digest'] = 'sha256:'+'ab'*32
        # GitHub percent-encodes the space; a derived URL joins the name as is.
        records['8']['assets']['81']['url'] = 'https://github.com/example/app/releases/download/v1.1/app%20setup.exe'
        acquired = dict(received_at=NOW, releases=records, history_complete=True)
        document = d.repository(None, acquired, repository_id=123, repository='example/app')
        self.assertDocument(document, '''\
$schema: "../../schemas/catalog.schema.yaml#/$defs/repository"
repository_id: 123
repository: "example/app"
observed_at: "2026-11-25T10:00:00Z"
history_complete: true
releases:
  "7":
    tag: "v1.0"
    published_at: "2026-10-01T00:00:00Z"
    prerelease: false
    assets:
      "70":
        name: "app-x86_64.AppImage"
        size: 10
  "8":
    tag: "v1.1"
    title: "Big release"
    published_at: "2026-11-01T00:00:00Z"
    prerelease: false
    assets:
      "80":
        name: "app.tar.gz"
        size: 10
        sha256pre: "abababababababab"
      "81":
        name: "app setup.exe"
        url: "https://github.com/example/app/releases/download/v1.1/app%20setup.exe"
        size: 10
''')


    def test_a_release_this_read_missed_keeps_its_last_seen_time_unless_proven_gone(self):
        earlier = dict(repository_id=123, repository='example/app', observed_at='2026-11-20T00:00:00Z', history_complete=False,
                       releases={'5': dict(tag='v0.9', published_at='2026-09-01T00:00:00Z', prerelease=False,
                                           observed_at='2026-11-10T00:00:00Z', assets={}),
                                 '6': dict(tag='v0.95', published_at='2026-09-15T00:00:00Z', prerelease=False, assets={})})
        records = {'7': release('v1.0', '2026-10-01T00:00:00Z')}
        partial = d.repository(earlier, dict(received_at=NOW, releases=records, history_complete=False),
                               repository_id=123, repository='example/app')
        self.assertEqual({rid: r.get('observed_at') for rid, r in partial['releases'].items()},
                         {'5': '2026-11-10T00:00:00Z', '6': '2026-11-20T00:00:00Z', '7': None})
        self.assertEqual(readers_accept(d.encode('repository', partial))[0::2], (0, 0))
        complete = d.repository(earlier, dict(received_at=NOW, releases=records, history_complete=True),
                                repository_id=123, repository='example/app')
        self.assertEqual(list(complete['releases']), ['7'])


    def test_retention_keeps_8_newest_tags_newest_stable_and_newest_linux_with_every_twin(self):
        records = {}
        for n in range(1, 12):  # tags t1..t11, published in order; t11 is a CI twin
            stable = n <= 2
            assets = [(str(n*10), 'app-x86_64.AppImage')] if n == 1 else [(str(n*10), 'app.exe')]
            records[str(n)] = release(f't{n}', f'2026-10-{n:02}T00:00:00Z', prerelease=not stable, assets=assets)
        records['12'] = release('t11', '2026-10-11T00:00:00Z', prerelease=True)
        document = d.repository(None, dict(received_at=NOW, releases=records, history_complete=True),
                                repository_id=123, repository='example/app')
        self.assertEqual(sorted({r['tag'] for r in document['releases'].values()}, key=lambda t: int(t[1:])),
                         ['t1', 't2', 't4', 't5', 't6', 't7', 't8', 't9', 't10', 't11'])
        self.assertIn('12', document['releases'])


    def test_a_failed_read_adds_its_failure_and_the_next_success_clears_it(self):
        never = d.failed(None, failed_at=NOW, failed_with='not_found', repository_id=9, repository='example/gone')
        self.assertDocument(never, '''\
$schema: "../../schemas/catalog.schema.yaml#/$defs/repository"
repository_id: 9
repository: "example/gone"
failed_at: "2026-11-25T10:00:00Z"
failed_with: "not_found"
releases: {}
''')
        seen = d.repository(None, dict(received_at='2026-11-24T00:00:00Z', releases={}, history_complete=True),
                            repository_id=9, repository='example/gone')
        later = d.failed(seen, failed_at=NOW, failed_with='transport', repository_id=9, repository='example/gone')
        self.assertEqual((later['observed_at'], later['failed_with']), ('2026-11-24T00:00:00Z', 'transport'))
        again = d.repository(later, dict(received_at='2026-11-26T00:00:00Z', releases={}, history_complete=True),
                             repository_id=9, repository='example/gone')
        self.assertNotIn('failed_at', again)
        self.assertNotIn('failed_with', again)


    def test_git_refs_are_keyed_by_name_and_inherit_the_read_time(self):
        import git_observations as g
        main, tag = 'refs/heads/main', 'refs/tags/v1'
        observed = dict(git_scope=dict(tags=True, tags_history_complete=True, branches={g.key(main): main}),
                        git_refs={g.key(tag): dict(name=tag, commit='c'*40, observed_at=NOW, position=0),
                                  g.key(main): dict(name=main, commit='a'*40, observed_at=NOW,
                                                    files={g.key('VERSION'): dict(path='VERSION', blob='b'*40,
                                                                                  observed_at=NOW, content='1\n')})},
                        completed_at=NOW)
        acquired = dict(received_at=NOW, releases={}, history_complete=True, **observed)
        document = d.repository(None, acquired, repository_id=123, repository='example/app')
        self.assertEqual(d.encode('repository', document).decode().split('releases: {}\n')[1], '''\
git_scope:
  tags: true
  tags_history_complete: true
git_refs:
  "refs/heads/main":
    commit: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    files:
      "VERSION":
        blob: "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        content: "1\\n"
  "refs/tags/v1":
    commit: "cccccccccccccccccccccccccccccccccccccccc"
    position: 0
''')
        self.assertEqual(readers_accept(d.encode('repository', document)), (0, b'', 0, b''))


class Apps(unittest.TestCase):
    def test_each_app_names_its_repository_file_and_labels_each_recipe(self):
        import shutil
        import tempfile
        from recipe_declarations import recipe_rows
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'programs/x86_64').mkdir(parents=True)
            shutil.copy(Path(__file__).resolve().parent/'test-recipes/x86_64/obsidian', root/'programs/x86_64/obsidian')
            declared, = recipe_rows(root)  # a short declaration recipe
            app, rid = declared['app'], declared['repository_id']
            names = {str(rid): 'example-source'}
            document = d.apps([declared, dict(app='catalog-only', repository_id=rid, repository=declared['repository'])],
                              names, root=root)
        self.assertEqual(document['apps'][app], dict(repository='repositories/example-source.yaml', x86_64='declaration'))
        self.assertEqual(document['apps']['catalog-only'], dict(repository='repositories/example-source.yaml'))
        self.assertEqual(readers_accept(d.encode('apps', document)), (0, b'', 0, b''))

    def test_a_recipe_that_is_not_a_declaration_for_this_repository_is_a_script(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'programs/x86_64').mkdir(parents=True)
            (root/'programs/aarch64').mkdir(parents=True)
            (root/'programs/x86_64/tool').write_text('#!/bin/sh\necho install by hand\n')
            (root/'programs/aarch64/tool').write_text('#!/bin/sh\n')
            document = d.apps([dict(app='tool', repository_id=5, repository='example/tool')], {'5': 'tool'}, root=root)
        self.assertEqual(document['apps']['tool'], dict(repository='repositories/tool.yaml', x86_64='script', aarch64='script'))


class Status(unittest.TestCase):
    def test_runs_keep_the_last_64(self):
        previous = dict(runs={f'{n}-1': dict(reported_at=NOW, enrolled=1, selected=1, succeeded=1, failed=0) for n in range(1, 65)})
        document = d.runs(previous, run_id=65, attempt=2, summary=dict(reported_at=NOW, enrolled=2, selected=2, succeeded=1,
                                                                        failed=1, http_attempts=3, stop_reason='quota'))
        self.assertEqual(len(document['runs']), 64)
        self.assertNotIn('1-1', document['runs'])
        self.assertEqual(document['runs']['65-2']['stop_reason'], 'quota')
        self.assertEqual(readers_accept(d.encode('runs', document)), (0, b'', 0, b''))
        self.assertEqual(list(d.runs(None, run_id=1, attempt=1, summary=dict(reported_at=NOW, enrolled=0, selected=0,
                                                                             succeeded=0, failed=0))['runs']), ['1-1'])

    def test_statistics_count_ages_from_observed_at(self):
        times = ['2026-11-25T09:00:00Z', '2026-11-24T10:00:00Z', '2026-11-24T09:59:59Z', '2026-11-11T10:00:00Z',
                 '2026-11-11T09:59:59Z', None]
        repositories = [dict(observed_at=t) if t else {} for t in times]
        document = d.statistics(repositories, measured_at=NOW)
        self.assertEqual(document, dict(measured_at=NOW, under_24h=1, from_24_to_48h=2, from_48h_to_14d=1,
                                        over_14d=1, never_collected=1))
        self.assertEqual(readers_accept(d.encode('statistics', document)), (0, b'', 0, b''))


class Platforms(unittest.TestCase):
    def test_guesses_over_real_asset_names(self):
        # Asset names from release-catalog-v3 (repositories/k*, n*, r*, o*), November 25, 2026.
        for name, linux, architecture in [
                ('KLens-0.6.5-x86_64.AppImage', True, 'x86_64'),
                ('nvim.appimage.zsync', True, None),
                ('k10s-0.1.0-linux-arm64.deb', True, 'aarch64'),
                ('kalk-Linux', True, None),
                ('kitty-0.38.0-x86_64.txz', False, 'x86_64'),
                ('KLens-0.6.5-x64.exe', False, 'x86_64'),
                ('KLens-0.6.5-amd64.deb', False, 'x86_64'),
                ('k8sdockside-0.1.11-darwin-arm64.dmg', False, 'aarch64'),
                ('checksums.txt.sig', False, None),
                ('kanri_0.3.0_armhf.deb', False, 'armv7l'),
                ('kade-1.0.0-i386.AppImage', True, 'i686')]:
            with self.subTest(name=name):
                self.assertEqual((d.linux(name), d.architecture(name)), (linux, architecture))

if __name__ == '__main__':
    unittest.main()
