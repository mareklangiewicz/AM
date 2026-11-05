"""YAML-only host recipes: actual manager install and standalone update, inert assets."""
from pathlib import Path
import subprocess
import tempfile
import unittest

from bounded import normalize
from retention import refresh
from host_catalog import configuration
from yaml_publication import git, publish_local
from yaml_adapter import schema_url
import test_yaml_manager_integration as integration
from test_yaml_cohort_shell import ROOT

NAMES = dict(zip(
    'appimagetool appimageupdatetool btop emmylua fzf kitty lazygit logseq-app-db-nightly logseq-app-og neovide neovide-nightly rclone rclone-ui satty yt-dlp zellij zmx nvim nvim-nightly obsidian sunshine'.split(),
    ['appimagetool-x86_64.AppImage','appimageupdatetool-x86_64.AppImage','btop-x86_64-unknown-linux-musl.tar.gz',
     'emmylua_ls-linux-musl.tar.gz','fzf-1.0-linux_amd64.tar.gz','kitty-1.0-x86_64.txz','lazygit_1.0_linux_x86_64.tar.gz',
     'Logseq-linux-x86_64-1.0.AppImage','Logseq-OG-linux-x64-1.0.AppImage','neovide.AppImage','neovide.AppImage',
     'rclone-v1.0-linux-amd64.zip','Rclone.UI_amd64.AppImage','Satty-1.0-x86_64.AppImage','yt-dlp_linux',
     'zellij-x86_64-unknown-linux-musl.tar.gz','zmx-1.0-linux-x86_64.tar.gz','nvim-linux-x86_64.appimage',
     'nvim-linux-x86_64.appimage','Obsidian-1.0.AppImage','Sunshine_1.0_x86_64.AppImage']))
NOW='2026-11-04T12:00:00Z'

