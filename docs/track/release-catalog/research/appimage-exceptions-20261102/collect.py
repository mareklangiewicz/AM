import sys,json,time,hashlib
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'tools/catalog-collector'))
import identity_batch as identity
from migration_evidence import release_request
from migration_batch import pipeline
import subprocess
# Reuse the bounded evidence transport in an isolated module, extending only
# its URL allowlist to the four exact numeric identity URLs below.
# Instead of changing production transport, load just fetch with a narrow
# regex facade permitting numeric identity URLs, all other regexes unchanged.
import types,re
class ScopedRegex:
 def fullmatch(self,pattern,value,*args,**kwargs):
  if pattern.startswith(r'https://api') and value in allowed: return re.fullmatch(re.escape(value),value)
  return re.fullmatch(pattern,value,*args,**kwargs)
 def __getattr__(self,key): return getattr(re,key)
ns=dict(identity.fetch.__globals__); ns['re']=ScopedRegex()
fetch=types.FunctionType(identity.fetch.__code__,ns,argdefs=identity.fetch.__defaults__)
fetch.__kwdefaults__=identity.fetch.__kwdefaults__
items=[('mysteryx93/NaturalGroundingPlayer',37950127),('DavidVentura/offline-translator-linux',1069135746),('Jermolene/TiddlyDesktop',15743523),('LifetimeLabsDev/privacynotes.app',1227817920)]
allowed={f'https://api.github.com/repositories/{rid}' for _,rid in items}
out=Path('docs/track/release-catalog/research/appimage-exceptions-20261102');out.mkdir(exist_ok=False)
(out/'.gitattributes').write_text('**/headers.txt -text\n')
payload=json.loads(identity.PAYLOAD.read_bytes()); result=[]; deadline=time.monotonic()+300
for n,(old,rid) in enumerate(items,1):
 def validate(v,b):
  assert type(v) is dict and v['id']==rid and v['private'] is False and v['visibility']=='public'
  assert re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',v['full_name'])
  return dict(identity={k:v[k] for k in ('id','full_name','private','visibility')})
 row=dict(original=old,repository_id=rid)
 report=fetch(f'https://api.github.com/repositories/{rid}',out/f'identity-{n}',deadline,validate_value=validate)
 row['identity']=report
 if report['accepted']:
  release=release_request(f'https://api.github.com/repositories/{rid}/releases',rid,out/f'release-{n}',deadline)
  row['release']=release
  if release['accepted']:
   body=(out/f'release-{n}'/'body.json').read_bytes(); releases=json.loads(body); assets={a['browser_download_url'] for r in releases for a in r['assets']}
   matches=[r for r in payload['rows'] if r['alias']==f'https://api.github.com/repos/{old}/releases']; assert len(matches)==1
   row['recipes']=[]
   for recipe in matches[0]['recipes']:
    selections=[]
    for key in ('install_selector','update_selector'):
     value=subprocess.run(['sh','-c','APP='+Path(recipe['path']).name+'\n'+pipeline(matches[0],recipe[key])],input=body,capture_output=True,check=True).stdout.decode().strip();selections.append(value)
    row['recipes'].append(dict(path=recipe['path'],selected=selections,actual_asset=selections[0]==selections[1] and selections[0] in assets))
 result.append(row)
 (out/'review.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(dict(original=old,identity=report.get('identity'),status=report.get('status'),recipes=row.get('recipes'))),flush=True)
