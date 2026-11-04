"""Small collector-attempt contract checks; fixture timestamps never use replay time."""
import sys
from pathlib import Path
# Legacy experiment entry point; runtime code lives in catalog-collector.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'catalog-collector'))
import json
import unittest

from attempt_adapter import merge_attempts
from bounded_experiment import release
from experiment import repository


class Attempts(unittest.TestCase):
    def setUp(self):
        self.old = repository()
        self.attempt = dict(repository_id=123,
                            descriptor=dict(url='https://api.github.com/repositories/123/releases'),
                            outcome='response',status=200,headers={},
                            request_started_at='2026-11-04T12:00:00.100+00:00',
                            response_completed_at='2026-11-04T12:00:01.900+00:00',
                            body=json.dumps([release()]).encode())

    def merge(self,pages,**options):
        return merge_attempts(self.old,pages,attempted_at='2026-11-04T12:00:00Z',**options)

    def preserved(self,result,reason):
        self.assertEqual(result['collection']['reason'],reason)
        for key in ('releases','observed_at','last_success'):
            self.assertEqual(result[key],self.old[key])

    def test_original_receipt_and_partial_retention(self):
        result = self.merge([(self.attempt,True)])
        self.assertEqual(result['observed_at'],'2026-11-04T12:00:01Z')
        self.assertEqual(result['releases']['456'],self.old['releases']['456'])
        self.assertIn('457',result['releases'])
        self.assertFalse(result['last_success']['history_complete'])

    def test_later_failure_rolls_back_new_release(self):
        broken = dict(self.attempt,body=b'{')
        self.preserved(self.merge([(self.attempt,True),(broken,False)],page_limit='all'),'invalid_response')

    def test_finite_scope_does_not_consume_later_attempts(self):
        def pages():
            yield self.attempt,True
            raise AssertionError('scope overread')
        self.assertEqual(self.merge(pages())['collection']['status'],'ok')

    def test_wrong_identity_latest_and_304_refuse(self):
        cases = [dict(self.attempt,repository_id=124),dict(self.attempt,status=304,body=b''),
                 dict(self.attempt,descriptor=dict(url='https://api.github.com/repositories/123/releases/latest')),
                 dict(self.attempt,body=b'[{"id":1,"id":2}]')]
        for attempt in cases:
            self.preserved(self.merge([(attempt,False)]),'invalid_response')

    def test_transport_and_rate_refusals(self):
        self.preserved(self.merge([(dict(self.attempt,outcome='timeout'),False)]),'transport')
        for status,headers in ((429,{}),(403,{'x-ratelimit-remaining':'0'})):
            self.preserved(self.merge([(dict(self.attempt,status=status,headers=headers),False)]),'rate_limited')
        self.preserved(self.merge([(dict(self.attempt,status=403),False)]),'invalid_response')

    def test_bad_receipt_is_not_replaced_with_now(self):
        for value in (None,'invalid','2026-11-04T12:00:01+01:00','2026-11-04T11:00:01+00:00'):
            self.preserved(self.merge([(dict(self.attempt,response_completed_at=value),False)]),'invalid_response')


if __name__ == '__main__':
    unittest.main()
