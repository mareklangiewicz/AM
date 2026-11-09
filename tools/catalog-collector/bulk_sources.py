"""Checkpointed public GitHub identity discovery for a hash-bound recipe scan.

Only reads public metadata. Does not enroll apps or execute recipe shell. Small
GraphQL batches avoid one identity/probe request pair per recipe. Full responses
are retained; partial NOT_FOUND results are explicit exceptions, never coverage.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess

from catalog_sources import REPOSITORY, ROOT, literals
from host_catalog import utc

BATCH = 25


def literal_sites(source):
    """Read standalone literal SITE assignments, including same-line variants."""
    pattern=r"(?:^|[ ;\t])SITE[123]?=(?:\"("+REPOSITORY+r")\"|'("+REPOSITORY+r")'|("+REPOSITORY+r"))(?=[;\s]|$)"
    return sorted({next(value for value in match if value) for match in re.findall(pattern,source,re.M)})


def inventory(scan):
    """Extend installer-ready discovery with explicit primary catalog sources.

    A literal SITE and its sole release endpoint bind catalog facts even when
    the surrounding installer needs custom migration. This grants no installer
    classification, selector approval or execution permission.
    """
    candidates={row['app']:dict(row,bindings=list(row['bindings'])) for row in scan['candidates']}
    unresolved=[]
    for path in scan['unsupported_recipes']:
        raw=(ROOT/path).read_bytes();text=raw.decode('utf-8');app=Path(path).name
        endpoints={m.lower() for m in re.findall(
            r'https://api[.]github[.]com/repos/('+REPOSITORY+r''')/releases(?:[/?"'\s|]|$)''',text)}
        sites=literals(text,'SITE')
        primary=[]
        aliases=literals(text,'CATALOG_ALIAS')
        alias_names=[re.fullmatch(r'https://api[.]github[.]com/repos/('+REPOSITORY+
            r')/releases(?:/latest)?(?:\?per_page=100)?',alias) for alias in aliases]
        if aliases and all(alias_names) and '# AM-CATALOG-RECIPE 1\n' in text and '# shellcheck source=modules/appimage.am\n' in text:
            primary=sorted({match[1] for match in alias_names})
        elif (len(endpoints)==1 and sites and set(n.lower() for n in sites)==endpoints):
            primary=[sites[0]]
        else:
            primary=sorted(set(re.findall(r'''\bversion=\$\(curl -Ls ["']?https://api[.]github[.]com/repos/('''
                +REPOSITORY+r''')/releases(?:[/?"'\s|]|$)''',text)))
            primary+=re.findall(r'''(?m)^[ \t]*version=.*?https://(?:api[.]github[.]com/repos|github[.]com)/('''
                +REPOSITORY+r''')/releases(?:[/?"'\s|]|$)''',text)
            if re.search(r'''https://api[.]github[.]com/repos/["']?\$(?:RELEASE|SITE)["']?/releases''',text):
                primary+=literal_sites(text)
            if re.search(r'''https://api[.]github[.]com/repos/["']?\$RELEASE["']?/releases''',text):
                for line in text.splitlines():
                    if not re.match(r'^SITE[123]?=',line):continue
                    for word in shlex.split(line):
                        key,equals,value=word.partition('=')
                        if re.fullmatch('SITE[123]?',key) and equals and re.fullmatch(REPOSITORY,value):
                            primary.append(value)
        if primary:
            for repository in sorted(set(primary)):
                proof=dict(recipe=path,sha256=hashlib.sha256(raw).hexdigest(),
                           repository=repository,proof='literal_primary_release_source')
                row=candidates.setdefault(app,dict(app=app,repository=repository,bindings=[]))
                row['bindings'].append(proof)
        else:
            mentions=sorted(set(re.findall(r'https://(?:api[.]github[.]com/repos|github[.]com)/('+REPOSITORY+r')',text)))
            unresolved.append(dict(recipe=path,sha256=hashlib.sha256(raw).hexdigest(),
                release_repositories=sorted(endpoints),github_mentions=mentions,
                reason='primary_source_review' if mentions else 'no_literal_github_source'))
    good=[];ambiguous=list(scan['ambiguous'])
    for row in sorted(candidates.values(),key=lambda row:row['app']):
        if len({p['repository'].lower() for p in row['bindings']})!=1:
            ambiguous.append(row)
        else:good.append(row)
    return dict(source=scan['source'],observed_at=utc(),candidates=good,
                ambiguous=ambiguous,unresolved=unresolved,
                note='Catalog source attribution; custom installers remain unconverted.')


def query(names):
    fields = []
    for index, name in enumerate(names):
        if not re.fullmatch(REPOSITORY, name) or any(part in ('.','..') for part in name.split('/')):
            raise ValueError('repository spelling')
        owner, repo = name.split('/')
        fields.append(f'r{index}: repository(owner:{json.dumps(owner)},name:{json.dumps(repo)}) '
                      '{databaseId nameWithOwner isPrivate releases(first:1) '
                      '{nodes {databaseId isDraft}}}')
    return '{rateLimit {remaining resetAt cost} '+ ' '.join(fields)+'}'


def parse(names, response):
    data = response.get('data')
    if not isinstance(data, dict):
        raise ValueError('missing GraphQL data')
    missing = set()
    for error in response.get('errors', []):
        path = error.get('path', [])
        if (error.get('type') != 'NOT_FOUND' or len(path) != 1 or
                path[0] not in {'r'+str(i) for i in range(len(names))}):
            raise ValueError('GraphQL error: '+str(error.get('type', 'unknown')))
        missing.add(path[0])
    rows = []
    for index, requested in enumerate(names):
        key = 'r'+str(index)
        if key not in data:
            raise ValueError('incomplete GraphQL response')
        obj = data[key]
        row = dict(requested_repository=requested)
        if obj is None:
            if key not in missing:
                raise ValueError('unexplained null repository')
            rows.append(dict(row, status='unavailable'))
            continue
        if key in missing:
            raise ValueError('inconsistent GraphQL error')
        rid, name = obj.get('databaseId'), obj.get('nameWithOwner')
        if (type(rid) is not int or rid < 1 or not isinstance(name, str) or
                not re.fullmatch(REPOSITORY, name) or type(obj.get('isPrivate')) is not bool):
            raise ValueError('invalid repository identity')
        if obj['isPrivate']:
            rows.append(dict(row, status='not_public'))
            continue
        nodes = obj.get('releases', {}).get('nodes')
        if not isinstance(nodes, list) or len(nodes)>1:
            raise ValueError('invalid release probe')
        if nodes and (type(nodes[0].get('databaseId')) is not int or
                      nodes[0]['databaseId'] < 1 or nodes[0].get('isDraft') is not False):
            raise ValueError('invalid public release')
        rows.append(dict(row, repository_id=rid, repository=name,
                         status='verified' if nodes else 'no_public_release',
                         release_id=nodes[0]['databaseId'] if nodes else None))
    rate = data.get('rateLimit', {})
    if type(rate.get('remaining')) is not int or type(rate.get('cost')) is not int:
        raise ValueError('missing rate accounting')
    return rows, rate


def acquire(names, work, ordinal):
    request = dict(query=query(names))
    path = work/f'{ordinal:04d}.json'
    if path.exists():
        saved = json.loads(path.read_text())
        if saved['request'] != request:
            raise ValueError('checkpoint request differs')
    else:
        result = subprocess.run(['gh','api','graphql','--input','-'],
            input=json.dumps(request),text=True,capture_output=True,timeout=45)
        # gh returns nonzero for scoped NOT_FOUND as well as global errors.
        try:
            response = json.loads(result.stdout)
        except ValueError:
            raise ValueError('GitHub request failed: '+result.stderr[:300]) from None
        parse(names, response)
        saved = dict(observed_at=utc(),request=request,response=response)
        path.write_text(json.dumps(saved,indent=2)+'\n')
    rows, rate = parse(names,saved['response'])
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return [dict(row,evidence=path.name,evidence_sha256=digest,
                 observed_at=saved['observed_at']) for row in rows], rate


def verify(scan, work):
    # Every proof still names exact current and committed bytes. No scan can
    # promote a stale recipe or silently follow a recipe symlink outside the tree.
    if not re.fullmatch('[0-9a-f]{40}',scan['source']):
        raise ValueError('source commit')
    tree = {}
    for record in subprocess.check_output(['git','-C',str(ROOT),'ls-tree','-rz',scan['source'],'--','programs/']).split(b'\0'):
        if record:
            metadata,path=record.split(b'\t',1)
            mode,kind,oid=metadata.split()
            if mode in (b'100644',b'100755') and kind==b'blob':
                tree[path.decode()]=oid.decode()
    for candidate in scan['candidates']:
        for proof in candidate['bindings']:
            path = proof['recipe']
            if not re.fullmatch(r'programs/(x86_64|aarch64|i686|armv7l)/[a-z0-9][a-z0-9_.+-]*',path):
                raise ValueError('recipe path')
            target = ROOT/path
            if target.is_symlink():
                raise ValueError('recipe symlink')
            raw = target.read_bytes()
            oid=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            if tree.get(path)!=oid or hashlib.sha256(raw).hexdigest()!=proof['sha256']:
                raise ValueError('stale recipe proof: '+path)
    names = sorted({row['repository'].lower() for row in scan['candidates']})
    work.mkdir(parents=True,exist_ok=True)
    rows = []; rates = []; ordinal = 0
    def batches(names):
        nonlocal ordinal
        result = []
        for offset in range(0,len(names),BATCH):
            if ordinal >= 400:
                raise ValueError('discovery request allowance')
            cached=(work/f'{ordinal:04d}.json').exists()
            found,rate = acquire(names[offset:offset+BATCH],work,ordinal)
            ordinal+=1;rates.append(rate);result.extend(found)
            if not cached:print(json.dumps(dict(batch=ordinal,reviewed=len(result),remaining=rate['remaining'])),flush=True)
            if not cached and rate['remaining'] < 100:
                raise ValueError('discovery rate reserve; checkpoints retained')
        return result
    rows = batches(names)
    canonical = sorted({row['repository'] for row in rows if 'repository' in row and
                        row['requested_repository'].lower()!=row['repository'].lower()})
    checked = {row['requested_repository'].lower():row for row in batches(canonical)}
    for row in rows:
        if 'repository' in row and row['requested_repository'].lower()!=row['repository'].lower():
            other = checked[row['repository'].lower()]
            if (other.get('repository_id')!=row['repository_id'] or
                    other.get('repository')!=row['repository'] or
                    other.get('status')!=row['status']):
                raise ValueError('canonical identity disagreement')
            row['canonical_evidence']=other['evidence']
            row['canonical_evidence_sha256']=other['evidence_sha256']
    result = dict(source=scan['source'],observed_at=utc(),requests=ordinal,
                  graphql_cost=sum(rate['cost'] for rate in rates),repositories=rows,
                  note='Identity/release probes only; no enrollment, recipe or publication writes.')
    (work/'identities.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scan',type=Path,required=True)
    output=parser.add_mutually_exclusive_group(required=True)
    output.add_argument('--work',type=Path)
    output.add_argument('--inventory',type=Path)
    args=parser.parse_args()
    scan=json.loads(args.scan.read_text())
    if args.inventory:
        result=inventory(scan)
        with args.inventory.open('x') as stream:stream.write(json.dumps(result,indent=2)+'\n')
        print(json.dumps({key:len(value) for key,value in result.items() if isinstance(value,list)}))
    else:verify(scan,args.work)


if __name__=='__main__':
    main()
