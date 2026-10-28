"""Read-only consumer contracts; fake HTTP and local child pipes only."""
import copy
from datetime import datetime,timedelta
import io,json,os
from pathlib import Path
import subprocess,sys,time
import unittest
from unittest.mock import patch

import test_storage as fixtures
from test_storage import GEN,REV
from collector import Refusal
from consumer import lookup,main
from public_http import get,REF_URL,RAW_ROOT
from reader import select,StaleObservation,verify_body
from storage import canonical,decode,digest,validate_index

PIN='b'*40
OTHER='c'*40


class ConsumerContract(unittest.TestCase):
    setUpClass=classmethod(fixtures.StorageContract.setUpClass.__func__)
    advance=classmethod(fixtures.StorageContract.advance.__func__)

    def setUp(self):
        self.calls=[]
        self.tree=dict(self.base)
        self.now=datetime.fromisoformat(GEN)

    def fetch(self,url,cap,deadline):
        self.calls.append(url)
        if url==REF_URL:
            return canonical({'ref':'refs/heads/release-catalog','object':{'type':'commit','sha':PIN}})
        prefix=RAW_ROOT+PIN+'/'
        self.assertTrue(url.startswith(prefix))
        raw=self.tree[url[len(prefix):]]
        self.assertLessEqual(len(raw),cap)
        return raw

    def read(self,**kwargs):
        return lookup(self.alias,fetch=self.fetch,utcnow=lambda:self.now,**kwargs)

    def test_resolve_once_and_fetch_only_requested_pinned_pair(self):
        raw,meta=self.read()
        self.assertEqual(len(self.calls),3)
        self.assertEqual(self.calls[0],REF_URL)
        self.assertEqual(raw,self.base['bodies/'+self.rid+'.json'])
        self.assertEqual(meta['commit'],PIN)
        self.assertFalse(meta['stale_accepted'])
        self.assertTrue(all(PIN in url for url in self.calls[1:]))
        self.calls=[]
        self.read(commit=PIN)
        self.assertEqual(len(self.calls),2)
        self.assertNotIn(REF_URL,self.calls)

    def test_branch_movement_never_reresolves_or_mixes_generations(self):
        resolution=[PIN,OTHER]
        def fetch(url,cap,deadline):
            if url==REF_URL:
                self.calls.append(url)
                return canonical({'ref':'refs/heads/release-catalog','object':{'type':'commit','sha':resolution.pop(0)}})
            return self.fetch(url,cap,deadline)
        raw,meta=lookup(self.alias,fetch=fetch,utcnow=lambda:self.now)
        self.assertEqual(meta['commit'],PIN)
        self.assertEqual(self.calls.count(REF_URL),1)
        self.assertEqual(resolution,[OTHER])

    def test_freshness_edge_and_exact_stale_acceptance_before_body_fetch(self):
        index=decode(self.tree['index.json']);obs=index['entries'][self.rid]['observation']
        edge=datetime.fromisoformat(obs['validated_at'])+timedelta(seconds=172800)
        self.now=edge;self.read(commit=PIN)
        self.calls=[];self.now=edge+timedelta(microseconds=1)
        with self.assertRaises(StaleObservation) as stale:self.read(commit=PIN)
        self.assertEqual(len(self.calls),1)
        expected={'commit':PIN,'request_id':self.rid,'sha256':obs['sha256']}
        self.assertEqual(stale.exception.acceptance,expected)
        _,meta=self.read(commit=PIN,stale_acceptance=expected)
        self.assertTrue(meta['stale_accepted'])
        for key,bad in [('commit',OTHER),('request_id','0'*64),('sha256','0'*64)]:
            wrong={**expected,key:bad};self.calls=[]
            with self.assertRaises(StaleObservation):self.read(commit=PIN,stale_acceptance=wrong)
            self.assertEqual(len(self.calls),1)

    def test_expiry_during_body_fetch_and_clock_regression_refuse(self):
        obs=decode(self.tree['index.json'])['entries'][self.rid]['observation']
        edge=datetime.fromisoformat(obs['validated_at'])+timedelta(seconds=172800)
        values=iter([edge,edge+timedelta(microseconds=1)])
        with self.assertRaises(StaleObservation):
            lookup(self.alias,commit=PIN,fetch=self.fetch,utcnow=lambda:next(values))
        values=iter([self.now,self.now-timedelta(seconds=1)])
        with self.assertRaises(Refusal):
            lookup(self.alias,commit=PIN,fetch=self.fetch,utcnow=lambda:next(values))

    def test_future_unmeasured_unavailable_unknown_and_removed_alias_refuse(self):
        for mutation in ('future_publication','future_observation','unmeasured','unavailable','removed','unknown'):
            index=decode(self.base['index.json']);entry=index['entries'][self.rid]
            if mutation=='future_publication':index['generated_at']='2099-01-01T00:00:00+00:00'
            if mutation=='future_observation':entry['observation']['validated_at']='2099-01-01T00:00:00+00:00'
            if mutation=='unmeasured':entry['observation']['received_time_basis']='saved-round-completion-upper-bound'
            if mutation=='unavailable':entry['availability']='unavailable'
            if mutation=='removed':
                manifest=json.loads(index['manifest_json']);manifest['sources'][0]['aliases']=[]
                index['manifest_json']=json.dumps(manifest);index['manifest_sha256']=digest(index['manifest_json'].encode())
                index['aliases'][self.alias]['active']=False
            if mutation=='unknown':entry.update(availability='unknown',observation=None,validators={})
            self.tree['index.json']=canonical(index);self.calls=[]
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):
                self.read(commit=PIN,stale_acceptance={'commit':PIN,'request_id':self.rid,'sha256':'0'*64})
            self.assertEqual(len(self.calls),1)

    def test_integrity_invalid_metadata_and_no_upstream_fallback(self):
        path='bodies/'+self.rid+'.json'
        for change in ('body','path','hash','length','manifest','schema','duplicate'):
            self.tree=dict(self.base);index=decode(self.tree['index.json']);obs=index['entries'][self.rid]['observation']
            if change=='body':self.tree[path]=b'[]'
            if change=='path':obs['path']='../outside'
            if change=='hash':obs['sha256']='0'*64
            if change=='length':obs['bytes']=-1
            if change=='manifest':index['manifest_sha256']='0'*64
            if change=='schema':index['schema_version']=2
            self.tree['index.json']=canonical(index)
            if change=='duplicate':self.tree['index.json']=b'{"schema_version":1,"schema_version":1}'
            self.calls=[]
            with self.subTest(change=change),self.assertRaises(ValueError):self.read(commit=PIN)
            self.assertTrue(all(url.startswith(RAW_ROOT+PIN+'/') for url in self.calls))

    def test_missing_body_does_not_resolve_again_or_fetch_newer_tip(self):
        self.tree.pop('bodies/'+self.rid+'.json')
        with self.assertRaises(KeyError):self.read()
        self.assertEqual(self.calls.count(REF_URL),1)
        self.assertEqual(len(self.calls),3)

    def test_invalid_pin_and_deadline_refuse_before_more_requests(self):
        with self.assertRaises(Refusal):self.read(commit='main')
        self.assertEqual(self.calls,[])
        ticks=iter([0,91])
        with self.assertRaises(Refusal):
            lookup(self.alias,fetch=self.fetch,utcnow=lambda:self.now,monotonic=lambda:next(ticks))
        self.assertEqual(self.calls,[REF_URL])

    def test_cli_outputs_only_exact_bytes_and_no_partial_body_on_refusal(self):
        class Out:
            def __init__(self):self.buffer=io.BytesIO()
        out=Out();err=io.StringIO()
        with patch('consumer.lookup',return_value=(b' []\n',{})),patch('consumer.sys.stdout',out),patch('consumer.sys.stderr',err):
            self.assertEqual(main([self.alias,'--commit',PIN]),0)
        self.assertEqual(out.buffer.getvalue(),b' []\n')
        out=Out();err=io.StringIO();acceptance={'commit':PIN,'request_id':self.rid,'sha256':'a'*64}
        with patch('consumer.lookup',side_effect=StaleObservation(acceptance)),patch('consumer.sys.stdout',out),patch('consumer.sys.stderr',err):
            self.assertEqual(main([self.alias,'--commit',PIN]),1)
        self.assertEqual(out.buffer.getvalue(),b'')
        self.assertEqual(json.loads(err.getvalue())['acceptance'],acceptance)


