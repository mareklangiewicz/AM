"""Six Brave selectors and shared lifecycle against accepted November 2 bytes."""
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile
import unittest

from delivery import unpack_artifact
from storage import validate
from test_appimage_lifecycle import selector_script, bound_recipe
from test_shell_consumer import ShellFixture, PIN
from shell_lookup import epoch

ROOT = Path(__file__).resolve().parents[2]
ALIAS = 'https://api.github.com/repos/ivan-hc/Brave-appimage/releases'
EVIDENCE = ROOT/'docs/track/release-catalog/research/brave-live-20261102-evidence.tar.gz'


def accepted_brave_tree():
    with tarfile.open(EVIDENCE) as archive:
        raw = archive.extractfile('collection.zip').read()
        artifacts = json.load(archive.extractfile('artifacts.json'))['artifacts']
    art = next(a for a in artifacts if a['name'].startswith('restricted-'))
    assert 'sha256:'+hashlib.sha256(raw).hexdigest() == art['digest']
    files = unpack_artifact(raw)
    tree = {p.removeprefix('candidate/'): b for p,b in files.items() if p.startswith('candidate/')}
    validate(tree)
    return tree


class BraveMigration(unittest.TestCase):
    def test_six_recipes_preserve_both_frozen_selectors_and_actual_assets(self):
        tree=accepted_brave_tree();index=validate(tree)
        rid=index['aliases'][ALIAS]['request_id']
        body=tree[index['entries'][rid]['observation']['path']]
        assets={a['browser_download_url'] for r in json.loads(body) for a in r['assets']}
        frozen=json.loads((ROOT/'docs/track/release-catalog/research/brave-enrollment-preparation.json').read_bytes())
        self.assertEqual(len(frozen['recipes']),6)
        for row in frozen['recipes']:
            path=ROOT/row['path']
            with self.subTest(path=row['path']):
                original=subprocess.check_output(['git','show','3c44b0ba4:'+row['path']],cwd=ROOT)
                self.assertEqual(hashlib.sha256(original).hexdigest(),row['sha256'])
                self.assertEqual(original.decode().count(row['original_selector']),2)
                prefix='version=$(curl -Ls '+ALIAS+' | '
                pipeline=row['original_selector'][len(prefix):-1]
                self.assertIn('select_asset() {\n\t'+pipeline+'\n}',path.read_text())
                before=subprocess.run(['sh','-c',pipeline],input=body,capture_output=True,check=True)
                after=subprocess.run(['sh','-c',selector_script(path)],input=body,capture_output=True,check=True)
                self.assertEqual(after.stdout,before.stdout)
                self.assertIn(after.stdout.decode().strip(),assets)
                empty=subprocess.run(['sh','-c',selector_script(path)],input=b'[]',capture_output=True,check=True)
                self.assertEqual(empty.stdout,b'')
                subprocess.run(['sh','-n',str(path)],check=True)
                self.assertNotIn('appimageupdatetool',path.read_text())


class BraveLifecycle(ShellFixture):
    catalog_alias=ALIAS

    @classmethod
    def setUpClass(cls):
        cls.base=accepted_brave_tree();cls.index=validate(cls.base)
        cls.rid=cls.index['aliases'][ALIAS]['request_id']
        cls.obs=cls.index['entries'][cls.rid]['observation']

    def test_all_six_install_standalone_failure_retry_and_checksum_repair(self):
        self.now=[epoch(self.index['generated_at'])]*3
        self.script('wget', """import os,pathlib,sys
if os.environ.get('DOWNLOAD_FAIL'): sys.exit(9)
pathlib.Path(sys.argv[sys.argv.index('-O')+1]).write_text('#!/bin/sh\\nmkdir -p squashfs-root\\ncase $2 in\\n*.desktop) printf "[Desktop Entry]\\\\nExec=brave\\\\nIcon=brave\\\\n" > squashfs-root/brave.desktop ;;\\n.DirIcon) printf icon > squashfs-root/.DirIcon ;;\\nesac\\n')
""")
        self.script('notify-send','pass\n')
        rows=json.loads((ROOT/'docs/track/release-catalog/research/brave-enrollment-preparation.json').read_bytes())['recipes']
        for row in rows:
            with self.subTest(path=row['path']):
                path=ROOT/row['path'];name=path.name
                root=self.path/(path.parent.name+'-'+name)
                (root/'usr/local/bin').mkdir(parents=True)
                (root/'usr/local/share/applications').mkdir(parents=True)
                source=bound_recipe(path.read_text()).replace('/opt/am/modules/catalog.am',str(ROOT/'modules/catalog.am')).replace('/opt/am/modules/appimage.am',str(ROOT/'modules/appimage.am'))
                source=source.replace('/opt/',str(root)+'/opt/').replace('/usr/local/',str(root)+'/usr/local/')
                recipe=root/'recipe';recipe.write_text(source)
                def run(script,fail=False):
                    self.stage()
                    return subprocess.run(['sh',str(script),'--commit',PIN],cwd=self.path,env={**self.env(),**({'DOWNLOAD_FAIL':'1'} if fail else {})},capture_output=True)
                result=run(recipe);self.assertEqual(result.returncode,0,result.stderr)
                app=root/'opt'/name;updater=app/'AM-updater'
                self.assertEqual(len(updater.read_text().splitlines()),3)
                expected=subprocess.run(['sh','-c',selector_script(path)],input=self.body,capture_output=True,check=True).stdout.strip()
                self.assertEqual((app/'version').read_bytes().strip(),expected)
                binary=(app/name).read_bytes();(app/'version').write_text('old\n')
                result=run(updater,True);self.assertNotEqual(result.returncode,0)
                self.assertEqual((app/name).read_bytes(),binary)
                self.assertEqual((app/'version').read_text(),'old\n')
                result=run(updater);self.assertEqual(result.returncode,0,result.stderr)
                (app/name).write_text('corrupt');(app/'AM-VERIFIED').write_text('Checksum failure\n')
                result=run(updater);self.assertEqual(result.returncode,0,result.stderr)
                self.assertEqual((app/name).read_bytes(),binary)


if __name__=='__main__': unittest.main()
