"""Partial API failures must never become verified identity coverage."""
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

import bulk_sources as b


class BulkSources(unittest.TestCase):
    def response(self):
        return dict(data=dict(rateLimit=dict(remaining=900,cost=1),
            r0=dict(databaseId=1,nameWithOwner='owner/project',isPrivate=False,
                    releases=dict(nodes=[dict(databaseId=2,isDraft=False)]))))

    def test_scoped_missing_is_reported_without_discarding_success(self):
        response=self.response()
        response['data']['r1']=None
        response['errors']=[dict(type='NOT_FOUND',path=['r1'])]
        rows,_=b.parse(['owner/project','gone/project'],response)
        self.assertEqual([row['status'] for row in rows],['verified','unavailable'])
        self.assertNotIn('repository_id',rows[1])

    def test_global_partial_errors_and_unexplained_null_refuse(self):
        for error in (dict(type='RATE_LIMITED'),dict(type='NOT_FOUND',path=['r9']),
                      dict(type='INTERNAL',path=['r0'])):
            response=self.response();response['errors']=[error]
            with self.assertRaises(ValueError):b.parse(['owner/project'],response)
        response=self.response();response['data']['r0']=None
        with self.assertRaises(ValueError):b.parse(['owner/project'],response)

    def test_private_draft_or_absent_release_is_never_coverage(self):
        response=self.response();response['data']['r0']['isPrivate']=True
        rows,_=b.parse(['owner/project'],response)
        self.assertEqual(rows[0]['status'],'not_public')
        response=self.response();response['data']['r0']['releases']['nodes']=[]
        rows,_=b.parse(['owner/project'],response)
        self.assertEqual(rows[0]['status'],'no_public_release')
        response=self.response();response['data']['r0']['releases']['nodes'][0]['isDraft']=True
        with self.assertRaises(ValueError):b.parse(['owner/project'],response)

    def test_shell_and_graphql_fragments_cannot_be_query_names(self):
        for name in ('owner/project") {viewer {login}}','owner/project;cat /etc/passwd',
                     'owner/project/extra','../project'):
            with self.assertRaises(ValueError):b.query([name])

    def test_catalog_inventory_does_not_enroll_incidental_dependency_mentions(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            path=root/'programs/x86_64/example';path.parent.mkdir(parents=True)
            path.write_text("APP=example\nSITE='owner/project'\nversion=$(curl -Ls 'https://api.github.com/repos/owner/project/releases' | head -1)\n")
            scan=dict(source='a'*40,candidates=[],ambiguous=[],unsupported_recipes=['programs/x86_64/example'])
            with patch.object(b,'ROOT',root):result=b.inventory(scan)
            self.assertEqual(result['candidates'][0]['repository'],'owner/project')
            path.write_text('APP=example\n# icon dependency: https://github.com/other/dependency\n')
            with patch.object(b,'ROOT',root):result=b.inventory(scan)
            self.assertEqual(result['candidates'],[])
            self.assertEqual(result['unresolved'][0]['reason'],'primary_source_review')

    def test_literal_site_endpoint_includes_same_line_source_variants(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);path=root/'programs/x86_64/example';path.parent.mkdir(parents=True)
            path.write_text('APP=example\nSITE1="owner/first"; SITE2="owner/second"\nSITE="$SITE1"\nversion=$(curl -Ls https://api.github.com/repos/"$SITE"/releases | head -1)\n')
            scan=dict(source='a'*40,candidates=[],ambiguous=[],unsupported_recipes=['programs/x86_64/example'])
            with patch.object(b,'ROOT',root):result=b.inventory(scan)
            self.assertEqual({r['repository'] for r in result['ambiguous'][0]['bindings']},
                             {'owner/first','owner/second'})
            self.assertEqual(b.literal_sites('SITE="$(touch /tmp/forbidden)"'),[])


if __name__=='__main__':unittest.main()