class PublicHttpContract(unittest.TestCase):
    def factory(self,data,*,hang=False,trickle=False):
        def spawn(command,**kwargs):
            self.command,self.options=command,kwargs
            if trickle:
                script='import sys,time\nfor b in '+repr(data)+':\n sys.stdout.buffer.write(bytes([b]));sys.stdout.buffer.flush();time.sleep(.01)'
            else:
                script='import sys,time;sys.stdout.buffer.write('+repr(data)+');sys.stdout.buffer.flush();'+('time.sleep(5)' if hang else '')
            self.process=subprocess.Popen([sys.executable,'-I','-S','-c',script],**kwargs)
            return self.process
        return spawn

    def test_bounded_exact_body_and_isolated_no_auth_config(self):
        with patch.dict(os.environ,{'GH_TOKEN':'POISON','HTTPS_PROXY':'poison','CURL_HOME':'poison'}):
            raw=get(REF_URL,100,time.monotonic()+1,spawn=self.factory(b'HTTP/1.1 200 OK\r\nContent-Length: 4\r\n\r\n []\n'))
        self.assertEqual(raw,b' []\n')
        self.assertEqual(self.options['env'],{'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'})
        self.assertEqual(self.command[:2],['/usr/bin/curl','-q'])
        self.assertNotIn('POISON',repr(self.command))
        self.assertNotIn('--location',self.command)
        self.assertNotIn('--retry',self.command)
        self.assertIsNotNone(self.process.returncode)
        self.assertTrue(self.process.stdout.closed)

    def test_redirect_malformed_compressed_truncated_and_oversized_refuse(self):
        cases=[b'HTTP/1.1 302 Found\r\nLocation: https://other/\r\n\r\n',
               b'HTTP/1.1 200 OK\r\nContent-Length : 4\r\n\r\nx',
               b'HTTP/1.1 200 OK\r\nContent-Encoding: gzip\r\n\r\nx',
               b'HTTP/1.1 200 OK\r\nContent-Length: 4\r\n\r\nx',
               b'HTTP/1.1 200 OK\r\nContent-Length: 101\r\n\r\n',
               b'HTTP/1.1 200 OK\r\nContent-Length: 0\r\nContent-Length: 0\r\n\r\n',
               b'HTTP/1.1 200 OK\r\nX: '+b'x'*8193+b'\r\n\r\n',
               b'HTTP/1.1 200 OK\r\n'+b'X: '+b'x'*8000+b'\r\n'+(b'X: '+b'x'*8000+b'\r\n')*8+b'\r\n',
               b'HTTP/1.1 200 OK\r\n\r\n'+b'x'*101]
        for data in cases:
            with self.subTest(length=len(data)),self.assertRaises(Refusal):
                get(REF_URL,100,time.monotonic()+1,spawn=self.factory(data))
            self.assertIsNotNone(self.process.returncode)

    def test_deadline_kills_hung_and_trickling_processes(self):
        for data,trickle in [(b'HTTP/1.1 200 OK\r\n\r\n',False),(b'HTTP/1.1 200 OK\r\n\r\nhello',True)]:
            start=time.monotonic()
            with self.assertRaises(Refusal):
                get(REF_URL,100,start+.15,spawn=self.factory(data,hang=not trickle,trickle=trickle))
            self.assertLess(time.monotonic()-start,1)
            self.assertIsNotNone(self.process.returncode)

    def test_arbitrary_hosts_paths_and_expired_requests_start_no_process(self):
        for url in ('https://api.github.com/repos/neovim/neovim/releases',RAW_ROOT+'main/index.json',
                    RAW_ROOT+PIN+'/../../bad','http://api.github.com/'):
            with patch('public_http.subprocess.Popen') as spawn,self.assertRaises(Refusal):
                get(url,100,time.monotonic()+1,spawn=spawn)
            spawn.assert_not_called()
        with patch('public_http.subprocess.Popen') as spawn,self.assertRaises(Refusal):
            get(REF_URL,100,time.monotonic()-1,spawn=spawn)
        spawn.assert_not_called()


if __name__=='__main__':unittest.main()
