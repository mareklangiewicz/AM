"""Read-only host inventory and exact local cutover review packages.

Never executes an installed manager/updater or mutates an installation. This is
maintainer tooling. Source commits and local inventory are trusted review inputs.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess

from yaml_installed_migration import directory, managed_updater

V1_REF = 'refs/heads/release-catalog'
V2_REF = 'refs/heads/release-catalog-yaml-v2'
ARCHES = ('x86_64', 'aarch64', 'i686', 'armv7l')


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()


def record(path):
    path = Path(path)
    directory(path.parent)
    info = path.lstat()
    result = dict(path=str(path),mode=stat.S_IMODE(info.st_mode),uid=info.st_uid,
                  gid=info.st_gid,size=info.st_size,links=info.st_nlink)
    if stat.S_ISLNK(info.st_mode):
        result.update(kind='symlink',target=os.readlink(path))
    elif stat.S_ISREG(info.st_mode):
        result.update(kind='file',sha256=sha256(path),xattrs=sorted(os.listxattr(path)))
    else:
        result['kind']='unsupported'
    latest=path.lstat()
    identity=lambda v: (v.st_dev,v.st_ino,v.st_mode,v.st_uid,v.st_gid,v.st_size,
                        v.st_nlink,v.st_mtime_ns,v.st_ctime_ns)
    if identity(latest) != identity(info):
        raise ValueError('file changed during inventory: '+str(path))
    return result


def updater_paths(roots):
    return sorted(str(p/'AM-updater') for root in roots for p in Path(root).iterdir()
                  if not p.is_symlink() and p.is_dir() and
                  ((p/'AM-updater').exists() or (p/'AM-updater').is_symlink()))


def verify_inventory(inventory):
    scope=inventory['scope']
    if updater_paths(scope['roots']) != scope['updater_paths']:
        raise ValueError('installed updater set changed')
    if sorted(str(p) for p in Path(scope['modules']).glob('*.am')) != scope['module_paths']:
        raise ValueError('installed module set changed')
    config=scope['appman_config']
    if (Path(config['path']).exists() or Path(config['path']).is_symlink()) != config['exists']:
        raise ValueError('AppMan configuration appeared/disappeared')
    for name,exists in inventory['scope']['config_probes'].items():
        if (Path(name).exists() or Path(name).is_symlink()) != exists:
            raise ValueError('manager configuration appeared/disappeared')
    for expected in inventory['files'].values():
        if record(expected['path']) != expected:
            raise ValueError('installed drift: '+expected['path'])


def text_file(path):
    entry = record(path)
    if entry['kind'] != 'file' or entry['size'] > 1048576:
        raise ValueError('unsupported script/config: '+str(path))
    return Path(path).read_text()


def inventory(roots, manager, modules, architecture, appman_config, am_data):
    if architecture not in ARCHES:
        raise ValueError('explicit architecture required')
    roots = sorted(set(str(directory(root)) for root in roots))
    directory(modules)
    files, clients = {}, []
    def capture(path):
        value = record(path)
        files[str(path)] = value
        return value
    if capture(manager)['kind'] != 'file':
        raise ValueError('manager must be a regular file, not a symlink')
    for path in sorted(Path(modules).glob('*.am')):
        capture(path)
    config = Path(appman_config)
    config_state = dict(path=str(config),exists=config.exists() or config.is_symlink())
    if config_state['exists']:
        capture(config)
        configured = text_file(config).strip()
        # Do not follow an unreviewed home-relative path or excluded tree.
        if not configured.startswith('/') or configured not in roots:
            raise ValueError('configured AppMan root must be explicitly included')
        config_state['root']=configured
    probes={}
    for path in (Path(am_data)/'newrepo-on',Path(am_data)/'betatester',
                 config.parent/'appman-mode'):
        probes[str(path)]=path.exists() or path.is_symlink()
        if probes[str(path)] and capture(path)['kind'] != 'file':
            raise ValueError('configuration probe must be a regular file')
    skipped=[]
    for root in roots:
        for installed in sorted(Path(root).iterdir()):
            if installed.is_symlink():
                skipped.append(dict(path=str(installed),reason='symlink not traversed'))
                continue
            if not installed.is_dir(): continue
            updater = installed/'AM-updater'
            if not updater.exists() and not updater.is_symlink():
                continue
            capture(updater)
            script = text_file(updater)
            recipe = installed/'recipe.am'
            recipe_text = ''
            if recipe.exists() or recipe.is_symlink():
                capture(recipe)
                recipe_text = text_file(recipe)
            shared = '# AM-CATALOG-UPDATER 1' in script.splitlines()
            catalog = bool(re.search(r'catalog(?:-yaml)?\.am|CATALOG_',script+'\n'+recipe_text))
            client = dict(installation=str(installed),app=installed.name,
                          recipe=f'{architecture}/{installed.name}',
                          kind='managed-catalog' if shared else
                               ('unrecognized-catalog' if catalog else 'legacy-standalone'),
                          format=2 if 'CATALOG_FORMAT=2' in recipe_text.splitlines() else
                                 (1 if catalog else None),catalog_reference=catalog)
            for name in ('version',installed.name):
                path = installed/name
                if path.exists() or path.is_symlink():
                    capture(path)
                else:
                    client.setdefault('missing',[]).append(name)
            clients.append(client)
    return dict(format=1,captured_at=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                scope=dict(roots=roots,architecture=architecture,manager=str(manager),
                           modules=str(modules),appman_config=config_state,
                           config_probes=probes,skipped=skipped,updater_paths=updater_paths(roots),
                           module_paths=sorted(str(p) for p in Path(modules).glob('*.am')),
                           completeness='explicit local roots only; no other-host assertion'),
                files=dict(sorted(files.items())),clients=clients)


def git(source,*args):
    return subprocess.check_output(['git','-C',str(source),*args])


def blob(source,pin,path):
    return git(source,'show',pin+':'+path)


def pin_check(source,pin):
    if not re.fullmatch('[0-9a-f]{40}',pin):
        raise ValueError('full source pin required')
    if git(source,'rev-parse',pin+'^{commit}').decode().strip() != pin:
        raise ValueError('source pin must name commit')


def quote(value):
    return '"'+value.replace('\\','\\\\').replace('"','\\"').replace('$','\\$').replace('`','\\`')+'"'


def bound_recipe(body, source_url, paths, modules):
    """Mirror the compact recipe binding subset; verify old bytes before reuse."""
    text = body.decode()
    entry = '. "/opt/am/modules/appimage.am"'
    if text.splitlines().count(entry) != 1 or '# AM-CATALOG-RECIPE 1' not in text.splitlines():
        raise ValueError('unsupported compact recipe')
    helper = 'catalog-yaml.am' if 'CATALOG_FORMAT=2' in text.splitlines() else 'catalog.am'
    binding = 'AMREPO=${AMREPO-'+quote(source_url)+'}\n'
    binding += ''.join(name+'='+quote(paths[name])+'\n' for name in
                       ('APPS_DIR','BIN_DIR','DESKTOP_DIR'))
    name = 'CATALOG_YAML_HELPER' if helper == 'catalog-yaml.am' else 'CATALOG_HELPER'
    binding += name+'='+quote(str(Path(modules)/helper))+'\n'
    return text.replace(entry,binding+'. '+quote(str(Path(modules)/'appimage.am'))).encode()


def installed_bindings(text):
    values = {}
    for name in ('APPS_DIR','BIN_DIR','DESKTOP_DIR'):
        rows = re.findall('^'+name+r'="([^"\n]+)"$',text,re.M)
        if len(rows) != 1 or not rows[0].startswith('/') or any(c in rows[0] for c in '\\$`'):
            raise ValueError('unsupported installed path binding: '+name)
        values[name]=rows[0]
    rows = re.findall(r'^AMREPO=\$\{AMREPO-"(https://raw\.githubusercontent\.com/[A-Za-z0-9_.+/-]+)"\}$',text,re.M)
    if len(rows) != 1:
        raise ValueError('unsupported installed source binding')
    return rows[0],values


def installation_key(path):
    return Path(path).name+'-'+hashlib.sha256(str(path).encode()).hexdigest()


def package(source,pin,legacy_pin,source_repository,observed,output):
    source = directory(source)
    for revision in (pin,legacy_pin): pin_check(source,revision)
    if not re.fullmatch('[A-Za-z0-9-]+/[A-Za-z0-9_.-]+',source_repository):
        raise ValueError('explicit source owner/repository required')
    verify_inventory(observed)
    output = Path(output)
    directory(output.parent)
    output.mkdir(mode=0o700,exist_ok=False)
    def save(name,data):
        path = output/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)
    save('inventory.json',(json.dumps(observed,sort_keys=True,indent=2)+'\n').encode())
    # Exact Git archive, never a dirty checkout or implicit rolling source ref.
    subprocess.run(['git','-C',str(source),'archive','--format=tar.gz',
                    '--output='+str(output/'source.tar.gz'),pin],check=True)
    for expected in observed['files'].values():
        path = Path(expected['path'])
        # Recovery package retains manager/modules and small installed scripts;
        # binaries are guarded by hashes, not claimed to be backed up.
        manager = observed['scope']['manager']
        modules = observed['scope']['modules']
        if str(path)==manager:
            save('before/APP-MANAGER',path.read_bytes())
        elif path.parent == Path(modules):
            if expected['kind']!='file': raise ValueError('unsupported installed module link')
            save('before/modules/'+path.name,path.read_bytes())
        elif path.name in ('recipe.am','AM-updater','version'):
            if expected['kind']!='file': raise ValueError('unsupported installed script link')
            save('before/clients/'+installation_key(path.parent)+'/'+path.name,path.read_bytes())
    source_url='https://raw.githubusercontent.com/'+source_repository+'/'+pin
    shared=git(source,'grep','-l','^# AM-CATALOG-RECIPE 1$',pin,'--','programs').splitlines()
    yaml_recipes=git(source,'grep','-l','^CATALOG_FORMAT=2$',pin,'--','programs').splitlines()
    clients=[]
    for client in observed['clients']:
        row=dict(client,installation_id=installation_key(client['installation']))
        row['replacement']=None
        if client['kind']!='managed-catalog':
            row['disposition']='separate-legacy-updater-adapter-required'
            clients.append(row)
            continue
        path=Path(client['installation'])/'recipe.am'
        old=path.read_bytes()
        replacement=blob(source,pin,'programs/'+client['recipe'])
        if b'CATALOG_FORMAT=2' not in replacement.splitlines():
            row['disposition']='retain-format-1-not-yaml-enrolled'
            clients.append(row)
            continue
        previous_source,paths=installed_bindings(old.decode())
        legacy=bound_recipe(blob(source,legacy_pin,'programs/'+client['recipe']),
                            previous_source,paths,observed['scope']['modules'])
        if old!=legacy:
            raise ValueError('installed recipe differs from exact legacy source binding: '+str(path))
        expected_updater=managed_updater(path)
        if path.with_name('AM-updater').read_bytes()!=expected_updater:
            raise ValueError('unsupported installed trampoline: '+str(path))
        final=bound_recipe(replacement,source_url,paths,observed['scope']['modules'])
        for name in ('PACKAGE_KIND','REFRESH_ALWAYS','CATALOG_ALIAS'):
            get=lambda b: re.findall(rb'^'+name.encode()+rb'=.*$',b,re.M)
            if get(old)!=get(final): raise ValueError('package semantics changed: '+name)
        if Path(paths['APPS_DIR']).resolve()/client['app'] != path.parent:
            raise ValueError('installed directory binding mismatch')
        name='replacements/'+row['installation_id']+'.am'
        save(name,final)
        row.update(disposition='bound-ready-pending-publication',replacement=name,
                   expected_old_sha256=hashlib.sha256(old).hexdigest(),
                   source_recipe_sha256=hashlib.sha256(replacement).hexdigest())
        clients.append(row)
    # Actual old hashes are included for delivery/rollback review. New source
    # manager and all modules are shipped byte-exact alongside the source archive.
    names=git(source,'ls-tree','-r','--name-only',pin,'modules').decode().splitlines()
    save('runtime/APP-MANAGER',blob(source,pin,'APP-MANAGER'))
    for name in names:
        if name.endswith('.am'):
            save('runtime/'+name,blob(source,pin,name))
    # Reject installed drift across package construction; no installed writes.
    verify_inventory(observed)
    payload={p.relative_to(output).as_posix():dict(sha256=sha256(p),size=p.stat().st_size)
             for p in sorted(output.rglob('*')) if p.is_file()}
    manifest=dict(format=1,source_pin=pin,legacy_source_pin=legacy_pin,
        source_coverage=dict(shared_recipe_paths=len(shared),format2_paths=len(yaml_recipes),
                             remaining_format1_paths=len(shared)-len(yaml_recipes)),
        source_repository=source_repository,source_url=source_url,
        publication=dict(format1_ref=V1_REF,format2_ref=V2_REF,
            status='local proposal; no refs created or remotely inspected',
            publication_pin=None,selected_records=None),
        apply_ready=False,clients=clients,payload=payload,
        remaining=['review source package and installed inventory',
            'accept policies/stale UI and validate realistic capacity',
            'authorize source publication and workflow/ref transition',
            'acquire and verify exact format-2 publication and selected records',
            'deliver exact manager/modules with guarded recovery',
            'create per-installation migrator plans and review stale consent',
            'unenrolled catalog clients and legacy standalone adapters remain separate scope',
            'binary update/rollback and natural scheduled cycle acceptance'])
    save('manifest.json',(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode())
    return manifest


def verify_package(output):
    output=directory(output)
    text_file(output/'manifest.json')
    manifest=json.loads((output/'manifest.json').read_text())
    actual=set()
    for path in output.rglob('*'):
        if path.is_symlink(): raise ValueError('package symlink refused')
        if path.is_file(): actual.add(path.relative_to(output).as_posix())
    if actual != set(manifest['payload'])|{'manifest.json'}:
        raise ValueError('package file set changed')
    for name,expected in manifest['payload'].items():
        if not re.fullmatch(r'[A-Za-z0-9_.+/-]+',name) or '..' in Path(name).parts or name.startswith('/'):
            raise ValueError('invalid package path')
        path=output/name
        if sha256(path)!=expected['sha256'] or path.stat().st_size!=expected['size']:
            raise ValueError('package payload drift: '+name)
    return manifest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    inv=commands.add_parser('inventory')
    inv.add_argument('--root',action='append',required=True)
    for key in ('manager','modules','architecture','appman-config','am-data','out'):
        inv.add_argument('--'+key,required=True)
    build=commands.add_parser('build')
    for key in ('source','pin','legacy-pin','source-repository','inventory','out'):
        build.add_argument('--'+key,required=True)
    verify=commands.add_parser('verify');verify.add_argument('directory')
    args=vars(parser.parse_args());command=args.pop('command')
    if command=='inventory':
        out=Path(args.pop('out'));roots=args.pop('root')
        value=inventory(roots,**args)
        with out.open('x') as stream: json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n')
    elif command=='build':
        observed=json.loads(text_file(args.pop('inventory')))
        output=args.pop('out')
        package(observed=observed,output=output,**args)
        verify_package(output)
    else:
        manifest=verify_package(args['directory'])
        print('verified source '+manifest['source_pin']+'; apply_ready='+str(manifest['apply_ready']))


if __name__=='__main__': main()
