"""Canonical format-3/status-1 projections and credential-free validation."""
import copy
import json
from pathlib import Path
import re
import yaml
from writer import document
from yaml_publication import SAFE_LOADER
from retention import observation
from retention_v3 import merge
from wire_validation import validate_wire

ROOT = Path(__file__).resolve().parents[2]
DEFINITIONS = json.loads((ROOT/'tools/catalog-contract/definitions.json').read_text())['definitions']
FILE_CAP = 2 * 1024 * 1024
TREE_CAP = 1024 * 1024 * 1024
NAME = r'[a-z0-9][a-z0-9_.+-]{0,63}'


def pin(value):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{40}', value):
        raise ValueError('exact revision required')
    return value


def header(kind, revision):
    version = 3 if kind in ('catalog','apps','repository','provenance') else 1
    contract = 'catalog-format-v3' if version == 3 else 'catalog-status-v1'
    return dict(format=version, schema=f'https://raw.githubusercontent.com/mareklangiewicz/AM/{pin(revision)}/docs/{contract}.md', kind=kind)


def canonical(obj, typename=None):
    """Order closed structures and exact decimal keys without interpreting YAML."""
    typename = typename or obj['kind']
    schema = DEFINITIONS[typename]
    if 'properties' in schema:
        if set(obj)-set(schema['properties']):
            raise ValueError('unknown field')
        keys = [k for k in schema['properties'] if k in obj]
        rules = schema['properties']
    else:
        keys = sorted(obj, key=int) if typename in ('releases','assets') else sorted(obj)
        rules = {k:next(iter(schema['patternProperties'].values())) for k in obj}
    result = {}
    for key in keys:
        value, rule = obj[key], rules[key]
        result[key] = canonical(value, rule['$ref'].split('/')[-1]) if '$ref' in rule else value
    return result


def emit_contract(obj, typename, depth=0):
    schema=DEFINITIONS[typename]
    rules=schema.get('properties')
    lines=[]
    for key,value in canonical(obj,typename).items():
        rule=rules[key] if rules is not None else next(iter(schema['patternProperties'].values()))
        prefix='  '*depth+(key if rules is not None else json.dumps(key))+':'
        if '$ref' in rule:
            lines.append(prefix+('' if value else ' {}'))
            if value: lines.extend(emit_contract(value,rule['$ref'].split('/')[-1],depth+1))
        else:
            text=json.dumps(value,ensure_ascii=False).replace('\u0085','\\N').replace('\u2028','\\L').replace('\u2029','\\P')
            lines.append(prefix+' '+text)
    return lines


def encode(obj):
    return ('\n'.join(emit_contract(obj,obj['kind']))+'\n').encode('utf-8')


def decode(raw, cap=FILE_CAP):
    if type(raw) is not bytes or len(raw)>cap:
        raise ValueError('document bound')
    validate_wire(raw,cap,contract=True)
    obj=yaml.load(raw,Loader=SAFE_LOADER)
    if encode(obj)!=raw:
        raise ValueError('noncanonical document')
    return obj


def encode_media_type(value):
    """None denotes the existing omitted octet-stream representation."""
    if value=='application/octet-stream': return None
    if value=='application/zip': return 'zip'
    if value=='' or (not value.startswith('=') and re.match(r'^[^\s/]+/[^\s/]+',value)):
        return value
    return '='+value


def decode_media_type(value):
    """An escape removes one '=' and returns literally, without alias lookup."""
    if value.startswith('='): return value[1:]
    if value=='zip': return 'application/zip'
    if value=='' or re.match(r'^[^\s/]+/[^\s/]+',value): return value
    raise ValueError('unknown MIME alias')


def compact_release(record):
    """Literal URL factoring; choose actual canonical encoded-byte savings."""
    release=copy.deepcopy(record)
    for asset in release['assets'].values():
        mime=encode_media_type(asset.pop('content_type'))
        if mime is not None:
            asset['media_type']=mime
    def cost(base):
        trial=copy.deepcopy(release)
        if base:
            trial['download_base']=base
            for asset in trial['assets'].values():
                if asset['url'].startswith(base):
                    asset['url_suffix']=asset.pop('url')[len(base):]
        return len(document(canonical(trial,'release')).encode()), trial
    original,_=cost(None)
    prefixes=set()
    urls=[asset['url'] for asset in release['assets'].values()]
    for url in urls:
        prefixes.update(url[:i+1] for i,c in enumerate(url) if c=='/' and i>=8)
    choices=[]
    for base in prefixes:
        if sum(url.startswith(base) for url in urls)<2:
            continue
        size,trial=cost(base)
        if size<original:
            choices.append((size,-len(base.encode('utf-8')),base.encode('utf-8'),trial))
    return min(choices,key=lambda row:row[:3])[3] if choices else release


