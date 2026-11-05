#!/usr/bin/env python3
"""Recognize complete pinned upstream recipes as inert text; never execute shell."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import re
import shlex
import sys
import subprocess

ROOT = Path(__file__).resolve().parent
TEMPLATE = 'github-appimage-3.5'
LIMIT = 1024 * 1024
APP = r'[a-z0-9][a-z0-9.+_-]*'
REPOSITORY = r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+'
# Literal settings accepted by the current shared-installer declaration header.
SETTINGS = set('APP CATALOG_FORMAT CATALOG_RECIPE CATALOG_ALIAS CATALOG_REPOSITORY_ID '
               'CATALOG_REPOSITORY CATALOG_CHANNEL CATALOG_ASSET_PATTERN PACKAGE_KIND '
               'PACKAGE_LAYOUT PACKAGE_TOOLS CATALOG_TOOL_ASSET_SUFFIX VERSION_IDENTITY '
               'REFRESH_ALWAYS CATALOG_FRESH_ONLY ARCHIVE_ROOT PACKAGE_EXECUTABLES '
               'PACKAGE_LAUNCHERS EXTRA_APP_LAUNCHERS DESKTOP_EXEC'.split())


class Unsupported(ValueError):
    pass


def read_text(path):
    with Path(path).open('rb') as stream:
        data = stream.read(LIMIT + 1)
    if len(data) > LIMIT:
        raise Unsupported('input exceeds 1 MiB')
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError as error:
        raise Unsupported('input is not UTF-8') from error
    if '\0' in text:
        raise Unsupported('NUL bytes are unsupported')
    return text


def declaration(value):
    if not isinstance(value, dict) or set(value) != {'template', 'app', 'repository'}:
        raise Unsupported('declaration requires exactly template, app and repository')
    if value['template'] != TEMPLATE:
        raise Unsupported('unknown template identity')
    for field, pattern in [('app', APP), ('repository', REPOSITORY)]:
        if not isinstance(value[field], str) or not re.fullmatch(pattern, value[field]):
            raise Unsupported('unsupported literal '+field)
    return value


def render(template, value):
    value = declaration(value)
    # The pinned upstream generator concatenates shell literals and three known
    # variables. Tokenize only its trusted, hash-checked excerpt; never evaluate it.
    assignment = read_text(ROOT/'upstream/github-appimage-function.txt').strip()
    if not assignment.startswith('FUNCTION='):
        raise ValueError('unsupported upstream generator assignment')
    words = shlex.split(assignment[len('FUNCTION='):])
    if len(words) != 1:
        raise ValueError('unsupported upstream generator concatenation')
    function = words[0].replace('$CURL_COMMAND_REF', 'curl -Ls https://api.github.com/repos')
    function = function.replace('$RESPONSE', value['repository']).replace('$q', "'")
    # Upstream passes FUNCTION through a sed replacement: doubled backslashes
    # become single backslashes in the resulting recipe.
    function = function.replace('\\\\', '\\')
    replacements = dict(SAMPLE=value['app'], REPLACETHIS=value['repository'], FUNCTION=function)
    return re.sub(r'SAMPLE|REPLACETHIS|FUNCTION(?=\))', lambda match: replacements[match[0]], template)


def load_template(identity):
    if identity != TEMPLATE:
        raise Unsupported('unknown template identity')
    metadata = json.loads(read_text(ROOT/'provenance.json'))
    template = read_text(ROOT/'upstream/AM-SAMPLE-AppImage')
    if metadata['template'] != identity or hashlib.sha256(template.encode()).hexdigest() != metadata['template_sha256']:
        raise ValueError('template provenance mismatch')
    excerpt = read_text(ROOT/'upstream/github-appimage-function.txt')
    if hashlib.sha256(excerpt.encode()).hexdigest() != metadata['generator_excerpt_sha256']:
        raise ValueError('generator excerpt hash mismatch')
    return template, metadata


def verify_upstream(repository, metadata):
    def source(commit, path):
        return subprocess.check_output(['git', '--no-replace-objects', '-C', str(repository.resolve()),
                                        'show', commit+':'+path], stderr=subprocess.PIPE)
    template = source(metadata['upstream_commit'], metadata['template_source'])
    if template != (ROOT/'upstream/AM-SAMPLE-AppImage').read_bytes():
        raise ValueError('upstream template snapshot differs')
    generator = source(metadata['upstream_commit'], metadata['generator_source'])
    if hashlib.sha256(generator).hexdigest() != metadata['generator_sha256']:
        raise ValueError('upstream generator hash differs')
    line = generator.splitlines(keepends=True)[metadata['generator_line']-1]
    if line != (ROOT/'upstream/github-appimage-function.txt').read_bytes():
        raise ValueError('upstream generator excerpt differs')
    for fixture in metadata['fixtures']:
        original = source(metadata['fixture_commit'], fixture['path'])
        if original != (ROOT/'fixtures'/Path(fixture['path']).name).read_bytes():
            raise ValueError('upstream fixture differs: '+fixture['path'])
    return dict(status='exact', template=metadata['template'], upstream_commit=metadata['upstream_commit'],
                fixtures_verified=len(metadata['fixtures']), generator_verified=True)


def from_short(source, identity):
    marker = '# shellcheck source=modules/appimage.am\n'
    header, separator, tail = source.partition(marker)
    if (not separator or tail != '. "/opt/am/modules/appimage.am"\nam_appimage "$0" "$@"\n'
            or not header.startswith('#!/bin/sh\n')
            or header.splitlines().count('# AM-RECIPE-DECLARATION 1') != 1):
        raise Unsupported('unsupported short recipe wrapper')
    settings = {}
    for line in header.splitlines():
        if not line or line.startswith('#') or line == 'set -eu':
            continue
        name, equals, literal = line.partition('=')
        if not equals or name not in SETTINGS or name in settings:
            raise Unsupported('unsupported or duplicate setting: '+name)
        try:
            words = shlex.split(literal)
        except ValueError as error:
            raise Unsupported('invalid literal: '+name) from error
        value = words[0] if words else ''
        double = literal == '"'+value+'"' and not any(c in value for c in '$`\\"')
        if len(words) > 1 or not (literal == shlex.quote(value) or double or literal == ''):
            raise Unsupported('nonliteral setting: '+name)
        settings[name] = value
    if (settings.get('CATALOG_FORMAT') != '2'
            or settings.get('CATALOG_RECIPE') != 'x86_64/'+settings.get('APP', '')
            or settings.get('PACKAGE_KIND', 'appimage') != 'appimage'
            or settings.get('PACKAGE_LAYOUT', 'raw') not in ('raw', 'appimage')):
        raise Unsupported('missing or inconsistent catalog recipe identity')
    return declaration(dict(template=identity, app=settings.get('APP'), repository=settings.get('CATALOG_REPOSITORY')))


def check(template, source, identity):
    app = re.search(r'^APP=('+APP+r')$', source, re.M)
    repository = re.search(r'^SITE="('+REPOSITORY+r')"$', source, re.M)
    if not app or not repository:
        raise Unsupported('missing supported literal APP/SITE assignments')
    candidate = declaration(dict(template=identity, app=app[1], repository=repository[1]))
    expected = render(template, candidate)
    if expected == source:
        return dict(status='exact', declaration=candidate, compatibility='unassessed')
    # Keep newline changes visible, including missing final LF.
    before, after = expected.splitlines(keepends=True), source.splitlines(keepends=True)
    diff = []
    for line in difflib.unified_diff(before, after, fromfile='reconstructed', tofile='incoming'):
        diff.append(line if line.endswith('\n') else line+'\n\\ No newline at end of file\n')
    return dict(status='review', candidate=candidate, compatibility='unassessed', diff=''.join(diff))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    inspect = sub.add_parser('check', help='check a complete upstream recipe; JSON on stdout')
    inspect.add_argument('recipe', type=Path)
    inspect.add_argument('--template', default=TEMPLATE)
    expand = sub.add_parser('render', help='render pinned upstream bytes on stdout')
    inputs = expand.add_mutually_exclusive_group(required=True)
    inputs.add_argument('--declaration', type=Path)
    inputs.add_argument('--short-recipe', type=Path)
    expand.add_argument('--template', required=True)
    verify = sub.add_parser('verify-upstream', help='verify snapshots against pinned Git objects; JSON on stdout')
    verify.add_argument('--repo', type=Path, required=True)
    verify.set_defaults(template=TEMPLATE)
    args = parser.parse_args(argv)
    try:
        template, metadata = load_template(args.template)
        if args.command == 'verify-upstream':
            print(json.dumps(verify_upstream(args.repo, metadata), indent=2))
            return 0
        if args.command == 'check':
            result = check(template, read_text(args.recipe), args.template)
            result['provenance'] = dict(template=metadata['template'], upstream_commit=metadata['upstream_commit'],
                                        source_path=metadata['template_source'], source_sha256=metadata['template_sha256'],
                                        generator_path=metadata['generator_source'], generator_line=metadata['generator_line'],
                                        generator_sha256=metadata['generator_sha256'])
            print(json.dumps(result, indent=2))
            return 0 if result['status'] == 'exact' else 1
        if args.short_recipe:
            value = from_short(read_text(args.short_recipe), args.template)
        else:
            value = declaration(json.loads(read_text(args.declaration)))
        sys.stdout.buffer.write(render(template, value).encode('utf-8'))
        return 0
    except Unsupported as error:
        result, code = dict(status='unsupported', reason=str(error)), 2
    except (OSError, ValueError, KeyError, IndexError, subprocess.CalledProcessError) as error:
        result, code = dict(status='error', reason=str(error)), 3
    print(json.dumps(result), file=sys.stderr if args.command == 'render' else sys.stdout)
    return code


if __name__ == '__main__':
    sys.exit(main())
