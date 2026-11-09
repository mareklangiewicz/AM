"""Shared names must not overwrite another architecture's source or old paths."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import bulk_enrollment as b


class Enrollment(unittest.TestCase):
    def test_distinct_architecture_sources_get_stable_aliases(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);folder=root/'tools/catalog-collector';folder.mkdir(parents=True)
            (folder/'source-names.json').write_text(json.dumps(dict(active={'1':'original-path'},retired=['project'])))
            identities=root/'evidence';identities.mkdir();rows=[];proofs=[]
            for arch,rid in (('x86_64',1),('aarch64',2)):
                path=root/'programs'/arch/'example';path.parent.mkdir(parents=True);path.write_text('APP=example\n')
                raw=b'public metadata';name=f'{rid:04d}.json';(identities/name).write_bytes(raw)
                rows.append(dict(requested_repository='owner/project'+str(rid),repository='owner/project'+str(rid),
                    repository_id=rid,status='verified',evidence=name,evidence_sha256=hashlib.sha256(raw).hexdigest(),observed_at='2026-11-09T12:00:00Z'))
                proofs.append(dict(recipe=f'programs/{arch}/example',repository='owner/project'+str(rid),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
            (identities/'identities.json').write_text(json.dumps(dict(source='a'*40,repositories=rows)))
            scan=dict(source='a'*40,candidates=[],ambiguous=[dict(app='example',bindings=proofs)],unresolved=[])
            with patch.object(b.host,'ROOT',root),patch.object(b.host,'configuration',return_value=([],{})):
                result=b.plan(scan,[identities])
            self.assertEqual({r['app']:r['repository_id'] for r in result['enrollment']},{'example':1,'example.src-2':2})
            self.assertEqual(result['registry']['active']['1'],'original-path')
            self.assertNotIn('project',result['registry']['active'].values())
            (identities/'0001.json').write_bytes(b'changed')
            with self.assertRaises(ValueError):b.identities([identities])


if __name__=='__main__':unittest.main()
