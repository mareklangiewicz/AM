"""Read literal declarations from recipe declaration headers, without executing shell."""
import json
import hashlib
import re
import shlex

MARKER = '# AM-RECIPE-DECLARATION 1\n'


def rows_json(rows):
    """A committed list of rows, one row per line, so a rewrite touches only
    the rows that changed (ticket 29). Readers just use json.loads."""
    if not rows:
        return '[]\n'
    return '[\n'+',\n'.join(json.dumps(row) for row in rows)+'\n]\n'


def validate_url_rules(rules):
    if (not isinstance(rules,list) or not 1<=len(rules)<=16 or any(
            not isinstance(rule,dict) or set(rule)!={'pattern','ignore_case','exclude'} or
            not isinstance(rule['pattern'],str) or not 1<=len(rule['pattern'])<=512 or
            any(ord(c)<32 for c in rule['pattern']) or
            type(rule['ignore_case']) is not bool or type(rule['exclude']) is not bool
            for rule in rules)):
        raise ValueError('invalid literal URL rules')
    return rules


def url_policy_rows(root):
    path=root/'tools/catalog-collector/recipe-url-policies.json'
    if not path.exists():return []
    rows=json.loads(path.read_text());result=[];seen=set()
    if not isinstance(rows,list):raise ValueError('URL policy registry')
    for row in rows:
        required={'recipe','source_recipe','source_sha256','repository_id','repository','channel','url_rules','catalog_app','dispatch_recipe','source_aliases'}
        optional={'selection','tag_pattern','tag_exclude','git_ref','git_file'}
        if not required<=set(row) or set(row)-required-optional:
            raise ValueError('URL policy fields')
        for key in ('recipe','source_recipe','dispatch_recipe'):
            if not re.fullmatch(r'(x86_64|aarch64|i686|armv7l)/[a-z0-9][a-z0-9_.+-]*',row[key]):
                raise ValueError('URL policy recipe')
        source=root/'programs'/row['source_recipe']
        if source.is_symlink() or hashlib.sha256(source.read_bytes()).hexdigest()!=row['source_sha256']:
            raise ValueError('URL policy source changed: '+row['source_recipe'])
        if (row['recipe'] in seen or type(row['repository_id']) is not int or row['repository_id']<1 or
                not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',row['repository']) or
                row['channel'] not in ('any','stable','nightly') or
                not re.fullmatch(r'[a-z0-9][a-z0-9_.+-]{0,63}',row['catalog_app'])):
            raise ValueError('URL policy identity')
        seen.add(row['recipe']);validate_url_rules(row['url_rules'])
        if row.get('selection','asset') not in ('asset','release','git-tag','git-branch','git-file'):
            raise ValueError('selection kind')
        for field in ('tag_pattern','tag_exclude','git_ref','git_file'):
            if field in row and (not isinstance(row[field],str) or len(row[field].encode())>1024 or
                    any(ord(c)<32 for c in row[field])):raise ValueError('selection literal')
        if row.get('selection') in ('git-branch','git-file'):
            from git_observations import valid_ref,valid_path
            if not valid_ref(row.get('git_ref','')) or not row['git_ref'].startswith('refs/heads/'):
                raise ValueError('branch selection')
            if row['selection']=='git-file' and not valid_path(row.get('git_file','')):raise ValueError('file selection')
        if (not isinstance(row['source_aliases'],list) or not row['source_aliases'] or any(
                not isinstance(alias,str) or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',alias)
                for alias in row['source_aliases'])):
            raise ValueError('URL policy source aliases')
        result.append(dict(row,app=row['recipe'].split('/')[1],asset_pattern='^.*$'))
    return result


