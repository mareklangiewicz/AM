#!/usr/bin/env python3
"""Convert an original recipe to a recipe declaration or a long recipe.

One entry point for both forms. No recipe shell is executed and nothing is
fetched: the original is read as text, and the catalog source identity is an
input. Whatever the conversion cannot account for is a Refusal, never a guess.

A recipe declaration is only produced from an original that is, line for line,
an instance of a reviewed upstream AppImage template (layouts.json) whose
release selector is a literal filter pipeline. A long recipe keeps the
original's install steps and replaces its release selection.
"""
import argparse
from dataclasses import dataclass,field
import hashlib
import json
from pathlib import Path
import re
import shlex
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/catalog-collector'),str(ROOT/'tools/recipe-reconstruction')]
import bulk_recipes
import bulk_recipe_urls
from originals import Originals,Template

FORMS=('declaration','long')
RECIPE=r'(x86_64|aarch64|i686|armv7l)/[a-z0-9][a-z0-9_.+-]*'
REPOSITORY=r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+'
LAYOUTS=Path(__file__).with_name('layouts.json')
SITE=re.compile(r'''\bSITE[0-9]+=["']('''+REPOSITORY+r''')["']''')
SELECTION=re.compile(r'curl -Ls\s+(?P<quote>["\']?)(?P<url>https://api[.]github[.]com/repos/(?P<site>'+REPOSITORY
    +r')/releases(?:/latest)?(?:\?per_page=100)?)(?P=quote)\s*\|\s*(?P<selector>[^\n]+)')
# The same literal written with other quotes. Upstream's generator writes
# APP=x and SITE="x"; hand-kept recipes also use single quotes.
QUOTING=((re.compile(r"(?m)^APP='([a-z0-9][a-z0-9.+_-]*)'$"),r'APP=\1'),
         (re.compile(r"(?m)^SITE='("+REPOSITORY+r")'$"),r'SITE="\1"'))


class Refusal(ValueError):
    """The conversion cannot account for this original; nothing was produced."""


@dataclass
class Layout(Template):
    """A reviewed template body and the declaration settings that reproduce
    what its install steps do beyond the shared installer's defaults."""
    settings:dict=field(default_factory=dict)


# Settings a review may attach to a layout, with their allowed literal values.
LAYOUT_SETTINGS={'DESKTOP_STRIP_NO_SANDBOX':{'true'}}


def layouts(repo=ROOT):
    """Reviewed upstream AppImage template bodies, read from pinned Git objects."""
    originals=Originals(repo);result=[]
    for row in json.loads(LAYOUTS.read_text()):
        body=originals.read(row['commit'],row['path'])
        if hashlib.sha256(body.encode()).hexdigest()!=row['sha256']:
            raise ValueError('layout differs from its reviewed hash: '+row['commit'])
        settings=row.get('settings',{})
        if any(value not in LAYOUT_SETTINGS.get(key,()) for key,value in settings.items()):
            raise ValueError('layout setting not supported: '+row['commit'])
        result.append(Layout(row['commit'],row['path'],body,'',dict(settings)))
    return result


def recognize(source,templates):
    """APP, SITE and the one release selection of a whole-template instance."""
    for pattern,plain in QUOTING:source=pattern.sub(plain,source)
    for template in templates:
        match=template.match(source)
        if match:break
    else:raise Refusal('not an instance of a reviewed AppImage template')
    values={}
    for slot,value in zip(template.slots,match['parameters']):values.setdefault(slot,set()).add(value)
    if set(values)!={'SAMPLE','REPLACETHIS','FUNCTION'} or any(len(found)!=1 for found in values.values()):
        raise Refusal('installer and updater disagree')
    app,site,function=(next(iter(values[slot])) for slot in ('SAMPLE','REPLACETHIS','FUNCTION'))
    if not re.fullmatch(REPOSITORY,site):raise Refusal('SITE is not a literal repository')
    selection=SELECTION.fullmatch(function)
    if not selection:raise Refusal('release selection is not one GitHub releases read')
    if selection['site'].lower()!=site.lower():raise Refusal('SITE and the release selection name different repositories')
    return dict(app=app,site=site,alias=selection['url'],selector=selection['selector'],template=template.identity,
                settings=getattr(template,'settings',{}))


def to_declaration(source,recipe,identities,templates):
    if len(identities)!=1:raise Refusal('a recipe declaration has exactly one catalog source')
    identity=identities[0]
    found=recognize(source,templates)
    row=dict(status='verified',repository_id=identity['repository_id'],repository=identity['repository'],
             requested_repository=identity.get('requested_repository',identity['repository']))
    if 'catalog_app' in identity:row['catalog_app']=identity['catalog_app']
    try:
        text,_=bulk_recipes.declare(dict(APP=found['app'],CATALOG_ALIAS=found['alias'],**found['settings']),
                                    found['selector'],recipe,row)
    except ValueError as error:raise Refusal(str(error)) from error
    return dict(form='declaration',text=text,policies=[],template=found['template'])


