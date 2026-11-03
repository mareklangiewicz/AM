#!/usr/bin/env python3
"""Offline retained-catalog semantics and revised shell-reader acceptance."""
import copy
import unittest
from experiment import Experiment, repository
from retention import RunBudget, collect, fresh, parameters, refresh

ATTEMPT='2026-11-04T00:00:00Z'
SEEN='2026-11-04T00:00:10Z'
LATER='2026-11-04T00:00:20Z'


def response(records=None, *, next=True, at=SEEN, **kw):
    return dict(received_at=at,releases=records or {},has_next=next,bytes=100,seconds=10,**kw)


class Retention(unittest.TestCase):
    run_reader=Experiment.run_reader
    accepted=Experiment.accepted
    def setUp(self):
        self.old=repository()
        self.facts=copy.deepcopy(self.old['releases']['456'])
        self.facts.pop('observed_at')

    def run_refresh(self,responses,**kw):
        result=refresh(self.old,responses,attempted_at=ATTEMPT,**kw)
        self.accepted(result)
        return result

    def test_defaults_merge_and_selected_freshness(self):
        before=copy.deepcopy(self.old)
        result=self.run_refresh([response({'457':self.facts})])
        self.assertEqual(result['collection']['status'],'ok')
        self.assertFalse(result['last_success']['history_complete'])
        self.assertEqual(result['releases']['456'],before['releases']['456'])
        self.assertEqual(result['releases']['457']['observed_at'],SEEN)
        self.assertEqual(self.old,before)
        self.assertFalse(fresh(result['releases']['456'],'2026-11-05T01:00:00Z'))
        self.assertTrue(fresh(result['releases']['457'],'2026-11-05T01:00:00Z'))
        # Older stable remains selectable even after a newer prerelease is merged.
        prerelease=dict(self.facts,prerelease=True)
        result=self.run_refresh([response({'457':prerelease})])
        text=self.accepted(result)
        rows=self.run_reader(text,'rows','releases','observed_at','prerelease')
        self.assertEqual(rows.returncode,0)
        self.assertEqual([r.split(b'\t')[0] for r in rows.stdout.splitlines() if r.endswith(b'\tfalse')],[b'456'])

    def test_replace_fetched_facts_and_assets(self):
        changed=dict(self.facts,assets={});changed.pop('title')
        result=self.run_refresh([response({'456':changed})])
        self.assertNotIn('title',result['releases']['456'])
        self.assertEqual(result['releases']['456']['assets'],{})
        self.assertEqual(result['releases']['456']['observed_at'],SEEN)

    def test_scope_completion_and_empty_fetch(self):
        result=self.run_refresh([response()])
        self.assertEqual(result['releases'],self.old['releases'])
        result=self.run_refresh([response(next=False)],page_limit=5,page_size=1)
        self.assertTrue(result['last_success']['history_complete'])
        self.assertEqual(result['last_success']['pages_fetched'],1)
        result=self.run_refresh([response({'457':self.facts}),response({'458':self.facts},next=False,at=LATER)],page_limit='all')
        self.assertEqual(result['releases']['457']['observed_at'],SEEN)
        self.assertEqual(result['releases']['458']['observed_at'],LATER)
        self.assertEqual(result['last_success']['completed_at'],LATER)
        self.assertIn('456',result['releases'])
        never={k:self.old[k] for k in ('format','schema','repository_id','repository')}
        empty=refresh(never,[response(next=False)],attempted_at=ATTEMPT)
        self.accepted(empty);self.assertEqual(empty['releases'],{})

    def test_failure_rolls_back_records_and_observation_metadata(self):
        for options in [dict(page_limit='all',max_requests=1),dict(page_limit=2,max_bytes=150),
                        dict(page_limit=2,max_seconds=15),dict(max_response_bytes=50),
                        dict(max_catalog_bytes=1),dict(max_line_bytes=1)]:
            result=self.run_refresh([response({'457':self.facts}),response({'458':self.facts},next=False,at=LATER)],**options)
            self.assertEqual(result['collection']['reason'],'collection_limit')
            self.assertEqual(result['releases'],self.old['releases'])
            self.assertEqual(result['last_success'],self.old['last_success'])
        result=self.run_refresh([response({'457':self.facts}),response({'457':self.facts},next=False,at=LATER)],page_limit='all')
        self.assertEqual(result['collection']['reason'],'invalid_response')
        result=self.run_refresh([response({'457':self.facts}),response(error='transport')],page_limit='all')
        self.assertEqual(result['releases'],self.old['releases'])
        never={k:self.old[k] for k in ('format','schema','repository_id','repository')}
        result=refresh(never,[],attempted_at=ATTEMPT)
        self.accepted(result);self.assertNotIn('last_success',result);self.assertNotIn('releases',result)

    def test_subset_and_parameter_validation(self):
        configured={123:self.old,124:dict(self.old,repository_id=124)}
        result=collect(configured,{123:[response()]},sources=[123],attempted_at=ATTEMPT)
        self.assertEqual(result[124],configured[124])
        self.assertEqual(collect(configured,{},sources=[],attempted_at=ATTEMPT),configured)
        all_result=collect(configured,{123:[response()],124:[response()]},attempted_at=ATTEMPT)
        self.assertTrue(all(r['last_success']['completed_at']==SEEN for r in all_result.values()))
        report={}
        limited=collect(configured,{123:[response({'457':self.facts})]},attempted_at=ATTEMPT,
                        run_budget=RunBudget(requests=1),report=report)
        self.assertEqual(report,{123:'ok',124:'unattempted_collection_limit'})
        self.assertEqual(limited[124],configured[124])
        for budget in (RunBudget(requests=1),RunBudget(bytes=150),RunBudget(seconds=15)):
            failed=self.run_refresh([response({'457':self.facts}),response({'458':self.facts},next=False,at=LATER)],
                                    page_limit='all',run_budget=budget)
            self.assertEqual(failed['collection']['reason'],'collection_limit')
            self.assertEqual(failed['releases'],self.old['releases'])
        for size in (0,101,True,'100'):
            with self.assertRaises(ValueError):parameters(size,1)
        for limit in (0,-1,False,'1','ALL'):
            with self.assertRaises(ValueError):parameters(100,limit)
        with self.assertRaises(ValueError):collect(configured,{},sources=[999],attempted_at=ATTEMPT)
        with self.assertRaises(ValueError):collect(configured,{},sources=[123,123],attempted_at=ATTEMPT)

    def test_candidate_explicit_reconciliation(self):
        with self.assertRaises(ValueError):self.run_refresh([response()],reconcile=True)
        result=self.run_refresh([response({'457':self.facts},next=False)],page_limit='all',reconcile=True)
        self.assertEqual(set(result['releases']),{'457'})
        result=self.run_refresh([response(next=False)],page_limit='all',reconcile=True)
        self.assertEqual(result['releases'],{})
        result=self.run_refresh([response({'457':self.facts})],page_limit='all',max_requests=1,reconcile=True)
        self.assertEqual(result['releases'],self.old['releases'])

    def test_revised_schema_rejects_inconsistent_scope_and_times(self):
        for mutate in [lambda r:r['collection'].update(page_size=101),
                       lambda r:r['collection'].update(page_limit=0),
                       lambda r:r['collection'].update(reconcile=True),
                       lambda r:r['last_success'].update(page_limit='all'),
                       lambda r:r['last_success'].update(pages_fetched=2),
                       lambda r:r['last_success'].update(page_limit=2),
                       lambda r:r['releases']['456'].pop('observed_at'),
                       lambda r:r['releases']['456'].update(observed_at='2026-11-04T00:00:00Z')]:
            obj=repository();mutate(obj)
            from experiment import document
            run=self.run_reader(document(obj),'get','repository')
            self.assertEqual((run.returncode,run.stdout),(2,b''),run.stderr)

if __name__=='__main__':unittest.main(verbosity=2)