def expand_release(record, default):
    release=copy.deepcopy(record)
    base=release.pop('download_base',None)
    release['observed_at']=observation(release,default)
    for asset in release['assets'].values():
        if 'url_suffix' in asset:
            asset['url']=base+asset.pop('url_suffix')
        mime=asset.pop('media_type','application/octet-stream')
        asset['content_type']=decode_media_type(mime)
    return release


def source(previous, acquired, *, rid, repository, revision):
    """Only successful source observations enter this pure, atomic projection."""
    previous=copy.deepcopy(previous or {})
    previous['releases']={key:expand_release(value,previous.get('observed_at'))
                          for key,value in previous.get('releases',{}).items()}
    at=acquired['received_at']
    fetched={key:dict(value,observed_at=at) for key,value in acquired['releases'].items()}
    records=merge(previous,fetched,completed_at=at)
    result=dict(header('repository',revision),repository_id=int(rid),repository=repository,
                collected_at=acquired.get('completed_at') or at,scope=dict(page_size=100,pages_fetched=1,history_complete=acquired['history_complete']),
                observed_at=at,releases={key:compact_release(value) for key,value in records.items()})
    if 'git_refs' in acquired:
        result.update(git_scope=acquired['git_scope'],git_refs=acquired['git_refs'])
    raw=encode(result)
    if len(raw)>FILE_CAP: raise ValueError('document_overflow')
    return decode(raw)


def provenance_path(source_path):
    if not re.fullmatch('repositories/'+NAME+r'\.yaml',source_path):
        raise ValueError('invalid provenance source path')
    return 'provenance/'+source_path.removeprefix('repositories/')


def partition_provenance(apps, bindings, revision):
    if set(apps)!=set(bindings): raise ValueError('provenance app coverage')
    groups={}
    for app,source_path in apps.items():
        groups.setdefault(provenance_path(source_path),{})[app]=bindings[app]
    return {path:encode(dict(header('provenance',revision),apps=entries))
            for path,entries in groups.items()}


def provenance_references(apps, sources, provenance, inputs):
    expected={}
    for app,path in apps.items():
        if path not in sources: raise ValueError('missing app source')
        expected.setdefault(provenance_path(path),set()).add(app)
    if set(provenance)!=set(expected): raise ValueError('provenance document coverage')
    for path,doc in provenance.items():
        if '/'+inputs['schemas']+'/' not in doc['schema']: raise ValueError('provenance schema binding')
        if set(doc['apps'])!=expected[path]: raise ValueError('provenance app coverage')
        for app,arches in doc['apps'].items():
            for arch,binding in arches.items():
                if sources[apps[app]]!=binding['repository_id']: raise ValueError('provenance source identity')
                if 'recipe' in binding and binding['recipe']['path']!=f'programs/{arch}/{app}':
                    raise ValueError('recipe architecture identity')
                if 'recipe' in binding and binding['recipe']['commit']!=inputs['recipes']: raise ValueError('recipe revision binding')
                if 'evidence' in binding and binding['evidence']['rules']!=inputs['rules']: raise ValueError('rule revision binding')


