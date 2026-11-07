"""Source discovery proves an explicit binding; metadata never migrates recipes."""
import contextlib
import hashlib
import io
import json
import urllib.error
from unittest.mock import MagicMock
import subprocess
import unittest
from unittest.mock import patch

import catalog_sources as discovery


class Sources(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalogue = discovery._catalogue(discovery.ROOT)

    def test_real_template_binding_refuses_custom_or_inconsistent_source(self):
        source = discovery.Originals(discovery.ROOT).read(
            'bbffd15c19d01ef9124fbf99b5b9c41d2661ea22', 'programs/x86_64/agent-skills')
        found = discovery.binding(source, 'agent-skills', self.catalogue)
        self.assertEqual(found['repository'], 'chrlsio/agent-skills')
        self.assertEqual(found['proof'], 'whole_upstream_template')
        for changed in (source+'\ntouch /tmp/not-executed\n',
                        source.replace('SITE="chrlsio/agent-skills"', 'SITE="other/source"', 1),
                        source.replace('APP=agent-skills', 'APP=$(command)', 1)):
            self.assertIsNone(discovery.binding(changed, 'agent-skills', self.catalogue))

    def test_literal_alias_is_binding_only_and_refuses_ambiguous_or_shell_values(self):
        source = (discovery.ROOT/'programs/x86_64/0xfx').read_text()
        self.assertEqual(discovery.binding(source, '0xfx', self.catalogue),
            dict(repository='averagenative/0xfx', proof='literal_catalog_alias'))
        for changed in (source+'\nCATALOG_ALIAS=https://api.github.com/repos/other/source/releases\n',
                        source.replace('averagenative/0xfx/releases', '$(command)/source/releases'),
                        source.replace('# AM-CATALOG-RECIPE 1\n', '')):
            self.assertIsNone(discovery.binding(changed, '0xfx', self.catalogue))

    def queue(self):
        path = 'programs/x86_64/0xfx'
        source = (discovery.ROOT/path).read_bytes()
        return dict(source=subprocess.check_output(['git','-C',str(discovery.ROOT),'rev-parse','HEAD'],
            text=True).strip(), candidates=[dict(app='0xfx', repository='averagenative/0xfx', bindings=[
                dict(recipe=path, sha256=hashlib.sha256(source).hexdigest())])])

    def verify(self, queue, replies, **kwargs):
        with patch.object(discovery, '_get', side_effect=replies) as get, \
                patch.object(discovery, 'configuration', return_value=([], {})), \
                contextlib.redirect_stdout(io.StringIO()):
            result = discovery.verify(queue, max_sources=128, max_requests=kwargs.pop('max_requests',200), **kwargs)
            return result, get.call_count

    def test_verified_public_identity_and_release_probe_produce_proposal_and_checkpoint(self):
        checkpoints = []
        result, requests = self.verify(self.queue(), [
            (dict(id=123, full_name='averagenative/0xfx', private=False), 'metadata-hash'),
            ([dict(id=456, draft=False)], 'release-hash')], checkpoint=checkpoints.append)
        self.assertEqual(requests, 2)
        self.assertEqual(result['proposals'][0]['enrollment'],
            dict(app='0xfx', repository_id=123, repository='averagenative/0xfx'))
        self.assertEqual(checkpoints[-1]['requests'], 2)
        self.assertEqual(result['proposals'][0]['metadata_sha256'], 'metadata-hash')

    def test_explicit_redirect_review_requires_same_public_numeric_identity(self):
        alias = (dict(id=123,full_name='renamed/project',private=False),'alias')
        direct = (dict(id=123,full_name='renamed/project',private=False),'canonical')
        result, requests = self.verify(self.queue(), [alias,direct,([dict(draft=False)],'release')],
                                       review_redirects=True)
        self.assertEqual(requests,3)
        proposal=result['proposals'][0]
        self.assertEqual(proposal['enrollment']['repository'],'renamed/project')
        self.assertEqual(proposal['canonical_metadata_sha256'],'canonical')
        for changed in (dict(id=124,full_name='renamed/project',private=False),
                        dict(id=123,full_name='renamed/project',private=True),
                        dict(id=123,full_name='another/project',private=False)):
            result, requests = self.verify(self.queue(), [alias,(changed,'changed')],review_redirects=True)
            self.assertEqual(result['proposals'],[])
            self.assertEqual(result['deferred'][0]['reason'],'redirect_identity_mismatch')
        result,requests=self.verify(self.queue(),[alias],max_requests=1,review_redirects=True)
        self.assertEqual(requests,1)
        self.assertEqual(result['proposals'],[])

    def test_identity_proposal_scope_is_independent_of_enrollment_cap(self):
        with patch.object(discovery,'configuration',return_value=([],{'1':'existing/project'})), \
                contextlib.redirect_stdout(io.StringIO()):
            with patch.object(discovery,'_get',return_value=(dict(private=True),'h')):
                result=discovery.verify(self.queue(),max_sources=224,max_requests=1)
        self.assertEqual(result['requests'],1)
        self.assertEqual(result['proposals'],[])

    def test_redirect_private_empty_probe_and_budget_do_not_enroll(self):
        for replies in ([ (dict(id=123, full_name='other/source', private=False), 'h') ],
                        [ (dict(id=123, full_name='averagenative/0xfx', private=True), 'h') ],
                        [ (dict(id=123, full_name='averagenative/0xfx', private=False), 'h'), ([], 'h') ]):
            result, _ = self.verify(self.queue(), replies)
            self.assertEqual(result['proposals'], [])
            self.assertEqual(len(result['deferred']), 1)
        result, requests = self.verify(self.queue(),
            [(dict(id=123,full_name='averagenative/0xfx',private=False),'h')], max_requests=1)
        self.assertEqual(requests, 1)
        self.assertEqual(result['proposals'], [])
        queue = self.queue()
        queue['candidates'][0]['repository'] = 'other/source'
        with self.assertRaisesRegex(ValueError, 'binding mismatch'):
            self.verify(queue, [])
        queue = self.queue()
        queue['candidates'][0]['bindings'][0]['sha256'] = 'changed'
        with self.assertRaisesRegex(ValueError, 'recipe changed'):
            self.verify(queue, [])

    def transport_verify(self, replies, *, budget=200, review=True):
        requests, errors, checkpoints = [], [], []
        def open_response(request):
            requests.append(request)
            reply = replies[len(requests)-1]
            if isinstance(reply, tuple):
                code, location = reply
                error = urllib.error.HTTPError(request.full_url, code, 'fixture',
                    {'Location':location}, io.BytesIO())
                errors.append(error)
                raise error
            response = MagicMock()
            response.__enter__.return_value = response
            response.status = 200
            response.url = request.full_url
            response.read.return_value = json.dumps(reply).encode()
            return response
        with patch.object(discovery, '_open', side_effect=open_response), \
                patch.object(discovery, 'configuration', return_value=([], {})), \
                patch.dict(discovery.os.environ, {'GH_TOKEN':'fixture-secret'}), \
                contextlib.redirect_stdout(io.StringIO()):
            result = discovery.verify(self.queue(), max_sources=500,
                max_requests=budget, review_redirects=review, checkpoint=checkpoints.append)
        self.assertEqual(result['requests'], len(requests))
        self.assertEqual(checkpoints[-1]['requests'],len(requests))
        for error in errors:
            self.assertTrue(error.fp.closed)
        return result, requests

    def test_transport_redirect_budget_and_explicit_identity_proof(self):
        metadata = dict(id=123, full_name='renamed/project', private=False)
        replies = [(301,'https://api.github.com/repositories/123'),
                   metadata, metadata, [dict(draft=False)]]
        for budget in (1,2,3,4):
            result, requests = self.transport_verify(replies,budget=budget)
            self.assertEqual(len(requests),budget)
            self.assertEqual(bool(result['proposals']),budget==4)
            self.assertEqual(result['request_accounting'],'transport_attempts_v1')
        self.assertEqual([r.full_url for r in requests], [
            'https://api.github.com/repos/averagenative/0xfx',
            'https://api.github.com/repositories/123',
            'https://api.github.com/repos/renamed/project',
            'https://api.github.com/repositories/123/releases?per_page=1&page=1'])
        self.assertTrue(all(r.get_header('Authorization')=='Bearer fixture-secret' for r in requests))
        bad = dict(metadata,id=124)
        result, requests = self.transport_verify([replies[0],metadata,bad])
        self.assertEqual(result['deferred'][0]['reason'],'redirect_identity_mismatch')
        self.assertEqual(len(requests),3)

    def test_transport_refuses_unexpected_destinations_before_forwarding(self):
        for location in ('http://api.github.com/repositories/123',
                'https://evil.example/repositories/123',
                'https://api.github.com.evil.example/repos/a/b',
                'https://secret@api.github.com/repositories/123',
                'https://api.github.com:443/repositories/123',
                '//api.github.com/repositories/123',
                'https://api.github.com/repositories/123?token=x',
                'https://api.github.com/repositories/123#fragment',
                'https://api.github.com/user',
                'https://api.github.com/repos/../user', ''):
            with self.subTest(location=location):
                result,requests=self.transport_verify([(301,location)])
                self.assertEqual(len(requests),1)
                self.assertEqual(result['deferred'][0]['reason'],'redirect_refused')
                self.assertEqual(result['proposals'],[])

    def test_transport_default_probe_redirect_and_loop_refusals(self):
        location='https://api.github.com/repositories/123'
        result,requests=self.transport_verify([(301,location)],review=False)
        self.assertEqual(len(requests),1)
        self.assertEqual(result['proposals'],[])
        metadata=dict(id=123,full_name='averagenative/0xfx',private=False)
        result,requests=self.transport_verify([metadata,(302,location)])
        self.assertEqual(len(requests),2)
        self.assertEqual(result['deferred'][0]['reason'],'redirect_refused')
        for code in (301,302,307,308):
            result,requests=self.transport_verify([(code,location)]*4)
            self.assertEqual(len(requests),4)
            self.assertEqual(result['deferred'][0]['reason'],'redirect_refused')
        for code in (401,403,429):
            result,requests=self.transport_verify([(code,'')])
            self.assertEqual(len(requests),1)
            self.assertEqual(result['deferred'][0]['reason'],'http_'+str(code))


if __name__ == '__main__':
    unittest.main()
