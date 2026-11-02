"""Conservation and refusal checks for the offline thousand-recipe work queue."""
import hashlib
import json
from pathlib import Path
import unittest

from throughput import audit

ROOT = Path(__file__).resolve().parents[2]
DIRECTORY = ROOT/'docs/track/release-catalog/research/appimage-next-large-batch-20261102'


class Throughput(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (DIRECTORY/'payload.json').read_bytes()
        cls.manifest = (ROOT/'docs/track/release-catalog/design/staged-manifest.json').read_bytes()

    def test_frozen_queue_conserved_and_identities_never_split(self):
        result = audit(self.raw, self.manifest, lambda p: (ROOT/p).read_bytes())
        payload = json.loads(self.raw)
        cohorts = result['cohorts']
        aliases = [a for c in cohorts for a in c['aliases']]
        recipes = [p for c in cohorts for p in c['recipes']]
        identities = [p for c in cohorts for p in c['identity_requests']]
        self.assertEqual(set(aliases), {r['alias'] for r in payload['rows']})
        self.assertEqual(len(aliases), 732)
        self.assertEqual(len(set(recipes)), 1000)
        self.assertEqual(len(recipes), 1000)
        self.assertEqual(len(identities), len(set(identities)))
        self.assertEqual(len(identities), 730)
        self.assertTrue(all(c['endpoints'] <= result['source_cap'] for c in cohorts))
        self.assertEqual(result['payload_sha256'], hashlib.sha256(self.raw).hexdigest())
        self.assertGreater(result['synthetic_union_manifest_bytes'], result['manifest_cap'])
        self.assertFalse(result['metadata_verified'])

    def test_changed_recipe_refuses_before_report(self):
        with self.assertRaisesRegex(ValueError, 'recipe_changed'):
            audit(self.raw, self.manifest, lambda p: b'changed')

    def test_duplicate_alias_or_path_refuses(self):
        payload = json.loads(self.raw)
        payload['rows'].append(payload['rows'][0])
        with self.assertRaisesRegex(ValueError, 'queue_alias'):
            audit(json.dumps(payload).encode(), self.manifest, lambda p: (ROOT/p).read_bytes())
        payload = json.loads(self.raw)
        payload['rows'][1]['recipes'].append(payload['rows'][0]['recipes'][0])
        with self.assertRaisesRegex(ValueError, 'queue_path'):
            audit(json.dumps(payload).encode(), self.manifest, lambda p: (ROOT/p).read_bytes())

    def test_substituting_a_smaller_manifest_retires_earlier_sources(self):
        from test_migration_capacity import files, initial_attempts, GEN, REV
        from test_brave_migration import accepted_brave_tree
        from storage import apply, canonical, validate
        base = accepted_brave_tree()
        _, tree = files(base, initial_attempts(base))
        previous = validate(tree)
        manifest = json.loads(previous['manifest_json'])
        manifest['sources'] = manifest['sources'][:6]
        candidate, _ = apply(tree, canonical(manifest), [],
            workflow_identity=previous['workflow_repository_id'], generated_at=GEN,
            revision=REV, run={'id': '2', 'attempt': '1'})
        after = validate(candidate)
        retired = [rid for rid, entry in after['entries'].items()
                   if entry['availability'] == 'retired']
        self.assertEqual(len(retired), 46)
        for rid in retired:
            self.assertEqual(after['entries'][rid]['observation'],
                             previous['entries'][rid]['observation'])
            self.assertFalse(any(target['active'] for target in after['aliases'].values()
                                 if target['request_id'] == rid))


if __name__ == '__main__':
    unittest.main()
