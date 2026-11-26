"""Write examples/bad-*.yaml and examples/bad.json from the good examples.

Each bad example is one good example with edits that break exactly one rule.
bad.json records, per example, the refusal both readers must report and
whether the schema alone can see the break (grammar and cross-field rules it
cannot). Rerun after changing a good example; every edit must apply exactly
once.
"""
import json
from pathlib import Path

EXAMPLES = Path(__file__).resolve().parents[1]/'examples'
R = 'repository.yaml'
NEVER = 'repository-never-collected.yaml'
NEW = 'repository-never-read.yaml'  # enrolled, not yet read (catalog-simplification ticket 27)
TAG_REF = '  "refs/tags/v1.0":\n    commit: "cccccccccccccccccccccccccccccccccccccccc"\n    position: 0\n'
GIT = 'git_scope:\n  tags: true\n  tags_history_complete: false\ngit_refs:\n'
GRAMMAR, SCHEMA, CROSS = 'grammar', 'schema', 'cross-field'

# name: (base, [(old, new), ...], refusal, layer)
BAD = {
    'comment': ('apps.yaml', [('apps:\n', '# apps\napps:\n')], 'missing colon', GRAMMAR),
    'blank-line': ('apps.yaml', [('apps:\n', '\napps:\n')], 'blank line', GRAMMAR),
    'trailing-space': ('apps.yaml', [('"declaration"\n', '"declaration" \n')], 'trailing space', GRAMMAR),
    'tab': ('statistics.yaml', [('over_14d: 14', 'over_14d:\t14')], 'control', GRAMMAR),
    'control-in-string': (R, [('"example/app"', '"example/\x7fapp"')], 'control', GRAMMAR),
    'implicit-empty': (R, [('assets: {}', 'assets:')], 'use {} for an empty mapping', SCHEMA),
    'unquoted-table-key': ('apps.yaml', [('  "example":', '  example:')], 'table key', GRAMMAR),
    'quoted-field-name': ('apps.yaml', [('    repository: "repositories/example.yaml"\n    x86_64: "declaration"',
                                         '    "repository": "repositories/example.yaml"\n    x86_64: "declaration"')], 'quoted field name', GRAMMAR),
    'field-order': ('statistics.yaml', [('under_24h: 2473\nfrom_24_to_48h: 1411', 'from_24_to_48h: 1411\nunder_24h: 2473')], 'out-of-order field', GRAMMAR),
    'table-order': ('apps.yaml', [('"example":', '"example-z":')], 'key order', GRAMMAR),
    'release-id-order': (R, [('  "9":', '  "12":')], 'key order', GRAMMAR),
    'run-order': ('runs.yaml', [('"9-1":', '"11-1":')], 'key order', GRAMMAR),
    'duplicate-key': ('statistics.yaml', [('never_collected: 0', 'never_collected: 0\nnever_collected: 0')], 'duplicate key', GRAMMAR),
    'unsupported-escape': (R, [('First \\"stable\\"', 'First \\x41')], 'unsupported escape', GRAMMAR),
    'schema-not-first': ('statistics.yaml', [('$schema: "../../schemas/catalog.schema.yaml#/$defs/statistics"\nmeasured_at: "2026-11-25T11:00:00Z"',
                                              'measured_at: "2026-11-25T11:00:00Z"\n$schema: "../../schemas/catalog.schema.yaml#/$defs/statistics"')], '$schema first', GRAMMAR),
    'text-after-string': ('apps.yaml', [('"declaration"\n', '"declaration" "x"\n')], 'text after string', GRAMMAR),
    'schema-wrong-depth': ('apps.yaml', [('"../schemas/', '"../../schemas/')], 'unknown $schema', SCHEMA),
    'null': ('statistics.yaml', [('never_collected: 0', 'never_collected: null')], 'scalar', SCHEMA),
    'negative': ('statistics.yaml', [('never_collected: 0', 'never_collected: -1')], 'scalar', SCHEMA),
    'id-over-64-bits': (NEVER, [('9223372036854775807', '9223372036854775808')], 'integer', SCHEMA),
    'unknown-field': ('statistics.yaml', [('never_collected: 0', 'never_collected: 0\nunknown: 0')], 'unknown or out-of-order field', SCHEMA),
    'missing-field': (R, [('    tag: "nightly"\n    published_at: "2026-11-23T00:00:00Z"\n    prerelease: true\n    assets: {}',
                           '    tag: "nightly"\n    prerelease: true\n    assets: {}')], 'missing field', SCHEMA),
    'retired-failure-code': (R, [('"transport"', '"same_tag_conflict"')], 'enum', SCHEMA),
    'retired-recipe-label': ('apps.yaml', [('"script"\n  "example-nightly"', '"custom"\n  "example-nightly"')], 'enum', SCHEMA),
    'sha256pre-short': (R, [('"0123456789abcdef"', '"0123456789abcde"')], 'pattern', SCHEMA),
    'sha256pre-uppercase': (R, [('"0123456789abcdef"', '"0123456789ABCDEF"')], 'pattern', SCHEMA),
    'calendar-date': ('statistics.yaml', [('2026-11-25T11', '2026-02-30T11')], 'timestamp', CROSS),
    'url-not-https': (R, [('"https://example.org/src.zip"', '"http://example.org/src.zip"')], 'pattern', SCHEMA),
    'tag-position-over-99': (R, [('position: 0', 'position: 100')], 'maximum', SCHEMA),
    'repository-path': ('apps.yaml', [('"repositories/example.yaml"\n    x86_64: "declaration"',
                                       '"repositories/../example.yaml"\n    x86_64: "declaration"')], 'pattern', SCHEMA),
    'ref-not-branch-or-tag': (R, [('"refs/heads/main"', '"refs/pull/1"')], 'table key', SCHEMA),
    'history-without-observation': (NEVER, [('failed_at:', 'history_complete: true\nfailed_at:')], 'observed_at and history_complete come together', CROSS),
    'failure-half': (NEVER, [('failed_with: "not_found"\n', '')], 'failed_at and failed_with come together', CROSS),
    'never-collected-with-release': (NEVER, [('releases: {}', 'releases:\n  "1":\n    tag: "v1"\n    published_at: "2026-10-01T00:00:00Z"\n    prerelease: false\n    assets: {}')],
                                     'a never-collected repository has no releases or Git refs', CROSS),
    'never-read-with-git': (NEW, [('releases: {}', 'releases: {}\ngit_scope:\n  tags: true\n  tags_history_complete: false\n'
                                   'git_refs:\n  "refs/tags/v1":\n    commit: "cccccccccccccccccccccccccccccccccccccccc"\n    position: 0')],
                            'a never-collected repository has no releases or Git refs', CROSS),
    'failure-before-observation': (R, [('failed_at: "2026-11-25T09:00:00Z"', 'failed_at: "2026-11-24T10:00:00Z"')], 'failure not after observation', CROSS),
    'release-seen-not-older': (R, [('    observed_at: "2026-11-20T10:00:00Z"', '    observed_at: "2026-11-24T10:00:00Z"')], 'release last seen not older', CROSS),
    'git-scope-without-refs': (R, [(GIT, 'git_scope:\n  tags: true\n  tags_history_complete: false\n'), (TAG_REF, ''),
                                   ('  "refs/heads/main":\n    commit: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"\n    files:\n      "src/version.txt":\n'
                                    '        blob: "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"\n        content: "1.0\\n"\n', '')],
                               'git_scope and git_refs come together', CROSS),
    'tag-history-without-tags': (R, [('tags: true\n  tags_history_complete: false', 'tags: false\n  tags_history_complete: true'), (TAG_REF, '')],
                                 'tag history without tags', CROSS),
    'tag-without-tags-scope': (R, [('tags: true', 'tags: false')], 'Git tag scope', CROSS),
    'tag-without-position': (R, [('\n    position: 0\n', '\n')], 'Git tag scope', CROSS),
    'tag-position-gap': (R, [('position: 0', 'position: 1')], 'Git tag position gap', CROSS),
    'branch-with-position': (R, [('"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"\n', '"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"\n    position: 1\n')], 'Git branch scope', CROSS),
    'git-file-dot-segment': (R, [('"src/version.txt"', '"src/../version.txt"')], 'Git file path', CROSS),
    'git-ref-dots': (R, [('"refs/heads/main"', '"refs/heads/ma..in"')], 'Git ref name', CROSS),
    'five-branches': (R, [('  "refs/heads/main":\n', ''.join(f'  "refs/heads/b{i}":\n    commit: "{"a"*40}"\n' for i in range(1, 5))+'  "refs/heads/main":\n')],
                      'more than 4 Git branches', CROSS),
    'run-counts': ('runs.yaml', [('succeeded: 498', 'succeeded: 499')], 'run counts', CROSS),
}
RUNS_HEAD = '$schema: "../../schemas/catalog.schema.yaml#/$defs/runs"\nruns:\n'
RUN = '    reported_at: "2026-11-24T10:00:00Z"\n    enrolled: 1\n    selected: 0\n    succeeded: 0\n    failed: 0\n'


def runs(count):
    return RUNS_HEAD+''.join(f'  "{i}-1":\n'+RUN for i in range(1, count+1))


def main():
    for old in EXAMPLES.glob('bad-*.yaml'):
        old.unlink()
    (EXAMPLES/'runs-64.yaml').write_text(runs(64))
    expected = {}
    for name, (base, edits, refusal, layer) in BAD.items():
        text = (EXAMPLES/base).read_text()
        for old, new in edits:
            if text.count(old) != 1:
                raise SystemExit(f'{name}: {old!r} occurs {text.count(old)} times in {base}')
            text = text.replace(old, new)
        (EXAMPLES/f'bad-{name}.yaml').write_text(text)
        expected[f'bad-{name}.yaml'] = dict(refusal=refusal, schema_sees=layer == SCHEMA)
    (EXAMPLES/'bad-65-runs.yaml').write_text(runs(65))
    expected['bad-65-runs.yaml'] = dict(refusal='more than 64', schema_sees=True)
    (EXAMPLES/'bad.json').write_text(json.dumps(expected, indent=1, sort_keys=True)+'\n')


if __name__ == '__main__':
    main()
