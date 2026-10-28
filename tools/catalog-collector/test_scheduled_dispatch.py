"""Offline dispatch orchestration; no real gh, credentials or network."""
import copy
import json
import unittest
from collector import Refusal
from scheduled_dispatch import dispatch, CRON

REV = 'a'*40
PIN = 'b'*40


class ScheduledDispatch(unittest.TestCase):
    def setUp(self):
        self.context = dict(repository='mareklangiewicz/AM', event='schedule', schedule=CRON,
            ref='refs/heads/main-marek', run_attempt='1', sha=REV, workflow_sha=REV,
            approved_revision=REV)
        self.responses = [dict(default_branch='main-marek'),dict(object=dict(sha=REV)),
            dict(total_count=3,workflows=[
                dict(path='.github/workflows/catalog-collector.yml',state='active'),
                dict(path='.github/workflows/catalog-schedule.yml',state='active'),
                dict(path='.github/workflows/lister.yml',state='disabled_manually')]),
            dict(workflow_runs=[dict(status='completed')]), dict(object=dict(sha=PIN))]
        self.calls=[]

    def execute(self,args):
        self.calls.append(args)
        if args[0]=='workflow':return b''
        return json.dumps(self.responses.pop(0)).encode()

    def invoke(self,context=None):
        return dispatch(context or self.context,execute=self.execute)

    def test_exact_pin_and_manifest_are_forwarded_once(self):
        result=self.invoke()
        self.assertEqual(result['previous_publication'],PIN)
        submitted=[c for c in self.calls if c[0]=='workflow']
        self.assertEqual(len(submitted),1)
        self.assertIn('approved_revision='+REV,submitted[0])
        self.assertIn('previous_publication='+PIN,submitted[0])

    def test_context_revision_and_rerun_refuse_before_api(self):
        for key,value in [('repository','other/AM'),('event','push'),('schedule','* * * * *'),('schedule','17 * * * *'),
                ('ref','refs/heads/main'),('run_attempt','2'),('sha','c'*40),
                ('workflow_sha','c'*40),('approved_revision','')]:
            with self.subTest(key=key):
                context={**self.context,key:value}
                with self.assertRaises(Refusal):self.invoke(context)
                self.assertEqual(self.calls,[])

    def test_remote_drift_active_work_and_invalid_pin_never_dispatch(self):
        changes=[(0,dict(default_branch='main')),(1,dict(object=dict(sha='c'*40))),
            (2,dict(total_count=0,workflows=[])),
            (3,dict(workflow_runs=[dict(status='in_progress')])),
            (4,dict(object=dict(sha='bad')))]
        original=copy.deepcopy(self.responses)
        for index,value in changes:
            with self.subTest(index=index):
                self.responses=copy.deepcopy(original);self.responses[index]=value;self.calls=[]
                with self.assertRaises(Refusal):self.invoke()
                self.assertFalse(any(c[0]=='workflow' for c in self.calls))

    def test_failed_or_ambiguous_dispatch_is_not_retried(self):
        def fail(args):
            if args[0]=='workflow':
                self.calls.append(args)
                raise TimeoutError('ambiguous dispatch')
            return self.execute(args)
        with self.assertRaises(TimeoutError):
            dispatch(self.context,execute=fail)
        self.assertEqual(len([c for c in self.calls if c[0]=='workflow']),1)
