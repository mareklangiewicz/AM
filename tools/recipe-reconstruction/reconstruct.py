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

ROOT = Path(__file__).resolve().parent
TEMPLATE = 'github-appimage-3.5-obsidian'
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
    return template.replace('{{APP}}', value['app']).replace('{{SITE}}', value['repository'])


def load_template(identity):
    if identity != TEMPLATE:
        raise Unsupported('unknown template identity')
    metadata = json.loads(read_text(ROOT/'provenance.json'))
    template = read_text(ROOT/'template.txt')
    if metadata['template'] != identity or hashlib.sha256(template.encode()).hexdigest() != metadata['template_sha256']:
        raise ValueError('template provenance mismatch')
    source = read_text(ROOT/'fixtures/obsidian')
    source_hash = next(row['sha256'] for row in metadata['fixtures'] if row['path'] == metadata['template_source'])
    if hashlib.sha256(source.encode()).hexdigest() != source_hash:
        raise ValueError('template source hash mismatch')
    if render(template, dict(template=identity, **metadata['template_parameters'])) != source:
        raise ValueError('template does not reconstruct pinned source')
    return template, metadata


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
    args = parser.parse_args(argv)
    try:
        template, metadata = load_template(args.template)
        if args.command == 'check':
            result = check(template, read_text(args.recipe), args.template)
            result['provenance'] = dict(template=metadata['template'], upstream_commit=metadata['upstream_commit'],
                                        source_path=metadata['template_source'], source_sha256=next(
                                            row['sha256'] for row in metadata['fixtures'] if row['path'] == metadata['template_source']),
                                        template_sha256=metadata['template_sha256'])
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
    except (OSError, ValueError, KeyError, StopIteration) as error:
        result, code = dict(status='error', reason=str(error)), 3
    print(json.dumps(result), file=sys.stderr if args.command == 'render' else sys.stdout)
    return code


if __name__ == '__main__':
    sys.exit(main())
