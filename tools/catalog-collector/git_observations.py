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
    """What to read from Git for each repository (id -> {tags, branches}), derived
    from the recipes' Git selections (ticket 29): tags for a git-tag selection,
    a branch for git-branch, and that branch's file for git-file."""
    from recipe_declarations import recipe_rows, url_policy_rows
    result={}
    for row in url_policy_rows(root)+recipe_rows(root):
        selection=row.get('selection','asset')
        if not selection.startswith('git-'):continue
        scope=result.setdefault(str(row['repository_id']),dict(tags=False,branches={}))
        if selection=='git-tag':
            scope['tags']=True;continue
        files=scope['branches'].setdefault(row['git_ref'].removeprefix('refs/heads/'),[])
        if selection=='git-file' and row['git_file'] not in files:files.append(row['git_file'])
    for scope in result.values():
        if len(scope['branches'])>4:raise ValueError('Git source scope')
        for branch,files in scope['branches'].items():
            if not valid_ref('refs/heads/'+branch) or len(files)>4 or not all(valid_path(path) for path in files):
                raise ValueError('Git branch/file scope')
    return result


def collect(scope,fetch):
    """The repository document's git_scope and git_refs (schemas/catalog.schema.yaml):
    refs keyed by name, tags in listing order, branch files keyed by path and
    bound to the observed commit. Every Git fact inherits the repository's observed_at."""
    refs={};complete=False
    def get(kind,endpoint):
        raw,_=fetch(kind,endpoint)
        return json.loads(raw,object_pairs_hook=unique_object)
    if scope['tags']:
        tags=get('tags','tags?per_page=100&page=1')
        if not isinstance(tags,list) or len(tags)>100:raise ValueError('Git tag response')
        complete=len(tags)<100
        for position,tag in enumerate(tags):
            name='refs/tags/'+tag['name'];commit=tag['commit']['sha']
            if not valid_ref(name) or not re.fullmatch('[0-9a-f]{40}',commit) or name in refs:
                raise ValueError('Git tag identity')
            refs[name]=dict(commit=commit,position=position)
    for branch,paths in scope['branches'].items():
        name='refs/heads/'+branch
        obj=get('ref-'+key(name),'git/ref/heads/'+quote(branch,safe=''))
        commit=obj['object']['sha']
        if obj.get('ref')!=name or obj['object'].get('type')!='commit' or not re.fullmatch('[0-9a-f]{40}',commit):
            raise ValueError('Git branch identity')
        files={}
        for path in paths:
            file=get('file-'+key(name+'\0'+path),'contents/'+quote(path,safe='/')+'?ref='+commit)
            if (file.get('type')!='file' or file.get('path')!=path or file.get('encoding')!='base64' or
                    type(file.get('size')) is not int or not 0<=file['size']<=1048576 or
                    not isinstance(file.get('content'),str) or len(file['content'])>1500000 or
                    not re.fullmatch('[0-9a-f]{40}',file.get('sha',''))):
                raise ValueError('Git file identity/size')
            try:raw=base64.b64decode(file['content'].replace('\n',''),validate=True)
            except (ValueError,UnicodeError):raise ValueError('Git file encoding') from None
            digest=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            if len(raw)!=file['size'] or digest!=file['sha']:raise ValueError('Git file blob mismatch')
            files[path]=dict(blob=digest,content=raw.decode('utf-8'))
        refs[name]=dict(commit=commit,files=files) if files else dict(commit=commit)
    return dict(git_scope=dict(tags=scope['tags'],tags_history_complete=complete),git_refs=refs)
