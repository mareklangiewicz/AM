#!/usr/bin/env python3
"""THROWAWAY acceptance experiment: python3 tools/catalog-yaml-prototype/experiment.py."""
import copy
import json
import pathlib
import os
import random
import subprocess
import tempfile
import time
import unittest

import yaml  # Reference parser in experiment only; reader has no YAML dependency.

HERE = pathlib.Path(__file__).resolve().parent
READER = HERE / 'reader.sh'
SCHEMA = 'https://raw.githubusercontent.com/example/AM/' + 'a' * 40 + '/docs/catalog-format-v2.md'


def repository():
    return dict(format=2, schema=SCHEMA, repository_id=123, repository='example/app',
                checked_at='2026-11-03T01:00:00Z', check_status='ok', releases={
                    '456': dict(tag='v2.0.0', title='Quotes " and \\; café 中文 🐧\n\r\t\n',
                                url='https://github.com/example/app/releases/tag/v2.0.0',
                                published_at='2026-11-02T12:00:00Z', prerelease=False,
                                assets={'789': dict(name="John's app #1.AppImage",
                                                    url='https://github.com/example/app/releases/download/v2.0.0/app?x=a:b#part',
                                                    size=0, content_type='')})})


def emit(obj, depth=0, context=''):
    lines = []
    for k, v in obj.items():
        key = json.dumps(k) if k.isdigit() or context == 'apps' else k
        prefix = '  ' * depth + key + ':'
        if isinstance(v, dict):
            lines.append(prefix + (' {}' if not v else ''))
            if v:
                lines.extend(emit(v, depth + 1, k))
        else:
            scalar = json.dumps(v, ensure_ascii=False)
            # Experimental extension: avoid YAML's Unicode line-break folding.
            scalar = scalar.replace('\u0085', '\\N').replace('\u2028', '\\L').replace('\u2029', '\\P')
            lines.append(prefix + ' ' + scalar)
    return lines


def document(obj):
    return '\n'.join(emit(obj)) + '\n'


