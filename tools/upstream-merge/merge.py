#!/usr/bin/env python3
"""Take upstream into the fork with converted recipes re-derived (ADR 0005).

    merge.py plan  --upstream REV --receipt FILE   dry run; changes nothing
    merge.py apply --upstream REV --receipt FILE   start the merge, write programs/
    merge.py gate  --receipt FILE                  check the merge before committing
    merge.py upstream-recipes [--revision REV]     every recipe a merge can touch, one per line

Upstream decides which recipes exist and what each original says. A recipe the
fork converted is never merged by hand: upstream's new text is converted again,
down the ladder same form, long recipe, upstream's original. `apply` leaves an
uncommitted `git merge` with every recipe resolved and only the hand-merged
files (APP-MANAGER, modules/install.am, README.md) still in conflict. It never
commits, pushes or touches an installed host.
"""
import argparse
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/recipe-conversion')]
import convert
import host_catalog
from recipe_declarations import MARKER, policy_rows, with_policy
from recipe_policy_source import generate
import appimage_policy_source

ARCHES=('x86_64','aarch64','i686','armv7l')
RECIPE=re.compile(r'programs/('+'|'.join(ARCHES)+r')/[^/]+')
LISTS=tuple('programs/'+arch+'-apps' for arch in ARCHES)
HAND=('APP-MANAGER','modules/install.am','README.md')
OWNED='tools/upstream-merge/fork-owned.txt'
COLLECTOR='tools/catalog-collector/'
ENROLLED=COLLECTOR+'collection-recipes.txt'
# The enrollment stage() checks the merged recipes against (host_catalog.enrollment).
ENROLLMENT=('catalog/apps.yaml','catalog/repositories',host_catalog.RETIRED)
POLICY='modules/catalog-yaml-policy.am'
OUTCOMES=('taken from upstream','re-converted','fell back','deleted','fork-owned kept','untouched')


class Problem(ValueError):
    """The merge cannot be planned until a person decides something."""


def git(root,*arguments,check=True):
    result=subprocess.run(['git','-C',str(root),*arguments],capture_output=True)
    if check and result.returncode:
        raise ValueError('git '+' '.join(arguments[:2])+': '+result.stderr.decode(errors='replace').strip())
    return result


def text(root,revision,path):
    return git(root,'show',revision+':'+path).stdout.decode()


def recipes(root,revision):
    """Every recipe file at a revision, as bytes by path."""
    present=git(root,'ls-tree','--name-only',revision,'--',*('programs/'+arch for arch in ARCHES)).stdout.decode().split()
    found={}
    if not present:return found
    archive=git(root,'archive',revision,'--',*present).stdout
    with tarfile.open(fileobj=io.BytesIO(archive)) as entries:
        for entry in entries:
            if entry.isdir():continue
            if not entry.isfile() or not RECIPE.fullmatch(entry.name):
                raise Problem('not a plain recipe file: '+entry.name)
            found[entry.name]=entries.extractfile(entry).read()
    return found


def form(data):
    """Which of the recipe forms a file is in."""
    source=data.decode('utf-8',errors='replace')
    if MARKER in source:return 'declaration'
    if source.partition('\n')[2].startswith(convert.bulk_recipe_urls.HEADER):return 'long'
    # A long recipe's policy lines sit inside its header (ticket 26).
    if '\nCATALOG_FORMAT=3\n' in source:
        try:
            if with_policy(source,[]).partition('\n')[2].startswith(convert.bulk_recipe_urls.HEADER):return 'long'
        except ValueError:pass
    if '# AM-CATALOG-' in source:return 'other converted'
    return 'original'


def digest(data):
    return None if data is None else hashlib.sha256(data).hexdigest()


def owned_paths(source):
    paths=[line.strip() for line in source.splitlines() if line.strip() and not line.startswith('#')]
    if len(set(paths))!=len(paths) or any(not RECIPE.fullmatch(path) for path in paths):
        raise Problem('fork-owned list needs unique programs/ARCH/APP lines')
    return set(paths)


def upstream_recipes(root,revision):
    """Every recipe path at a revision that an upstream merge can touch: all of
    programs/ARCH/ except the fork-owned list. Long tests delete them all to
    show the Fast tier reads none of them (ticket 28)."""
    listed=git(root,'ls-tree','-r','-z','--name-only',revision,'--',*('programs/'+arch for arch in ARCHES)).stdout
    owned=owned_paths(text(root,revision,OWNED))
    return sorted(path for path in listed.decode().split('\0') if RECIPE.fullmatch(path) and path not in owned)


