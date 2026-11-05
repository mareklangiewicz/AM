"""Compile recipe-owned host selection settings into the trusted awk registry."""
import json
from pathlib import Path

from host_recipes import recipe_rows

ROOT = Path(__file__).resolve().parents[2]
START = '# BEGIN single-user policies\n'
END = '# END single-user policies\n'


def generate():
    rows = recipe_rows(ROOT)
    lines = [START.rstrip(), '# Generated from marked host recipes by host_policy_source.py.',
             'function host_recipe(recipe) {']
    for row in rows:
        lines.append('    if(recipe=='+json.dumps('x86_64/'+row['app'])+') { host_repository='+
            json.dumps(str(row['repository_id']))+'; host_channel='+json.dumps(row['channel'])+
            '; host_pattern='+json.dumps(row['asset_pattern'])+
            '; host_tools='+json.dumps(' '.join(row.get('tools', [])))+
            '; host_tool_suffix='+json.dumps(row.get('tool_asset_suffix', ''))+
            '; host_fresh_only='+str(int(row.get('fresh_only', False)))+'; return 1 }')
    lines += ['    return 0', '}', 'function host_eligible(name, tag, preview, tool) {',
        '    if(host_channel=="stable" && (preview!="false" || tag=="nightly")) return 0',
        '    if(host_channel=="nightly" && tag!="nightly") return 0',
        '    if(tolower(name) ~ /aarch64|arm64|armv7|i386|i686|macos|darwin|windows/) return 0',
        '    if(host_tools!="") {',
        '        tool=ENVIRON["AM_YAML_TOOL"]; split(host_tools,tools," "); if(tool=="") tool=tools[1]',
        '        if(index(" " host_tools " "," " tool " ")==0) return 0',
        '        return name==tool host_tool_suffix',
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
    guard='    if(host_fresh_only && ENVIRON["AM_YAML_ACCEPT"]!="") refuse("toolset requires fresh observations; refresh the catalog")\n'
    if guard not in source:
        source=source.replace('    if(check_only) exit\n', guard+'    if(check_only) exit\n')
    path.write_text(source)


if __name__=='__main__':generate()
