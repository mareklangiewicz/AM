"""Legacy URL predicates remain inert and keep positive/negative URL filtering."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import bulk_recipes as b
import recipe_policy_source as compiler

SOURCE='90a9f01b09f8262b38710d01f7d2b7ee510af525'


class BulkRecipes(unittest.TestCase):
    def source(self):
        return subprocess.check_output(['git','-C',str(b.ROOT),'show',
            SOURCE+':programs/x86_64/0xfx'],text=True)

    def identity(self):
        return dict(status='verified',repository_id=123,repository='averagenative/0xFX',
                    requested_repository='averagenative/0xfx')

    def test_unknown_shell_and_inconsistent_identity_refuse(self):
        source=self.source()
        for changed in (source.replace('head -1','head -1; touch /tmp/unwanted'),
                        source.replace('set -eu','set -eu\ntouch /tmp/unwanted'),
                        source.replace(b.TAIL,b.TAIL+'echo extra\n')):
            with self.assertRaises(ValueError):b.translate(changed,'x86_64/0xfx',self.identity())
        identity=self.identity();identity['repository_id']=123;identity['requested_repository']='other/project'
        with self.assertRaises(ValueError):b.translate(source,'x86_64/0xfx',identity)

    def test_native_url_rules_filter_the_whole_url_without_widening(self):
        source=self.source();translated,rules=b.translate(source,'x86_64/0xfx',self.identity())
        self.assertNotIn('select_asset()',translated)
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);(root/'modules').mkdir()
            policy=root/'modules/catalog-yaml-policy.am'
            shutil.copy2(b.ROOT/'modules/catalog-yaml-policy.am',policy)
            recipe=root/'programs/x86_64/0xfx';recipe.parent.mkdir(parents=True)
            recipe.write_text(translated)
            with patch.object(compiler,'ROOT',root):compiler.generate()
            cases=[('v1','App.AppImage',True),('v1','App-aarch64.AppImage',False),
                   ('v1','App-armhf.AppImage',False),('arm64','App.AppImage',False),
                   ('v1','App.APPIMAGE',True),('v1','App.AppImage.zsync',False)]
            for tag,name,allowed in cases:
                url=f'https://github.com/averagenative/0xfx/releases/download/{tag}/{name}'
                facts='\t'.join(['1','2',*map(json.dumps,[
                    '2026-11-09T12:00:00Z','2026-11-09T11:00:00Z',tag,name,url]),'false'])+'\n'
                for command in (['mawk'],['gawk'],['busybox','awk']):
                    result=subprocess.run([*command,'-f',str(policy)],input=facts,text=True,capture_output=True,
                        env={**os.environ,'LC_ALL':'C','AM_YAML_RECIPE':'x86_64/0xfx',
                             'AM_YAML_REPOSITORY':'123','AM_YAML_NOW':'2026-11-09T12:00:00Z',
                             'AM_YAML_PIN':'a'*40})
                    self.assertEqual(result.returncode,0 if allowed else 3,(command,tag,name,result.stderr))
                    if allowed:self.assertEqual(result.stdout.splitlines()[-1],url)

    def test_unsupported_payload_layout_and_backreferences_refuse(self):
        for selector in ('sed x | grep -oi "https.*tar.gz$" | head -1',
                         "sed 's/[()\",{} ]/\\n/g' | grep -oi 'https.*tar.gz$' | head -1",
                         "sed 's/[()\",{} ]/\\n/g' | grep -oi 'https.*\\1mage$' | head -1"):
            with self.assertRaises(ValueError):b.url_rules(selector)

    def test_architecture_source_alias_does_not_rename_installed_app(self):
        translated,_=b.translate(self.source(),'x86_64/0xfx',self.identity())
        translated=translated.replace('APP=0xfx\n','APP=0xfx\nCATALOG_APP=0xfx.x86_64\n')
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);(root/'modules').mkdir()
            policy=root/'modules/catalog-yaml-policy.am';shutil.copy2(b.ROOT/'modules/catalog-yaml-policy.am',policy)
            recipe=root/'programs/x86_64/0xfx';recipe.parent.mkdir(parents=True);recipe.write_text(translated)
            row=b.recipe_rows(root)[0]
            self.assertEqual((row['app'],row['catalog_app']),('0xfx','0xfx.x86_64'))
            with patch.object(compiler,'ROOT',root):compiler.generate()
            result=subprocess.run(['awk','-f',str(policy)],input='',text=True,capture_output=True,
                env={**os.environ,'AM_YAML_RECIPE':'x86_64/0xfx','AM_YAML_CHECK_RECIPE':'1',
                     'AM_YAML_APP_NAME':'1'})
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(result.stdout,'0xfx.x86_64\n')
            recipe.write_text(translated.replace('CATALOG_APP=0xfx.x86_64','CATALOG_APP=other/project'))
            with self.assertRaises(ValueError):b.recipe_rows(root)


if __name__=='__main__':unittest.main()