def declared_policies(recipe,data):
    """The URL policy rows a recipe's own CATALOG_* lines declare (ticket 26)."""
    try:
        source=data.decode('utf-8')
    except UnicodeDecodeError:
        return []
    if MARKER in source or 'CATALOG_FORMAT=3' not in source.split('\n'):return []
    return policy_rows(recipe,source)[0]


def reconvert(recipe,base,ours,theirs,templates):
    """Convert upstream's new original down the ladder; never keep the old form."""
    before=form(ours)
    try:
        identities=(convert.declaration_identities(ours.decode()) if before=='declaration'
                    else convert.policy_identities(declared_policies(recipe,ours)))
    except (convert.Refusal,UnicodeDecodeError):
        identities=[]
    ladder=[before] if before in convert.FORMS else []
    if 'long' not in ladder:ladder.append('long')
    row=dict(form_before=before,refusals=[])
    try:
        source=theirs.decode('utf-8')
    except UnicodeDecodeError:
        source=None;row['refusals'].append(dict(form='any',reason='upstream text is not UTF-8'))
    result=None
    for rung in ladder if source is not None else []:
        try:
            result=convert.convert(source,recipe,rung,identities,templates);break
        except convert.Refusal as refusal:
            row['refusals'].append(dict(form=rung,reason=str(refusal)))
    if result is None:
        row.update(outcome='fell back',form_after='original',data=theirs,policies=[])
    else:
        row.update(outcome='re-converted' if result['form']==before else 'fell back',form_after=result['form'],
                   data=result['text'].encode(),policies=result['policies'])
    # A fork form the conversion cannot rebuild from the base original was
    # edited by hand; those edits end here (ADR 0005) and the receipt says so.
    reproduced=False
    if before in convert.FORMS and base is not None:
        try:
            again=convert.convert(base.decode('utf-8'),recipe,before,identities,templates)
            reproduced=again['text'].encode()==ours  # the text holds its policies
        except (convert.Refusal,UnicodeDecodeError):pass
    row['fork_form_reproduced']=reproduced
    row['identities']=identities
    return row


def plan(base,ours,theirs,owned,templates):
    """One row per recipe path in either parent; raises Problem on an undecided case."""
    rows=[];problems=[]
    for path in sorted(set(base)|set(ours)|set(theirs)):
        b,o,t=base.get(path),ours.get(path),theirs.get(path)
        recipe=path.removeprefix('programs/')
        if o is None and t is None:continue
        row=dict(path=path)
        if path in owned:
            if o is None:problems.append('fork-owned recipe is missing from the fork: '+path);continue
            row.update(outcome='fork-owned kept',data=o)
            if t!=b:row['upstream']='added' if b is None else 'deleted' if t is None else 'changed'
        elif t==b:
            if b is None:problems.append('fork-only recipe is not in the fork-owned list: '+path);continue
            row.update(outcome='untouched',data=o)
        elif t is None:
            row.update(outcome='deleted',data=None,form_before=form(o) if o is not None else None)
            try:
                row['identities']=(convert.declaration_identities(o.decode()) if row['form_before']=='declaration'
                                   else convert.policy_identities(declared_policies(recipe,o)))
            except (convert.Refusal,UnicodeDecodeError):row['identities']=[]
        elif o is None or o==b or o==t:
            if b is not None and o is None:row['note']='the fork had deleted this recipe'
            row.update(outcome='taken from upstream',data=t)
        elif b is None:
            problems.append('fork and upstream both added a different '+path+'; list it as fork-owned or remove the fork copy')
            continue
        else:
            row.update(reconvert(recipe,b,o,t,templates))
        row['sha256']=digest(row['data'])
        rows.append(row)
    for path in sorted(owned-set(ours)):problems.append('fork-owned list names a recipe the fork does not have: '+path)
    if problems:raise Problem('\n'.join(sorted(set(problems))))
    return rows


