"""Read literal declarations from recipe declaration headers, without executing shell."""
import re
import shlex

MARKER = '# AM-RECIPE-DECLARATION 1\n'


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
        if settings['CATALOG_FORMAT'] != '2':
            raise ValueError('unsupported declaration format: '+str(path))
        if (not re.fullmatch(r'[1-9][0-9]*', settings['CATALOG_REPOSITORY_ID']) or
                not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', settings['CATALOG_REPOSITORY'])):
            raise ValueError('invalid repository identity: '+str(path))
        app = settings['APP']
        if not re.fullmatch(r'[a-z0-9][a-z0-9_.+-]*', app):
            raise ValueError('invalid app identity: '+str(path))
        if app != path.name or settings['CATALOG_RECIPE'] != path.parent.name+'/'+app:
            raise ValueError('recipe identity mismatch: '+str(path))
        tools = settings.get('PACKAGE_TOOLS', '').split()
        kind = settings.get('PACKAGE_KIND', 'appimage')
        layout = settings.get('PACKAGE_LAYOUT', 'raw' if kind == 'executable' else 'appimage')
        if kind not in ('appimage','executable') or (layout == 'toolset') != bool(tools):
            raise ValueError('inconsistent package kind/tools: '+str(path))
        if settings['CATALOG_CHANNEL'] not in ('any','stable','nightly'):
            raise ValueError('unsupported channel: '+str(path))
        for boolean in ('REFRESH_ALWAYS','CATALOG_FRESH_ONLY'):
            if settings.get(boolean,'false') not in ('true','false'):
                raise ValueError('invalid recipe boolean: '+boolean)
        if layout not in ('appimage', 'raw', 'tar', 'zip', 'toolset'):
            raise ValueError('unsupported package layout: '+str(path))
        row = dict(recipe=settings['CATALOG_RECIPE'], app=app, repository_id=int(settings['CATALOG_REPOSITORY_ID']),
                   repository=settings['CATALOG_REPOSITORY'], channel=settings['CATALOG_CHANNEL'],
                   asset_pattern=settings['CATALOG_ASSET_PATTERN'], layout=layout,
                   version_identity=settings.get('VERSION_IDENTITY', 'url'),
                   refresh_always=settings.get('REFRESH_ALWAYS', 'false') == 'true',
                   fresh_only=settings.get('CATALOG_FRESH_ONLY', 'false') == 'true',
                   settings=settings)
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
        if app in apps and apps[app] != rid:
            raise ValueError('conflicting app identity: '+str(path))
        repositories[rid], apps[app] = repository, rid
        rows.append(row)
    if not rows:
        raise ValueError('no recipe declaration headers')
    return rows
