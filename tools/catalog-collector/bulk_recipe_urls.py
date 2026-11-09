"""Move literal release-selection pipelines to v3, preserving installer bodies.

Recognized URL predicates become trusted policy data. Package staging, launchers,
desktop entries and embedded updater bodies stay in their original recipes.
Only the exact legacy appimageupdatetool bypass is removed: v3 selects the asset.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess

import host_catalog as host
from bulk_recipes import url_rules
from recipe_policy_source import generate

REPOSITORY=r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+'
VERSION=re.compile(r'''version=(?P<outer>"?)\$\(curl -Ls\s+(?P<quote>["']?)(?P<url>https://api[.]github[.]com/repos/'''
    +REPOSITORY+r'''/releases(?:/latest)?(?:\?per_page=100)?)(?P=quote)\s*\|\s*(?P<selector>[^\n]+)\)(?P=outer)''')
DYNAMIC=re.compile(r'''version=\$\(curl -Ls\s+https://api[.]github[.]com/repos/(?P<site>"\$RELEASE"|REPLACETHIS)/releases(?P<latest>/latest)?\s*\|\s*(?P<selector>[^\n]+)\)''')
BYPASS=('if command -v appimageupdatetool >/dev/null 2>&1; then\n'
    '\tcd "/opt/$APP" || exit 1\n'
    '\tappimageupdatetool -Or ./"$APP" && chmod a+x ./"$APP" && echo "$version" > ./version && exit 0\nfi\n')
HEADER='# AM-CATALOG-RECIPE 1\nCATALOG_FORMAT=3\nAMREPO=${AMREPO-}\nexport AMREPO\n'
BYPASS_PATTERN=re.compile(r'(?m)^[ \t]*if command -v appimageupdatetool >/dev/null 2>&1; then\n'
    r'[ \t]+cd "/opt/\$APP" \|\| exit 1\n'
    r'[ \t]+appimageupdatetool -Or ./"\$APP" && chmod a\+x ./"\$APP" && echo "\$version" > ./version && exit 0\n[ \t]*fi\n')


def translate(source,recipe,bindings):
    if '# AM-CATALOG-RECIPE 1\n' in source:raise ValueError('shared or already migrated recipe')
    known={row['repository'].lower():row for row in bindings}
    # Requested aliases are recorded separately from canonical numeric identity.
    for row in bindings:
        if row.get('requested_repository'):known[row['requested_repository'].lower()]=row
    policies={};changes=[]
    def predicates(selector):
        selector=selector.replace('${APP}','$APP')
        if re.search(r'\$[A-Za-z_{(0-9@*?#$!]',selector.replace('$APP','')) or '`' in selector:
            raise ValueError('dynamic selector')
        # Only a literal, repeated APP may parameterize a URL predicate.
        from catalog_sources import literals
        apps=literals(source,'APP')
        if '$APP' in selector:
            if not apps or len(set(apps))!=1:raise ValueError('dynamic APP selector')
            selector=selector.replace('$APP',apps[0])
        return url_rules(selector,require_appimage=False)
    def policy(binding,channel,rules,requested):
        identity=json.dumps([binding['repository_id'],channel,rules],sort_keys=True)
        if identity not in policies:
            key=recipe if not policies else recipe+'.select-'+str(len(policies)+1)
            policies[identity]=dict(recipe=key,source_recipe=recipe,source_sha256='',
                repository_id=binding['repository_id'],repository=binding['repository'],channel=channel,
                url_rules=rules,catalog_app=binding['catalog_app'],dispatch_recipe=key,
                source_aliases=sorted({binding['repository'],requested}))
        return policies[identity]
    def replace(match):
        url=match['url'];requested=re.search(r'/repos/('+REPOSITORY+r')/releases',url)[1]
        binding=known.get(requested.lower())
        if binding is None:raise ValueError('unverified selection source: '+requested)
        rules=predicates(match['selector'])
        channel='stable' if '/releases/latest' in url else 'any'
        key=policy(binding,channel,rules,requested)['recipe']
        changes.append(dict(original=match[0],policy=key,requested_repository=requested))
        return 'version=$(sh "/opt/am/modules/catalog-yaml.am" '+shlex.quote(key)+' --url "$@") || exit 1'
    changed=VERSION.sub(replace,source)
    def dynamic(match):
        rules=predicates(match['selector']);channel='stable' if match['latest'] else 'any'
        dispatch=None
        for binding in bindings:
            row=policy(binding,channel,rules,binding.get('requested_repository',binding['repository']))
            dispatch=dispatch or row['recipe'];row['dispatch_recipe']=dispatch
        if dispatch is None:raise ValueError('unverified variant sources')
        changes.append(dict(original=match[0],policy=dispatch,requested_repository=match['site']))
        return ('version=$(sh "/opt/am/modules/catalog-yaml.am" '+shlex.quote(dispatch)+
                ' --source-repository '+match['site']+' --url "$@") || exit 1')
    changed=DYNAMIC.sub(dynamic,changed)
    if not changes:raise ValueError('no supported literal URL selection')
    if 'api.github.com/repos/' in changed:raise ValueError('unconverted API selection or auxiliary API read')
    changed=BYPASS_PATTERN.sub('',changed)
    if re.search(r'(?m)^[ \t]*appimageupdatetool\s+-',changed):raise ValueError('custom native-update bypass')
    changed,count=re.subn(r'(?m)^(#!/bin/(?:ba)?sh\n)',lambda m:m[0]+HEADER,changed)
    if not count or not source.startswith('#!'):raise ValueError('unsupported shell binding')
    # Both installer and quoted embedded updater receive persisted source/module
    # bindings through the existing catalog-recipe manager path.
    result=subprocess.run(['bash' if source.startswith('#!/bin/bash') else 'sh','-n'],
        input=changed,text=True,capture_output=True)
    if result.returncode:raise ValueError('translated shell syntax')
    digest=hashlib.sha256(changed.encode()).hexdigest()
    for row in policies.values():row['source_sha256']=digest
    return changed,list(policies.values()),changes


def plan(enrollment):
    groups={}
    for binding in enrollment['bindings']:
        groups.setdefault(binding['recipe'],[]).append(binding)
    ready=[];exceptions=[];policies=[]
    for path,bindings in sorted(groups.items()):
        raw=(host.ROOT/path).read_bytes();source=raw.decode('utf-8')
        if '# AM-CATALOG-RECIPE 1\n' in source:continue
        if any(hashlib.sha256(raw).hexdigest()!=row['sha256'] for row in bindings):raise ValueError('stale recipe: '+path)
        try:
            changed,rows,changes=translate(source,path.removeprefix('programs/'),bindings)
            ready.append(dict(recipe=path,before_sha256=hashlib.sha256(raw).hexdigest(),
                after_sha256=hashlib.sha256(changed.encode()).hexdigest(),after=changed,changes=changes))
            policies.extend(rows)
        except ValueError as error:exceptions.append(dict(recipe=path,reason=str(error)))
    return dict(source=enrollment['source'],observed_at=host.utc(),ready=ready,exceptions=exceptions,policies=policies)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--enrollment',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    result=plan(json.loads(args.enrollment.read_text()))
    if args.out.exists():raise ValueError('receipt already exists')
    if args.apply:
        policy_path=host.ROOT/'tools/catalog-collector/recipe-url-policies.json'
        if policy_path.exists():raise ValueError('existing URL policies need explicit merge')
        for row in result['ready']:(host.ROOT/row['recipe']).write_text(row['after'])
        policy_path.write_text(json.dumps(result['policies'],indent=2)+'\n')
        generate()
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(recipes=len(result['ready']),policies=len(result['policies']),exceptions=len(result['exceptions']))))


if __name__=='__main__':main()
