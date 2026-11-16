"""Every recipe installed on the host: real manager install and standalone update.

Slow, and it follows whatever recipes the tree holds. Run before an upstream
merge and on demand: `-p 'tree_*.py'`.
"""
import unittest

from installed_recipe import managed_updater
import test_host_cutover


class TreeHostCutover(test_host_cutover.HostCutoverCase):
    def test_all_host_recipes_manager_install_and_standalone_update(self):
        for row in self.rows:
            with self.subTest(app=row['app']):
                app=self.install('x86_64/'+row['app'])
                self.assertEqual((app/'AM-updater').read_bytes(), managed_updater(app/'recipe.am'))
                self.assertEqual((app/'version').read_text().strip(),'2026-11-02T00:00:00Z' if row['app']=='logseq-app-db-nightly' else (app/'download-url').read_text().strip())
                result=self.standalone(app/'AM-updater')
                self.assertEqual(result.returncode,0,result.stderr)
                if row['app']=='emmylua':
                    for tool in ('emmylua_ls','emmylua_check','emmylua_doc_cli','luafmt'):
                        self.assertEqual((app/tool).read_bytes(),b'tool')
                        self.assertTrue((self.root/'usr/local/bin'/tool).is_symlink())
                if row['app']=='kitty':self.assertTrue((self.root/'usr/local/bin/kitten').is_symlink())


if __name__=='__main__':unittest.main()
