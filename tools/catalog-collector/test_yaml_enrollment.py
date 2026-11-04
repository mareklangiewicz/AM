"""Real static AM enrollment and local pinned-state integration, without HTTP."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from collector import Refusal
from test_collector import Credential, FakeTransport, response
from test_yaml_adapter import ClockNow, ROOT, RAW
from yaml_adapter import schema_url
from yaml_enrollment import collect_pinned, enroll, prepare_pinned, shared_recipes
from yaml_publication import decode_document, git, load_local, publish_local

CAP = 2*1024*1024
REV = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', '2f9292218']).decode().strip()


class Enrollment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.recipes = list(shared_recipes(ROOT))
        obj = json.loads(RAW)
        obj['schema'] = 2
        obj['sources'] = [obj['sources'][0], obj['sources'][2]]
        cls.raw = json.dumps(obj).encode()
        cls.small_recipes = [(p,b) for p,b in cls.recipes if p in
                             ('programs/x86_64/obsidian', 'programs/x86_64/nvim')]

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.repo = Path(self.directory.name)/'git'
        self.repo.mkdir()
        git(self.repo, 'init', '--bare')

    def collect(self, pin=None, *, raw=None, recipes=None, scripts=None, **scope):
        clock = ClockNow()
        transport = FakeTransport(clock, scripts or [])
        options = dict(max_run_requests=100, max_run_bytes=8_000_000)
        options.update(scope)
        tree, report = collect_pinned(self.repo, pin, raw or self.raw, 1,
            self.small_recipes if recipes is None else recipes, lambda value: transport,
            clock, Credential(), source_revision=REV, max_file_bytes=CAP, **options)
        return tree, report, transport

    def seed(self):
        tree, report, _ = self.collect()
        docs = {p: decode_document(b,CAP) for p,b in tree.items()}
        apps = docs.pop('apps.yaml')['apps']
        repos = {p.split('/')[1][:-5]: obj for p,obj in docs.items()}
        return publish_local(self.repo, apps, repos, schema=schema_url(REV),
                             max_file_bytes=CAP, expected_parent=None)

    def test_real_enrollment_is_scoped_and_uses_actual_names(self):
        apps, identities, report = enroll(RAW, 1, self.recipes, source_revision=REV)
        self.assertEqual((len(apps),len(identities),len(report['recipes']),len(report['excluded'])),
                         (255,49,475,987))
        self.assertEqual(apps['criteria1d'],286458735)
        self.assertEqual(apps['obsidian'],262342594)
        self.assertEqual(apps['nvim'],16408992)
        self.assertEqual(identities['16408992']['repository'],'neovim/neovim')
        self.assertNotIn('wezterm',apps)  # Its current recipe is unmarked legacy code.
        self.assertTrue(all('collection' not in obj for obj in identities.values()))

    def test_complete_real_bootstrap_creates_no_synthetic_observations(self):
        tree, report, transport = self.collect(raw=RAW, recipes=self.recipes)
        self.assertEqual(len(transport.calls),49)
        self.assertEqual(len(tree),50)
        self.assertEqual(len(decode_document(tree['apps.yaml'],CAP)['apps']),255)
        self.assertIsNone(report['previous_publication'])
        for path,body in tree.items():
            if path != 'apps.yaml':
                obj = decode_document(body,CAP)
                self.assertEqual(obj['releases'],{})
                self.assertEqual(obj['collection']['status'],'ok')
                self.assertTrue(obj['observed_at'].startswith('2026-11-04T13:00:'))

    def test_incomplete_bootstrap_refuses_instead_of_inventing_attempts(self):
        with self.assertRaisesRegex(Refusal,'incomplete_bootstrap') as caught:
            self.collect(scripts=[response(status=429)])
        self.assertEqual(caught.exception.report['bootstrap_unattempted_repositories'], ['16408992'])
        self.assertEqual(caught.exception.report['not_attempted_repositories'], ['16408992'])
        self.assertEqual(git(self.repo,'for-each-ref'),b'')
        with self.assertRaisesRegex(Refusal,'incomplete_bootstrap'):
            self.collect(sources=['262342594'])

    def test_attempted_bootstrap_failure_is_honest_and_publishable_locally(self):
        tree, report, _ = self.collect(scripts=[response(body=b'{'),response()])
        obj = decode_document(tree['repositories/262342594.yaml'],CAP)
        self.assertEqual(obj['collection']['status'],'failed')
        self.assertNotIn('observed_at',obj)
        self.assertNotIn('last_success',obj)
        self.assertNotIn('releases',obj)

    def test_pinned_refresh_keeps_unselected_bytes_and_does_not_move_ref(self):
        pin = self.seed()
        before = git(self.repo,'show',pin+':repositories/16408992.yaml')
        tree, report, transport = self.collect(pin,sources=['262342594'])
        self.assertEqual(tree['repositories/16408992.yaml'],before)
        self.assertEqual(report['previous_publication'],pin)
        self.assertEqual(len(transport.calls),1)
        self.assertEqual(git(self.repo,'rev-parse','refs/heads/catalog').decode().strip(),pin)

    def test_exact_pin_survives_moving_tip_and_retains_old_aliases(self):
        pin = self.seed()
        apps, repos = load_local(self.repo,pin,max_file_bytes=CAP)
        changed = copy.deepcopy(repos)
        changed['16408992']['repository'] = 'renamed/display'
        tip = publish_local(self.repo,apps,changed,schema=schema_url(REV),max_file_bytes=CAP,
                            expected_parent=pin)
        self.assertNotEqual(pin,tip)
        value, appmap, loaded, evidence = prepare_pinned(self.repo,pin,self.raw,1,[],
            source_revision=REV,max_file_bytes=CAP,sources=['262342594'])
        self.assertEqual(loaded['16408992']['repository'],'neovim/neovim')
        self.assertEqual(appmap,apps)
        with self.assertRaises(ValueError):
            prepare_pinned(self.repo,'refs/heads/catalog',self.raw,1,self.small_recipes,
                           source_revision=REV,max_file_bytes=CAP)

    def test_conflicting_cross_arch_names_and_nonstatic_recipe_refuse(self):
        body = dict(self.small_recipes)['programs/x86_64/obsidian']
        wrong = body.replace(b'obsidianmd/obsidian-releases',b'neovim/neovim')
        with self.assertRaisesRegex(Refusal,'conflicting_app_identity'):
            enroll(self.raw,1,[('programs/x86_64/obsidian',body),
                              ('programs/aarch64/obsidian',wrong)],source_revision=REV)
        for bad in (body.replace(b'APP=obsidian',b'APP=$(anything)'),
                    body+b'CATALOG_ALIAS="duplicate"\n'):
            with self.assertRaises(Refusal):
                enroll(self.raw,1,[('programs/x86_64/obsidian',bad)],source_revision=REV)

    def test_saved_real_100_release_response_bootstrap_and_pinned_refresh(self):
        from datetime import datetime, timedelta
        import hashlib
        saved = ROOT/'docs/track/release-catalog/research/appimage-batch-20261102/release-07'
        report = json.loads((saved/'report.json').read_bytes())
        body = (saved/'body.json').read_bytes()
        self.assertEqual(hashlib.sha256(body).hexdigest(), report['body_sha256'])
        self.assertEqual(len(body),report['body_bytes'])
        manifest = json.loads(RAW)
        manifest['schema'] = 2
        manifest['sources'] = [r for r in manifest['sources'] if r['repository_id'] == 980873950]
        raw = json.dumps(manifest).encode()
        started = datetime.fromisoformat(report['started_at'])
        received = datetime.fromisoformat(report['completed_at'])
        class SavedClock(ClockNow):
            def utcnow(self):
                return started + timedelta(seconds=self.seconds)
        def replay(pin):
            clock = SavedClock()
            headers = tuple(report['public_headers'].items())
            transport = FakeTransport(clock,[response(body=body,headers=headers,
                delay=(received-started).total_seconds())])
            return collect_pinned(self.repo,pin,raw,1,self.recipes,lambda value: transport,
                clock,Credential(),source_revision=REV,max_file_bytes=CAP,
                max_run_requests=1,max_run_bytes=1_000_000)
        tree, outcome = replay(None)
        apps = decode_document(tree['apps.yaml'],CAP)['apps']
        self.assertTrue(apps)
        self.assertEqual(set(apps.values()),{980873950})
        obj = decode_document(tree['repositories/980873950.yaml'],CAP)
        original = {str(r['id']): r for r in json.loads(body) if not r['draft']}
        self.assertEqual(set(obj['releases']),set(original))
        self.assertEqual(obj['observed_at'],received.strftime('%Y-%m-%dT%H:%M:%SZ'))
        for rid, facts in obj['releases'].items():
            self.assertEqual(facts['tag'],original[rid]['tag_name'])
            self.assertEqual({aid: a['name'] for aid,a in facts['assets'].items()},
                             {str(a['id']):a['name'] for a in original[rid]['assets']})
        pin = publish_local(self.repo,apps,{'980873950':obj},schema=schema_url(REV),
                            max_file_bytes=CAP,expected_parent=None)
        refreshed, outcome = replay(pin)
        self.assertEqual(refreshed,tree)
        self.assertEqual(outcome['previous_publication'],pin)
        self.assertEqual(git(self.repo,'rev-parse','refs/heads/catalog').decode().strip(),pin)

    def test_prior_alias_reassignment_refuses_before_transport(self):
        pin = self.seed()
        body = dict(self.small_recipes)['programs/x86_64/obsidian']
        wrong = body.replace(b'obsidianmd/obsidian-releases',b'neovim/neovim')
        with self.assertRaisesRegex(Refusal,'conflicting_app_identity'):
            self.collect(pin,recipes=[('programs/x86_64/obsidian',wrong)])


if __name__ == '__main__':
    unittest.main()