class Experiment(unittest.TestCase):
    def run_reader(self, text, command='validate', *keys):
        with tempfile.NamedTemporaryFile() as f:
            f.write(text.encode()); f.flush()
            env = dict(os.environ)
            if os.environ.get('AM_YAML_AWK_PATH'):
                env['PATH'] = os.environ['AM_YAML_AWK_PATH'] + ':' + env['PATH']
            return subprocess.run(['sh', str(READER), command, f.name, *keys],
                                  capture_output=True, env=env)

    def accepted(self, obj):
        text = document(obj)
        self.assertEqual(yaml.safe_load(text), obj)
        result = self.run_reader(text)
        self.assertEqual((result.returncode, result.stdout), (0, b''), result.stderr)
        return text

    def test_valid_states(self):
        base = repository()
        self.accepted(base)
        empty = copy.deepcopy(base); empty['releases'] = {}; self.accepted(empty)
        no_assets = copy.deepcopy(base); no_assets['releases']['456']['assets'] = {}; self.accepted(no_assets)
        retained = dict(list(base.items())[:5], check_status='failed', check_reason='transport', releases=base['releases'])
        self.accepted(retained)
        never = dict(format=2, schema=SCHEMA, repository_id=123, repository='example/app',
                     check_status='failed', check_reason='rate_limited')
        self.accepted(never)
        self.accepted(dict(format=2, schema=SCHEMA, apps={'app': 123, 'app-beta': 123}))
        self.accepted(dict(format=2, schema=SCHEMA, apps={}))
        self.accepted(dict(format=2, schema=SCHEMA, apps={'123': 123, 'null': 123, 'on': 123, 'true': 123}))

    def test_queries_preserve_values(self):
        obj = repository(); text = self.accepted(obj)
        cases = [('releases', (), b'456\n'), ('assets', ('456',), b'789\n'),
                 ('get', ('releases', '456', 'title'), obj['releases']['456']['title'].encode()),
                 ('get', ('releases', '456', 'prerelease'), b'false'),
                 ('get', ('releases', '456', 'assets', '789', 'size'), b'0'),
                 ('get', ('releases', '456', 'assets', '789', 'content_type'), b'')]
        for command, keys, expected in cases:
            with self.subTest(command=command, keys=keys):
                result = self.run_reader(text, command, *keys)
                self.assertEqual((result.returncode, result.stdout), (0, expected), result.stderr)
        missing = self.run_reader(text, 'get', 'releases', '456', 'assets', '789', 'digest')
        self.assertEqual((missing.returncode, missing.stdout), (3, b''))
        missing_parent = self.run_reader(text, 'assets', '999')
        self.assertEqual((missing_parent.returncode, missing_parent.stdout), (3, b''))

    def test_malformed(self):
        good = document(repository())
        variants = {
            'format': good.replace('format: 2', 'format: 3'),
            'duplicate root': good + 'repository_id: 123\n',
            'unknown field': good + 'unknown: "x"\n',
            'trailing content': good + '---\n',
            'comment': good + '# comment\n',
            'blank': good + '\n',
            'tab indentation': good.replace('  "456":', '\t"456":'),
            'odd indentation': good.replace('  "456":', ' "456":'),
            'depth jump': good.replace('  "456":', '      "456":'),
            'trailing space': good.replace('format: 2', 'format: 2 '),
            'CRLF': good.replace('\n', '\r\n'),
            'null': good.replace('content_type: ""', 'content_type: null'),
            'unquoted string': good.replace('tag: "v2.0.0"', 'tag: v2.0.0'),
            'single quotes': good.replace('tag: "v2.0.0"', "tag: 'v2.0.0'"),
            'unicode escape': good.replace('tag: "v2.0.0"', 'tag: "\\u0076"'),
            'unknown escape': good.replace('tag: "v2.0.0"', 'tag: "\\q"'),
            'quote injection': good.replace('tag: "v2.0.0"', 'tag: "v"x"'),
            'unfinished escape': good.replace('tag: "v2.0.0"', 'tag: "v\\"'),
            'tagged': good.replace('tag: "v2.0.0"', 'tag: !!str "v2.0.0"'),
            'anchor': good.replace('releases:', 'releases: &x'),
            'block scalar': good.replace('tag: "v2.0.0"', 'tag: |'),
            'list': good.replace('  "456":', '  - id: 456'),
            'leading zero id': good.replace('"456":', '"0456":'),
            'numeric key': good.replace('"456":', '456:'),
            'overflow': good.replace('repository_id: 123', 'repository_id: 9223372036854775808'),
            'zero repository': good.replace('repository_id: 123', 'repository_id: 0'),
            'negative size': good.replace('size: 0', 'size: -1'),
            'float': good.replace('size: 0', 'size: 1.0'),
            'wrong boolean': good.replace('prerelease: false', 'prerelease: "false"'),
            'wrong timestamp': good.replace('2026-11-02T12:00:00Z', '2026-02-30T12:00:00Z'),
            'timezone': good.replace('2026-11-03T01:00:00Z', '2026-11-03T01:00:00+00:00'),
            'http': good.replace('url: "https:', 'url: "http:'),
            'URL newline': good.replace('tag/v2.0.0"', 'tag/v2.0.0\\n"'),
            'schema branch': good.replace('/' + 'a' * 40 + '/', '/main/'),
            'missing check time': good.replace('checked_at: "2026-11-03T01:00:00Z"\n', ''),
            'missing required asset': good.replace('        size: 0\n', ''),
            'empty implicit map': good.replace('releases:', 'releases: {}'),
            'wrong status': good.replace('check_status: "ok"', 'check_status: "unknown"'),
            'mixed roots': good + 'apps: {}\n',
            'NEL changes value in YAML': good.replace('tag: "v2.0.0"', 'tag: "a\u0085b"'),
            'literal line separator': good.replace('tag: "v2.0.0"', 'tag: "a \u2028b"'),
            'literal paragraph separator': good.replace('tag: "v2.0.0"', 'tag: "a \u2029b"'),
            'C1 invalid YAML': good.replace('tag: "v2.0.0"', 'tag: "a\u0080b"'),
            'invalid YAML noncharacter': good.replace('tag: "v2.0.0"', 'tag: "a\ufffeb"'),
            'raw ASCII control': good.replace('tag: "v2.0.0"', 'tag: "a\x01b"'),
            'overlong line': good.replace('tag: "v2.0.0"', 'tag: "' + 'x' * 65536 + '"'),
        }
        # A later malformed field must suppress even an earlier valid query.
        for name, text in variants.items():
            with self.subTest(case=name):
                result = self.run_reader(text, 'get', 'repository')
                self.assertEqual((result.returncode, result.stdout), (2, b''), result.stderr)

    def test_order_duplicates_and_empty(self):
        obj = repository()
        release = obj['releases']['456']
        obj['releases']['457'] = copy.deepcopy(release)
        text = self.accepted(obj)
        for bad in [text.replace('"457":', '"456":'),
                    text.replace('"457":', '"455":'),
                    text.replace('    prerelease: false\n', ''),
                    text.replace('    prerelease: false\n', '    prerelease: false\n    tag: "x"\n')]:
            result = self.run_reader(bad)
            self.assertEqual((result.returncode, result.stdout), (2, b''), result.stderr)
        empty = repository(); empty['releases'] = {}
        text = self.accepted(empty)
        self.assertEqual(self.run_reader(text, 'releases').stdout, b'')
        self.assertEqual(self.run_reader(text, 'releases').returncode, 0)
        self.assertEqual(self.run_reader(text.replace('releases: {}', 'releases:')).returncode, 2)

    def test_large_integer_ids_are_exact(self):
        obj = repository(); r = obj['releases'].pop('456')
        obj['releases'] = {'9007199254740992': r, '9007199254740993': copy.deepcopy(r),
                           '9223372036854775807': copy.deepcopy(r)}
        text = self.accepted(obj)
        result = self.run_reader(text, 'releases')
        self.assertEqual(result.stdout, b'9007199254740992\n9007199254740993\n9223372036854775807\n')

    def test_no_evaluation(self):
        with tempfile.TemporaryDirectory() as folder:
            marker = pathlib.Path(folder) / 'executed'
            obj = repository(); obj['releases']['456']['title'] = f'$(touch {marker}) `touch {marker}`'
            text = self.accepted(obj)
            result = self.run_reader(text, 'get', 'releases', '456', 'title')
            self.assertEqual(result.stdout.decode(), obj['releases']['456']['title'])
            self.assertFalse(marker.exists())

    def test_string_roundtrips(self):
        rng = random.Random(20261103)
        alphabet = 'abc XYZ012:#[]{}!?/$()`\'"\\\n\r\t café中文🐧\u0085\u2028\u2029'
        # Exercise escape adjacency and Unicode against an independent YAML parser.
        obj = repository(); example = obj['releases'].pop('456')
        expected = {}
        for i in range(1, 101):
            release = copy.deepcopy(example)
            release['title'] = ''.join(rng.choice(alphabet) for _ in range(rng.randrange(0, 120)))
            obj['releases'][str(i)] = release
            expected[str(i)] = release['title']
        text = self.accepted(obj)
        for i in ('1', '2', '10', '50', '100'):
            result = self.run_reader(text, 'get', 'releases', i, 'title')
            self.assertEqual((result.returncode, result.stdout), (0, expected[i].encode()))


def benchmark():
    obj = repository(); example = obj['releases'].pop('456')
    example['assets'] = {str(i): copy.deepcopy(example['assets']['789']) for i in range(1, 9)}
    obj['releases'] = {str(i): copy.deepcopy(example) for i in range(1, 1001)}
    text = document(obj)
    start = time.monotonic()
    result = Experiment().run_reader(text)
    print(json.dumps(dict(synthetic_releases=1000, synthetic_assets=8000,
                          bytes=len(text.encode()), seconds=round(time.monotonic()-start, 4),
                          exit=result.returncode, diagnostic=result.stderr.decode())), flush=True)
    if result.returncode:
        raise SystemExit(1)


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Experiment)
    if not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful():
        raise SystemExit(1)
    benchmark()
