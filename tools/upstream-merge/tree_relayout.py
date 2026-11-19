"""Whole-tree replays: relayout reproduces the two re-conversions that shipped.

Ticket 33 converted the long recipes that are instances of layout bb53f3180
(082502f64, on cf6255fc3). Ticket 32 added DESKTOP_STRIP_NO_SANDBOX=true to
the 579 declarations from layout cf50304fc, template 3.6 (d85c3851b). Both ran
on the originals of upstream ba061a639, the merge base then and now.
"""
import unittest

import relayout as r

UPSTREAM='ba061a639a'


def changed(old,new):
    out=r.merge.git(r.ROOT,'diff','--name-only',old,new,'--','programs').stdout.decode().split()
    return set(out)


def show(commit,path):
    return r.merge.git(r.ROOT,'show',commit+':'+path).stdout


class Replay(unittest.TestCase):
    def replay(self,layout,ours,shipped,form):
        result=r.plan(r.ROOT,layout,ours,UPSTREAM,(form,))
        converted={row['path']:row['data'] for row in result['rows'] if row['outcome']=='re-converted'}
        self.assertEqual(set(converted),changed(ours,shipped))
        for path,data in converted.items():self.assertEqual(data,show(shipped,path),path)
        self.assertEqual(result['differences'],[])
        self.assertEqual(result['retire'],{})
        return result

    def test_ticket_33_long_recipes_become_declarations(self):
        result=self.replay('bb53f3180','cf6255fc3','082502f64','long')
        self.assertEqual(len([row for row in result['rows'] if row['outcome']=='re-converted']),1171)
        self.assertEqual(sorted(result['refused']),['programs/aarch64/python','programs/x86_64/deadbeef-nightly',
                                                    'programs/x86_64/python'])
        for path in (r.merge.REGISTRY,r.merge.POLICY):
            self.assertEqual(result['files'][path].encode(),show('082502f64',path),path)

    def test_ticket_32_declarations_gain_the_layout_setting(self):
        result=self.replay('cf50304fc','d85c3851b^','d85c3851b','declaration')
        # 579 in the tree (ticket 32 Answer); the pinned corpus has 586.
        self.assertEqual(len([row for row in result['rows'] if row['outcome']=='re-converted']),579)
        # Written by hand in the v3 migration (80122f46e), with their own asset
        # patterns; ticket 32 left them alone, and re-converting would not.
        self.assertEqual(sorted(result['refused']),['programs/x86_64/'+app for app in
            ('0x808','0xsynth','3mf-katalog-manager','aeroftp','ag-repatch','agent-buddy')])
        for reason in result['refused'].values():self.assertRegex(reason,'^selection would change: .*asset_pattern')
        for path,content in result['files'].items():
            self.assertEqual(content.encode(),show('d85c3851b',path),path)


if __name__=='__main__':unittest.main()
