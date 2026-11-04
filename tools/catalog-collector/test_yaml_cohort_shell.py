"""Offline portable selection and real shared lifecycle in disposable roots."""
import copy
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/catalog-yaml-prototype'))
from recipe_cohort import fixtures, COHORT
from cohort_lifecycle import module_candidate, recipe_candidate
from yaml_publication import candidate_tree, git, publish_local
from yaml_recipe_cohort import select_cohort
from experiment import SCHEMA

HELPER = ROOT/'tools/catalog-collector/yaml_cohort.sh'
NOW = '2026-10-27T15:18:00Z'


class ShellCohort(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        saved = fixtures()
        cls.repositories = {str(k): v[2] for k, v in saved.items()}
        cls.apps = {'obsidian':262342594, 'nvim':16408992, 'nvim-nightly':16408992}
        cls.tmp = tempfile.TemporaryDirectory(prefix='yaml-cohort-tests-')
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.shared = Path(cls.tmp.name)
        cls.repo = cls.shared/'git'; cls.repo.mkdir()
        git(cls.repo, 'init', '--bare')
        cls.pin = publish_local(cls.repo, cls.apps, cls.repositories, schema=SCHEMA,
                               max_file_bytes=2097152, expected_parent=None)

    def setUp(self):
        self.tmpcase = tempfile.TemporaryDirectory(prefix='yaml-cohort-case-')
        self.addCleanup(self.tmpcase.cleanup)
        self.path = Path(self.tmpcase.name)
        self.bin = self.path/'bin'; self.bin.mkdir()
        self.session = self.path/'session'; self.session.mkdir(mode=0o700)
        self.env = dict(os.environ, LC_ALL='C', PATH=str(self.bin)+':'+os.environ['PATH'],
                        AM_YAML_SESSION=str(self.session))

    def run_selection(self, recipe='x86_64/obsidian', now=NOW, acceptance='', pin=None):
        return subprocess.run(['/bin/dash', str(HELPER), str(self.repo), pin or self.pin,
            recipe, now, acceptance], capture_output=True, env=self.env)

    def test_five_saved_policies_match_python_on_three_awk_tools(self):
        for tool in ('mawk', 'gawk', 'busybox'):
            shim = self.bin/'awk'
            shim.write_text('#!/bin/sh\nexec '+tool+(' awk' if tool=='busybox' else '')+' "$@"\n')
            shim.chmod(0o755)
            for recipe in COHORT:
                with self.subTest(awk=tool, recipe=recipe):
                    r = self.run_selection(recipe)
                    self.assertEqual(r.returncode, 0, r.stderr)
                    ref = select_cohort(recipe, self.repositories[str(self.apps[recipe.split('/')[1]])],
                        self.pin, now=datetime.fromisoformat(NOW.replace('Z','+00:00')))
                    self.assertEqual(r.stdout.decode().splitlines(), [self.pin, ref['repository_id'],
                        ref['release_id'], ref['asset_id'], ref['observed_at'], ref['asset']['url']])

    def test_shell_entry_points_and_private_arena_cleanup(self):
        temp=self.path/'tmp'; temp.mkdir()
        self.env['TMPDIR']=str(temp)
        for shell in (['/bin/dash'],['/bin/bash'],['busybox','ash']):
            actual=subprocess.run([*shell,str(HELPER),str(self.repo),self.pin,
                'x86_64/obsidian',NOW],env=self.env,capture_output=True)
            self.assertEqual(actual.returncode,0,actual.stderr)
            self.assertEqual(list(temp.iterdir()),[])
            refused=subprocess.run([*shell,str(HELPER),str(self.repo),self.pin,
                'x86_64/obsidian','2026-11-04T12:00:00Z'],env=self.env,capture_output=True)
            self.assertNotEqual(refused.returncode,0)
            self.assertEqual(refused.stdout,b'')
            self.assertEqual(list(temp.iterdir()),[])

    def test_command_cache_reuses_acquisition_rechecks_acceptance_and_pin(self):
        first = self.run_selection(); self.assertEqual(first.returncode, 0, first.stderr)
        files = {p: (p.stat().st_mtime_ns, hashlib.sha256(p.read_bytes()).hexdigest())
                 for p in self.session.rglob('*.yaml')}
        second = self.run_selection(); self.assertEqual(second.stdout, first.stdout)
        self.assertEqual(files, {p:(p.stat().st_mtime_ns,hashlib.sha256(p.read_bytes()).hexdigest()) for p in files})
        stale = self.run_selection(now='2026-11-04T12:00:00Z')
        self.assertNotEqual(stale.returncode, 0); self.assertEqual(stale.stdout, b'')
        token = ':'.join(first.stdout.decode().splitlines()[:5])
        self.assertEqual(self.run_selection(now='2026-11-04T12:00:00Z', acceptance=token).stdout, first.stdout)
        wrong = self.run_selection('x86_64/nvim', now='2026-11-04T12:00:00Z', acceptance=token)
        self.assertNotEqual(wrong.returncode, 0); self.assertEqual(wrong.stdout,b'')
        # A moved local tip must not change a read at the original explicit pin.
        other = copy.deepcopy(self.repositories)
        other['262342594']['collection']['status']='failed'
        other['262342594']['collection']['reason']='transport'
        after = publish_local(self.repo, self.apps, other, schema=SCHEMA,
                             max_file_bytes=2097152, expected_parent=self.pin)
        self.assertNotEqual(after, self.pin)
        self.assertEqual(self.run_selection().stdout, first.stdout)

    def test_invalid_suffix_oversize_identity_and_invalid_now_emit_nothing(self):
        self.assertEqual(self.run_selection().returncode, 0)
        repository = self.session/self.pin/'repositories/262342594.yaml'
        original = repository.read_bytes()
        for raw in (original+b'unknown: true\n', b'x'*2097153,
                    original.replace(b'repository_id: 262342594', b'repository_id: 262342595')):
            repository.write_bytes(raw)
            r = self.run_selection()
            self.assertNotEqual(r.returncode, 0); self.assertEqual(r.stdout, b'')
        repository.write_bytes(original)
        for now in ('2026-02-30T12:00:00Z', '2026-11-04T12:00:00+00:00', '2026-10-26T00:00:00Z'):
            r = self.run_selection(now=now)
            self.assertNotEqual(r.returncode, 0); self.assertEqual(r.stdout,b'')

    def test_adversarial_shell_ties_escapes_channels_and_freshness(self):
        self.repo = self.path/'adversarial.git'; self.repo.mkdir()
        git(self.repo,'init','--bare')
        repository = copy.deepcopy(self.repositories['16408992'])
        repository['observed_at']='2026-11-04T12:00:00Z'
        repository['last_success']['completed_at']='2026-11-04T12:00:00Z'
        r = copy.deepcopy(next(iter(repository['releases'].values())))
        r.pop('observed_at',None)
        r.update(tag='v2-rc1', prerelease=True, published_at='2026-11-01T00:00:00Z')
        a = copy.deepcopy(next(iter(r['assets'].values())))
        a.update(name='a\tquote"\\line\n', url='https://github.com/neovim/neovim/releases/download/v2/nvim.AppImage')
        r['assets']={'9007199254740992':dict(a), '9007199254740993':dict(a)}
        repository['releases']={'9007199254740992':copy.deepcopy(r), '9007199254740993':r}
        apps={'nvim':16408992,'nvim-nightly':16408992}
        self.pin = publish_local(self.repo,apps,{'16408992':repository},schema=SCHEMA,
                                max_file_bytes=2097152,expected_parent=None)
        for tool in ('mawk','gawk','busybox'):
            shim=self.bin/'awk'
            shim.write_text('#!/bin/sh\nexec '+tool+(' awk' if tool=='busybox' else '')+' "$@"\n');shim.chmod(0o755)
            for now in ('2026-11-04T12:00:00Z','2026-11-06T12:00:00Z'):
                actual=self.run_selection('aarch64/nvim',now=now)
                self.assertEqual(actual.returncode,0,actual.stderr)
                lines=actual.stdout.decode().splitlines()
                self.assertEqual(lines[2:4],['9007199254740993','9007199254740992'])
            stale=self.run_selection('aarch64/nvim',now='2026-11-06T12:00:01Z')
            self.assertNotEqual(stale.returncode,0);self.assertEqual(stale.stdout,b'')
            empty=self.run_selection('x86_64/nvim-nightly',now='2026-11-04T12:00:00Z')
            self.assertNotEqual(empty.returncode,0);self.assertEqual(empty.stdout,b'')
        # Exact nightly tag gate rejects the old URL-substring-only case.
        r['tag']='nightly-experiment'
        for asset in r['assets'].values():
            asset['url']='https://github.com/neovim/neovim/releases/download/nightly/nvim.AppImage'
        repository['releases']={'9007199254740993':r}
        self.pin=publish_local(self.repo,apps,{'16408992':repository},schema=SCHEMA,
                              max_file_bytes=2097152,expected_parent=self.pin)
        self.assertNotEqual(self.run_selection('x86_64/nvim-nightly',now='2026-11-04T12:00:00Z').returncode,0)
        r['tag']='v2'
        r={'observed_at':'2026-11-01T12:00:00Z',**r}
        for asset in r['assets'].values():
            asset['url']='https://github.com/neovim/neovim/releases/download/v2/nvim.AppImage'
        fresh=copy.deepcopy(r); fresh.pop('observed_at')
        fresh['published_at']='2026-10-01T00:00:00Z'
        repository['releases']={'1':fresh,'9007199254740993':r}
        repository['collection'].update(status='failed',reason='transport')
        self.pin=publish_local(self.repo,apps,{'16408992':repository},schema=SCHEMA,
                              max_file_bytes=2097152,expected_parent=self.pin)
        stale=self.run_selection('x86_64/nvim',now='2026-11-04T12:00:00Z')
        self.assertNotEqual(stale.returncode,0);self.assertEqual(stale.stdout,b'')
        token=':'.join([self.pin,'16408992','9007199254740993','9007199254740992',r['observed_at']])
        accepted=self.run_selection('x86_64/nvim',now='2026-11-04T12:00:00Z',acceptance=token)
        self.assertEqual(accepted.returncode,0,accepted.stderr)
        self.assertEqual(accepted.stdout.decode().splitlines()[4],r['observed_at'])

    def prepare_lifecycle(self, recipe):
        module = self.path/'appimage.am'; module.write_text(module_candidate())
        script = self.path/(recipe.replace('/','-')+'.sh')
        script.write_text(recipe_candidate(recipe, module, self.repo, self.pin, NOW))
        self.env.update(APPS_DIR=str(self.path/'root/opt'), BIN_DIR=str(self.path/'root/bin'),
            DESKTOP_DIR=str(self.path/'root/desktop'), FAKE_APP=recipe.split('/')[1], TEST_ROOT=str(self.path))
        wget = self.bin/'wget'
        wget.write_text('''#!/bin/sh
[ "${DOWNLOAD_FAIL-}" != 1 ] || exit 9
printf '%s\\n' "$3" >> "$TEST_ROOT/downloads"
cat > "$2" <<'PAYLOAD'
#!/bin/sh
mkdir -p squashfs-root
case $2 in
  '*.desktop') printf '[Desktop Entry]\\nExec=%s --no-sandbox\\nIcon=%s\\n' "$FAKE_APP" "$FAKE_APP" > "squashfs-root/$FAKE_APP.desktop" ;;
  .DirIcon) printf icon > squashfs-root/.DirIcon ;;
esac
PAYLOAD
''')
        wget.chmod(0o755)
        notify = self.bin/'notify-send'; notify.write_text('#!/bin/sh\nexit 0\n'); notify.chmod(0o755)
        return script, self.path/'root/opt'/recipe.split('/')[1]

    def run_script(self, script, *args):
        return subprocess.run(['/bin/dash', str(script), *args], env=self.env,
                              cwd=self.path, capture_output=True)

    def snapshot(self):
        root = self.path/'root'
        return {str(p.relative_to(root)): ('link', os.readlink(p)) if p.is_symlink()
                else ('file',p.read_bytes()) if p.is_file() else ('dir',)
                for p in root.rglob('*')}

    def test_all_five_install_and_generated_updater_bindings(self):
        for recipe in COHORT:
            with self.subTest(recipe=recipe):
                script, app = self.prepare_lifecycle(recipe)
                r = self.run_script(script); self.assertEqual(r.returncode,0,r.stderr)
                url = self.run_selection(recipe).stdout.decode().splitlines()[5]
                self.assertEqual((app/'version').read_text(),url+'\n')
                self.assertEqual((self.path/'downloads').read_text().splitlines()[-1],url)
                self.assertIn(str(HELPER),(app/'recipe.am').read_text())
                self.assertIn(self.pin,(app/'recipe.am').read_text())
                r = self.run_script(app/'AM-updater'); self.assertEqual(r.returncode,0,r.stderr)
                self.assertEqual((app/'version').read_text(),url+'\n')
                if recipe.endswith('/obsidian'):
                    self.assertNotIn('--no-sandbox',(self.path/'root/desktop/obsidian-AM.desktop').read_text())

    def test_update_skip_nightly_refresh_repair_and_failed_download_retry(self):
        for recipe in ('x86_64/obsidian','x86_64/nvim-nightly'):
            script, app = self.prepare_lifecycle(recipe)
            self.assertEqual(self.run_script(script).returncode,0)
            downloads=self.path/'downloads'
            before=len(downloads.read_text().splitlines())
            r=self.run_script(app/'AM-updater'); self.assertEqual(r.returncode,0,r.stderr)
            self.assertEqual(len(downloads.read_text().splitlines()),before+(recipe.endswith('nightly')))
            (app/'AM-VERIFIED').write_text('Checksum failure\n')
            self.assertEqual(self.run_script(app/'AM-updater').returncode,0)
            self.assertEqual(len(downloads.read_text().splitlines()),before+1+(recipe.endswith('nightly')))
            (app/'version').write_text('old\n'); binary=(app/app.name).read_bytes()
            self.env['DOWNLOAD_FAIL']='1'
            self.assertNotEqual(self.run_script(app/'AM-updater').returncode,0)
            self.assertEqual((app/'version').read_text(),'old\n')
            self.assertEqual((app/app.name).read_bytes(),binary)
            self.env.pop('DOWNLOAD_FAIL')
            self.assertEqual(self.run_script(app/'AM-updater').returncode,0)
            self.assertNotEqual((app/'version').read_text(),'old\n')

    def test_stale_refusal_before_install_cleanup_update_and_batch_acceptance(self):
        script, app = self.prepare_lifecycle('x86_64/obsidian')
        self.assertEqual(self.run_script(script).returncode,0)
        installed=app/'recipe.am'
        installed.write_text(installed.read_text().replace(NOW,'2026-11-04T12:00:00Z'))
        script.write_text(script.read_text().replace(NOW,'2026-11-04T12:00:00Z'))
        (app/'version').unlink(); (app/'tmp').mkdir()
        before=self.snapshot()
        r=self.run_script(script)
        self.assertNotEqual(r.returncode,0); self.assertEqual(self.snapshot(),before)
        r=self.run_script(app/'AM-updater')
        self.assertNotEqual(r.returncode,0); self.assertEqual(self.snapshot(),before)
        # Disposable batch driver shares only command acquisition, with per-app waiver.
        original=self.run_selection().stdout.decode().splitlines()
        self.env['CATALOG_YAML_ACCEPT']=':'.join(original[:5])
        accepted=self.run_script(script)
        self.assertEqual(accepted.returncode,0,accepted.stderr)
        script, nvim=self.prepare_lifecycle('x86_64/nvim')
        script.write_text(script.read_text().replace(NOW,'2026-11-04T12:00:00Z'))
        before=self.snapshot()
        self.assertNotEqual(self.run_script(script).returncode,0)
        self.assertEqual(self.snapshot(),before)
        self.assertFalse(nvim.exists())


if __name__ == '__main__':
    unittest.main()
