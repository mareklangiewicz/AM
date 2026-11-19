#!/usr/bin/env python3
"""Re-convert the recipes a reviewed layout covers (ticket 35).

    relayout.py --layout COMMIT[:PATH] [--from FORM] [--upstream REV]   dry run
    relayout.py --layout COMMIT[:PATH] [--from FORM] --write            write recipes and derived files

Every converted recipe whose original at merge-base(HEAD, upstream) is an
instance of that layout (convert.layouts) is converted again as a recipe
declaration from its own identities. A recipe whose conversion would select
differently (any of FIELDS: repository, channel, asset pattern, URL rules,
catalog app, fresh-only, release/tag/Git selection, tools) is refused and left as it is. The derived files come from the
upstream merge tool (merge.derive, merge.stage). It never commits.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import tempfile

import merge
from merge import ROOT,Problem,convert,recipe_rows,url_policy_rows

# What a recipe selects: compared before and after a re-conversion. A missing
# field is its default, so an explicit default is not a change.
FIELDS=('recipe','repository_id','repository','channel','asset_pattern','url_rules','catalog_app','fresh_only',
        'selection','tag_pattern','tag_exclude','git_ref','git_file','tools','tool_asset_suffix')
DEFAULTS={'url_rules':[],'selection':'asset'}


def selections(recipes,policies):
    """The compiled selection rows of these recipes, by recipe path."""
    with tempfile.TemporaryDirectory(prefix='am-relayout-') as temporary:
        tree=Path(temporary)
        for path,data in recipes.items():
            (tree/path).parent.mkdir(parents=True,exist_ok=True);(tree/path).write_bytes(data)
        (tree/merge.REGISTRY).parent.mkdir(parents=True,exist_ok=True)
        (tree/merge.REGISTRY).write_text(json.dumps(policies))
        declared=any(merge.MARKER.encode() in data for data in recipes.values())
        rows=url_policy_rows(tree)+(recipe_rows(tree) if declared else [])
    found={}
    for row in rows:
        selection={field:row.get(field,DEFAULTS.get(field)) for field in FIELDS}
        found.setdefault('programs/'+row.get('source_recipe',row['recipe']),[]).append(selection)
    return {path:sorted(found.get(path,[]),key=lambda row:json.dumps(row,sort_keys=True)) for path in recipes}


def changes(before,before_policies,after,after_policies):
    """What selects differently, by recipe path: the changed fields, or the row counts."""
    old,new=selections(before,before_policies),selections(after,after_policies);found={}
    for path in sorted(set(old)|set(new)):
        a,b=old.get(path,[]),new.get(path,[])
        if a==b:continue
        if len(a)!=len(b):found[path]=f'{len(a)} selection rows before, {len(b)} after';continue
        found[path]=', '.join(sorted({field for x,y in zip(a,b) for field in FIELDS if x[field]!=y[field]}))+' changed'
    return found


def differences(before,before_policies,after,after_policies):
    """One line per recipe whose selection rows differ between the two states."""
    return [path.removeprefix('programs/')+': '+reason
            for path,reason in changes(before,before_policies,after,after_policies).items()]


def chosen(layouts,name):
    """The one reviewed layout named COMMIT (a prefix) or COMMIT:PATH."""
    commit,_,path=name.partition(':')
    found=[layout for layout in layouts if layout.commit.startswith(commit) and path in ('',layout.path)]
    if len(found)!=1:
        raise Problem(f'{len(found)} reviewed layouts match {name!r}'
                      +(': '+', '.join(layout.identity for layout in found)+'; name one as COMMIT:PATH' if found else ''))
    return found[0]


def plan(root,layout,ours='HEAD',upstream='upstream/main',forms=convert.FORMS):
    """Re-convert, as declarations from this one layout, every converted recipe
    whose original at merge-base(ours, upstream) is an instance of it and
    whose form is one of forms. A recipe whose conversion would select
    differently is refused and left as it is.

    Changes nothing. Returns the recipe rows (merge.plan's vocabulary:
    're-converted' or 'untouched'), the derived files that change, the
    recipes the layout covers but that refuse (path -> reason), sources to
    retire, and the selection differences (empty when nothing selects
    differently)."""
    ours=merge.git(root,'rev-parse','--verify',ours+'^{commit}').stdout.decode().strip()
    base=merge.git(root,'merge-base',ours,upstream).stdout.decode().strip()
    layout=chosen(convert.layouts(root),layout)
    fork,originals=merge.recipes(root,ours),merge.recipes(root,base)
    registry=json.loads(merge.text(root,ours,merge.REGISTRY));by_recipe={}
    for policy in registry:by_recipe.setdefault(policy['source_recipe'],[]).append(policy)
    rows,refused=[],{}
    for path,data in sorted(fork.items()):
        rows.append(row:=dict(path=path,outcome='untouched',data=data))
        before,original=merge.form(data),originals.get(path)
        if before not in forms or original is None:continue
        recipe=path.removeprefix('programs/')
        try:
            source=original.decode('utf-8');convert.recognize(source,[layout])
        except (convert.Refusal,UnicodeDecodeError):continue
        try:
            identities=(convert.declaration_identities(data.decode()) if before=='declaration'
                        else convert.policy_identities(by_recipe.get(recipe,[])))
            result=convert.convert(source,recipe,'declaration',identities,[layout])
        except convert.Refusal as refusal:
            refused[path]=str(refusal);continue
        if result['text'].encode()!=data:
            row.update(outcome='re-converted',form_before=before,form_after='declaration',
                       data=result['text'].encode(),policies=[],identities=identities)
    candidates=[row for row in rows if row['outcome']=='re-converted']
    selecting=changes({row['path']:fork[row['path']] for row in candidates},
                      [policy for row in candidates for policy in by_recipe.get(row['path'].removeprefix('programs/'),[])],
                      {row['path']:row['data'] for row in candidates},[])
    for row in candidates:
        if row['path'] in selecting:
            refused[row['path']]='selection would change: '+selecting[row['path']]
            for key in ('form_before','form_after','policies','identities'):row.pop(key)
            row.update(outcome='untouched',data=fork[row['path']])
    files,retire=merge.derive(root,ours,rows)
    files[merge.POLICY]=merge.stage(root,ours,rows,files)
    files={path:content for path,content in files.items() if content!=merge.text(root,ours,path)}
    converted={row['path'] for row in rows if row['outcome']=='re-converted'}
    after=json.loads(files.get(merge.REGISTRY,json.dumps(registry)))
    mine=lambda policies,inside:[p for p in policies if ('programs/'+p['source_recipe'] in converted)==inside]
    found=differences({path:fork[path] for path in converted},mine(registry,True),
                      {row['path']:row['data'] for row in rows if row['path'] in converted},mine(after,True))
    if mine(registry,False)!=mine(after,False):found.append('policy rows of recipes not re-converted changed')
    return dict(ours=ours,base=base,layout=layout.identity,rows=rows,files=files,refused=refused,
                retire=retire,differences=found)


def write(root,result):
    """Write the re-converted recipes and changed derived files into a checkout
    at the planned commit with those paths unmodified."""
    head=merge.git(root,'rev-parse','HEAD').stdout.decode().strip()
    if head!=result['ours']:raise Problem('HEAD moved since the plan: '+head)
    paths=[row['path'] for row in result['rows'] if row['outcome']=='re-converted']+sorted(result['files'])
    if paths and merge.git(root,'status','--porcelain','--',*paths).stdout.strip():
        raise Problem('uncommitted changes in paths relayout writes; commit or stash them first')
    for row in result['rows']:
        if row['outcome']=='re-converted':(Path(root)/row['path']).write_bytes(row['data'])
    for path,content in result['files'].items():(Path(root)/path).write_text(content,encoding='utf-8')


def summary(result):
    converted=Counter(row['form_before'] for row in result['rows'] if row['outcome']=='re-converted')
    commit,_,path=result['layout'].partition(':')
    lines=[f"layout {commit[:9]}:{path}, originals at {result['base'][:9]}, fork at {result['ours'][:9]}",
           're-converted: '+(', '.join(f'{count} from {form}' for form,count in sorted(converted.items())) or 'none'),
           f"refused: {len(result['refused'])}"]
    lines+=['  '+path.removeprefix('programs/')+': '+reason for path,reason in sorted(result['refused'].items())]
    lines.append('derived files changed: '+(', '.join(sorted(result['files'])) or 'none'))
    if result['retire']:lines.append('sources to retire: '+', '.join(map(str,sorted(result['retire'].values()))))
    if result['differences']:lines+=['SELECTION DIFFERS:']+['  '+line for line in result['differences']]
    return '\n'.join(lines)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--layout',required=True,help='a reviewed layout in layouts.json: COMMIT (prefix), or COMMIT:PATH when a commit has two')
    parser.add_argument('--from',dest='forms',action='append',choices=convert.FORMS,
                        help='only re-convert recipes now in this form (repeatable; default both)')
    parser.add_argument('--upstream',default='upstream/main')
    parser.add_argument('--repo',type=Path,default=ROOT)
    parser.add_argument('--write',action='store_true',help='write the result into the checkout (never commits)')
    args=parser.parse_args(argv)
    try:
        result=plan(args.repo,args.layout,'HEAD',args.upstream,tuple(args.forms or convert.FORMS))
        print(summary(result),flush=True)
        if result['differences']:return 1
        if args.write:
            write(args.repo,result);print('written, not committed',flush=True)
        return 0
    except Problem as problem:
        print('cannot proceed: '+str(problem),file=sys.stderr)
        return 2


if __name__=='__main__':sys.exit(main())
