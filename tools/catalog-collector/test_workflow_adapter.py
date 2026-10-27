"""Offline context and staging checks; no credentials or socket operations."""
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from collector import Refusal
from workflow_adapter import preflight, run

REV = 'a' * 40
MANIFEST = Path(__file__).resolve().parents[2] / 'docs/track/release-catalog/design/staged-manifest.json'


class WorkflowPreparation(unittest.TestCase):
    def raw(self, enrolled=False):
        obj = json.loads(MANIFEST.read_bytes())
        if enrolled:
            # Synthetic ID only in memory, never written to staged enrollment.
            from collector import Descriptor
            row = obj['sources'][-1]
            row.update(repository_id=999, url='https://api.github.com/repositories/999/releases?per_page=100',
                       identity_evidence='docs/track/release-catalog/research/fixture.md#synthetic')
            row['request_id'] = Descriptor(row['url']).request_id
        else:
            row = obj['sources'][-1]
            row.update(repository_id=None, url=None, identity_evidence=None, request_id=None)
        return json.dumps(obj).encode()

    def context(self, raw):
        return dict(repository='mareklangiewicz/AM', repository_id='1', event='workflow_dispatch',
                    ref='refs/heads/main-marek', sha=REV, workflow_sha=REV, approved_revision=REV,
                    run_id='1', run_attempt='1', manifest_sha256=hashlib.sha256(raw).hexdigest())

    def test_incomplete_real_manifest_refuses_before_transport_or_token(self):
        raw = self.raw()
        with patch('workflow_adapter.SupervisedTransport') as transport, patch('workflow_adapter.Token') as token:
            with self.assertRaisesRegex(Refusal, 'unenrolled_source'):
                run(self.context(raw), raw, REV, b'FIXTURE', 'unused')
            transport.assert_not_called()
            token.assert_not_called()

    def test_synthetic_enrollment_yields_six_numeric_unconditional_requests(self):
        raw = self.raw(True)
        value = preflight(self.context(raw), raw, REV)
        self.assertEqual(len(value.requests), 6)
        self.assertTrue(all('/repositories/' in r.source.descriptor.url and not r.condition
                            for r in value.requests))
        self.assertIn('https://api.github.com/repos/wez/wezterm/releases?per_page=100',
                      value.requests[4].source.aliases)

    def test_reviewed_real_manifest_is_ready_for_offline_preflight(self):
        raw = MANIFEST.read_bytes()
        value = preflight(self.context(raw), raw, REV)
        self.assertEqual(value.requests[-1].source.repository_id, 19416551)
        self.assertEqual(len(value.requests), 6)
        self.assertTrue(all(not r.condition for r in value.requests))

    def test_context_revision_hash_and_own_repository_refusals(self):
        raw = self.raw(True)
        for key, bad in [('repository', 'other/AM'), ('event', 'push'), ('ref', 'refs/heads/main'),
                         ('repository_id', '01'), ('repository_id', '262342594'),
                         ('sha', 'b'*40), ('workflow_sha', 'b'*40), ('approved_revision', 'b'*40),
                         ('run_id', '0'), ('run_attempt', 'x'), ('manifest_sha256', 'b'*64)]:
            context = self.context(raw); context[key] = bad
            with self.subTest(key=key, bad=bad), self.assertRaises(Refusal):
                preflight(context, raw, REV)
        with self.assertRaises(Refusal):
            preflight(self.context(raw), raw, 'b'*40)


if __name__ == '__main__':
    unittest.main()
