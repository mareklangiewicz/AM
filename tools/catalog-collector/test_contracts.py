"""Shared wire fixtures: shell, browser, editor schemas, writer and pure merges."""
import copy
import hashlib
import json
import os
import shutil
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import jsonschema

import contracts as c
from contracts import header,encode,decode,source,expand_release
from retention_v3 import merge
from test_yaml_reader import repository
from publication import git,publish_tree,REF
import collection_interface as interface
import host_catalog as host
from provenance import Evaluator,review_url

ROOT=c.ROOT
FIXTURES=ROOT/'tools/catalog-contract/fixtures'
PIN='a'*40
OLD='2026-11-03T01:00:00Z'
NEW='2026-11-08T01:00:00Z'


def sample():
    record=repository()['releases']['456'];record.pop('observed_at')
    record['assets']['790']=dict(name='base',url='https://github.com/example/app/releases/download/v2.0.0/',size=1,content_type='Text/Plain; charset=UTF-8')
    record['assets']['9007199254740993']=dict(name='中文 \\N?%2F',url='https://github.com/example/app/releases/download/v2.0.0/中文?x=%2F#y',size=9223372036854775807,content_type='application/octet-stream')
    record['assets']['9223372036854775807']=dict(name='last',url='https://elsewhere.example/exact?x=a%2Fb',size=0,content_type='application/zip')
    return source(None,dict(received_at=OLD,releases={'9007199254740993':record},history_complete=False),rid='9007199254740993',repository='example/app',revision=PIN)


def unknown(): return dict(state='unknown')
def known(value): return dict(state='known',value=value)


def documents():
    inputs={key:PIN for key in ('source','policy','recipes','rules','schemas')}
    docs={
      'catalog':dict(header('catalog',PIN),inputs=inputs,producer=dict(id=123,attempt=2),retention='32-plus-stable-exact-tag-v1'),
      'apps':dict(header('apps',PIN),apps={'1':'repositories/example.yaml','10':'repositories/example.yaml','2':'repositories/example.yaml','example':'repositories/example.yaml','example-nightly':'repositories/example.yaml'}),
      'repository':sample(),
      'provenance':dict(header('provenance',PIN),apps={'example':{'x86_64':dict(repository_id=9007199254740993,availability='unknown',classification='unknown')}}),
      'summary':dict(header('summary',PIN),run=dict(id=123,attempt=2),inputs=inputs,input_catalog=PIN,started_at=OLD,reported_at=NEW,collection='partial',validation='ok',publication=dict(state='not_attempted'),compatibility_publication=dict(state='not_attempted'),counts={k:known(v) for k,v in zip(('enrolled','selected','attempted','successful','failed','unknown','unattempted','deferred'),(5,4,3,2,1,0,1,1))},stop_reason='quota',metrics={k:unknown() for k in c.DEFINITIONS['metrics']['properties']},budgets=dict(requests=500,bytes=536870912,acquisition_milliseconds=900000,document_bytes=c.FILE_CAP),actions_url='https://github.com/mareklangiewicz/AM/actions/runs/123',recent_runs_url='https://github.com/mareklangiewicz/AM/actions/workflows/catalog.yml'),
      'status':dict(header('status',PIN),schemas=PIN,last_report='runs/123-2/summary.yaml',reported_at=NEW,last_confirmed_publication=dict(state='confirmed',commit=PIN),summaries={'123-2':'runs/123-2/summary.yaml'},details={'123-2':NEW}),
      'source':dict(header('source',PIN),run=dict(id=123,attempt=2),input_catalog=PIN,repository_id=9007199254740993,repository='example/app',outcome='failed',reason='source_validation',attempted_at=OLD),
      'statistics':dict(header('statistics',PIN),measured_at=NEW,freshness=dict(catalog=PIN,evaluated_at=NEW,**{k:unknown() for k in ('under_24h','from_24_to_48h','at_least_48h','no_success','unknown')}),days={'2026-11-08':dict(reported_attempts=1,successful_sources=2,failed_sources=1,first_report=NEW,last_report=NEW)})}
    return docs


