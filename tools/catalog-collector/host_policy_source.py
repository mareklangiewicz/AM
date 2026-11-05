"""Compile the single-user app manifest into trusted shell policies and recipes."""
import json
import shlex
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = Path(__file__).with_name('host-apps.json')
START = '# BEGIN single-user policies\n'
END = '# END single-user policies\n'


def generate():
    rows = json.loads(CONFIG.read_text())
    lines = [START.rstrip(), 'function host_recipe(recipe) {']
    for row in rows:
        lines.append('    if(recipe=='+json.dumps('x86_64/'+row['app'])+') { host_repository='+
            json.dumps(str(row['repository_id']))+'; host_channel='+json.dumps(row['channel'])+
            '; host_pattern='+json.dumps(row['asset_pattern'])+'; return 1 }')
    lines += ['    return 0', '}', 'function host_eligible(name, tag, preview, tool) {',
        '    if(host_channel=="stable" && (preview!="false" || tag=="nightly")) return 0',
        '    if(host_channel=="nightly" && tag!="nightly") return 0',
        '    if(tolower(name) ~ /aarch64|arm64|armv7|i386|i686|macos|darwin|windows/) return 0',
        '    if(app=="emmylua") {',
        '        tool=ENVIRON["AM_YAML_TOOL"]; if(tool=="") tool="emmylua_ls"',
        '        if(tool!="emmylua_ls" && tool!="emmylua_check" && tool!="emmylua_doc_cli" && tool!="luafmt") return 0',
        '        return name==tool "-linux-musl.tar.gz"',
        '    }', '    return name ~ host_pattern', '}', END.rstrip(), '']
    path=ROOT/'modules/catalog-yaml-policy.am'
    source=path.read_text()
    if START in source:
        before, rest=source.split(START,1); _,after=rest.split(END,1)
        source=before+after
    source=source.replace('BEGIN {\n','\n'.join(lines)+'BEGIN {\n',1)
    source=source.replace('    utility=am_utils_recipe(recipe)', '    host=host_recipe(recipe)\n    utility=am_utils_recipe(recipe)') if '    host=host_recipe(recipe)' not in source else source
    source=source.replace('known=(utility || image ||','known=(host || utility || image ||')
    source=source.replace('    if(utility && ENVIRON', '    if(host && ENVIRON["AM_YAML_REPOSITORY"]!=host_repository) refuse("host_repository_mismatch")\n    if(!host && utility && ENVIRON') if 'host_repository_mismatch' not in source else source
    source=source.replace('    if(image && ENVIRON','    if(!host && image && ENVIRON')
    source=source.replace('    if(image) {','    if(host) {\n        eligible=host_eligible(name,tag,$8)\n    } else if(image) {') if 'eligible=host_eligible' not in source else source
    source=source.replace('    print best_url\n','    print best_url\n    if(ENVIRON["AM_YAML_INCLUDE_PUBLICATION"]=="1") print best_published\n') if 'print best_published' not in source else source
    path.write_text(source)
    for row in rows:
        app=row['app'];layout=row['layout']
        text='#!/bin/sh\n# AM INSTALL SCRIPT VERSION 3.5\n# AM-CATALOG-RECIPE 1\nset -eu\n'
        text+='APP='+app+'\nCATALOG_FORMAT=2\nCATALOG_RECIPE="x86_64/'+app+'"\n'
        text+='CATALOG_ALIAS="https://api.github.com/repos/'+row['repository']+'/releases"\n'
        if layout!='appimage':text+='PACKAGE_KIND=executable\nPACKAGE_LAYOUT='+layout+'\n'
        if row['version_identity']=='published_at':text+='VERSION_IDENTITY=published_at\n'
        if row['refresh_always']:text+='REFRESH_ALWAYS=true\n'
        for key, variable in (('extra_app_launchers', 'EXTRA_APP_LAUNCHERS'),
                              ('desktop_exec', 'DESKTOP_EXEC')):
            if key in row:text+=variable+'='+shlex.quote(row[key])+'\n'
        text+='\n# shellcheck source=modules/appimage.am\n. "/opt/am/modules/appimage.am"\nam_appimage "$0" "$@"\n'
        (ROOT/'programs/x86_64'/app).write_text(text)


if __name__=='__main__':generate()