def merge_list(base,ours,theirs):
    """Upstream's app list plus the lines the fork added, in name order."""
    added=[line for line in ours.splitlines() if line not in set(base.splitlines())]
    lines=theirs.splitlines()
    name=lambda line:line.split(' : ')[0].casefold()
    for line in added:
        if line in lines:continue
        index=next((i for i,other in enumerate(lines) if name(other)>name(line)),len(lines))
        lines.insert(index,line)
    return '\n'.join(lines)+'\n'


def derive(root,ours_revision,rows):
    """The fork-side files that follow from the recipe rows."""
    # An enrolled declaration that is no longer one leaves collection-recipes.txt
    # (not installable from the catalog any more); its app stays in
    # catalog/apps.yaml, so the collector keeps its source.
    enrolled=text(root,ours_revision,ENROLLED).splitlines()
    declared={row['path'].removeprefix('programs/') for row in rows
              if row['data'] is not None and form(row['data'])=='declaration'}
    kept=[line for line in enrolled if not line or line.startswith('#') or line in declared]
    # Sources no surviving recipe selects from. Retiring them is a separate
    # collector step; this merge only names them. A recipe's policies are its
    # own lines (ticket 26): a recipe taken from upstream has none.
    bound=set()
    for row in rows:
        if row['data'] is not None:
            bound.update(policy['repository_id'] for policy in
                         declared_policies(row['path'].removeprefix('programs/'),row['data']))
        if row['outcome']=='fell back' and row['form_after']=='original':
            bound.update(identity['repository_id'] for identity in row['identities'])
        elif row['data'] is not None and form(row['data'])=='declaration':
            bound.update(identity['repository_id'] for identity in convert.declaration_identities(row['data'].decode()))
    retire={}
    for row in rows:
        if row['outcome']!='deleted':continue
        for identity in row.get('identities',[]):
            if identity['repository_id'] not in bound:retire[identity['repository_id']]=identity['repository']
    return {ENROLLED:'\n'.join(kept)+'\n'},retire