class Contracts(unittest.TestCase):
    def shell(self,raw,operation='validate',*keys):
        with tempfile.NamedTemporaryFile() as f:
            f.write(raw);f.flush()
            return subprocess.run(['sh',str(ROOT/'modules/catalog-contract-reader.am'),operation,f.name,*keys],capture_output=True)

    def browser(self,raw):
        js="import {parseDocument} from './tools/catalog-contract/reader.mjs';let s='';for await(const b of process.stdin)s+=b;try{parseDocument(s)}catch(e){console.error(e.message);process.exitCode=2}"
        return subprocess.run(['node','--input-type=module','-e',js],input=raw,capture_output=True,cwd=ROOT)

    def test_shared_positive_negative_fixtures(self):
        for path in sorted(FIXTURES.glob('*.yaml')):
            raw=path.read_bytes(); valid=not path.name.startswith('bad-')
            with self.subTest(path=path.name):
                shell=self.shell(raw);browser=self.browser(raw)
                self.assertEqual(shell.returncode,0 if valid else 2,shell.stderr)
                self.assertEqual(browser.returncode,0 if valid else 2,browser.stderr)
                if valid:
                    obj=decode(raw);self.assertEqual(encode(obj),raw)
                    schema=json.loads((ROOT/'schemas/catalog'/f"{obj['kind']}.schema.json").read_text())
                    jsonschema.Draft202012Validator(schema).validate(obj)
                else:
                    with self.assertRaises(ValueError):decode(raw)
                    if path.stem in ('bad-null','bad-path','bad-unknown-field','bad-overflow','bad-version','bad-unknown-kind','bad-schema'):
                        import yaml
                        obj=yaml.safe_load(raw)
                        kind='repository' if path.stem=='bad-unknown-kind' else obj['kind']
                        schema=json.loads((ROOT/'schemas/catalog'/f'{kind}.schema.json').read_text())
                        self.assertFalse(jsonschema.Draft202012Validator(schema).is_valid(obj))

    def test_portable_awk_fixture_parity(self):
        for command in (['mawk'],['gawk'],['busybox','awk']):
            self.assertIsNotNone(shutil.which(command[0]))
            for path in sorted(FIXTURES.glob('*.yaml')):
                with self.subTest(awk=command,fixture=path.name):
                    result=subprocess.run([*command,'-f',str(ROOT/'modules/catalog-contract-tables.am'),'-f',str(ROOT/'modules/catalog-contract-parser.am')],input=path.read_bytes(),capture_output=True,env=dict(os.environ,LC_ALL='C',AM_YAML_OPERATION='validate'))
                    self.assertEqual(result.returncode,2 if path.name.startswith('bad-') else 0,result.stderr)

    def test_exact_query_and_reconstructed_facts(self):
        doc=sample();raw=encode(doc);rid='9007199254740993';aid='9007199254740993'
        release=expand_release(doc['releases'][rid],doc['observed_at'])
        for field,expected in (('url',release['assets'][aid]['url']),('media_type','application/octet-stream'),('content_type','application/octet-stream'),('size','9223372036854775807')):
            result=self.shell(raw,'get','releases',rid,'assets',aid,field)
            self.assertEqual((result.returncode,result.stdout),(0,expected.encode()),result.stderr)
        result=self.shell(raw,'get','releases',rid,'observed_at')
        self.assertEqual(result.stdout,OLD.encode())
        self.assertEqual(self.shell(raw,'get','releases',rid,'assets',aid,'digest').returncode,3)
        bad=raw+b'unknown: "invalid"\n'
        result=self.shell(bad,'get','repository_id')
        self.assertEqual((result.returncode,result.stdout),(2,b''))
        js="import {parseDocument,releaseFacts} from './tools/catalog-contract/reader.mjs';let s='';for await(const b of process.stdin)s+=b;let d=parseDocument(s),r=releaseFacts(d,'9007199254740993');console.log(d.repository_id.toString());console.log(r.assets['9007199254740993'].url);console.log(r.assets['9007199254740993'].size.toString());"
        result=subprocess.run(['node','--input-type=module','-e',js],input=raw,capture_output=True,cwd=ROOT)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout.decode().splitlines(),['9007199254740993',release['assets'][aid]['url'],'9223372036854775807'])

    def test_retention_replacement_timestamp_fallback_and_failure_atomicity(self):
        records={str(i):dict(tag='v'+str(i),url='https://example.org/release',created_at=f'2026-10-{i%28+1:02d}T00:00:00Z',prerelease=True,assets={},observed_at=OLD) for i in range(1,41)}
        records['1']['prerelease']=False
        before=dict(observed_at=OLD,releases=records);original=copy.deepcopy(before)
        result=merge(before,{},completed_at=NEW)
        self.assertEqual(len(result),33);self.assertIn('1',result)
        self.assertEqual(before,original)
        fetched={'99':dict(records['1'],observed_at=NEW)}
        result=merge(before,fetched,completed_at=NEW)
        self.assertNotIn('1',result);self.assertIn('99',result)
        with self.assertRaises(ValueError):merge(before,dict(fetched,**{'100':fetched['99']}),completed_at=NEW)
        bad=copy.deepcopy(before);del bad['releases']['1']['created_at']
        with self.assertRaises((ValueError,TypeError)):merge(bad,{},completed_at=NEW)
        self.assertEqual(before,original)

    def test_custom_review_changed_inputs_and_no_recipe_execution(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);git(root,'init','--quiet','--template=')
            recipe=root/'programs/x86_64/example';recipe.parent.mkdir(parents=True)
            marker=root/'executed'
            recipe.write_text('#!/bin/sh\ntouch '+str(marker)+'\n')
            (root/'modules').mkdir();(root/'modules/test.am').write_text('inert dependency\n')
            git(root,'add','programs','modules');git(root,'commit','-qm','Fixture')
            revision=git(root,'rev-parse','HEAD').decode().strip()
            inputs={key:revision for key in ('source','policy','recipes','rules','schemas')}
            evaluator=Evaluator(root,inputs,NEW)
            unknown=evaluator.classify('example','x86_64',1)
            self.assertEqual(unknown['classification'],'unknown')
            review=dict(recipe=unknown['recipe'],recipe_sha256=hashlib.sha256(recipe.read_bytes()).hexdigest(),rules=revision,description='Reviewed custom fixture',dependencies={})
            custom=evaluator.classify('example','x86_64',1,review=review)
            self.assertEqual(custom['classification'],'custom')
            review['rules']='b'*40
            self.assertEqual(evaluator.classify('example','x86_64',1,review=review)['classification'],'unknown')
            self.assertFalse(marker.exists())

    def test_tree_identity_and_channel_whitelists(self):
        d=documents();tree={k+'.yaml':encode(d[k]) for k in ('catalog','apps','provenance')}
        tree['repositories/example.yaml']=encode(d['repository'])
        c.validate_tree(tree)
        for path,raw in [('status.yaml',encode(d['status'])),('repositories/../escape.yaml',encode(d['repository'])),('repositories/duplicate.yaml',encode(d['repository']))]:
            with self.subTest(path=path),self.assertRaises(ValueError):c.validate_tree(dict(tree,**{path:raw}))
        status={'status.yaml':encode(d['status']),'runs/123-2/summary.yaml':encode(d['summary']),'runs/123-2/sources/example.yaml':encode(d['source']),'statistics.yaml':encode(d['statistics'])}
        c.validate_tree(status,'status')
        with self.assertRaises(ValueError):c.validate_tree(status)
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp);(path/'catalog.yaml').symlink_to('/etc/passwd')
            with self.assertRaises(ValueError):c.read_directory(path)

    def test_collection_one_acquisition_two_independent_parents_no_ref_advance(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);repo=root/'repo';git(root,'init','--bare','--quiet','--template=',str(repo))
            old=repository();old['repository_id']=123
            from yaml_publication import candidate_tree,schema_url
            legacy=candidate_tree({'example':123},{'123':old},schema=schema_url(PIN),max_file_bytes=host.FILE_CAP)
            parent=publish_tree(repo,legacy,None)
            evidence=root/'saved';evidence.mkdir()
            (evidence/'123-releases.json').write_text('[]');(evidence/'123-receipt.txt').write_text(NEW)
            registry=root/'names.json';registry.write_text(json.dumps(dict(active={'123':'example'},retired=[])))
            rows=[dict(app='example',repository_id=123,repository='example/app')]
            with patch.object(interface,'verify_checkout_inputs'),patch.object(host,'configuration',return_value=(rows,{'123':'example/app'})),patch.object(host,'_open',side_effect=AssertionError('offline network')):
                interface.main(['collect','--repo',str(repo),'--parent',parent,'--evidence',str(evidence),'--output',str(root/'output'),'--registry',str(registry),'--run-id','123'])
            self.assertEqual(git(repo,'rev-parse',REF).decode().strip(),parent)
            self.assertEqual(json.loads((root/'output/report.json').read_text())['acquisition']['http_attempts'],0)
            for channel in ('format-2','format-3'):
                interface.main(['validate','--candidate',str(root/'output'/channel),'--channel',channel])
            current=c.read_directory(root/'output/format-3')
            self.assertEqual(decode(current['repositories/example.yaml'])['observed_at'],NEW)
            # Empty successful new scope retains no prior v3 records at bootstrap;
            # the independent v2 parent still contains its unfetched release.
            self.assertEqual(decode(current['repositories/example.yaml'])['releases'],{})
            import yaml
            self.assertIn('456',yaml.safe_load((root/'output/format-2/repositories/123.yaml').read_bytes())['releases'])
            # An exceptional target overflow preserves its own exact prior bytes,
            # independently of the compatibility source result.
            v3repo=root/'v3.git';git(root,'init','--bare','--quiet','--template=',str(v3repo))
            previous_doc=sample();previous_doc['repository_id']=123
            current['repositories/example.yaml']=encode(previous_doc)
            current['provenance.yaml']=encode(dict(header('provenance',PIN),apps={}))
            v3pin=publish_tree(v3repo,current,None)
            with patch.object(interface,'verify_checkout_inputs'),patch.object(host,'configuration',return_value=(rows,{'123':'example/app'})),patch.object(host,'_open',side_effect=AssertionError('offline network')),patch.object(c,'source',side_effect=ValueError('document_overflow')):
                interface.main(['collect','--repo',str(repo),'--parent',parent,'--v3-repo',str(v3repo),'--v3-parent',v3pin,'--evidence',str(evidence),'--output',str(root/'overflow'),'--registry',str(registry),'--run-id','123'])
            result=c.read_directory(root/'overflow/format-3')
            self.assertEqual(result['repositories/example.yaml'],current['repositories/example.yaml'])
            outcome=json.loads((root/'overflow/report.json').read_text())
            self.assertEqual(outcome['sources'][0]['reason'],'document_overflow')
            self.assertEqual(outcome['target_counts']['successful'],0)
            self.assertEqual(git(v3repo,'rev-parse',REF).decode().strip(),v3pin)
            with self.assertRaises(ValueError):
                interface.main(['validate','--candidate',str(root/'output/format-3'),'--expected-rules','b'*40])


    def test_normalization_time_fallback_is_explicit_and_generated_files_are_stable(self):
        from bounded import normalize
        raw=[dict(id=1,draft=False,tag_name='v1',html_url='https://example.org/v1',published_at=None,created_at=OLD,prerelease=False,assets=[])]
        with self.assertRaises((TypeError,ValueError)):normalize(raw,100)
        normalized=normalize(raw,100,allow_missing_published=True)
        self.assertNotIn('published_at',normalized['1'])
        self.assertEqual(source(None,dict(received_at=NEW,releases=normalized,history_complete=True),rid=1,repository='example/app',revision=PIN)['releases']['1']['created_at'],OLD)
        paths=[*sorted((ROOT/'schemas/catalog').glob('*.json')),ROOT/'modules/catalog-contract-tables.am',ROOT/'tools/catalog-contract/definitions.json',ROOT/'tools/catalog-contract/definitions.mjs']
        before={p:p.read_bytes() for p in paths}
        subprocess.run(['python3',str(ROOT/'tools/catalog-contract/build.py')],check=True)
        self.assertEqual(before,{p:p.read_bytes() for p in paths})

    def test_provenance_positive_predicates_and_catalog_only_recipe(self):
        revision=git(ROOT,'rev-parse','HEAD').decode().strip()
        evaluator=Evaluator(ROOT,{key:revision for key in ('source','policy','recipes','rules','schemas')},NEW)
        shared=evaluator.classify('20x','x86_64',1152028865)
        self.assertEqual(shared['classification'],'shared')
        self.assertIn('/blob/'+revision+'/programs/x86_64/20x',review_url(shared))
        template=evaluator.classify('actual','x86_64',0)
        self.assertEqual(template['classification'],'template')
        existing=evaluator.classify('ageha-editor','x86_64',1016549971)
        self.assertEqual(existing['availability'],'present')
        absent=evaluator.classify('not-a-real-recipe-012345','aarch64',1)
        self.assertEqual((absent['availability'],absent['classification']),('absent','unknown'))
        custom=evaluator.classify('am','x86_64',1)
        # An unmatched file never acquires the custom verdict by default.
        self.assertNotEqual(custom['classification'],'custom')


if __name__=='__main__':unittest.main()
