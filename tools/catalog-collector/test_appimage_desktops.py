"""The shared installer installs every desktop launcher an AppImage ships (ticket 37).

A declaration is installed through modules/appimage.am with an authored inert
AppImage whose --appimage-extract copies members from a fixture directory; the
selection helper, wget and all paths are confined to a TemporaryDirectory.
"""
import os
import shutil
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
NOW='2026-11-17T12:00:00Z'


def script(path,source):
    path.write_text('#!/bin/sh\nset -eu\n'+source);path.chmod(0o755)


def entry(name,*extra):
    return '\n'.join(['[Desktop Entry]','Name='+name,'Exec=upstream-'+name+' --no-sandbox %U','Icon=upstream',*extra])+'\n'


class Desktops(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory(prefix='appimage-desktops-');self.addCleanup(tmp.cleanup)
        self.home=home=Path(tmp.name)
        self.members=home/'members';self.members.mkdir()
        (self.members/'.DirIcon').write_text('fixture-icon')
        tools=home/'tools';tools.mkdir()
        script(tools/'wget','[ "$1" = -O ] || exit 94\ncp "$FIXTURE_PAYLOAD" "$2"\n')
        script(tools/'curl','exit 98\n')
        script(home/'payload','''[ "$1" = --appimage-extract ] || exit 95
mkdir -p squashfs-root
case "$2" in
 '*.desktop') for f in "$FIXTURE_MEMBERS"/*.desktop; do [ -e "$f" ] || [ -L "$f" ] || continue; cp -P "$f" squashfs-root/; done ;;
 *) [ -e "$FIXTURE_MEMBERS/$2" ] || [ -L "$FIXTURE_MEMBERS/$2" ] || exit 0  # like the real tool: nothing, status 0
    mkdir -p "squashfs-root/$(dirname "$2")"; cp -P "$FIXTURE_MEMBERS/$2" "squashfs-root/$2" ;;
esac
''')
        script(home/'select','printf "%s\\n" 1 1 1 '+NOW+' https://example.invalid/v1/App.AppImage\n')
        self.desktops=home/'desktops'
        self.env=dict(PATH=str(tools)+os.pathsep+os.environ['PATH'],HOME=str(home),
            APPS_DIR=str(home/'apps'),BIN_DIR=str(home/'links'),DESKTOP_DIR=str(self.desktops),
            CATALOG_YAML_HELPER=str(home/'select'),FIXTURE_PAYLOAD=str(home/'payload'),
            FIXTURE_MEMBERS=str(self.members))

    def install(self,settings=''):
        recipe=self.home/'recipe'
        recipe.write_text('#!/bin/sh\nset -eu\nAPP=demo\nCATALOG_FORMAT=3\nCATALOG_RECIPE=x86_64/demo\n'+settings+
                          '. "'+str(ROOT/'modules/appimage.am')+'"\nam_appimage "$0" "$@"\n')
        return subprocess.run(['sh',str(recipe)],env=self.env,capture_output=True,timeout=20)

    def installed(self):
        return {path.name:path.read_text() for path in sorted(self.desktops.iterdir())} if self.desktops.exists() else {}

    def remove(self):
        result=subprocess.run(['sh',str(self.home/'apps/demo/remove')],env=self.env,capture_output=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stderr)

    def test_an_icon_link_to_the_build_machines_appdir_resolves_inside_the_appimage(self):
        # rclone-ui: .DirIcon -> /home/runner/.../Rclone UI.AppDir/Rclone UI.png
        (self.members/'.DirIcon').unlink()
        (self.members/'.DirIcon').symlink_to('/home/runner/work/x/bundle/Demo UI.AppDir/Demo UI.png')
        (self.members/'Demo UI.png').write_text('real-icon')
        (self.members/'a-main.desktop').write_text(entry('main'))
        result=self.install()
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual((self.home/'apps/demo/icons/demo').read_text(),'real-icon')

    def test_an_unresolvable_icon_link_installs_without_an_icon(self):
        (self.members/'.DirIcon').unlink()
        (self.members/'.DirIcon').symlink_to('/nowhere/missing.png')
        (self.members/'a-main.desktop').write_text(entry('main'))
        result=self.install()
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertFalse(os.path.lexists(self.home/'apps/demo/icons/demo'))
        self.assertIn('demo-AM.desktop',self.installed())

    def test_every_launcher_is_installed_and_removed(self):
        # The first in byte order is the main launcher.
        (self.members/'b-tools.desktop').write_text(entry('tools'))
        (self.members/'a-main.desktop').write_text(entry('main'))
        result=self.install()
        self.assertEqual(result.returncode,0,result.stderr)
        icon=str(self.home/'apps/demo/icons/demo')
        self.assertEqual(self.installed(),{
            'demo-2-AM.desktop':'[Desktop Entry]\nName=tools\nExec=demo --no-sandbox %U\nIcon='+icon+'\n',
            'demo-AM.desktop':'[Desktop Entry]\nName=main\nExec=demo --no-sandbox %U\nIcon='+icon+'\n'})
        self.remove()
        self.assertEqual(self.installed(),{})

    def test_handlers_are_named_apart_and_copies_of_the_main_launcher_skipped(self):
        (self.members/'a-url-handler.desktop').write_text(entry('url','NoDisplay=true'))
        (self.members/'b-main.desktop').write_text(entry('main'))
        (self.members/'c-same.desktop').write_text(entry('main'))
        (self.members/'d-mime-handler.desktop').write_text(entry('mime','NoDisplay=true'))
        (self.members/'e-extra.desktop').write_text(entry('extra'))
        self.assertEqual(self.install().returncode,0)
        self.assertEqual({name:text.split('\n')[1] for name,text in self.installed().items()},{
            'demo-AM.desktop':'Name=main','demo-2-AM.desktop':'Name=extra',
            'demo-handler-AM.desktop':'Name=url','demo-handler-2-AM.desktop':'Name=mime'})
        self.remove()
        self.assertEqual(self.installed(),{})

    @unittest.skipUnless(shutil.which('bash') and 'en_US.utf8' in subprocess.run(['locale','-a'],capture_output=True,text=True).stdout,
                         'needs bash and the en_US.UTF-8 locale')
    def test_main_launcher_is_chosen_in_byte_order_whatever_the_locale(self):
        # bash as sh sorts globs by locale; en_US would put demo.desktop first.
        (self.members/'demo.desktop').write_text(entry('dot'))
        (self.members/'demo-tools.desktop').write_text(entry('dash'))
        (self.members/'Zeta.desktop').write_text(entry('upper'))
        shell=self.home/'bash-as-sh';shell.mkdir();(shell/'sh').symlink_to(shutil.which('bash'))
        self.env.update(PATH=str(shell)+os.pathsep+self.env['PATH'],LC_ALL='en_US.UTF-8')
        self.assertEqual(self.install().returncode,0)
        self.assertEqual({name:text.split('\n')[1] for name,text in self.installed().items()},{
            'demo-AM.desktop':'Name=upper','demo-2-AM.desktop':'Name=dash','demo-3-AM.desktop':'Name=dot'})

    def test_lone_hidden_entry_installs_as_the_handler_and_is_removed(self):
        (self.members/'demo.desktop').write_text(entry('url','NoDisplay=true'))
        self.assertEqual(self.install().returncode,0)
        self.assertEqual(list(self.installed()),['demo-handler-AM.desktop'])
        self.remove()
        self.assertEqual(self.installed(),{})

    def test_no_desktop_file_installs_without_a_launcher(self):
        result=self.install()
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(self.installed(),{})
        self.assertEqual((self.home/'apps/demo/icons/demo').read_text(),'fixture-icon')
        self.assertTrue((self.home/'links/demo').is_symlink())

    def test_symlinked_launchers_resolve_and_two_links_to_one_entry_install_once(self):
        (self.members/'usr/share/applications').mkdir(parents=True)
        (self.members/'usr/share/applications/real.desktop').write_text(entry('main'))
        (self.members/'usr/share/applications/hop.desktop').symlink_to('real.desktop')
        (self.members/'a.desktop').symlink_to('usr/share/applications/real.desktop')
        # A link to a link: each hop resolves against the AppImage root.
        (self.members/'b.desktop').symlink_to('usr/share/applications/hop.desktop')
        (self.members/'usr/share/applications/hop.desktop').unlink()
        (self.members/'usr/share/applications/hop.desktop').symlink_to('usr/share/applications/real.desktop')
        self.assertEqual(self.install().returncode,0)
        self.assertEqual(list(self.installed()),['demo-AM.desktop'])
        self.assertIn('Name=main',self.installed()['demo-AM.desktop'])

    def test_settings_apply_to_every_launcher(self):
        (self.members/'a.desktop').write_text(entry('main'))
        (self.members/'b.desktop').write_text(entry('other'))
        (self.members/'c.desktop').write_text(entry('url','NoDisplay=true'))
        result=self.install('DESKTOP_STRIP_NO_SANDBOX=true\nDESKTOP_EXEC=installed\n')
        self.assertEqual(result.returncode,0,result.stderr)
        executable=str(self.home/'apps/demo/demo')
        for name,text in self.installed().items():
            self.assertIn('\nExec="'+executable+'" %U\n',text,name)

    def test_existing_extra_launcher_is_preserved_and_left_to_its_owner(self):
        (self.members/'a.desktop').write_text(entry('main'))
        (self.members/'b.desktop').write_text(entry('other'))
        self.desktops.mkdir();(self.desktops/'demo-2-AM.desktop').write_text('custom')
        result=self.install()
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn(b'Preserving desktop launcher',result.stdout)
        self.assertEqual(self.installed()['demo-2-AM.desktop'],'custom')
        self.remove()
        self.assertEqual(self.installed(),{'demo-2-AM.desktop':'custom'})


if __name__=='__main__':unittest.main()
