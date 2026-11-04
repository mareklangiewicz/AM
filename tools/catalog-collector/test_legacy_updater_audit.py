"""Legacy adapter review refuses scope changes and byte drift before classification."""
import copy
import tempfile
from pathlib import Path
import unittest

from legacy_updater_audit import ADAPTERS,audit
from yaml_cutover_package import record


class LegacyAudit(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.inventory=dict(clients=[],files={})
        for app,(_,marker,_) in ADAPTERS.items():
            folder=self.root/'installed'/app;folder.mkdir(parents=True)
            script=folder/'AM-updater';script.write_text('# fixture behavior marker\n'+marker+'\n')
            source=self.root/'programs/x86_64'/app;source.parent.mkdir(parents=True,exist_ok=True)
            source.write_text('# fixture legacy source\n')
            self.inventory['clients'].append(dict(app=app,installation=str(folder),
                recipe='x86_64/'+app,kind='legacy-standalone'))
            self.inventory['files'][str(script)]=record(script)

    def test_exact_scope_and_updater_byte_drift_refuse(self):
        rows=audit(self.inventory,self.root)
        self.assertEqual(rows['count'],17)
        self.assertTrue(all(not row['apply_ready'] for row in rows['clients']))
        bad=copy.deepcopy(self.inventory);bad['clients'].pop()
        with self.assertRaisesRegex(ValueError,'reviewed 17-client scope'):audit(bad,self.root)
        script=self.root/'installed/emmylua/AM-updater'
        script.write_text(script.read_text()+'changed')
        with self.assertRaisesRegex(ValueError,'updater drift'):audit(self.inventory,self.root)


if __name__=='__main__':unittest.main()