class HostCutover(unittest.TestCase):
    script=integration.YAMLManager.script
    env=integration.YAMLManager.env
    stage=integration.YAMLManager.stage
    calls=integration.YAMLManager.calls
    install=integration.YAMLManager.install
    standalone=integration.YAMLManager.standalone
    run_manager_install=integration.YAMLManager.run_manager_install
    snapshot=integration.YAMLManager.snapshot
    @classmethod
    def setUpClass(cls):
        cls.rows,sources=configuration()
        cls.tmp=tempfile.TemporaryDirectory(prefix='host-cutover-');cls.addClassCleanup(cls.tmp.cleanup)
        cls.repo=Path(cls.tmp.name)/'git';cls.repo.mkdir();git(cls.repo,'init','--bare')
        repositories={}
        for rid,source in sources.items():
            app_rows=[r for r in cls.rows if str(r['repository_id'])==rid]
            releases=[]
            for n,tag in enumerate(('v1','nightly'),1):
                assets={}
                for row in app_rows:
                    names=[NAMES[row['app']]]
                    if row['app']=='emmylua':names=[t+'-linux-musl.tar.gz' for t in ('emmylua_ls','emmylua_check','emmylua_doc_cli','luafmt')]
                    for name in names:
                        assets[name]=dict(id=len(assets)+1,name=name,browser_download_url='https://example.org/'+row['app']+'/'+name,size=1,content_type='application/octet-stream')
                releases.append(dict(id=n,tag_name=tag,draft=False,prerelease=tag=='nightly',html_url='https://example.org/releases/'+tag,
                    published_at='2026-11-0'+str(n)+'T00:00:00Z',created_at='2026-11-01T00:00:00Z',assets=list(assets.values())))
            base=dict(format=2,schema=schema_url('a'*40),repository_id=int(rid),repository=source)
            repositories[rid]=refresh(base,[dict(received_at=NOW,releases=normalize(releases,100),has_next=False,bytes=100,seconds=0)],attempted_at=NOW,max_catalog_bytes=2097152)
        cls.repositories=repositories
        cls.pin=publish_local(cls.repo,{r['app']:r['repository_id'] for r in cls.rows},repositories,schema=schema_url('a'*40),max_file_bytes=2097152,expected_parent=None)

    def setUp(self):
        integration.YAMLManager.setUp(self)
        self.clock=NOW
        # Existing inert AppImage downloader remains for raw assets. Archive
        # downloads instead contain independent, minimal reviewed layouts.
        original=(self.bin/'wget').read_text()
        (self.bin/'appimage-download').write_text(original);(self.bin/'appimage-download').chmod(0o755)
        self.script('wget', '''import io,os,pathlib,subprocess,sys,tarfile,zipfile
url=sys.argv[-1];out=pathlib.Path(sys.argv[sys.argv.index('-O')+1]);app=url.split('/')[-2]
if not url.endswith(('.tar.gz','.txz','.zip')):
 raise SystemExit(subprocess.call([str(pathlib.Path(__file__).with_name('appimage-download')),*sys.argv[1:]]))
if os.environ.get('DOWNLOAD_FAIL'):raise SystemExit(9)
with (pathlib.Path(os.environ['FIXTURE'])/'downloads').open('a') as f:f.write(url+'\\n')
if app=='btop':files={'btop/bin/btop':b'bin','btop/share/theme':b'theme'}
elif app=='kitty':files={'bin/kitty':b'kitty','bin/kitten':b'kitten','lib/helper':b'helper'}
elif app=='rclone':files={'rclone-v1.0-linux-amd64/rclone':b'rclone','rclone-v1.0-linux-amd64/README':b'doc'}
elif app=='emmylua':files={url.split('/')[-1].split('-linux')[0]:b'tool'}
else:files={app:b'bin','LICENSE':b'license'}
if url.endswith('.zip'):
 with zipfile.ZipFile(out,'w') as stream:
  for name,body in files.items():stream.writestr(name,body)
else:
 with tarfile.open(out,'w:gz') as stream:
  for name,body in files.items():
   info=tarfile.TarInfo(name);info.size=len(body);info.mode=0o755;stream.addfile(info,io.BytesIO(body))
''')

    # Deliberately collect only this subclass's tests; inherited historical
    # rollout assertions belong to their original format-1/2 source revisions.
    def test_all_host_recipes_manager_install_and_standalone_update(self):
        for row in self.rows:
            with self.subTest(app=row['app']):
                app=self.install('x86_64/'+row['app'])
                self.assertIn('# AM-CATALOG-UPDATER 1',(app/'AM-updater').read_text())
                self.assertEqual((app/'version').read_text().strip(),'2026-11-02T00:00:00Z' if row['app']=='logseq-app-db-nightly' else (app/'download-url').read_text().strip())
                result=self.standalone(app/'AM-updater')
                self.assertEqual(result.returncode,0,result.stderr)
                if row['app']=='emmylua':
                    for tool in ('emmylua_ls','emmylua_check','emmylua_doc_cli','luafmt'):
                        self.assertEqual((app/tool).read_bytes(),b'tool')
                        self.assertTrue((self.root/'usr/local/bin'/tool).is_symlink())
                if row['app']=='kitty':self.assertTrue((self.root/'usr/local/bin/kitten').is_symlink())

    def test_old_installed_archive_recipes_survive_module_only_refresh(self):
        from unittest.mock import patch
        import test_appimage_lifecycle as lifecycle
        old_module=self.path/'old-appimage.am'
        old_module.write_bytes(subprocess.check_output(['git','-C',str(ROOT),'show','4e718e27f:modules/appimage.am']))
        for name in ('btop','kitty','rclone','emmylua'):
            with self.subTest(app=name):
                old_recipe=self.path/('old-'+name)
                old_recipe.write_bytes(subprocess.check_output(['git','-C',str(ROOT),'show',
                    '4e718e27f:programs/x86_64/'+name]))
                with patch.object(lifecycle,'LIFECYCLE',old_module):
                    result=self.run_manager_install(amrepo=integration.SOURCE,recipe=old_recipe,app_name=name)
                self.assertEqual(result.returncode,0,result.stderr)
                app=self.root/'opt'/name
                before={n:(app/n).read_bytes() for n in ('recipe.am','AM-updater','remove')}
                # Deliver current modules, without touching installed recipes.
                for module in ROOT.joinpath('modules').glob('*.am'):
                    (self.module_dir/module.name).write_bytes(module.read_bytes())
                (app/'version').write_text('force replacement\n')
                (app/'precious').write_text('keep')
                result=self.standalone(app/'AM-updater')
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertNotEqual((app/'version').read_text(),'force replacement\n')
                self.assertEqual((app/'precious').read_text(),'keep')
                self.assertEqual(before,{n:(app/n).read_bytes() for n in before})
                row=next(r for r in self.rows if r['app']==name)
                for entry in row['archive'].get('executables',row.get('tools',[])):
                    self.assertTrue((app/entry).is_file())

    def test_toolset_mixed_release_refuses_before_download(self):
        app=self.install('x86_64/emmylua')
        helper=self.path/'mixed-selection'
        helper.write_text('''#!/bin/sh
case " $* " in *" --tool "*) release=2 ;; *) release=1 ;; esac
printf '%s\\n' '''+self.pin+''' 872860168 "$release" 1 '''+NOW+''' https://example.org/tool
''')
        recipe=app/'recipe.am'
        recipe.write_text(recipe.read_text().replace('am_appimage "$0" "$@"',
            'CATALOG_YAML_HELPER="'+str(helper)+'"\nAM_ARCHIVE_POLICY="'+str(self.module_dir/'archive-policy.am')+'"\nam_appimage "$0" "$@"'))
        before=(self.path/'downloads').read_bytes()
        version=(app/'version').read_bytes()
        result=self.standalone(app/'AM-updater')
        self.assertNotEqual(result.returncode,0)
        self.assertIn(b'must come from one release',result.stderr)
        self.assertEqual((self.path/'downloads').read_bytes(),before)
        self.assertEqual((app/'version').read_bytes(),version)

    def test_archive_missing_executable_and_traversal_refuse(self):
        import io, tarfile, zipfile
        for layout,files in (('kitty',{'bin/kitty':b'only one'}),
                             ('btop',{'../escape':b'bad'}),
                             ('rclone',{'../escape':b'bad'})):
            with self.subTest(layout=layout):
                stage=self.path/('invalid-'+layout);stage.mkdir()
                if layout=='rclone':
                    with zipfile.ZipFile(stage/'asset','w') as archive:
                        for name,body in files.items():archive.writestr(name,body)
                else:
                    with tarfile.open(stage/'asset','w:gz') as archive:
                        for name,body in files.items():
                            info=tarfile.TarInfo(name);info.size=len(body)
                            archive.addfile(info,io.BytesIO(body))
                result=subprocess.run(['sh','-c',
                    'AM_ARCHIVE_POLICY="$1/archive-policy.am"; . "$1/appimage.am"; am_archive_stage "$2" "$3" "$2"',
                    'sh',str(ROOT/'modules'),layout,str(stage)],capture_output=True)
                self.assertNotEqual(result.returncode,0,result.stderr)
                self.assertFalse(list((stage/'payload').iterdir()))
                self.assertFalse((self.path/'escape').exists())

    def test_failed_download_retains_binary_version_and_custom_data(self):
        app=self.install('x86_64/neovide-nightly');(app/'my-data').write_text('keep')
        before={n:(app/n).read_bytes() for n in ('neovide-nightly','version','my-data')}
        result=self.standalone(app/'AM-updater',env={**self.env(),'DOWNLOAD_FAIL':'1'})
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(before,{n:(app/n).read_bytes() for n in before})

    def test_format1_refuses_without_creating_app(self):
        recipe=self.path/'old';recipe.write_text('APP=old\nCATALOG_FORMAT=1\n. "'+str(ROOT/'modules/appimage.am')+'"\nam_appimage "$0"\n')
        result=subprocess.run(['sh',str(recipe)],env={**self.env(),'APPS_DIR':str(self.root/'opt')},capture_output=True)
        self.assertEqual(result.returncode,3);self.assertFalse((self.root/'opt/old').exists())

    def test_cutover_apply_preserves_data_launchers_and_metadata_snapshot(self):
        from host_cutover import apply
        import json
        root=self.path/'apply-root';manager=root/'opt/am';(manager/'modules').mkdir(parents=True)
        (manager/'APP-MANAGER').write_text('old manager');(manager/'modules/old.am').write_text('old module')
        bins=root/'usr/local/bin';bins.mkdir(parents=True)
        desktop=root/'usr/local/share/applications';desktop.mkdir(parents=True)
        prepared=self.path/'prepared';prepared.mkdir()
        selections={}
        source=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
        for row in self.rows:
            app=row['app'];path=root/'opt'/app;path.mkdir()
            (path/'my-settings').write_text('precious')
            (path/'AM-updater').write_text('old updater');(path/'remove').write_text('old remover')
            (desktop/(app+'-AM.desktop')).write_text('custom launcher')
            payload=prepared/app/'payload';payload.mkdir(parents=True)
            entry='bin/'+app if app in ('kitty','btop') else app
            (payload/entry).parent.mkdir(parents=True,exist_ok=True);(payload/entry).write_text('new binary')
            selections[app]={app:dict(url='https://example.org/'+app,published_at=NOW)}
        (prepared/'manifest.json').write_text(json.dumps(dict(source=source,catalog=self.pin,apps=self.rows,selections=selections)))
        custom=bins/'kitty';custom.symlink_to('/custom/kitty-wrapper')
        apply(prepared,root)
        self.assertEqual(custom.readlink(),Path('/custom/kitty-wrapper'))
        self.assertEqual(json.loads((prepared/'before/launchers.json').read_text())[str(custom)]['target'],'/custom/kitty-wrapper')
        for row in self.rows:
            app=row['app'];path=root/'opt'/app
            self.assertEqual((path/'my-settings').read_text(),'precious')
            self.assertEqual((path/'remove').read_text(),'old remover')
            self.assertEqual((desktop/(app+'-AM.desktop')).read_text(),'custom launcher')
            self.assertEqual((prepared/'before'/app/'AM-updater').read_text(),'old updater')
            self.assertIn('# AM-CATALOG-UPDATER 1',(path/'AM-updater').read_text())
            self.assertIn(source,(path/'recipe.am').read_text())
        self.assertEqual((prepared/'before/APP-MANAGER').read_text(),'old manager')

    def test_partial_extraction_failure_is_not_accepted(self):
        self.script('tar', '''import pathlib,sys
if '-tf' in sys.argv:print('fzf')
else:
 target=pathlib.Path(sys.argv[sys.argv.index('-C')+1]);(target/'fzf').write_text('partial');raise SystemExit(9)
''')
        stage=self.path/'partial';stage.mkdir();(stage/'asset').write_text('archive')
        result=subprocess.run(['sh','-c','. "$1"; AM_ARCHIVE_POLICY="$(dirname "$1")/archive-policy.am"; am_archive_stage tar "$2" fzf || exit 1','sh',
            str(ROOT/'modules/appimage.am'),str(stage)],env=self.env(),capture_output=True)
        self.assertNotEqual(result.returncode,0)
        self.assertFalse((stage/'payload/fzf').exists())

    def test_emmylua_stale_consent_is_explicitly_fresh_only(self):
        result=subprocess.run(['sh',str(ROOT/'modules/catalog-yaml.am'),'x86_64/emmylua',
            '--accept-stale-release',self.pin,'872860168','1','1',NOW],env=self.env(),capture_output=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn(b'requires fresh observations',result.stderr)

    def test_reinstall_preserves_custom_executable_and_desktop_launchers(self):
        app=self.install('x86_64/obsidian')
        desktop=self.root/'usr/local/share/applications/obsidian-AM.desktop'
        desktop.write_text('custom desktop launcher')
        link=self.root/'usr/local/bin/obsidian';link.unlink();link.symlink_to('/custom/obsidian-wrapper')
        # A custom alias inside the app directory must not look manager-owned.
        gui=self.root/'usr/local/bin/obsidian-gui';gui.unlink();gui.symlink_to(app/'obsidian-gui')
        self.stage()
        result=subprocess.run(['sh',str(app/'recipe.am')],env=self.env(),capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(desktop.read_text(),'custom desktop launcher')
        self.assertEqual(link.readlink(),Path('/custom/obsidian-wrapper'))
        self.assertEqual(gui.readlink(),app/'obsidian-gui')
        result=subprocess.run(['sh',str(app/'remove')],capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue(gui.is_symlink())

    def test_obsidian_gui_alias_desktop_and_removal(self):
        app=self.install('x86_64/obsidian')
        gui=self.root/'usr/local/bin/obsidian-gui'
        self.assertEqual(gui.readlink(),app/'obsidian')
        self.assertEqual((self.root/'usr/local/bin/obsidian').readlink(),app/'obsidian')
        desktop=self.root/'usr/local/share/applications/obsidian-AM.desktop'
        self.assertIn('Exec="'+str(app/'obsidian')+'" --no-sandbox',desktop.read_text())
        # A second install retains the working alias and existing desktop entry.
        self.stage()
        result=subprocess.run(['sh',str(app/'recipe.am')],env=self.env(),capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(gui.readlink(),app/'obsidian')
        result=subprocess.run(['sh',str(app/'remove')],capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertFalse(gui.is_symlink())

    def test_obsidian_desktop_path_escaping(self):
        directory=self.path/'space \\ dollar$ quote" tick` percent% amp& hash#'
        desktop=self.path/'obsidian.desktop'
        desktop.write_text('Exec=obsidian --no-sandbox %U\n')
        source=(ROOT/'modules/appimage.am').read_text()
        lines=source.splitlines()
        start=next(n for n,line in enumerate(lines) if line.lstrip().startswith('gui=$('))
        script='dir=$1; APP=obsidian\n'+'\n'.join(lines[start:start+2])
        result=subprocess.run(['sh','-c',script,'test',str(directory)],cwd=self.path,capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        path=str(directory/'obsidian')
        quoted=''.join(('\\\\\\\\' if c=='\\' else '\\\\'+c if c in '"`$' else '%%' if c=='%' else c) for c in path)
        self.assertEqual(desktop.read_text(),'Exec="'+quoted+'" --no-sandbox %U\n')

    def test_another_recipe_can_request_gui_aliases_and_installed_desktop(self):
        app=self.install('x86_64/neovide')
        desktop=self.root/'usr/local/share/applications/neovide-AM.desktop'
        self.assertIn('Exec=neovide --no-sandbox',desktop.read_text())
        desktop.unlink()
        recipe=app/'recipe.am'
        recipe.write_text(recipe.read_text().replace('APP=neovide\n',
            'APP=neovide\nEXTRA_APP_LAUNCHERS="neovide-gui neovide-window"\nDESKTOP_EXEC=installed\n'))
        self.stage()
        result=subprocess.run(['sh',str(recipe)],env=self.env(),capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        for name in ('neovide-gui','neovide-window'):
            self.assertEqual((self.root/'usr/local/bin'/name).readlink(),app/'neovide')
        self.assertIn('Exec="'+str(app/'neovide')+'" --no-sandbox',desktop.read_text())
        result=subprocess.run(['sh',str(app/'remove')],capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        for name in ('neovide-gui','neovide-window'):
            self.assertFalse((self.root/'usr/local/bin'/name).is_symlink())

    def test_recipe_rejects_invalid_launcher_settings_before_download(self):
        app=self.install('x86_64/obsidian')
        recipe=app/'recipe.am'
        original=recipe.read_text()
        for setting in ('EXTRA_APP_LAUNCHERS=../escape', 'EXTRA_APP_LAUNCHERS="*"',
                        'EXTRA_APP_LAUNCHERS=obsidian', 'DESKTOP_EXEC=unknown'):
            with self.subTest(setting=setting):
                recipe.write_text(original.replace('am_appimage "$0" "$@"',
                    setting+'\nam_appimage "$0" "$@"'))
                self.stage()
                before=(self.path/'downloads').read_bytes()
                result=subprocess.run(['sh',str(recipe)],env=self.env(),capture_output=True)
                self.assertNotEqual(result.returncode,0)
                self.assertEqual((self.path/'downloads').read_bytes(),before)


if __name__=='__main__':
    suite=unittest.TestSuite(HostCutover(n) for n in HostCutover.__dict__ if n.startswith('test_'))
    raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())
