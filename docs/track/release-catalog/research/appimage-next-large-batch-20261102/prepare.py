import sys,json,collections,hashlib,re,subprocess,difflib,tempfile
from pathlib import Path
sys.path.insert(0,'tools/catalog-collector')
from recipe_inventory import recipe
import migration_batch
root=Path.cwd();frames=set(json.load(open('docs/track/release-catalog/research/recipe-family-inventory.json'))['batch_family_fingerprints']);excluded={r['alias'] for r in json.load(open('docs/track/release-catalog/research/remaining-appimage-preparation-20261102.json'))['rows']};groups=collections.defaultdict(list)
def pipeline(row,selector):
 m=re.fullmatch(r"version=\$\(curl -Ls\s+(['\"]?)"+re.escape(row['alias'])+r"\1\s*\| (.*)\)",selector)
 if not m:raise ValueError(selector)
 return m.group(2)
migration_batch.pipeline=pipeline
for arch in ('x86_64','aarch64','i686','armv7l'):
 for p in (root/'programs'/arch).iterdir():
  if not p.is_file():continue
  r,b=recipe(p)
  if r['fingerprint'] not in frames:continue
  versions=[l.strip() for l in b.decode().splitlines() if l.strip().startswith('version=')];urls={q['url'] for q in r['requests']}
  if len(versions)!=2 or len(set(versions))!=1 or len(urls)!=1:continue
  alias=next(iter(urls))
  if alias in excluded or not re.fullmatch(r'https://api.github.com/repos/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/releases(?:/latest)?',alias):continue
  r.update(sha256=hashlib.sha256(b).hexdigest(),install_selector=versions[0],update_selector=versions[1])
  try:pipeline(dict(alias=alias),versions[0])
  except ValueError:continue
  groups[alias].append(r)
selected=[];count=0
for alias in sorted(groups,key=lambda a:(-len(groups[a]),a)):
 if count>=1000:break
 selected.append(dict(alias=alias,identity_request=alias.split('/releases')[0],recipes=groups[alias]));count+=len(groups[alias])
out=root/'docs/track/release-catalog/research/appimage-next-large-batch-20261102';out.mkdir(exist_ok=True);patch=[];before=after=0
with tempfile.TemporaryDirectory() as tmp:
 for row in selected:
  for r in row['recipes']:
   p=root/r['path'];old=p.read_text();new=migration_batch.compact_recipe(r,row);candidate=Path(tmp)/p.name;candidate.write_text(new);subprocess.run(['sh','-n',str(candidate)],check=True)
   before+=len(old.splitlines());after+=len(new.splitlines())
   for line in difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+r['path'],tofile='b/'+r['path']):patch.append(line if line.endswith('\n') else line+'\n\\ No newline at end of file\n')
value=dict(source_revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),available_recipes=sum(map(len,groups.values())),available_endpoints=len(groups),candidate_recipes=count,candidate_endpoints=len(selected),identity_requests=sorted({r['identity_request'] for r in selected}),rows=selected,static_candidate_lines_removed=before-after,metadata_verified=False,production_applied=False)
(out/'payload.json').write_text(json.dumps(value,indent=2)+'\n');(out/'recipes.patch').write_text(''.join(patch))
subprocess.run(['git','apply','--check',str(out/'recipes.patch')],check=True)
print(json.dumps({k:v for k,v in value.items() if k not in ('rows','identity_requests')},indent=2));print('identity requests:',len(value['identity_requests']))
