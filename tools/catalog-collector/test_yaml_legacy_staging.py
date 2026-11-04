"""Offline legacy layout/identity refusals; no network or installed file access."""
import copy
import json
import subprocess
import sys
from unittest.mock import patch
import io
from pathlib import Path
import tarfile
import tempfile
import unittest
import zipfile
from yaml_legacy_staging import APPIMAGES, TOOLS, ROOT, contracts, stage, unpack

class LegacyStaging(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='legacy-stage-');self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.counter=0

    def record(self, asset=1):
        return dict(commit='a'*40,repository_id='12',release_id='34',asset_id=str(asset),
                    observed_at='2026-11-04T12:00:00Z',published_at='2026-11-03T12:00:00Z',
                    tag='nightly',asset={'url':'https://example.org/nightly/tool.AppImage'})

    def download(self, files=None, *, zip=False, data=b'inert-selected-A', asset=1):
        self.counter+=1;path=self.root/str(self.counter)
        if files is None: path.write_bytes(data)
        elif zip:
            with zipfile.ZipFile(path,'w') as stream:
                for name,body in files.items():stream.writestr(name,body)
        else:
            with tarfile.open(path,'w:gz') as stream:
                for name,body in files.items():
                    info=tarfile.TarInfo(name);info.size=len(body)
                    info.mode=0o755 if name.endswith('helper') else 0o644
                    stream.addfile(info,io.BytesIO(body))
        return dict(path=str(path),selection=self.record(asset))

    def test_audit_and_transition_requirements(self):
        rows=contracts();self.assertEqual(len(rows),17)
        for row in rows.values():
            self.assertFalse(row['apply_ready']);self.assertFalse(row['enrollment_ready'])
            self.assertEqual(len(row['updater_sha256']),64)
            self.assertIn('recipe-only migrator is ineligible',row['transition_requirements'][-1])
        with self.assertRaises(FileNotFoundError):contracts(self.root)
        source=(ROOT/'programs/x86_64/appimageupdatetool').read_text()
        self.assertIn('real_version=${real_version%.zsync}',source)

    def test_direct_adapters_keep_selected_A_despite_embedded_B(self):
        for app in (*APPIMAGES,'yt-dlp'):
            with self.subTest(app=app):
                entry=self.download(data=b'#!/bin/sh\nexit 99 # embedded-target-B\n')
                out=self.root/app;report=stage(app,{app:entry},out)
                self.assertEqual((out/'payload'/app).read_bytes(),Path(entry['path']).read_bytes())
                identity='published_at' if app=='logseq-app-db-nightly' else None
                self.assertEqual(report['version'],entry['selection'][identity] if identity else entry['selection']['asset']['url'])
                self.assertFalse(report['apply_ready'])

    def test_logseq_same_url_new_publication(self):
        entry=self.download();app='logseq-app-db-nightly'
        a=stage(app,{app:entry},self.root/'a')
        entry['selection']['published_at']='2026-11-04T12:00:00Z'
        b=stage(app,{app:entry},self.root/'b')
        self.assertNotEqual(a['version'],b['version']);self.assertEqual(a['payload'],b['payload'])

    def test_all_archive_layouts_keep_supporting_files(self):
        layouts={'btop':{'btop/bin/btop':b'bin','btop/share/theme':b'theme'},
                 'kitty':{'bin/kitty':b'bin','bin/kitten':b'bin','lib/helper':b'helper'},
                 'rclone':{'rclone-v1.2-linux-amd64/rclone':b'bin','rclone-v1.2-linux-amd64/README':b'doc'},
                 **{a:{a:b'bin','LICENSE':b'license'} for a in ('fzf','lazygit','zellij','zmx')}}
        for app,files in layouts.items():
            with self.subTest(app=app):
                report=stage(app,{app:self.download(files,zip=app=='rclone')},self.root/app)
                self.assertEqual(len(report['payload']),len(files))
                binary='bin/'+app if app in ('kitty','btop') else app
                self.assertEqual((self.root/app/'payload'/binary).read_bytes(),b'bin')
                if app=='kitty':
                    self.assertEqual((self.root/app/'payload/lib/helper').stat().st_mode & 0o777,0o755)

    def test_emmylua_four_distinct_assets_same_release(self):
        entries={t:self.download({t:t.encode()},asset=i) for i,t in enumerate(TOOLS,1)}
        self.assertEqual(set(stage('emmylua',entries,self.root/'good')['payload']),set(TOOLS))
        for key,value in [('release_id','99'),('repository_id','99'),('commit','b'*40),('asset_id','1')]:
            bad=copy.deepcopy(entries);bad[TOOLS[-1]]['selection'][key]=value
            with self.assertRaises(ValueError):stage('emmylua',bad,self.root/'bad')
            self.assertFalse((self.root/'bad').exists())
        del entries[TOOLS[-1]]
        with self.assertRaises(ValueError):stage('emmylua',entries,self.root/'bad')

    def test_unknown_layouts_refuse_before_output(self):
        for app,files in [('fzf',{'nested/fzf':b'x'}),('btop',{'bin/btop':b'x'}),
                          ('kitty',{'kitty/bin/kitty':b'x'}),('rclone',{'rclone':b'x'})]:
            with self.assertRaises(ValueError):stage(app,{app:self.download(files)},self.root/'bad')
            self.assertFalse((self.root/'bad').exists())

    def test_traversal_links_duplicates_and_collisions_refuse(self):
        for name in ('../escape','/absolute','a/../../escape','a\\escape','a//b','a/./b','a\nb'):
            with self.assertRaises(ValueError):unpack(self.download({name:b'x'})['path'])
        for kind in ('symlink','hardlink','fifo','duplicate','collision','directory-collision','empty-directory'):
            path=self.root/kind
            with tarfile.open(path,'w') as stream:
                info=tarfile.TarInfo('x');info.size=1;stream.addfile(info,io.BytesIO(b'x'))
                if kind in ('directory-collision','empty-directory'):
                    info=tarfile.TarInfo('x/empty' if kind=='directory-collision' else 'empty')
                    info.type=tarfile.DIRTYPE;stream.addfile(info)
                elif kind=='duplicate':stream.addfile(info,io.BytesIO(b'x'))
                elif kind=='collision':
                    info=tarfile.TarInfo('x/y');info.size=1;stream.addfile(info,io.BytesIO(b'x'))
                else:
                    info=tarfile.TarInfo('link');info.linkname='x'
                    info.type={'symlink':tarfile.SYMTYPE,'hardlink':tarfile.LNKTYPE,'fifo':tarfile.FIFOTYPE}[kind]
                    stream.addfile(info)
            with self.assertRaises(ValueError):unpack(path)
        self.assertFalse((self.root/'escape').exists())

    def test_channels_empty_bytes_and_existing_output(self):
        for app in ('logseq-app-db-nightly','neovide-nightly'):
            entry=self.download();entry['selection']['tag']='stable'
            entry['selection']['asset']['url']='https://example.org/stable/tool.AppImage'
            with self.assertRaises(ValueError):stage(app,{app:entry},self.root/'bad')
        with self.assertRaises(ValueError):stage('yt-dlp',{'yt-dlp':self.download(data=b'')},self.root/'bad')
        out=self.root/'existing';out.mkdir();(out/'keep').write_bytes(b'original')
        with self.assertRaises(FileExistsError):stage('yt-dlp',{'yt-dlp':self.download()},out)
        self.assertEqual(list(out.iterdir()),[out/'keep'])
        self.assertEqual((out/'keep').read_bytes(),b'original')

    def test_cli_private_output_and_unchanged_download(self):
        entry=self.download();before=Path(entry['path']).read_bytes()
        manifest=self.root/'downloads.json';manifest.write_text(json.dumps({'yt-dlp':entry}))
        out=self.root/'cli'
        result=subprocess.run([sys.executable,str(ROOT/'tools/catalog-collector/yaml_legacy_staging.py'),
            '--app','yt-dlp','--downloads',str(manifest),'--out',str(out)],capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(out.stat().st_mode & 0o777,0o700)
        self.assertEqual(Path(entry['path']).read_bytes(),before)
        self.assertEqual(json.loads((out/'review.json').read_text())['version'],entry['selection']['asset']['url'])

    def test_limits_symlink_parent_and_source_drift(self):
        oversized=self.download(data=b'12345678')
        with patch('yaml_legacy_staging.MAX_BYTES',7):
            with self.assertRaisesRegex(ValueError,'download byte budget'):
                stage('yt-dlp',{'yt-dlp':oversized},self.root/'bad')
        entry=self.download({'fzf':b'1234','LICENSE':b'5678'})
        with patch('yaml_legacy_staging.MAX_BYTES',7):
            with self.assertRaises(ValueError):stage('fzf',{'fzf':entry},self.root/'bad')
        with patch('yaml_legacy_staging.MAX_FILES',1):
            with self.assertRaises(ValueError):unpack(entry['path'])
        alias=self.root/'alias';alias.symlink_to(self.root,target_is_directory=True)
        with self.assertRaises(ValueError):stage('yt-dlp',{'yt-dlp':self.download()},alias/'bad')
        with patch('yaml_legacy_staging.regular',return_value={'sha256':'0'*64}):
            with self.assertRaisesRegex(ValueError,'source drift'):contracts()

if __name__=='__main__':unittest.main()
