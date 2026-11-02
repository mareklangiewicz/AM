"""Frozen evidence orchestration: failures do not block independent endpoints."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import migration_evidence as evidence


class MigrationEvidence(unittest.TestCase):
    def test_release_validation_and_unchanged_bounds(self):
        def fake_fetch(url, out, deadline, *, validate_value, body_cap, token):
            self.assertEqual(body_cap,8_000_000)
            self.assertEqual(token,b'explicit')
            valid=[dict(id=1,tag_name='v1',draft=False,assets=[],published_at='2026-11-02T11:00:00+00:00')]
            report=validate_value(valid,json.dumps(valid).encode())
            self.assertEqual(report['release_count'],1)
            with self.assertRaises(ValueError):
                validate_value({},b'{}')
            return report
        with patch.object(evidence,'fetch',fake_fetch):
            evidence.release_request('https://api.github.com/repositories/123/releases',123,
                                     Path('/unused'),10,token=b'explicit')

    def test_isolates_identity_and_release_failures_and_preserves_quota_pending(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            rows=[dict(identity_request='https://api.github.com/repos/owner/'+name,
                       alias='https://api.github.com/repos/owner/'+name+'/releases')
                  for name in ('missing','redirect','good','quota','pending')]
            calls=[]
            def identity(url,out,deadline,**kwargs):
                calls.append(url)
                if url.endswith('/missing'): return dict(accepted=False,status=404)
                if url.endswith('/quota'): return dict(accepted=False,status=429)
                return dict(accepted=True,identity=dict(id=123))
            def release(url,repository_id,out,deadline,**kwargs):
                return dict(accepted=len(calls)!=2,status=301 if len(calls)==2 else 200)
            with patch.object(evidence,'ROOT',root), patch.object(evidence,'load_payload',return_value=dict(rows=rows)), \
                 patch.object(evidence,'saved_identities',return_value=({},set())), \
                 patch.object(evidence,'request',identity), patch.object(evidence,'release_request',release):
                summary=evidence.collect(root/'out')
            self.assertEqual(len(calls),4)
            self.assertEqual(len(summary['failures']),3)
            self.assertEqual(len(summary['releases']),2)
            self.assertTrue(summary['releases'][-1]['accepted'])
            self.assertEqual(summary['pending'],[rows[-1]['alias']])
            self.assertEqual(summary,json.loads((root/'out/batch.json').read_bytes()))


if __name__=='__main__': unittest.main()