def validate_tree(tree, channel='catalog'):
    if type(tree) is not dict or sum(map(len,tree.values()))>TREE_CAP or len(tree)>(100000 if channel=='status' else 20000):
        raise ValueError('tree bound')
    docs={}
    ids={}
    for path,raw in tree.items():
        if channel=='catalog':
            allowed=path in ('catalog.yaml','apps.yaml') or re.fullmatch('(repositories|provenance)/'+NAME+r'\.yaml',path)
        else:
            allowed=path in ('status.yaml','statistics.yaml') or re.fullmatch(r'runs/[1-9][0-9]*-[1-9][0-9]*/(?:summary\.yaml|sources/'+NAME+r'\.yaml)',path)
        if not allowed:
            raise ValueError('unexpected contract path')
        obj=decode(raw)
        expected=(path[:-5] if '/' not in path else ('provenance' if path.startswith('provenance/') else 'repository') if channel=='catalog' else 'summary' if path.endswith('/summary.yaml') else 'source')
        if obj['kind']!=expected:
            raise ValueError('path kind')
        docs[path]=obj
        if obj['kind']=='repository':
            rid=obj['repository_id']
            if rid in ids: raise ValueError('duplicate numeric source')
            ids[rid]=path
    if channel=='catalog':
        if not {'catalog.yaml','apps.yaml'}<=docs.keys():
            raise ValueError('missing catalog roots')
        revision=docs['catalog.yaml']['inputs']['schemas']
        if any('/'+revision+'/' not in doc['schema'] for doc in docs.values()):
            raise ValueError('catalog schema binding')
        provenance_references(docs['apps.yaml']['apps'],
            {path:doc['repository_id'] for path,doc in docs.items() if doc['kind']=='repository'},
            {path:doc for path,doc in docs.items() if doc['kind']=='provenance'},docs['catalog.yaml']['inputs'])

    else:
        if 'status.yaml' not in docs: raise ValueError('missing status root')
        status=docs['status.yaml']
        if len(status['summaries'])>64 or len(status['details'])>8: raise ValueError('status retention')
        for key,path in status['summaries'].items():
            if path!=f'runs/{key}/summary.yaml' or path not in docs: raise ValueError('summary reference')
        if status['last_report'] not in status['summaries'].values(): raise ValueError('last report')
        for path,obj in docs.items():
            if obj['kind'] in ('source','summary'):
                key=str(obj['run']['id'])+'-'+str(obj['run']['attempt'])
                if not path.startswith('runs/'+key+'/'): raise ValueError('run path identity')
            if obj['kind']=='source' and key not in status['details']: raise ValueError('detail coverage')
        if 'statistics.yaml' in docs and len(docs['statistics.yaml']['days'])>90: raise ValueError('daily retention')
    return docs


def read_directory(directory, channel='catalog'):
    directory=Path(directory)
    tree={}
    if directory.is_symlink(): raise ValueError('candidate directory symlink')
    # Do not follow links or include unexpected files from transferred candidates.
    for path in directory.rglob('*'):
        if path.is_symlink() or not (path.is_file() or path.is_dir()): raise ValueError('candidate file type')
        if path.is_dir():
            name=path.relative_to(directory).as_posix()
            allowed=(name in ('repositories','provenance')) if channel=='catalog' else bool(name=='runs' or re.fullmatch(r'runs/[1-9][0-9]*-[1-9][0-9]*(/sources)?',name))
            if not allowed: raise ValueError('unexpected candidate directory')
        if path.is_file():
            if path.stat().st_size>FILE_CAP: raise ValueError('document bound')
            tree[path.relative_to(directory).as_posix()]=path.read_bytes()
            if sum(map(len,tree.values()))>TREE_CAP or len(tree)>(100000 if channel=='status' else 20000): raise ValueError('tree bound')
    validate_tree(tree,channel)
    return tree


def read_local(repo, commit, channel='catalog'):
    from publication import bounded, environment
    pin(commit)
    def local(*args,cap):
        return bounded(['git','-C',str(repo),'-c','core.hooksPath=/dev/null',*args],env=environment(),cap=cap)
    listing=local('ls-tree','-rz',commit,cap=(32 if channel=='status' else 4)*1024*1024)
    tree={}; total=0
    for row in listing.split(b'\0'):
        if not row: continue
        metadata,name=row.split(b'\t',1); mode,kind,oid=metadata.split(b' ')
        if mode!=b'100644' or kind!=b'blob': raise ValueError('catalog file type')
        path=name.decode('ascii')
        size=int(local('cat-file','-s',oid.decode(),cap=64))
        total+=size
        if size>FILE_CAP or total>TREE_CAP or len(tree)>=(100000 if channel=='status' else 20000): raise ValueError('catalog bound')
        tree[path]=local('cat-file','blob',oid.decode(),cap=FILE_CAP)
    validate_tree(tree,channel)
    return tree


def schema_revision(repo,commit):
    """Read only the bounded authority root; do not trust other parent blobs."""
    from publication import bounded,environment
    pin(commit)
    raw=bounded(['git','-C',str(repo),'-c','core.hooksPath=/dev/null','show',commit+':catalog.yaml'],
                env=environment(),cap=FILE_CAP)
    descriptor=decode(raw)
    if descriptor['kind']!='catalog':raise ValueError('schema parent descriptor kind')
    revision=descriptor['inputs']['schemas']
    if '/'+revision+'/' not in descriptor['schema']:raise ValueError('schema parent descriptor binding')
    return revision
