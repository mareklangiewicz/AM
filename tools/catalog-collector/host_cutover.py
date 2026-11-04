"""Single-user AM cutover: stage downloads, preserve metadata, reinstall in place.

No uninstall scripts or home/config cleanup. Interrupted application is repaired
by rerunning apply or reinstalling; no transactional binary rollback is promised.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from host_catalog import configuration, ROOT, FILE_CAP
from yaml_installed_migration import managed_updater
from yaml_publication import load_local


def run(*args, **options):
    return subprocess.run(list(map(str,args)),check=True,**options)


def select(rows, repo, pin):
    apps, repositories = load_local(repo,pin,max_file_bytes=FILE_CAP)
    results = {}
    now = subprocess.check_output(['date','-u','+%Y-%m-%dT%H:%M:%SZ'],text=True).strip()
    with tempfile.TemporaryDirectory(prefix='am-host-select-') as scratch:
        for row in rows:
            app=row['app'];rid=str(row['repository_id'])
            if apps.get(app)!=row['repository_id']:
                raise ValueError('catalog source mismatch: '+app)
            document=Path(scratch)/(rid+'.yaml')
            if not document.exists():
                document.write_bytes(subprocess.check_output(['git','-C',str(repo),'show',pin+':repositories/'+rid+'.yaml']))
            facts=subprocess.check_output(['sh',str(ROOT/'modules/catalog-yaml-reader.am'),'asset_facts',str(document)])
            tools=('emmylua_ls','emmylua_check','emmylua_doc_cli','luafmt') if app=='emmylua' else (app,)
            selections={}
            for tool in tools:
                env=dict(os.environ,LC_ALL='C',AM_YAML_RECIPE='x86_64/'+app,
                    AM_YAML_PIN=pin,AM_YAML_REPOSITORY=rid,AM_YAML_NOW=now,
                    AM_YAML_TOOL=tool if app=='emmylua' else '',AM_YAML_INCLUDE_PUBLICATION='1',AM_YAML_ACCEPT='')
                fields=subprocess.check_output(['awk','-f',str(ROOT/'modules/catalog-yaml-policy.am')],input=facts,env=env).decode().splitlines()
                if len(fields)!=7:raise ValueError('selection protocol')
                selections[tool]=dict(commit=fields[0],repository_id=fields[1],release_id=fields[2],
                    asset_id=fields[3],observed_at=fields[4],url=fields[5],published_at=fields[6])
            if len({s['release_id'] for s in selections.values()})!=1:
                raise ValueError('EmmyLua release mismatch')
            results[app]=selections
    return results


def prepare(repo, out, cache):
    rows,_=configuration()
    pin=subprocess.check_output(['git','-C',str(repo),'rev-parse','refs/heads/catalog'],text=True).strip()
    selections=select(rows,repo,pin)
    source=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
    out.mkdir(mode=0o700)
    cache.mkdir(parents=True,exist_ok=True,mode=0o700)
    manifest=dict(source=source,catalog=pin,apps=rows,selections=selections)
    for row in rows:
        app=row['app'];target=out/app;target.mkdir()
        downloads={}
        for tool,selection in selections[app].items():
            # Cache by selected numeric asset, preserving complete files only.
            path=cache/(selection['repository_id']+'-'+selection['asset_id'])
            if not path.exists():
                partial=path.with_suffix('.part')
                run('curl','--silent','--show-error','--fail','--location','--connect-timeout','15','--max-time','600',
                    '--output',partial,selection['url'])
                if not partial.stat().st_size:raise ValueError('empty download')
                partial.rename(path)
            downloads[tool]=path
        if row['layout'] in ('raw','appimage'):
            (target/'payload').mkdir()
            shutil.copyfile(downloads[app],target/'payload'/app)
            (target/'payload'/app).chmod(0o755)
        else:
            stage=target/'archive';stage.mkdir()
            if row['layout']=='emmylua':
                for tool,path in downloads.items():shutil.copyfile(path,stage/(tool+'.tar.gz'))
            else:shutil.copyfile(downloads[app],stage/'asset')
            # Exercise the actual delivered archive adapter, not a second extractor.
            run('sh','-c','. "$1"; am_archive_stage "$2" "$3" "$4"','sh',
                ROOT/'modules/appimage.am',row['layout'],stage,app)
            (stage/'payload').rename(target/'payload')
            shutil.rmtree(stage)
        print('Staged '+app,flush=True)
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


def apply(prepared, root):
    manifest=json.loads((prepared/'manifest.json').read_text())
    source=manifest['source']
    if subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()!=source:
        raise ValueError('use the source revision that prepared this cutover')
    manager=root/'opt/am';apps=root/'opt';bins=root/'usr/local/bin'
    desktop=root/'usr/local/share/applications'
    # One simple, exclusive snapshot of manager and small app metadata. User
    # data remains where it is; binaries are replaceable downloads.
    backup=prepared/'before'
    if backup.exists() and not (backup/'complete').exists():
        raise ValueError('incomplete metadata snapshot; inspect before retry')
    if not backup.exists():
        backup.mkdir(mode=0o700)
        shutil.copy2(manager/'APP-MANAGER',backup/'APP-MANAGER')
        shutil.copytree(manager/'modules',backup/'modules',symlinks=True)
        for row in manifest['apps']:
            app=row['app'];path=apps/app;dest=backup/app;dest.mkdir()
            if not path.is_dir():raise ValueError('installed app missing: '+app)
            for name in ('AM-updater','recipe.am','version','remove','download-url','AM-VERIFIED'):
                if (path/name).is_file():shutil.copy2(path/name,dest/name)
            launcher=desktop/(app+'-AM.desktop')
            if launcher.is_file():shutil.copy2(launcher,dest/'launcher.desktop')
        (backup/'complete').write_text('Metadata snapshot complete\n')
    # This is deliberately a maintenance-window operation, not pair-atomic delivery.
    shutil.copy2(ROOT/'APP-MANAGER',manager/'APP-MANAGER')
    for module in (ROOT/'modules').glob('*.am'):shutil.copy2(module,manager/'modules'/module.name)
    for row in manifest['apps']:
        app=row['app'];path=apps/app;layout=row['layout'];payload=prepared/app/'payload'
        shutil.copytree(payload,path,dirs_exist_ok=True,symlinks=True)
        text=(ROOT/'programs/x86_64'/app).read_text()
        bindings='\n'.join(['AMREPO=${AMREPO-"https://raw.githubusercontent.com/mareklangiewicz/AM/'+source+'"}',
            'APPS_DIR="'+str(apps)+'"','BIN_DIR="'+str(bins)+'"','DESKTOP_DIR="'+str(desktop)+'"',
            'CATALOG_YAML_HELPER="'+str(manager/'modules/catalog-yaml.am')+'"'])+'\n'
        text=text.replace('. "/opt/am/modules/appimage.am"',bindings+'. "'+str(manager/'modules/appimage.am')+'"')
        (path/'recipe.am').write_text(text)
        (path/'AM-updater').write_bytes(managed_updater(path/'recipe.am'));(path/'AM-updater').chmod(0o755)
        first=next(iter(manifest['selections'][app].values()))
        version=first['published_at'] if row['version_identity']=='published_at' else first['url']
        (path/'version').write_text(version+'\n');(path/'download-url').write_text(first['url']+'\n')
        targets=([('kitty','bin/kitty'),('kitten','bin/kitten')] if layout=='kitty' else
                 [('btop','bin/btop')] if layout=='btop' else
                 [(t,t) for t in ('emmylua_ls','emmylua_check','emmylua_doc_cli','luafmt')] if layout=='emmylua' else [(app,app)])
        for name,entry in targets:
            link=bins/name
            if link.is_symlink():link.unlink()
            elif link.exists():raise ValueError('refuse replacing non-symlink launcher: '+str(link))
            link.symlink_to(path/entry)
        print('Reinstalled '+app,flush=True)
    (prepared/'applied.json').write_text(json.dumps(dict(source=source,catalog=manifest['catalog']),indent=2)+'\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    p=commands.add_parser('prepare');p.add_argument('--repo',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--cache',type=Path,required=True)
    p=commands.add_parser('apply');p.add_argument('--prepared',type=Path,required=True)
    p.add_argument('--root',type=Path,required=True,help='/ for the live host, disposable absolute root for rehearsal')
    args=parser.parse_args()
    if args.command=='prepare':prepare(args.repo,args.out,args.cache)
    else:apply(args.prepared,args.root)


if __name__=='__main__':main()
