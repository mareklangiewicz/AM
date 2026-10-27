from pathlib import Path
import os,stat,hashlib,json,datetime,subprocess,tempfile,shutil
repo=Path('/home/marek/code/shell/AM'); payload=repo/'docs/track/release-catalog/pilot'
manifest=json.loads((payload/'manifest.json').read_text())
expected={'APP-MANAGER':'bb32c8ea853b06660f2d50cd9300f241a6403b08088cd6c80dc1fc952a0800f9','install.am':'695bbefd85e62cf7a9a0755fc88350c7255b239b56e01a786ee55080007b6796','catalog.am':None,'AM-updater':'aa94662966dcd31ff09dbda5ece63f2f55a8c3edc3326d8bb43a0aff5dc9d969'}
targets={'APP-MANAGER':Path('/opt/am/APP-MANAGER'),'install.am':Path('/opt/am/modules/install.am'),'catalog.am':Path('/opt/am/modules/catalog.am'),'AM-updater':Path('/opt/obsidian/AM-updater')}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot(p):
 s=p.lstat()
 return {'sha256':digest(p),'mode':stat.S_IMODE(s.st_mode),'uid':s.st_uid,'gid':s.st_gid,'symlink':os.readlink(p) if p.is_symlink() else None}
watch=[Path(x) for x in ['/opt/obsidian/obsidian','/opt/obsidian/version','/usr/local/bin/obsidian','/usr/local/share/applications/obsidian-AM.desktop']]
before={str(p):snapshot(p) for p in watch}
assert before['/opt/obsidian/obsidian']['sha256']=='6362ddbeeeebb7bbccb48fae009572cf2284ef92f5c919c1332aba48de6ffeaa'
assert before['/opt/obsidian/version']['sha256']=='8318ae383cf75a90dbb710380d80b70ca49bf069a46488a98da586785e53f6a1'
assert not Path('/opt/obsidian/AM-VERIFIED').exists()
old={}
for name,p in targets.items():
 assert not p.is_symlink()
 if expected[name] is None:assert not p.exists();old[name]=None
 else:
  assert stat.S_ISREG(p.lstat().st_mode) and digest(p)==expected[name],str(p)+' drift'
  old[name]=snapshot(p)
 assert digest(payload/name)==manifest['files'][name]['sha256']
 subprocess.run(['bash' if name in ('APP-MANAGER','install.am') else 'sh','-n',str(payload/name)],check=True)
backup=Path('/opt/am/catalog-pilot-backups')/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
backup.mkdir(parents=True,mode=0o700)
for name,p in targets.items():
 if old[name] is not None:
  shutil.copy2(p,backup/name);os.chown(backup/name,old[name]['uid'],old[name]['gid'])
  assert snapshot(backup/name)==old[name]
record={'backup':str(backup),'old':old,'targets':{n:str(p) for n,p in targets.items()},'payload':manifest,'unchanged_before':before}
(backup/'manifest.json').write_text(json.dumps(record,indent=2)+'\n')
staged={};done=[]
def stage(p,data,metadata):
 fd,tmp=tempfile.mkstemp(prefix='.catalog-pilot-',dir=p.parent)
 try:
  with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
  os.chown(tmp,metadata['uid'],metadata['gid']);os.chmod(tmp,metadata['mode'])
 except BaseException:
  os.unlink(tmp);raise
 return Path(tmp)
try:
 for name,p in targets.items():
  meta=old[name] or {**old['APP-MANAGER'],'mode':0o644}
  staged[name]=stage(p,(payload/name).read_bytes(),meta)
  assert digest(staged[name])==manifest['files'][name]['sha256']
 for name,p in targets.items():
  if old[name] is None:assert not p.exists() and not p.is_symlink()
  else:assert snapshot(p)==old[name]
  os.replace(staged[name],p);done.append(name)
 for name,p in targets.items():
  assert digest(p)==manifest['files'][name]['sha256']
  meta=old[name] or {**old['APP-MANAGER'],'mode':0o644}
  s=p.stat();assert (s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode))==(meta['uid'],meta['gid'],meta['mode'])
  subprocess.run(['bash' if name in ('APP-MANAGER','install.am') else 'sh','-n',str(p)],check=True)
 after={str(p):snapshot(p) for p in watch};assert before==after
 assert not Path('/opt/obsidian/AM-VERIFIED').exists()
 record.update(status='delivered',installed={n:snapshot(p) for n,p in targets.items()},unchanged_after=after,completed=datetime.datetime.now(datetime.timezone.utc).isoformat())
except BaseException:
 for name in reversed(done):
  p=targets[name]
  if old[name] is None:p.unlink()
  else:os.replace(stage(p,(backup/name).read_bytes(),old[name]),p)
 record['status']='rolled_back_after_failure'
 (backup/'result.json').write_text(json.dumps(record,indent=2)+'\n')
 raise
finally:
 for p in staged.values():
  if p.exists():p.unlink()
(backup/'result.json').write_text(json.dumps(record,indent=2)+'\n')
(repo/'docs/track/release-catalog/research/installed-pilot-delivery-result.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'status':record['status'],'backup':str(backup),'verified_files':len(targets),'app_state_unchanged':before==after},indent=2))
