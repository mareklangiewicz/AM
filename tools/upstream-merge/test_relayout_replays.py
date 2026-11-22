"""Replays of pinned commits: relayout reproduces the two re-conversions that shipped.

Ticket 33 converted the long recipes that are instances of layout bb53f3180
(082502f64, on cf6255fc3). Ticket 32 added DESKTOP_STRIP_NO_SANDBOX=true to
the 579 declarations from layout cf50304fc, template 3.6 (d85c3851b). Both ran
on the originals of upstream ba061a639, the merge base then and now.

The derived row files are compared by their rows: since ticket 29 they are
written one row per line, and these replays start from indented copies.
"""
import json
import unittest

import relayout as r

UPSTREAM='ba061a639a'
ROWS={r.merge.REGISTRY,r.merge.CATALOG_ONLY,r.merge.APPIMAGES}


def changed(old,new):
    out=r.merge.git(r.ROOT,'diff','--name-only',old,new,'--','programs').stdout.decode().split()
    return set(out)


def show(commit,path):
    return r.merge.git(r.ROOT,'show',commit+':'+path).stdout


class Replay(unittest.TestCase):
    def replay(self,layout,ours,shipped,form,derived):
        result=r.plan(r.ROOT,layout,ours,UPSTREAM,(form,))
        converted={row['path']:row['data'] for row in result['rows'] if row['outcome']=='re-converted'}
        self.assertEqual(set(converted),changed(ours,shipped))
        for path,data in converted.items():self.assertEqual(data,show(shipped,path),path)
        self.assertEqual(result['differences'],[])
        self.assertEqual(result['retire'],{})
        # Exactly the derived files the shipped commit changed: the policy byte
        # for byte, the row files row for row; a reformat alone is no change.
        files={path:content for path,content in result['files'].items()
               if path not in ROWS or json.loads(content)!=json.loads(r.merge.text(r.ROOT,ours,path))}
        self.assertEqual(sorted(files),derived)
        for path,content in files.items():
            if path in ROWS:self.assertEqual(json.loads(content),json.loads(show(shipped,path)),path)
            else:self.assertEqual(content.encode(),show(shipped,path),path)
        return result

    def test_ticket_33_long_recipes_become_declarations(self):
        result=self.replay('bb53f3180','cf6255fc3','082502f64','long',sorted((r.merge.REGISTRY,r.merge.POLICY)))
        self.assertEqual(len([row for row in result['rows'] if row['outcome']=='re-converted']),1171)
        self.assertEqual(sorted(result['refused']),['programs/aarch64/python','programs/x86_64/deadbeef-nightly',
                                                    'programs/x86_64/python'])

    def test_ticket_32_declarations_gain_the_layout_setting(self):
        result=self.replay('cf50304fc:templates/AM-SAMPLE-AppImage','d85c3851b^','d85c3851b','declaration',[])
        # 579 in the tree (ticket 32 Answer); the pinned corpus has 586.
        self.assertEqual(len([row for row in result['rows'] if row['outcome']=='re-converted']),579)
        # Written by hand in the v3 migration (80122f46e), with their own asset
        # patterns; ticket 32 left them alone, and re-converting would not.
        self.assertEqual(sorted(result['refused']),['programs/x86_64/'+app for app in
            ('0x808','0xsynth','3mf-katalog-manager','aeroftp','ag-repatch','agent-buddy')])
        for reason in result['refused'].values():self.assertRegex(reason,'^selection would change: .*asset_pattern')


if __name__=='__main__':unittest.main()
