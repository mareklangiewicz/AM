"""Run-local validated Git snapshots; no imported receipt can establish trust.

A new process streams the exact parent once. Only metadata survives validation;
untouched source records are not decoded/materialized during subsequent updates.
"""
from collections.abc import Mapping
import hashlib
from pathlib import Path
import re
import time

import contracts
from publication import bounded, environment
from writer import document
from yaml_publication import decode_document

_TRUST=object()


def rules():
    paths=['tools/catalog-collector/incremental.py','tools/catalog-collector/contracts.py',
           'tools/catalog-collector/writer.py','tools/catalog-contract/definitions.json',
           'modules/catalog-contract-parser.am','modules/catalog-contract-tables.am',
           'modules/catalog-contract-reader.am','modules/catalog-yaml-reader.am','modules/catalog-yaml-parser.am']
    digest=hashlib.sha256()
    for path in paths:
        digest.update(path.encode()+b'\0'+(contracts.ROOT/path).read_bytes()+b'\0')
    return digest.hexdigest()


def oid(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()


def allowed(path,channel):
    if channel=='status-1': return path in ('status.yaml','statistics.yaml') or bool(re.fullmatch(r'runs/[1-9][0-9]*-[1-9][0-9]*/(?:summary\.yaml|sources/'+contracts.NAME+r'\.yaml)',path))
    if channel=='format-2': return path=='apps.yaml' or bool(re.fullmatch(r'repositories/[1-9][0-9]*\.yaml',path))
    return path in ('catalog.yaml','apps.yaml') or bool(re.fullmatch('(repositories|provenance)/'+contracts.NAME+r'\.yaml',path))


def decode(path,raw,channel):
    if not allowed(path,channel): raise ValueError('unexpected catalog path')
    if channel=='status-1':
        obj=contracts.decode(raw)
        expected=path[:-5] if '/' not in path else 'summary' if path.endswith('/summary.yaml') else 'source'
        if obj['kind']!=expected: raise ValueError('status kind/path')
        if expected!='source': return obj,dict(root=obj)
        return obj,dict(repository_id=obj['repository_id'],run=obj['run'])
    if channel=='format-2':
        obj=decode_document(raw,contracts.FILE_CAP)
        if document(obj).encode()!=raw: raise ValueError('noncanonical format-2 document')
        if path=='apps.yaml': return obj,dict(apps=obj['apps'])
        if path!=f"repositories/{obj['repository_id']}.yaml": raise ValueError('source path identity')
        meta=dict(repository_id=obj['repository_id'],repository=obj['repository'],
                  attempted_at=obj['collection']['attempted_at'],
                  completed_at=obj.get('last_success',{}).get('completed_at'))
    else:
        obj=contracts.decode(raw)
        expected=path[:-5] if '/' not in path else 'provenance' if path.startswith('provenance/') else 'repository'
        if obj['kind']!=expected: raise ValueError('catalog kind/path')
        if expected!='repository': return obj,dict(root=obj)
        meta=dict(repository_id=obj['repository_id'],repository=obj['repository'],
                  attempted_at=obj['collected_at'],completed_at=obj['collected_at'])
    return obj,meta


def references(metadata,channel):
    if channel=='status-1':
        if 'status.yaml' not in metadata: raise ValueError('missing status root')
        status=metadata['status.yaml']['root']
        if len(status['summaries'])>64 or len(status['details'])>8: raise ValueError('status retention')
        for key,path in status['summaries'].items():
            if path!=f'runs/{key}/summary.yaml' or path not in metadata: raise ValueError('status summary reference')
        if status['last_report'] not in status['summaries'].values(): raise ValueError('last report reference')
        for path,meta in metadata.items():
            if not path.startswith('runs/'):continue
            run=meta.get('run') or meta['root']['run'];key=str(run['id'])+'-'+str(run['attempt'])
            if not path.startswith('runs/'+key+'/'):raise ValueError('run path identity')
            if '/sources/' in path and key not in status['details']:raise ValueError('source detail coverage')
        if 'statistics.yaml' in metadata and len(metadata['statistics.yaml']['root']['days'])>90: raise ValueError('daily retention')
        return
    ids={}
    for path,meta in metadata.items():
        if path.startswith('repositories/'):
            rid=meta['repository_id']
            if rid in ids: raise ValueError('duplicate numeric source')
            ids[rid]=path
    if 'apps.yaml' not in metadata: raise ValueError('missing apps')
    if channel=='format-2':
        apps=metadata['apps.yaml']['apps']
        if any(type(rid) is not int or rid not in ids for rid in apps.values()): raise ValueError('app source identity')
        return
    if 'catalog.yaml' not in metadata: raise ValueError('missing catalog roots')
    contracts.provenance_references(metadata['apps.yaml']['root']['apps'],
        {path:meta['repository_id'] for path,meta in metadata.items() if path.startswith('repositories/')},
        {path:meta['root'] for path,meta in metadata.items() if path.startswith('provenance/')},metadata['catalog.yaml']['root']['inputs'])



class Snapshot(Mapping):
    def __init__(self,repo,commit,channel='format-3'):
        contracts.pin(commit)
        self.repo=Path(repo);self.commit=commit;self.channel=channel;self.rule_id=rules()
        self.entries={};self.metadata={};self._trust=None
        started=time.monotonic()
        listing=self.local('ls-tree','-rlz',commit,cap=(32 if channel=='status-1' else 4)*1024*1024)
        total=0
        for row in listing.split(b'\0'):
            if not row: continue
            attributes,name=row.split(b'\t',1);mode,kind,blob,size=attributes.split()
            path=name.decode('ascii');size=int(size)
            total+=size
            if mode!=b'100644' or kind!=b'blob' or not allowed(path,channel): raise ValueError('catalog Git layout')
            if size>contracts.FILE_CAP or total>contracts.TREE_CAP or len(self.entries)>=(100000 if channel=='status-1' else 20000): raise ValueError('snapshot bound')
            self.entries[path]=(blob.decode(),size)
        # A descriptor's or imported artifact's validation claim is never trusted.
        for path in self.entries:
            _,self.metadata[path]=decode(path,self[path],channel)
        references(self.metadata,channel)
        self._trust=_TRUST
        self.validation=dict(mode='full_parent_fallback',documents=len(self.entries),bytes=total,
                             seconds=time.monotonic()-started,rules=self.rule_id,commit=commit)

    def local(self,*args,cap):
        return bounded(['git','-C',str(self.repo),'-c','core.hooksPath=/dev/null',*args],env=environment(),cap=cap)

    def __getitem__(self,path):
        blob,size=self.entries[path]
        raw=self.local('cat-file','blob',blob,cap=contracts.FILE_CAP)
        if len(raw)!=size or oid(raw)!=blob: raise ValueError('blob identity')
        return raw

    def __iter__(self): return iter(self.entries)
    def __len__(self): return len(self.entries)

    def trusted(self):
        return self._trust is _TRUST and self.rule_id==rules()


class Records(Mapping):
    """Source records decode only when the collection selects them."""
    def __init__(self,snapshot):
        self.snapshot=snapshot
        self.paths={str(meta['repository_id']):path for path,meta in snapshot.metadata.items() if path.startswith('repositories/')}
        self.metadata={rid:snapshot.metadata[path] for rid,path in self.paths.items()}
    def __iter__(self): return iter(self.paths)
    def __len__(self): return len(self.paths)
    def __getitem__(self,rid): return decode(self.paths[rid],self.snapshot[self.paths[rid]],self.snapshot.channel)[0]


class Candidate(Mapping):
    def __init__(self,parent,changed,channel='format-3',removed=()):
        if parent is not None and (not isinstance(parent,Snapshot) or not parent.trusted() or parent.channel!=channel):
            raise ValueError('untrusted parent: perform full snapshot validation')
        self.parent=parent;self.channel=channel;self.changed=dict(changed)
        self.metadata=dict(parent.metadata) if parent else {}
        self.entries=dict(parent.entries) if parent else {}
        for path in removed:
            self.metadata.pop(path,None);self.entries.pop(path,None)
        decoded=0;reused=0
        for path,raw in self.changed.items():
            if type(raw) is not bytes or len(raw)>contracts.FILE_CAP: raise ValueError('changed document bound')
            entry=(oid(raw),len(raw))
            if parent and parent.entries.get(path)==entry:
                reused+=1
            else:
                _,self.metadata[path]=decode(path,raw,channel);decoded+=1
            self.entries[path]=entry
        if sum(size for _,size in self.entries.values())>contracts.TREE_CAP or len(self.entries)>(100000 if channel=='status-1' else 20000): raise ValueError('candidate bound')
        references(self.metadata,channel)
        unchanged=sum(parent.entries.get(path)==entry for path,entry in self.entries.items()) if parent else 0
        self.validation=dict(changed_documents=decoded,reused_documents=unchanged,
                             tree_bytes=sum(size for _,size in self.entries.values()),documents=len(self.entries),rules=rules())
    def __iter__(self): return iter(self.entries)
    def __len__(self): return len(self.entries)
    def __getitem__(self,path):
        if path not in self.entries: raise KeyError(path)
        if path in self.changed: return self.changed[path]
        return self.parent[path]
