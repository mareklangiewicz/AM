"""The host reader's fact rows: what catalog-yaml-policy.am selects from.

Rows are tab-separated quoted tokens, as the document writes them. A derived
value (a URL the document leaves out, a release's inherited observed_at) is
filled in, so the policy never derives anything. Expected rows are worked out
by hand from examples/repository.yaml.
"""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = Path(__file__).resolve().parent/'examples/repository.yaml'
NEVER = Path(__file__).resolve().parent/'examples/repository-never-collected.yaml'
APPS = Path(__file__).resolve().parent/'examples/apps.yaml'
READER = ROOT/'modules/catalog-reader.am'


def reader(*args):
    return subprocess.run(['sh', str(READER), *map(str, args)], capture_output=True)


def rows(*cells):
    return ('\t'.join(cells)+'\n').encode()


class Facts(unittest.TestCase):
    def test_asset_rows_fill_derived_urls_and_inherited_times(self):
        run = reader('asset_facts', EXAMPLE)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(run.stdout, b''.join([
            rows('9', '90', '"2026-11-20T10:00:00Z"', '"2026-10-01T00:00:00Z"', '"v1.0"', '"app-x86_64.AppImage"',
                 '"https://github.com/example/app/releases/download/v1.0/app-x86_64.AppImage"', 'false'),
            rows('11', '110', '"2026-11-24T10:00:00Z"', '"2026-11-23T00:00:00Z"', '"nightly"', '"中文 app.tar.gz"',
                 '"https://cdn.example.org/app?x=a:b#part"', 'true'),
        ]))

    def test_release_rows_fill_page_and_source_archive_urls(self):
        run = reader('release_facts', EXAMPLE)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(run.stdout, b''.join([
            rows('9', '', '"2026-11-20T10:00:00Z"', '"2026-10-01T00:00:00Z"', '"v1.0"', '""',
                 '"https://github.com/example/app/releases/tag/v1.0"', 'false',
                 '"https://api.github.com/repos/example/app/tarball/v1.0"', '"https://api.github.com/repos/example/app/zipball/v1.0"'),
            rows('10', '', '"2026-11-24T10:00:00Z"', '"2026-11-23T00:00:00Z"', '"nightly"', '""',
                 '"https://github.com/example/app/releases/tag/nightly"', 'true',
                 '"https://api.github.com/repos/example/app/tarball/nightly"', '"https://api.github.com/repos/example/app/zipball/nightly"'),
            rows('11', '', '"2026-11-24T10:00:00Z"', '"2026-11-23T00:00:00Z"', '"nightly"', '""',
                 '"https://github.com/example/app/releases/tag/nightly-elsewhere"', 'true',
                 '"https://api.github.com/repos/example/app/tarball/nightly"', '"https://example.org/src.zip"'),
        ]))

    def test_git_rows_one_per_file_or_per_ref(self):
        run = reader('git_facts', EXAMPLE)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(run.stdout, b''.join([
            rows('"refs/heads/main"', '"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"', '"2026-11-24T10:00:00Z"', '',
                 '"src/version.txt"', '"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"', '"1.0\\n"'),
            rows('"refs/tags/v1.0"', '"cccccccccccccccccccccccccccccccccccccccc"', '"2026-11-24T10:00:00Z"', '0',
                 '""', '""', '""'),
        ]))

    def test_a_never_collected_repository_has_no_rows(self):
        for operation in ('asset_facts', 'release_facts', 'git_facts'):
            with self.subTest(operation=operation):
                self.assertEqual((reader(operation, NEVER).returncode, reader(operation, NEVER).stdout), (0, b''))

    def test_get_reads_one_scalar(self):
        self.assertEqual(reader('get', APPS, 'apps', 'example', 'repository').stdout, b'repositories/example.yaml')
        self.assertEqual(reader('get', EXAMPLE, 'repository_id').stdout, b'123')
        missing = reader('get', APPS, 'apps', 'unknown', 'repository')
        self.assertEqual((missing.returncode, missing.stdout), (3, b''))

    def test_a_document_that_fails_validation_yields_nothing(self):
        bad = Path(__file__).resolve().parent/'examples/bad-release-seen-not-older.yaml'
        for args in (('asset_facts', bad), ('get', bad, 'repository_id')):
            with self.subTest(args=args[0]):
                run = reader(*args)
                self.assertEqual((run.returncode, run.stdout), (2, b''))

    def test_kind_names_the_schema_fragment(self):
        self.assertEqual(reader('kind', APPS).stdout, b'apps')
        self.assertEqual(reader('kind', EXAMPLE).stdout, b'repository')

    def test_facts_need_a_repository_document(self):
        self.assertEqual(reader('asset_facts', APPS).returncode, 2)


if __name__ == '__main__':
    unittest.main()
