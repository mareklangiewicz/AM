"""Translate exact legacy shared AppImage wrappers to literal v3 declarations.

No source shell is executed. The existing shared installer lifecycle is retained;
only the retired JSON selection function becomes trusted URL predicate data.
Unknown commands/settings, ambiguous identities and unavailable sources refuse.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex

from catalog_sources import ROOT, literals
from recipe_declarations import recipe_rows
from recipe_policy_source import generate
from host_catalog import utc

SEAM='# shellcheck source=modules/appimage.am\n'
TAIL='. "/opt/am/modules/appimage.am"\nam_appimage "$0" "$@"\n'
SETTINGS={'APP','CATALOG_ALIAS','EXTRA_APP_LAUNCHERS','DESKTOP_EXEC','DESKTOP_STRIP_NO_SANDBOX'}


def ere(bre):
    result='';i=0
    while i<len(bre):
        char=bre[i]
        if char=='\\':
            i+=1
            if i==len(bre) or bre[i] not in '|.[]*^$\\()+?{}':
                raise ValueError('unsupported BRE escape')
            char=bre[i]
            result+=char if char in '|()+?{}' else '\\'+char
        else:
            result+=('\\'+char if char in '+?(){}|' else char)
        i+=1
    return result


def url_rules(selector,*,require_appimage=True):
    lexer=shlex.shlex(selector,posix=True,punctuation_chars='|');lexer.whitespace_split=True;lexer.commenters=''
    tokens=list(lexer)
    stages=[[]]
    for token in tokens:
        if token=='|':stages.append([])
        else:stages[-1].append(token)
    splitter=stages[0] in (['sed','s/[()",{} ]/\\n/g'],
                         ['sed','s/[()",{}]/ /g; s/ /\\n/g'],['sed','s/[",{} ]/\\n/g'])
    if not require_appimage and len(stages[0])==3 and stages[0][0]=='tr' and stages[0][2]=='\\n':
        splitter=all(c in '\\">< ' for c in stages[0][1])
    if (len(stages)<3 or not splitter or stages[-1] not in
            (['head','-1'],['head','-n1'],['head','-n','1'])):
        raise ValueError('unsupported selector pipeline')
    rules=[];extractions=0
    for index,stage in enumerate(stages[1:-1]):
        if len(stage)==2 and stage[0]=='grep':stage=['grep','',stage[1]]
        flags=stage[1][1:] if len(stage)==3 and stage[1].startswith('-') else ''
        if (len(stage)!=3 or stage[0]!='grep' or (stage[1] and not stage[1].startswith('-')) or
                any(c not in 'Eiov' for c in flags) or not 1<=len(stage[2])<=512):
            raise ValueError('unsupported selector predicate')
        if 'o' in flags:
            extractions+=1
            if extractions>1 or not stage[2].lower().startswith('https') or 'v' in flags:
                raise ValueError('unsupported URL extraction')
        pattern=stage[2] if 'E' in flags else ere(stage[2])
        if any(c in pattern for c in '\n\r\0'):
            raise ValueError('invalid predicate')
        rules.append(dict(pattern=pattern,ignore_case='i' in flags,exclude='v' in flags))
    # This translator only claims raw AppImages. An archive selector needs a
    # separately established payload layout, not a guessed extension contract.
    if require_appimage and (extractions!=1 or not any(not rule['exclude'] and rule['pattern'].lower().endswith('mage$') for rule in rules)):
        raise ValueError('selector does not establish a direct AppImage suffix')
    if not any(not rule['exclude'] and
               (re.match(r'^\^?https?',rule['pattern'].lower()) or 'download' in rule['pattern'].lower())
               for rule in rules):
        raise ValueError('selector does not establish an asset URL')
    return rules


def translate(source,recipe,identity):
    if source.count('select_asset() {\n')!=1 or source.count(SEAM)!=1:
        raise ValueError('not a legacy shared wrapper')
    before,rest=source.split('select_asset() {\n')
    selector,after=rest.split('\n}',1)
    if after!='\n\n'+SEAM+TAIL:
        raise ValueError('custom wrapper tail')
    settings={}
    for line in before.splitlines():
        if not line or line.startswith('#') or line=='set -eu':continue
        key,equals,value=line.partition('=')
        words=shlex.split(value)
        if not equals or key not in SETTINGS or key in settings or len(words)!=1:
            raise ValueError('custom wrapper setting')
        decoded=words[0]
        if value!=shlex.quote(decoded) and value!='"'+decoded+'"':
            raise ValueError('nonliteral wrapper setting')
        if any(c in decoded for c in '$`\\\n\r\0'):
            raise ValueError('nonliteral wrapper setting')
        settings[key]=decoded
    if settings.get('APP')!=recipe.split('/')[1]:raise ValueError('app identity')
    if identity['status'] not in ('verified','no_public_release','retained_identity'):
        raise ValueError('source has no verified public identity')
    requested=identity['requested_repository']
    endpoint=re.fullmatch(r'https://api[.]github[.]com/repos/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/releases(/latest)?(?:\?per_page=100)?',settings.get('CATALOG_ALIAS',''))
    if not endpoint or endpoint[1].lower()!=requested.lower():
        raise ValueError('source alias mismatch')
    rules=url_rules(selector.strip())
    settings.update(CATALOG_FORMAT='3',CATALOG_RECIPE=recipe,
        CATALOG_REPOSITORY_ID=str(identity['repository_id']),CATALOG_REPOSITORY=identity['repository'],
        CATALOG_CHANNEL='stable' if endpoint[2] else 'any',CATALOG_ASSET_PATTERN='^.*$',
        CATALOG_URL_RULES=json.dumps(rules,separators=(',',':')))
    if identity.get('catalog_app',settings['APP'])!=settings['APP']:settings['CATALOG_APP']=identity['catalog_app']
    result=('#!/bin/sh\n# AM INSTALL SCRIPT VERSION 3.5\n# AM-CATALOG-RECIPE 1\n'
        '# AM-RECIPE-DECLARATION 1\nset -eu\n'+
        ''.join(key+'='+shlex.quote(value)+'\n' for key,value in settings.items())+'\n'+SEAM+TAIL)
    return result,rules


def plan(scan,identities,enrollment=None):
    known={row['requested_repository'].lower():row for row in identities['repositories']}
    ready=[];exceptions=[]
    aliases={(row['recipe'],row['repository_id']):row for row in (enrollment or {}).get('bindings',[])}
    seen=set()
    for candidate in scan['candidates']+scan.get('ambiguous',[]):
        for proof in candidate['bindings']:
            path=ROOT/proof['recipe'];raw=path.read_bytes();source=raw.decode('utf-8')
            if '# AM-CATALOG-RECIPE 1\n' not in source or 'CATALOG_FORMAT=3' in source or proof['recipe'] in seen:continue
            seen.add(proof['recipe'])
            if hashlib.sha256(raw).hexdigest()!=proof['sha256']:raise ValueError('stale before-image')
            identity=known.get(proof['repository'].lower())
            if identity:
                identity=dict(identity)
                alias=aliases.get((proof['recipe'],identity.get('repository_id')))
                if alias:identity['catalog_app']=alias['catalog_app']
            try:
                if identity is None:raise ValueError('identity not verified')
                result,rules=translate(source,proof['recipe'].removeprefix('programs/'),identity)
                ready.append(dict(recipe=proof['recipe'],before_sha256=proof['sha256'],
                    after_sha256=hashlib.sha256(result.encode()).hexdigest(),after=result,
                    repository_id=identity['repository_id'],repository=identity['repository'],
                    selector_rules=rules,identity_evidence=identity['evidence'],
                    identity_evidence_sha256=identity['evidence_sha256']))
            except ValueError as error:exceptions.append(dict(recipe=proof['recipe'],reason=str(error)))
    return dict(source=scan['source'],observed_at=utc(),ready=ready,exceptions=exceptions)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scan',type=Path,required=True)
    parser.add_argument('--identities',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--enrollment',type=Path)
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    result=plan(json.loads(args.scan.read_text()),json.loads(args.identities.read_text()),
                json.loads(args.enrollment.read_text()) if args.enrollment else None)
    if args.out.exists():raise ValueError('refusing to overwrite receipt')
    if args.apply:
        for row in result['ready']:(ROOT/row['recipe']).write_text(row['after'])
        recipe_rows(ROOT)
        generate()
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(ready=len(result['ready']),exceptions=len(result['exceptions']),applied=args.apply)))


if __name__=='__main__':main()
