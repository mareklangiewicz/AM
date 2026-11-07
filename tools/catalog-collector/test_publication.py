"""Current collection/publication contract, using only disposable local Git."""
import copy
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import host_catalog
import publication
from bounded import normalize
from retention import refresh
from test_yaml_reader import repository, SCHEMA
from yaml_publication import load_local, publish_local, schema_url


class Publication(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)
        self.repo = self.path/'catalog.git'
        self.repo.mkdir()
        publication.git(self.repo, 'init', '--bare', '--quiet', '--template=')

    def publish(self, parent=None, obj=None):
        return publish_local(self.repo, {'app':123}, {'123':obj or repository()},
            schema=SCHEMA, max_file_bytes=2097152, expected_parent=parent)

    def tip(self):
        return publication.git(self.repo, 'rev-parse', publication.REF).decode().strip()

    def test_pinned_round_trip_exact_parent_and_remote_refusal(self):
        first = self.publish()
        changed = copy.deepcopy(repository())
        changed['releases']['456']['tag'] = 'v3'
        second = self.publish(first, changed)
        self.assertEqual(load_local(self.repo, first, max_file_bytes=2097152)[1]['123'], repository())
        self.assertEqual(load_local(self.repo, second, max_file_bytes=2097152)[1]['123'], changed)
        with self.assertRaisesRegex(ValueError, 'stale_parent'):
            self.publish(first)
        self.assertEqual(self.tip(), second)
        publication.git(self.repo, 'remote', 'add', 'origin', 'https://example.invalid/no-network')
        with self.assertRaisesRegex(ValueError, 'remote_publication'):
            self.publish(second)
        self.assertEqual(self.tip(), second)

    def test_delta_publication_reuses_blobs_and_exactly_replaces_tree(self):
        tree = {'apps.yaml':b'original', 'repositories/1.yaml':b'keep',
                'repositories/2.yaml':b'remove'}
        first = publication.publish_tree(self.repo, tree, None)
        replacement = {'apps.yaml':b'changed', 'repositories/1.yaml':b'keep',
                       'repositories/3.yaml':b'add'}
        with patch.object(publication, 'git', wraps=publication.git) as calls:
            second = publication.publish_tree(self.repo, replacement, first)
        writes = [call for call in calls.call_args_list
                  if call.args[1:4] == ('hash-object', '-w', '--stdin')]
        self.assertEqual(len(writes), 2)
        listing = publication.git(self.repo, 'ls-tree', '-r', '--name-only', second)
        self.assertEqual(set(listing.decode().splitlines()), set(replacement))
        for path, raw in replacement.items():
            self.assertEqual(publication.git(self.repo, 'show', second+':'+path), raw)
        with patch.object(publication, 'git', wraps=publication.git) as calls:
            third = publication.publish_tree(self.repo, replacement, second)
        self.assertFalse(any(call.args[1:4] == ('hash-object', '-w', '--stdin')
                             for call in calls.call_args_list))
        self.assertEqual(publication.git(self.repo,'rev-parse',third+'^{tree}'),
                         publication.git(self.repo,'rev-parse',second+'^{tree}'))
        self.assertEqual(publication.git(self.repo,'rev-parse',third+'^').decode().strip(),second)

    def test_local_load_validates_each_document_once_with_safe_loader_fallback(self):
        import yaml_publication as snapshot
        first = self.publish()
        with patch.object(snapshot, 'decode_document', wraps=snapshot.decode_document) as decode:
            accelerated = load_local(self.repo, first, max_file_bytes=2097152)
        self.assertEqual(decode.call_count, 2)
        with patch.object(snapshot, 'SAFE_LOADER', snapshot.yaml.SafeLoader):
            self.assertEqual(load_local(self.repo, first, max_file_bytes=2097152), accelerated)

    def test_invalid_document_and_history_limit_leave_tip_unchanged(self):
        first = self.publish()
        bad = repository(); bad['unexpected'] = True
        with self.assertRaises(ValueError):
            self.publish(first, bad)
        with patch.object(publication, 'HISTORY_CAP', 1):
            with self.assertRaisesRegex(ValueError, 'history_bound'):
                self.publish(first)
        self.assertEqual(self.tip(), first)
        with self.assertRaisesRegex(ValueError, 'invalid_prior_pin'):
            load_local(self.repo, 'HEAD', max_file_bytes=2097152)
        with self.assertRaisesRegex(ValueError, 'yaml_prior_byte_bound'):
            load_local(self.repo, first, max_file_bytes=1)

    def test_git_environment_ignores_injected_repository_config_and_credentials(self):
        with patch.dict(os.environ, {'GIT_DIR':'/not-the-repository',
                'GIT_INDEX_FILE':'/not-the-index','GIT_CONFIG_COUNT':'1',
                'GIT_CONFIG_KEY_0':'core.bare','GIT_CONFIG_VALUE_0':'false',
                'GH_TOKEN':'secret','GIT_ASKPASS':'/not-a-command'}):
            first = self.publish()
            self.assertEqual(load_local(self.repo,first,max_file_bytes=2097152)[0],{'app':123})
            env = publication.environment()
            self.assertNotIn('GH_TOKEN', env)
            self.assertNotIn('GIT_ASKPASS', env)
            self.assertNotIn('GIT_DIR', env)
            self.assertEqual(env['GIT_TERMINAL_PROMPT'],'0')

    def test_bounded_process_refuses_output_time_and_nonzero_exit(self):
        env = publication.environment()
        for code,cap,seconds in [('print("too long")',2,5),
                ('import time; time.sleep(5)',100,.05),('raise SystemExit(9)',100,5)]:
            with self.subTest(code=code), self.assertRaisesRegex(ValueError,'delivery_command_refusal'):
                publication.bounded([sys.executable,'-c',code],env=env,cap=cap,seconds=seconds)
        self.assertEqual(publication.bounded([sys.executable,'-c','print("ok")'],
            env=env,cap=3),b'ok\n')

    def test_two_new_enrollments_publish_saved_facts_and_select_through_reader(self):
        import hashlib
        import tarfile
        research = host_catalog.ROOT/'docs/track/release-catalog/research'
        receipt = json.loads((research/'two-candidate-upstream-evidence.json').read_text())
        archive = research/receipt['evidence_archive']
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(), receipt['evidence_archive_sha256'])
        rows, sources = host_catalog.configuration()
        # The historical pair remains enrolled as later batches are added.
        self.assertGreaterEqual(len(rows), 23)
        self.assertGreaterEqual(len(sources), 21)
        expected_ids = {'20x':1152028865, '2fac':1337965664}
        old_rows = [row for row in rows if row['app'] not in expected_ids]
        prior = {}
        stamp = '2026-11-06T01:00:00Z'
        for row in old_rows:
            rid = str(row['repository_id'])
            seed = dict(format=2,schema=SCHEMA,repository_id=int(rid),repository=row['repository'])
            prior[rid] = refresh(seed,[dict(received_at=stamp,releases={},has_next=False,
                bytes=2,seconds=0)],attempted_at=stamp,max_catalog_bytes=2097152)
        first = publish_local(self.repo,{r['app']:r['repository_id'] for r in old_rows},prior,
                              schema=SCHEMA,max_file_bytes=2097152,expected_parent=None)
        candidate = copy.deepcopy(prior)
        with tarfile.open(archive) as evidence:
            for app, rid in expected_ids.items():
                row = next(r for r in rows if r['app']==app)
                self.assertEqual(row['repository_id'], rid)
                source = next(r for r in receipt['receipts'] if r['app']==app and r['kind']=='releases')
                raw = evidence.extractfile(app+'-releases.json').read()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), source['sha256'])
                observed = source['observed_at'][:19]+'Z'
                seed = dict(format=2,schema=SCHEMA,repository_id=rid,repository=row['repository'])
                # The real saved page is per_page=30: preserve its Link evidence,
                # rather than misrepresenting it as a complete 100-release response.
                candidate[str(rid)] = refresh(seed,[dict(received_at=observed,
                    releases=normalize(json.loads(raw),30),has_next=app=='20x',bytes=len(raw),seconds=0)],
                    attempted_at=observed,page_size=30,page_limit=1,max_catalog_bytes=2097152)
                self.assertEqual(candidate[str(rid)]['collection']['status'], 'ok')
                self.assertEqual(candidate[str(rid)]['last_success']['history_complete'], app=='2fac')
        second = publish_local(self.repo,{r['app']:r['repository_id'] for r in rows},candidate,
                               schema=SCHEMA,max_file_bytes=2097152,expected_parent=first)
        apps, after = load_local(self.repo,second,max_file_bytes=2097152)
        self.assertEqual(apps,{r['app']:r['repository_id'] for r in rows})
        self.assertEqual({rid:after[rid] for rid in prior},prior)
        self.assertEqual(set(after)-set(prior),set(map(str,expected_ids.values())))
        for app,rid in expected_ids.items():
            raw = publication.git(self.repo,'show',second+':repositories/'+str(rid)+'.yaml')
            self.assertLess(len(raw),host_catalog.FILE_CAP)
            document = self.path/(str(rid)+'.yaml');document.write_bytes(raw)
            result = subprocess.run(['sh',str(host_catalog.ROOT/'modules/catalog-yaml-reader.am'),
                'asset_facts',str(document)],capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode,0,result.stderr)
            expected = next(r['narrow_declaration_url'] for r in receipt['selection_comparison'] if r['app']==app)
            env = dict(os.environ,LC_ALL='C',AM_YAML_RECIPE='x86_64/'+app,
                AM_YAML_REPOSITORY=str(rid),AM_YAML_NOW=after[str(rid)]['observed_at'],AM_YAML_PIN=second)
            for command in (['mawk'], ['gawk'], ['busybox','awk']):
                with self.subTest(app=app,command=command):
                    selected = subprocess.run([*command,'-f',str(host_catalog.ROOT/'modules/catalog-yaml-policy.am')],
                        input=result.stdout,capture_output=True,text=True,env=env,timeout=10)
                    self.assertEqual(selected.returncode,0,selected.stderr)
                    self.assertEqual(selected.stdout.splitlines()[-1],expected)
        self.assertEqual(load_local(self.repo,first,max_file_bytes=2097152)[0],
                         {r['app']:r['repository_id'] for r in old_rows})

    def test_current_workflow_batch_publish_and_failure_preserves_source_facts(self):
        rows, sources = host_catalog.configuration()
        previous = {}
        evidence = self.path/'responses'; evidence.mkdir()
        now = '2026-11-05T20:00:00Z'
        for rid, name in sources.items():
            seed = dict(format=2,schema=schema_url('a'*40),repository_id=int(rid),repository=name)
            previous[rid] = refresh(seed,[dict(received_at=now,releases={},has_next=False,
                bytes=2,seconds=0)],attempted_at=now,max_catalog_bytes=2097152)
            (evidence/(rid+'-releases.json')).write_text('[]')
            (evidence/(rid+'-receipt.txt')).write_text(now)
        first = publish_local(self.repo,{r['app']:r['repository_id'] for r in rows},previous,
            schema=schema_url('a'*40),max_file_bytes=2097152,expected_parent=None)
        report = self.path/'report.json'
        args = ['host_catalog.py','--repo',str(self.repo),'--parent',first,
                '--evidence',str(evidence),'--report',str(report),'--batch-size','500']
        with patch.object(sys,'argv',args), patch('urllib.request.urlopen',side_effect=AssertionError('network')), redirect_stdout(io.StringIO()):
            host_catalog.main()
        second = self.tip()
        receipt = json.loads(report.read_text())
        self.assertEqual(receipt['pin'],second)
        self.assertEqual(receipt['metrics']['requests'],0)
        self.assertEqual(receipt['metrics']['attempted_sources'],len(sources))
        self.assertEqual(receipt['metrics']['successful_sources'],len(sources))
        self.assertEqual(receipt['metrics']['unattempted_sources'],0)
        self.assertEqual(receipt['metrics']['stop_reason'],'complete')
        self.assertLessEqual(receipt['metrics']['history_guard_bytes'],receipt['metrics']['history_cap'])
        apps, observed = load_local(self.repo,second,max_file_bytes=2097152)
        self.assertEqual(len(apps),len(rows));self.assertEqual(set(observed),set(sources))
        # Batch mode isolates a malformed upstream source while preserving that
        # source's observations, rather than failing the entire publication.
        broken = str(json.loads(report.read_text())['sources'][0]['repository_id'])
        before = observed[broken]
        (evidence/(broken+'-releases.json')).write_text('[invalid')
        args[args.index('--parent')+1]=second
        with patch.object(sys,'argv',args), redirect_stdout(io.StringIO()):
            host_catalog.main()
        after = load_local(self.repo,self.tip(),max_file_bytes=2097152)[1][broken]
        self.assertTrue(any(row['repository_id']==int(broken) and row['status']=='failed'
                            for row in json.loads(report.read_text())['sources']))
        # Oldest-attempt rotation may leave this source untouched in the next
        # run; either way, no unsuccessful attempt changes release observations.
        self.assertEqual(after['releases'],before['releases'])
        self.assertEqual(after['observed_at'],before['observed_at'])
        workflow = (host_catalog.ROOT/'.github/workflows/catalog.yml').read_text()
        self.assertIn('tools/catalog-collector/host_catalog.py',workflow)
        self.assertNotIn('--bootstrap',workflow)
