"""Bounded Git reference/file observations, without synthetic release IDs."""
import base64
import hashlib
import json
import re
from urllib.parse import quote

from bounded import unique_object


def key(name):return hashlib.sha256(name.encode('utf-8')).hexdigest()


def valid_ref(name):
    return (isinstance(name,str) and len(name.encode())<=1024 and
        re.fullmatch(r'refs/(heads|tags)/[^\s\x00-\x1f\x7f~^:?*\\\[]+',name) is not None and
        not any(part in name for part in ('..','@{','//')) and not name.endswith(('/','.','.lock')))


def valid_path(path):
    return (isinstance(path,str) and 0<len(path.encode())<=1024 and not path.startswith('/') and
            not re.search(r'[\x00-\x1f\x7f]',path) and not any(p in ('.','..') for p in path.split('/')))


def configuration(root):
    path=root/'tools/catalog-collector/git-sources.json'
    if not path.exists():return {}
    result=json.loads(path.read_text(),object_pairs_hook=unique_object)
    if not isinstance(result,dict):raise ValueError('Git source configuration')
    for rid,scope in result.items():
        if (not re.fullmatch('[1-9][0-9]*',rid) or not isinstance(scope,dict) or
                set(scope)!={'tags','branches'} or type(scope['tags']) is not bool or
                not isinstance(scope['branches'],dict) or len(scope['branches'])>4):
            raise ValueError('Git source scope')
        for branch,files in scope['branches'].items():
            if (not valid_ref('refs/heads/'+branch) or not isinstance(files,list) or
                    len(files)>4 or len(set(files))!=len(files) or not all(valid_path(path) for path in files)):
                raise ValueError('Git branch/file scope')
    return result


def collect(scope,fetch):
    refs={};times=[];complete=False
    def get(kind,endpoint):
        raw,at=fetch(kind,endpoint);times.append(at)
        return json.loads(raw,object_pairs_hook=unique_object),at
    if scope['tags']:
        tags,at=get('tags','tags?per_page=100&page=1')
        if not isinstance(tags,list) or len(tags)>100:raise ValueError('Git tag response')
        complete=len(tags)<100
        for position,tag in enumerate(tags):
            name='refs/tags/'+tag['name'];commit=tag['commit']['sha']
            if not valid_ref(name) or not re.fullmatch('[0-9a-f]{40}',commit) or key(name) in refs:
                raise ValueError('Git tag identity')
            refs[key(name)]=dict(name=name,commit=commit,observed_at=at,position=position)
    branches={}
    for branch,files in scope['branches'].items():
        name='refs/heads/'+branch
        obj,at=get('ref-'+key(name),'git/ref/heads/'+quote(branch,safe=''))
        commit=obj['object']['sha']
        if obj.get('ref')!=name or obj['object'].get('type')!='commit' or not re.fullmatch('[0-9a-f]{40}',commit):
            raise ValueError('Git branch identity')
        record=dict(name=name,commit=commit,observed_at=at)
        observations={}
        for path in files:
            file,observed=get('file-'+key(name+'\0'+path),'contents/'+quote(path,safe='/')+'?ref='+commit)
            if (file.get('type')!='file' or file.get('path')!=path or file.get('encoding')!='base64' or
                    type(file.get('size')) is not int or not 0<=file['size']<=1048576 or
                    not isinstance(file.get('content'),str) or len(file['content'])>1500000 or
                    not re.fullmatch('[0-9a-f]{40}',file.get('sha',''))):
                raise ValueError('Git file identity/size')
            try:raw=base64.b64decode(file['content'].replace('\n',''),validate=True)
            except (ValueError,UnicodeError):raise ValueError('Git file encoding') from None
            digest=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            if len(raw)!=file['size'] or digest!=file['sha']:raise ValueError('Git file blob mismatch')
            observations[key(path)]=dict(path=path,blob=digest,observed_at=observed,content=raw.decode('utf-8'))
        if observations:record['files']=observations
        refs[key(name)]=record;branches[key(name)]=name
    return dict(git_scope=dict(tags=scope['tags'],tags_history_complete=complete,branches=branches),
                git_refs=refs,completed_at=max(times) if times else None)
