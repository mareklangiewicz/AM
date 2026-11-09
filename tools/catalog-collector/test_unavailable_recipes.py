"""Unverified identities refuse explicitly, without IDs, network or installer writes."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]


class Unavailable(unittest.TestCase):
    def test_all_unverified_bindings_are_hash_bound_and_fail_before_side_effects(self):
        receipt=json.loads((ROOT/'tools/catalog-collector/unavailable-github-recipes.json').read_text())
        self.assertEqual(len(receipt['recipes']),49)
        with tempfile.TemporaryDirectory() as temporary:
            directory=Path(temporary)
            for row in receipt['recipes']:
                path=ROOT/row['recipe'];raw=path.read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(),row['source_sha256'])
                self.assertIn(b'# AM-CATALOG-UNAVAILABLE 1\n',raw)
                self.assertNotIn(b'CATALOG_REPOSITORY_ID=',raw)
                self.assertNotIn(b'curl',raw);self.assertNotIn(b'wget',raw)
                result=subprocess.run(['/bin/sh',str(path)],cwd=directory,capture_output=True,text=True,env={'PATH':'/nonexistent'})
                self.assertEqual(result.returncode,1);self.assertEqual(result.stdout,'')
                self.assertIn(row['repository'],result.stderr)
                self.assertIn('cannot verify GitHub source',result.stderr)
            self.assertEqual(list(directory.iterdir()),[])


if __name__=='__main__':unittest.main()