def to_long(source,recipe,identities):
    bindings=[]
    for identity in identities:
        binding=dict(repository=identity['repository'],repository_id=identity['repository_id'],
                     catalog_app=identity.get('catalog_app',recipe.split('/')[1]))
        if 'requested_repository' in identity:binding['requested_repository']=identity['requested_repository']
        bindings.append(binding)
    # A recipe that picks its repository at run time reads "$RELEASE"; the
    # policies then cover only the identities given. Every repository it
    # offers (SITE1, SITE2, ...) must be among them, or a choice would refuse
    # at install time instead of here.
    known={name.lower() for binding in bindings for name in (binding['repository'],binding.get('requested_repository',''))}
    for site in SITE.findall(source) if bulk_recipe_urls.DYNAMIC.search(source) else ():
        if site.lower() not in known:raise Refusal('no verified identity for source: '+site)
    try:
        text,policies,_=bulk_recipe_urls.translate(source,recipe,bindings)
    except ValueError as error:raise Refusal(str(error)) from error
    return dict(form='long',text=text,policies=policies)


def declaration_identities(text):
    """The catalog source a recipe declaration is bound to."""
    settings={}
    for line in text.partition(bulk_recipes.SEAM)[0].splitlines():
        name,equals,literal=line.partition('=')
        if equals and re.fullmatch(r'[A-Z][A-Z0-9_]*',name):
            words=shlex.split(literal)
            settings[name]=words[0] if len(words)==1 else ''
    alias=re.fullmatch(r'https://api[.]github[.]com/repos/('+REPOSITORY+r')/releases.*',settings.get('CATALOG_ALIAS',''))
    if (not re.fullmatch(r'[1-9][0-9]*',settings.get('CATALOG_REPOSITORY_ID',''))
            or not re.fullmatch(REPOSITORY,settings.get('CATALOG_REPOSITORY',''))):
        raise Refusal('declaration has no literal repository identity')
    identity=dict(repository_id=int(settings['CATALOG_REPOSITORY_ID']),repository=settings['CATALOG_REPOSITORY'])
    if alias:identity['requested_repository']=alias[1]
    if settings.get('CATALOG_APP'):identity['catalog_app']=settings['CATALOG_APP']
    return [identity]


def policy_identities(rows):
    """The catalog sources a long recipe's selection policies are bound to."""
    identities=[]
    for row in rows:
        for alias in row['source_aliases']:
            identity=dict(repository_id=row['repository_id'],repository=row['repository'],catalog_app=row['catalog_app'])
            if alias!=row['repository']:identity['requested_repository']=alias
            if identity not in identities:identities.append(identity)
    # A source known under another name is listed once, under that name.
    renamed={identity['repository_id'] for identity in identities if 'requested_repository' in identity}
    return [identity for identity in identities
            if 'requested_repository' in identity or identity['repository_id'] not in renamed]


def convert(source,recipe,form,identities,templates=None):
    """Return the converted text and its selection policies, or raise Refusal.

    identities: the recipe's verified catalog sources, one per repository it
    selects from. Each has repository_id and repository, and optionally
    requested_repository (the name the original uses, when it differs) and
    catalog_app (when it differs from the app name).
    """
    if form not in FORMS:raise ValueError('unknown form: '+str(form))
    if not re.fullmatch(RECIPE,recipe):raise ValueError('recipe must be ARCH/APP')
    if not identities:raise Refusal('no verified catalog source')
    for identity in identities:
        if (type(identity.get('repository_id')) is not int or identity['repository_id']<1
                or not re.fullmatch(REPOSITORY,identity.get('repository',''))):
            raise ValueError('identity needs a numeric repository_id and OWNER/NAME repository')
    if '# AM-CATALOG-RECIPE 1\n' in source:raise Refusal('already converted')
    if form=='declaration':
        return to_declaration(source,recipe,identities,layouts() if templates is None else templates)
    return to_long(source,recipe,identities)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('original',type=Path,help='file holding the original recipe')
    parser.add_argument('--recipe',required=True,help='ARCH/APP, for example x86_64/0xfx')
    parser.add_argument('--form',required=True,choices=FORMS)
    parser.add_argument('--repository-id',type=int)
    parser.add_argument('--repository',help='verified OWNER/NAME of the catalog source')
    parser.add_argument('--requested-repository',help='name the original uses, when it differs')
    parser.add_argument('--catalog-app',help='catalog app name, when it differs from APP')
    parser.add_argument('--identities',type=Path,help='JSON list of sources, for a recipe with several')
    parser.add_argument('--policies',type=Path,help='write the long recipe selection policies here (JSON)')
    args=parser.parse_args(argv)
    if args.identities:
        if args.repository_id or args.repository:parser.error('--identities replaces the single-source options')
        identities=json.loads(args.identities.read_text())
    else:
        if not args.repository_id or not args.repository:parser.error('--repository-id and --repository are required')
        identities=[dict(repository_id=args.repository_id,repository=args.repository)]
        if args.requested_repository:identities[0]['requested_repository']=args.requested_repository
        if args.catalog_app:identities[0]['catalog_app']=args.catalog_app
    try:
        result=convert(args.original.read_text(),args.recipe,args.form,identities)
    except Refusal as refusal:
        print('refused: '+str(refusal),file=sys.stderr)
        return 2
    if result['policies'] and not args.policies:
        print('refused: a long recipe needs --policies for its selection policies',file=sys.stderr)
        return 2
    if args.policies:args.policies.write_text(json.dumps(result['policies'],indent=2)+'\n')
    sys.stdout.write(result['text'])
    return 0


if __name__=='__main__':sys.exit(main())