def stage(root,ours_revision,rows,files):
    """Build the merged fork-side state in a scratch tree and compile it.

    Returns the compiled policy module. A declaration or policy the merged
    recipes do not support refuses here, before anything real is written.
    """
    with tempfile.TemporaryDirectory(prefix='am-upstream-merge-') as temporary:
        tree=Path(temporary)
        for row in rows:
            if row['data'] is None:continue
            target=tree/row['path'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(row['data'])
        (tree/POLICY).parent.mkdir(parents=True,exist_ok=True)
        (tree/POLICY).write_text(text(root,ours_revision,POLICY))
        with tarfile.open(fileobj=io.BytesIO(git(root,'archive',ours_revision,'--',*ENROLLMENT).stdout)) as enrollment:
            enrollment.extractall(tree,filter='data')
        for path,content in files.items():
            (tree/path).parent.mkdir(parents=True,exist_ok=True);(tree/path).write_text(content)
        generate(tree)
        appimage_policy_source.generate(tree)
        host_catalog.enrollment(root=tree)
        return (tree/POLICY).read_text()


def prepare(root,upstream,ours_revision='HEAD'):
    """Everything `plan` reports and `apply` writes, with nothing changed."""
    upstream=git(root,'rev-parse','--verify',upstream+'^{commit}').stdout.decode().strip()
    ours_revision=git(root,'rev-parse','--verify',ours_revision+'^{commit}').stdout.decode().strip()
    base=git(root,'merge-base',ours_revision,upstream).stdout.decode().strip()
    if base==upstream:raise Problem('the fork already contains '+upstream)
    owned=owned_paths(text(root,ours_revision,OWNED))
    rows=plan(recipes(root,base),recipes(root,ours_revision),recipes(root,upstream),owned,convert.layouts(root))
    files,retire=derive(root,ours_revision,rows)
    files[POLICY]=stage(root,ours_revision,rows,files)
    for path in LISTS:
        versions=[git(root,'show',revision+':'+path,check=False) for revision in (base,ours_revision,upstream)]
        if any(version.returncode for version in versions):continue
        b,o,t=(version.stdout.decode() for version in versions)
        if o!=b and t!=b:files[path]=merge_list(b,o,t)
    attention=dict(
        fell_back=[dict(path=row['path'],form_before=row['form_before'],form_after=row['form_after'],
                        refusals=row['refusals']) for row in rows if row['outcome']=='fell back'],
        hand_edits_ended=[row['path'] for row in rows if row['outcome'] in ('re-converted','fell back')
                          and row['form_before'] in convert.FORMS and not row['fork_form_reproduced']],
        fork_owned_upstream_changes=[dict(path=row['path'],upstream=row['upstream']) for row in rows if row.get('upstream')],
        sources_to_retire=[dict(repository_id=rid,repository=name) for rid,name in sorted(retire.items())])
    receipt=dict(format=2,ours=ours_revision,upstream=upstream,base=base,
        counts=dict(Counter(row['outcome'] for row in rows)),
        files={path:hashlib.sha256(content.encode()).hexdigest() for path,content in sorted(files.items())},
        hand_merged=list(HAND),attention=attention,recipes_sha256=listing_digest(listing(rows)))
    return receipt,rows,files


def listing(rows):
    """The per-recipe outcomes without their bytes: what the gate checks a merge against."""
    return [{key:value for key,value in row.items() if key not in ('data','policies','identities')} for row in rows]


def listing_digest(recipes):
    return hashlib.sha256(json.dumps(recipes,sort_keys=True).encode()).hexdigest()


def listing_path(root):
    """Where `apply` leaves the listing: inside the Git directory, so it is never committed."""
    return Path(git(root,'rev-parse','--absolute-git-dir').stdout.decode().strip())/'upstream-merge-recipes.json'


def with_listing(receipt,path):
    """The receipt with its per-recipe listing, read from `path` unless the receipt carries it (format 1)."""
    if 'recipes' in receipt:return receipt
    if not path.is_file():raise Problem('no per-recipe listing at '+str(path)+'; run apply here, or pass --recipes')
    recipes=json.loads(path.read_text())
    if listing_digest(recipes)!=receipt['recipes_sha256']:raise Problem(str(path)+' is not the listing of this receipt')
    return dict(receipt,recipes=recipes)


def summary(receipt):
    lines=['upstream '+receipt['upstream'][:12]+' into '+receipt['ours'][:12]+' (base '+receipt['base'][:12]+')']
    lines+=[f'  {receipt["counts"].get(outcome,0):6d}  {outcome}' for outcome in OUTCOMES]
    for name,entries in receipt['attention'].items():
        lines.append(f'  {len(entries):6d}  {name.replace("_"," ")}')
    return '\n'.join(lines)


def unmerged(root):
    return sorted(set(git(root,'diff','--name-only','--diff-filter=U').stdout.decode().splitlines()))


def apply(root,upstream,receipt_path,recipes_path=None):
    if git(root,'status','--porcelain').stdout.strip():raise Problem('the checkout has uncommitted or untracked changes')
    if git(root,'rev-parse','-q','--verify','MERGE_HEAD',check=False).returncode==0:raise Problem('a merge is already in progress')
    receipt,rows,files=prepare(root,upstream)
    git(root,'merge','--no-commit','--no-ff',receipt['upstream'],check=False)
    if git(root,'rev-parse','-q','--verify','MERGE_HEAD',check=False).returncode:
        raise Problem('git did not start the merge')
    for arch in ARCHES:shutil.rmtree(root/'programs'/arch,ignore_errors=True)
    for row in rows:
        if row['data'] is None:continue
        target=root/row['path'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(row['data'])
    for path,content in files.items():(root/path).write_text(content)
    present=[str(root/'programs'/arch) for arch in ARCHES]
    git(root,'add','-A','--',*present,*files)
    receipt['unmerged_after_apply']=unmerged(root)
    receipt_path.write_text(json.dumps(receipt,indent=1)+'\n')
    (recipes_path or listing_path(root)).write_text(json.dumps(listing(rows),indent=1)+'\n')
    return receipt


def gate(root,receipt):
    """Decision 7 of ticket 17, checked against the merge as it stands."""
    failures=[]
    head=git(root,'rev-parse','HEAD').stdout.decode().strip()
    merging=git(root,'rev-parse','-q','--verify','MERGE_HEAD',check=False)
    if merging.returncode==0:
        ours,theirs=head,merging.stdout.decode().strip()
    else:
        parents=git(root,'rev-list','--parents','-n','1','HEAD').stdout.decode().split()[1:]
        if len(parents)!=2:return ['HEAD is neither a merge in progress nor a merge commit']
        ours,theirs=parents
    if (ours,theirs)!=(receipt['ours'],receipt['upstream']):
        failures.append('the receipt is for another pair of parents')
    left=unmerged(root)
    if left:failures.append('still unmerged: '+', '.join(left))
    before,after=recipes(root,ours),recipes(root,theirs)
    merged={}
    for arch in ARCHES:
        for path in sorted((root/'programs'/arch).glob('*')) if (root/'programs'/arch).is_dir() else []:
            merged['programs/'+arch+'/'+path.name]=path.read_bytes()
    listed=Counter(row['path'] for row in receipt['recipes'])
    for path in sorted(set(before)|set(after)):
        if listed[path]!=1:failures.append(f'{path}: {listed[path]} receipt rows')
    for row in receipt['recipes']:
        path,outcome=row['path'],row['outcome']
        if outcome not in OUTCOMES:failures.append(path+': unknown outcome');continue
        if digest(merged.get(path))!=row['sha256']:failures.append(path+': differs from the receipt')
        expected={'untouched':before.get(path),'fork-owned kept':before.get(path),
                  'taken from upstream':after.get(path),'deleted':None}
        if outcome in expected and merged.get(path)!=expected[outcome]:
            failures.append(path+': not what "'+outcome+'" means')
        if outcome=='fell back' and row['form_after']=='original' and merged.get(path)!=after.get(path):
            failures.append(path+': fell back but is not upstream\'s original')
    for path in sorted(set(merged)-set(listed)):failures.append(path+': in the merge but not in the receipt')
    for path,expected in receipt['files'].items():
        if digest((root/path).read_bytes())!=expected:failures.append(path+': differs from the receipt')
    # The fork's own lines in the hand-merged runtime.
    for path in HAND[:2]:
        old,new=text(root,ours,path),(root/path).read_text()
        for pattern in (r'(?m)^AMREPO="https://raw\.githubusercontent\.com/[^"\n]+"$',r'(?m)^ALT_GH="[^"\n]+"$'):
            for line in re.findall(pattern,old):
                if line not in new.splitlines():failures.append(path+': lost '+line)
    marks=git(root,'grep','-c','MAREK-FORK',ours,'--','.',':!docs',':!tools',check=False).stdout.decode().splitlines()
    for entry in marks:
        _,path,count=entry.split(':')
        current=(root/path).read_text(errors='replace').count('MAREK-FORK') if (root/path).is_file() else 0
        if current<int(count):failures.append(f'{path}: {current} of {count} MAREK-FORK marks left')
    return failures


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    commands=parser.add_subparsers(dest='command',required=True)
    for name in ('plan','apply','gate'):
        command=commands.add_parser(name)
        command.add_argument('--receipt',type=Path,required=True)
        command.add_argument('--repo',type=Path,default=ROOT)
        command.add_argument('--recipes',type=Path,help='per-recipe listing; apply and gate default to a file inside the Git directory')
        if name!='gate':command.add_argument('--upstream',required=True)
    listed=commands.add_parser('upstream-recipes',help='print every recipe path an upstream merge can touch')
    listed.add_argument('--repo',type=Path,default=ROOT)
    listed.add_argument('--revision',default='HEAD')
    args=parser.parse_args(argv)
    try:
        if args.command=='upstream-recipes':
            print(''.join(path+'\n' for path in upstream_recipes(args.repo,args.revision)),end='')
            return 0
        if args.command=='gate':
            failures=gate(args.repo,with_listing(json.loads(args.receipt.read_text()),args.recipes or listing_path(args.repo)))
            print('\n'.join(failures) if failures else 'gate: recipes, fork files and fork marks agree with the receipt')
            return 1 if failures else 0
        if args.command=='plan':
            if args.receipt.exists():raise Problem('receipt already exists: '+str(args.receipt))
            receipt,rows,_=prepare(args.repo,args.upstream)
            args.receipt.write_text(json.dumps(receipt,indent=1)+'\n')
            if args.recipes:args.recipes.write_text(json.dumps(listing(rows),indent=1)+'\n')
        else:
            receipt=apply(args.repo,args.upstream,args.receipt,args.recipes)
            print('merge started, not committed; hand-merge then run gate. Still unmerged: '
                  +(', '.join(receipt['unmerged_after_apply']) or 'nothing'))
        print(summary(receipt))
        return 0
    except Problem as problem:
        print('cannot proceed:\n'+str(problem),file=sys.stderr)
        return 2


if __name__=='__main__':sys.exit(main())