def recipe_rows(root):
    rows = []
    repositories, apps = {}, {}
    paths = (path for arch in ('x86_64', 'aarch64', 'i686', 'armv7l')
             for path in (root/'programs'/arch).glob('*'))
    for path in sorted(paths):
        if not path.is_file():
            continue
        source = path.read_text()
        if MARKER not in source:
            continue
        header, separator, _ = source.partition('# shellcheck source=modules/appimage.am\n')
        if not separator:
            raise ValueError('missing shared installer seam: '+str(path))
        settings = {}
        for line in header.splitlines():
            if not line or line.startswith('#') or line == 'set -eu':
                continue
            name, equals, literal = line.partition('=')
            tokens = shlex.split(literal)
            value = tokens[0] if tokens else ''
            quoted = literal == shlex.quote(value)
            double_quoted = literal == '"'+value+'"' and not any(c in value for c in '$`\\"')
            if (not equals or not re.fullmatch(r'[A-Z][A-Z0-9_]*', name) or len(tokens)>1
                    or not (quoted or double_quoted or literal == '')):
                raise ValueError('recipes require literal declarations: '+str(path))
            if name in settings:
                raise ValueError('duplicate recipe declaration: '+name)
            settings[name] = value
        required = ('APP', 'CATALOG_FORMAT', 'CATALOG_RECIPE', 'CATALOG_REPOSITORY_ID',
                    'CATALOG_REPOSITORY', 'CATALOG_CHANNEL', 'CATALOG_ASSET_PATTERN')
        if any(not settings.get(key) for key in required):
            raise ValueError('missing recipe declaration: '+str(path))
        if settings['CATALOG_FORMAT'] != '3':
            raise ValueError('unsupported declaration format: '+str(path))
        if (not re.fullmatch(r'[1-9][0-9]*', settings['CATALOG_REPOSITORY_ID']) or
                not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', settings['CATALOG_REPOSITORY'])):
            raise ValueError('invalid repository identity: '+str(path))
        app = settings['APP']
        if not re.fullmatch(r'[a-z0-9][a-z0-9_.+-]*', app):
            raise ValueError('invalid app identity: '+str(path))
        if app != path.name or settings['CATALOG_RECIPE'] != path.parent.name+'/'+app:
            raise ValueError('recipe identity mismatch: '+str(path))
        catalog_app=settings.get('CATALOG_APP',app)
        if not re.fullmatch(r'[a-z0-9][a-z0-9_.+-]{0,63}',catalog_app):
            raise ValueError('catalog app identity: '+str(path))
        tools = settings.get('PACKAGE_TOOLS', '').split()
        kind = settings.get('PACKAGE_KIND', 'appimage')
        layout = settings.get('PACKAGE_LAYOUT', 'raw' if kind == 'executable' else 'appimage')
        if kind not in ('appimage','executable') or (layout == 'toolset') != bool(tools):
            raise ValueError('inconsistent package kind/tools: '+str(path))
        if settings['CATALOG_CHANNEL'] not in ('any','stable','nightly'):
            raise ValueError('unsupported channel: '+str(path))
        # CATALOG_FRESH_ONLY (removed, ticket 23) is ignored so history replays;
        # tree_host_policy_source refuses it in the live tree.
        for boolean in ('REFRESH_ALWAYS','DESKTOP_STRIP_NO_SANDBOX'):
            if settings.get(boolean,'false') not in ('true','false'):
                raise ValueError('invalid recipe boolean: '+boolean)
        if layout not in ('appimage', 'raw', 'tar', 'zip', 'toolset'):
            raise ValueError('unsupported package layout: '+str(path))
        row = dict(recipe=settings['CATALOG_RECIPE'], app=app, repository_id=int(settings['CATALOG_REPOSITORY_ID']),
                   repository=settings['CATALOG_REPOSITORY'], channel=settings['CATALOG_CHANNEL'],
                   asset_pattern=settings['CATALOG_ASSET_PATTERN'], layout=layout,
                   version_identity=settings.get('VERSION_IDENTITY', 'url'),
                   refresh_always=settings.get('REFRESH_ALWAYS', 'false') == 'true',
                   settings=settings)
        row['catalog_app']=catalog_app
        if 'CATALOG_URL_RULES' in settings:
            rules=json.loads(settings['CATALOG_URL_RULES'])
            row['url_rules']=validate_url_rules(rules)
        if tools:
            row.update(tools=tools, tool_asset_suffix=settings['CATALOG_TOOL_ASSET_SUFFIX'])
        if layout in ('tar', 'zip', 'toolset'):
            row['archive'] = dict(kind=layout, root=settings.get('ARCHIVE_ROOT', '.'),
                executables=tools or settings.get('PACKAGE_EXECUTABLES', app).split(),
                launchers=[t+':'+t for t in tools] or settings.get('PACKAGE_LAUNCHERS', app+':'+app).split())
        for key, variable in (('extra_app_launchers', 'EXTRA_APP_LAUNCHERS'), ('desktop_exec', 'DESKTOP_EXEC')):
            if variable in settings:
                row[key] = settings[variable]
        rid, repository = row['repository_id'], row['repository'].lower()
        if rid in repositories and repositories[rid] != repository:
            raise ValueError('conflicting repository identity: '+str(path))
        if catalog_app in apps and apps[catalog_app] != rid:
            raise ValueError('conflicting app identity: '+str(path))
        repositories[rid], apps[catalog_app] = repository, rid
        rows.append(row)
    if not rows:
        raise ValueError('no recipe declaration headers')
    return rows


# A recipe's selection policies as CATALOG_* lines in its own header (ticket
# 26): the contiguous CATALOG_* lines right after its first CATALOG_FORMAT=3.
# A URL policy recipe has one to three selections; the 2nd and 3rd carry _2 and
# _3, and their key is <recipe>.select-N. An AppImage policy recipe has one,
# marked by CATALOG_APPIMAGE_ENDPOINT. Only a field that differs from its
# default is written.
FORMAT_LINE = 'CATALOG_FORMAT=3'
KEPT = ('CATALOG_RECIPE', 'CATALOG_ALIAS')
SELECTIONS = 3
URL_FIELDS = ('REPOSITORY_ID', 'REPOSITORY', 'CHANNEL', 'URL_RULES', 'APP', 'DISPATCH_RECIPE',
              'SOURCE_ALIASES', 'SELECTION', 'TAG_PATTERN', 'TAG_EXCLUDE', 'GIT_REF', 'GIT_FILE')
OPTIONAL = {'SELECTION': 'selection', 'TAG_PATTERN': 'tag_pattern', 'TAG_EXCLUDE': 'tag_exclude',
            'GIT_REF': 'git_ref', 'GIT_FILE': 'git_file'}
APPIMAGE_FIELDS = ('APPIMAGE_ENDPOINT', 'REPOSITORY_ID', 'CHANNEL', 'URL_RULES')
RELEASE_RULES = {'any': 'published_desc', 'stable': 'stable_published_desc'}
RECIPE = r'(x86_64|aarch64|i686|armv7l)/[a-z0-9][a-z0-9_.+-]*'
POLICY_NAME = re.compile(r'CATALOG_(?P<field>[A-Z][A-Z_]*[A-Z])(?:_(?P<n>[2-9]))?')


def literal(line):
    """NAME and value of one literal shell assignment, or ValueError."""
    name, equals, text = line.partition('=')
    tokens = shlex.split(text)
    value = tokens[0] if tokens else ''
    quoted = text == shlex.quote(value)
    double_quoted = text == '"'+value+'"' and not any(c in value for c in '$`\\"')
    if (not equals or not re.fullmatch(r'[A-Z][A-Z0-9_]*', name) or len(tokens) > 1
            or not (quoted or double_quoted or text == '')):
        raise ValueError('not a literal declaration: '+line)
    return name, value


def _block(text):
    lines = text.split('\n')
    if FORMAT_LINE not in lines:
        raise ValueError('no '+FORMAT_LINE+' line')
    start = end = lines.index(FORMAT_LINE)+1
    while end < len(lines) and re.match(r'CATALOG_[A-Z0-9_]*=', lines[end]):
        end += 1
    return lines, start, end


def _policy_name(name):
    match = POLICY_NAME.fullmatch(name)
    if not match or (match['field'] not in URL_FIELDS and match['field'] != 'APPIMAGE_ENDPOINT'):
        return None
    if match['n'] and (match['field'] not in URL_FIELDS or int(match['n']) > SELECTIONS):
        return None
    return match['field'], int(match['n'] or 1)


def _assign(name, value):
    return name+'='+shlex.quote(value)


def _rules(rules):
    return json.dumps(validate_url_rules(rules), separators=(',', ':'))


def policy_lines(urls, image):
    """The CATALOG_* lines for one recipe's URL selections (rows in order) or AppImage row."""
    if urls and image:
        raise ValueError('a recipe has URL or AppImage policies, not both')
    if image:
        channel = {rule: channel for channel, rule in RELEASE_RULES.items()}[image['release_rule']]
        if image['endpoint'] not in ('list', 'latest'):
            raise ValueError('AppImage endpoint')
        return [_assign('CATALOG_APPIMAGE_ENDPOINT', image['endpoint']),
                _assign('CATALOG_REPOSITORY_ID', str(image['repository_id'])),
                _assign('CATALOG_CHANNEL', channel), _assign('CATALOG_URL_RULES', _rules(image['rules']))]
    if len(urls) > SELECTIONS:
        raise ValueError('more than %d selections' % SELECTIONS)
    lines = []
    for n, row in enumerate(urls, 1):
        suffix = '' if n == 1 else '_%d' % n
        source = row['source_recipe']
        if row['recipe'] != (source if n == 1 else '%s.select-%d' % (source, n)):
            raise ValueError('selection key: '+row['recipe'])
        repository = row['repository']
        if repository not in row['source_aliases']:
            raise ValueError('aliases omit the repository: '+row['recipe'])
        fields = dict(REPOSITORY_ID=str(row['repository_id']), REPOSITORY=repository,
                      CHANNEL=row['channel'], URL_RULES=_rules(row['url_rules']))
        if row['catalog_app'] != source.split('/')[1]:
            fields['APP'] = row['catalog_app']
        if row['dispatch_recipe'] != row['recipe']:
            fields['DISPATCH_RECIPE'] = row['dispatch_recipe']
        extra = [alias for alias in row['source_aliases'] if alias.lower() != repository.lower()]
        if extra:
            fields['SOURCE_ALIASES'] = ' '.join(extra)
        for field, key in OPTIONAL.items():
            if key in row:
                fields[field] = row[key]
        lines += [_assign('CATALOG_'+field+suffix, value) for field, value in fields.items()]
    return lines


def with_policy(text, lines):
    """TEXT with its policy lines replaced by LINES; every other line unchanged."""
    all_lines, start, end = _block(text)
    kept = []
    for line in all_lines[start:end]:
        name = line.partition('=')[0]
        if name in KEPT:
            kept.append(line)
        elif _policy_name(name) is None:
            raise ValueError('unknown catalog declaration: '+name)
    return '\n'.join(all_lines[:start]+kept+list(lines)+all_lines[end:])


def policy_rows(recipe, text):
    """(URL policy rows in selection order, AppImage row or None) declared in TEXT."""
    if not re.fullmatch(RECIPE, recipe):
        raise ValueError('policy recipe: '+recipe)
    lines, start, end = _block(text)
    fields = {}
    for line in lines[start:end]:
        name, value = literal(line)
        if name in KEPT:
            continue
        key = _policy_name(name)
        if key is None:
            raise ValueError('unknown catalog declaration: '+name)
        if key in fields:
            raise ValueError('duplicate catalog declaration: '+name)
        fields[key] = value
    if not fields:
        return [], None
    app = recipe.split('/')[1]

    def identity(n):
        value = fields.get(('REPOSITORY_ID', n), '')
        if not re.fullmatch(r'[1-9][0-9]*', value):
            raise ValueError('policy repository id: '+recipe)
        return int(value)

    def rules(n):
        try:
            return validate_url_rules(json.loads(fields[('URL_RULES', n)]))
        except (KeyError, json.JSONDecodeError):
            raise ValueError('policy URL rules: '+recipe) from None

    if ('APPIMAGE_ENDPOINT', 1) in fields:
        if set(fields) != {(field, 1) for field in APPIMAGE_FIELDS}:
            raise ValueError('AppImage policy fields: '+recipe)
        if fields[('APPIMAGE_ENDPOINT', 1)] not in ('list', 'latest') or fields[('CHANNEL', 1)] not in RELEASE_RULES:
            raise ValueError('AppImage policy: '+recipe)
        return [], dict(recipe=recipe, repository_id=identity(1), endpoint=fields[('APPIMAGE_ENDPOINT', 1)],
                        release_rule=RELEASE_RULES[fields[('CHANNEL', 1)]], rules=rules(1))
    count = max(n for _, n in fields)
    if {n for _, n in fields} != set(range(1, count+1)):
        raise ValueError('policy selections out of order: '+recipe)
    urls = []
    for n in range(1, count+1):
        key = recipe if n == 1 else '%s.select-%d' % (recipe, n)
        repository = fields.get(('REPOSITORY', n), '')
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
            raise ValueError('policy repository: '+recipe)
        channel = fields.get(('CHANNEL', n))
        if channel not in ('any', 'stable', 'nightly'):
            raise ValueError('policy channel: '+recipe)
        catalog_app = fields.get(('APP', n), app)
        dispatch = fields.get(('DISPATCH_RECIPE', n), key)
        if not re.fullmatch(r'[a-z0-9][a-z0-9_.+-]{0,63}', catalog_app) or not re.fullmatch(
                RECIPE+r'(\.select-[2-9])?', dispatch):
            raise ValueError('policy identity: '+recipe)
        aliases = sorted({repository, *fields.get(('SOURCE_ALIASES', n), '').split()})
        row = dict(recipe=key, source_recipe=recipe, repository_id=identity(n), repository=repository,
                   channel=channel, url_rules=rules(n), catalog_app=catalog_app, dispatch_recipe=dispatch,
                   source_aliases=aliases)
        for field, name in OPTIONAL.items():
            if (field, n) in fields:
                row[name] = fields[(field, n)]
        urls.append(row)
    return urls, None
