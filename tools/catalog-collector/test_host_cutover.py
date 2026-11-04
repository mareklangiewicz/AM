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
        apply(prepared,root)
        for row in self.rows:
            app=row['app'];path=root/'opt'/app
            self.assertEqual((path/'my-settings').read_text(),'precious')
            self.assertEqual((path/'remove').read_text(),'old remover')
            self.assertEqual((desktop/(app+'-AM.desktop')).read_text(),'custom launcher')
            self.assertEqual((prepared/'before'/app/'AM-updater').read_text(),'old updater')
            self.assertIn('# AM-CATALOG-UPDATER 1',(path/'AM-updater').read_text())
            self.assertIn(source,(path/'recipe.am').read_text())
        self.assertEqual((prepared/'before/APP-MANAGER').read_text(),'old manager')


if __name__=='__main__':
    suite=unittest.TestSuite(HostCutover(n) for n in HostCutover.__dict__ if n.startswith('test_'))
    unittest.TextTestRunner(verbosity=2).run(suite)
