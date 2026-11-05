"""Read literal declarations from marked host recipes, without executing shell."""
import re
import shlex

MARKER = '# AM-HOST-RECIPE 1\n'


def recipe_rows(root):
    rows = []
    for path in sorted((root/'programs/x86_64').iterdir()):
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
                raise ValueError('host recipes require literal declarations: '+str(path))
            if name in settings:
                raise ValueError('duplicate recipe declaration: '+name)
            settings[name] = value
        app = settings['APP']
        if app != path.name or settings['CATALOG_RECIPE'] != 'x86_64/'+app:
            raise ValueError('host recipe identity mismatch: '+str(path))
        tools = settings.get('PACKAGE_TOOLS', '').split()
        layout = settings.get('PACKAGE_LAYOUT', 'appimage')
        if layout not in ('appimage', 'raw', 'tar', 'zip', 'toolset'):
            raise ValueError('unsupported host package layout: '+str(path))
        row = dict(app=app, repository_id=int(settings['CATALOG_REPOSITORY_ID']),
                   repository=settings['CATALOG_REPOSITORY'], channel=settings['CATALOG_CHANNEL'],
                   asset_pattern=settings['CATALOG_ASSET_PATTERN'], layout=layout,
                   version_identity=settings.get('VERSION_IDENTITY', 'url'),
                   refresh_always=settings.get('REFRESH_ALWAYS', 'false') == 'true',
                   settings=settings)
        if tools:
            row.update(tools=tools, tool_asset_suffix=settings['CATALOG_TOOL_ASSET_SUFFIX'],
                       fresh_only=settings.get('CATALOG_FRESH_ONLY', 'false') == 'true')
        if layout in ('tar', 'zip', 'toolset'):
            row['archive'] = dict(kind=layout, root=settings.get('ARCHIVE_ROOT', '.'),
                executables=tools or settings.get('PACKAGE_EXECUTABLES', app).split(),
                launchers=[t+':'+t for t in tools] or settings.get('PACKAGE_LAUNCHERS', app+':'+app).split())
        for key, variable in (('extra_app_launchers', 'EXTRA_APP_LAUNCHERS'), ('desktop_exec', 'DESKTOP_EXEC')):
            if variable in settings:
                row[key] = settings[variable]
        rows.append(row)
    if not rows:
        raise ValueError('no marked host recipes')
    return rows
