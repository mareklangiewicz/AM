"""Source selection changes preserve package/desktop bodies and fail closed."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import bulk_recipe_urls as b
import recipe_policy_source as compiler
import test_yaml_manager_integration as integration
import fixture_manager as harness


class BodyMigration(unittest.TestCase):
    def source(self):
        return subprocess.check_output(['git','-C',str(b.host.ROOT),'show',
            '90a9f01b09f8262b38710d01f7d2b7ee510af525:programs/x86_64/1aivault'],text=True)

    def bindings(self):
        return [dict(repository='stoicsoft/1aivault-releases',repository_id=123,catalog_app='1aivault')]

    def test_only_selection_and_exact_native_update_bypass_change(self):
        source=self.source();changed,rows,changes=b.translate(source,'x86_64/1aivault',self.bindings())
        self.assertEqual(len(changes),2)
        self.assertEqual(len(rows),1)
        self.assertNotIn('api.github.com/repos/',changed)
        self.assertNotIn('appimageupdatetool -Or',changed)
        self.assertEqual(changed.count('AMREPO=${AMREPO-}\n'),2)
        self.assertIn(' --url "$@") || exit 1',changed)
        self.assertEqual(source.split('# LAUNCHER & ICON')[1],changed.split('# LAUNCHER & ICON')[1])
        self.assertEqual(rows[0]['source_sha256'],hashlib.sha256(changed.encode()).hexdigest())
        self.assertEqual(rows[0]['url_rules'][-1],dict(pattern='appimage$',ignore_case=True,exclude=False))

    def test_auxiliary_api_and_custom_bypass_are_not_silently_discarded(self):
        for source in (self.source()+'curl -Ls https://api.github.com/repos/another/project\n',
                       self.source().replace('appimageupdatetool -Or','appimageupdatetool -O')):
            with self.assertRaises(ValueError):b.translate(source,'x86_64/1aivault',self.bindings())

    def test_unknown_source_and_command_in_predicate_refuse(self):
        with self.assertRaises(ValueError):b.translate(self.source(),'x86_64/1aivault',[])
        source=self.source().replace('grep -i "appimage$"','grep -i "$(touch /tmp/unwanted)appimage$"')
        with self.assertRaises(ValueError):b.translate(source,'x86_64/1aivault',self.bindings())

    def test_variant_selection_is_bound_to_reviewed_sources(self):
        source=subprocess.check_output(['git','-C',str(b.host.ROOT),'show',
            '90a9f01b09f8262b38710d01f7d2b7ee510af525:programs/x86_64/mpv'],text=True)
        changed,rows,_=b.translate(source,'x86_64/mpv',[
            dict(repository='pkgforge-dev/mpv-AppImage',repository_id=123,catalog_app='mpv'),
            dict(repository='ivan-hc/MPV-appimage',repository_id=124,catalog_app='mpv.src-124')])
        self.assertEqual(len(rows),2)
        self.assertIn('--source-repository "$RELEASE"',changed)
        self.assertIn('--source-repository REPLACETHIS',changed)
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);(root/'modules').mkdir();(root/'tools/catalog-collector').mkdir(parents=True)
            path=root/'programs/x86_64/mpv';path.parent.mkdir(parents=True);path.write_text(changed)
            dummy=root/'programs/x86_64/20x';dummy.write_bytes((b.host.ROOT/'programs/x86_64/20x').read_bytes())
            registry=root/'tools/catalog-collector/recipe-url-policies.json';registry.write_text(json.dumps(rows))
            policy=root/'modules/catalog-yaml-policy.am';shutil.copy2(b.host.ROOT/'modules/catalog-yaml-policy.am',policy)
            with patch.object(compiler,'ROOT',root):compiler.generate()
            for requested,expected in (('pkgforge-dev/mpv-AppImage','mpv'),('ivan-hc/MPV-appimage','mpv.src-124'),('evil/project',None)):
                result=subprocess.run(['awk','-f',str(policy)],input='',text=True,capture_output=True,
                    env={**os.environ,'AM_YAML_RECIPE':'x86_64/mpv','AM_YAML_SOURCE_REPOSITORY':requested,
                         'AM_YAML_CHECK_RECIPE':'1','AM_YAML_APP_NAME':'1'})
                self.assertEqual(result.returncode,0 if expected else 3,result.stderr)
                if expected:self.assertEqual(result.stdout,expected+'\n')
            path.write_text(changed+'# drift\n')
            with patch.object(compiler,'ROOT',root),self.assertRaises(ValueError):compiler.generate()


class BodyManager(unittest.TestCase):
    setUp=integration.YAMLManager.setUp
    script=integration.YAMLManager.script
    env=integration.YAMLManager.env
    stage=integration.YAMLManager.stage
    calls=integration.YAMLManager.calls
    standalone=integration.YAMLManager.standalone
    run_manager_install=integration.YAMLManager.run_manager_install

    @classmethod
    def setUpClass(cls):harness.setup_catalog(cls)

    def test_actual_manager_embeds_modules_source_and_v3_updater(self):
        source=subprocess.check_output(['git','-C',str(b.host.ROOT),'show',
            'bb53f3180ec92f862020f8bdccef0f6614015bae:programs/x86_64/obsidian'],text=True)
        changed,rows,_=b.translate(source,'x86_64/obsidian',[
            dict(repository='obsidianmd/obsidian-releases',repository_id=262342594,catalog_app='obsidian')])
        root=self.path/'policy';(root/'modules').mkdir(parents=True)
        (root/'tools/catalog-collector').mkdir(parents=True)
        path=root/'programs/x86_64/obsidian';path.parent.mkdir(parents=True);path.write_text(changed)
        dummy=root/'programs/x86_64/dummy'
        dummy.write_text((b.host.ROOT/'programs/x86_64/20x').read_text()
            .replace('APP=20x','APP=dummy').replace('x86_64/20x','x86_64/dummy'))
        (root/'tools/catalog-collector/recipe-url-policies.json').write_text(json.dumps(rows))
        policy=root/'modules/catalog-yaml-policy.am'
        shutil.copy2(b.host.ROOT/'modules/catalog-yaml-policy.am',policy)
        with patch.object(compiler,'ROOT',root):compiler.generate()
        shutil.copy2(policy,self.module_dir/'catalog-yaml-policy.am')
        self.script('wget', '''import os,pathlib,sys,urllib.parse
p=pathlib.Path(os.environ['FIXTURE']);url=sys.argv[-1]
with (p/'downloads').open('a') as f:f.write(url+'\\n')
name=urllib.parse.unquote(url.rsplit('/',1)[-1])
pathlib.Path(name).write_text("#!/bin/sh\\nmkdir -p squashfs-root\\ncase $2 in\\n*.desktop) printf '[Desktop Entry]\\\\nExec=obsidian --no-sandbox\\\\nIcon=obsidian\\\\n' > squashfs-root/obsidian.desktop ;;\\n.DirIcon) printf icon > squashfs-root/.DirIcon ;;\\nesac\\n")
''')
        result=self.run_manager_install(amrepo=integration.SOURCE,recipe=path,app_name='obsidian')
        self.assertEqual(result.returncode,0,result.stderr)
        app=self.root/'opt/obsidian'
        updater=(app/'AM-updater').read_text()
        self.assertIn(str(self.module_dir/'catalog-yaml.am'),updater)
        self.assertIn(integration.SOURCE,updater)
        self.assertNotIn('api.github.com/repos/obsidianmd/',updater)
        self.assertTrue((app/'version').read_text().strip().startswith('https://github.com/obsidianmd/'))
        before={p.name:p.read_bytes() for p in app.iterdir() if p.is_file() and not p.is_symlink()}
        self.assertEqual(self.standalone(app/'AM-updater').returncode,0)
        self.clock='2026-11-09T12:00:00Z'
        refused=self.standalone(app/'AM-updater')
        self.assertNotEqual(refused.returncode,0)
        self.assertEqual(before,{p.name:p.read_bytes() for p in app.iterdir() if p.is_file() and not p.is_symlink()})


if __name__=='__main__':unittest.main()
