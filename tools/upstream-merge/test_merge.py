"""Each recipe path gets exactly one outcome, and the gate catches a wrong merge.

Recipe texts are pinned Git objects: originals from the upstream merge base
and converted forms from the fork commit that published the bulk conversion.
"""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import merge as m
from originals import Originals

BASE='7b4f831e66705ef7a0064fff25940ce972d331bf'
FORK='6277377aeb91daff3bed22f98bea39ba67a4b2c3'
ORIGINALS=Originals(m.ROOT)
TEMPLATES=m.convert.layouts()
DECLARED='programs/x86_64/0xfx'
LONG='programs/x86_64/1devtool'
POLICIES=[dict(recipe='x86_64/1devtool',source_recipe='x86_64/1devtool',
    source_sha256='e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    repository_id=1179864103,repository='stoicsoft/1devtool-releases',channel='any',url_rules=[],
    catalog_app='1devtool',dispatch_recipe='x86_64/1devtool',source_aliases=['stoicsoft/1devtool-releases'])]


def show(commit,path):
    return ORIGINALS.read(commit,path).encode()


def plan(base,ours,theirs,owned=(),registry=()):
    return {row['path']:row for row in m.plan(base,ours,theirs,set(owned),list(registry),TEMPLATES)}


class Plan(unittest.TestCase):
    def setUp(self):
        self.original=show(BASE,DECLARED)
        # The fork's declaration as converted since ticket 32: 0xfx is a 3.6
        # instance, so it opts in to the template's --no-sandbox strip.
        self.declaration=show(FORK,DECLARED).replace(b'/releases\nCATALOG_FORMAT=',
            b'/releases\nDESKTOP_STRIP_NO_SANDBOX=true\nCATALOG_FORMAT=',1)
        assert b'DESKTOP_STRIP_NO_SANDBOX' in self.declaration
        self.base={DECLARED:self.original};self.ours={DECLARED:self.declaration}

    def one(self,theirs,**options):
        return plan(self.base,self.ours,{DECLARED:theirs} if theirs is not None else {},**options)[DECLARED]

    def test_converted_recipe_upstream_left_alone_is_kept_byte_for_byte(self):
        row=self.one(self.original)
        self.assertEqual((row['outcome'],row['data']),('untouched',self.declaration))

    def test_upstream_change_is_converted_again_in_the_same_form(self):
        changed=self.original.replace(b'armv7l" | head',b'armv7l\\|riscv64" | head')
        self.assertEqual(changed.count(b'riscv64'),2)
        row=self.one(changed)
        self.assertEqual((row['outcome'],row['form_before'],row['form_after']),('re-converted','declaration','declaration'))
        self.assertIn(b'armv7l|riscv64',row['data'])
        self.assertTrue(row['fork_form_reproduced'])
        self.assertEqual(row['sha256'],m.digest(row['data']))

    def test_refused_declaration_falls_to_a_long_recipe_then_to_the_original(self):
        extra=self.original.replace(b'# LINK TO PATH\n',b'# LINK TO PATH\necho linked\n')
        row=self.one(extra)
        self.assertEqual((row['outcome'],row['form_after']),('fell back','long'))
        self.assertEqual([refusal['form'] for refusal in row['refusals']],['declaration'])
        self.assertIn(b'echo linked\n',row['data'])
        self.assertEqual(row['policies'][0]['repository_id'],1186679146)
        dynamic=self.original.replace(b'grep -oi "https.*download.*mage$"',b'grep -oi "https.*$(uname -m).*mage$"')
        row=self.one(dynamic)
        self.assertEqual((row['outcome'],row['form_after'],row['data']),('fell back','original',dynamic))
        self.assertEqual([refusal['form'] for refusal in row['refusals']],['declaration','long'])
        self.assertEqual(row['policies'],[])

    def test_new_source_repository_is_never_bound_to_the_old_identity(self):
        moved=self.original.replace(b'averagenative/0xfx',b'someone-else/0xfx')
        row=self.one(moved)
        self.assertEqual((row['outcome'],row['form_after'],row['data']),('fell back','original',moved))

    def test_hand_edits_to_a_converted_form_end_and_are_reported(self):
        edited=self.declaration.replace(b"CATALOG_CHANNEL=any",b"CATALOG_CHANNEL=stable")
        changed=self.original.replace(b'armv7l" | head',b'armv7l\\|riscv64" | head')
        row=plan(self.base,{DECLARED:edited},{DECLARED:changed})[DECLARED]
        self.assertEqual(row['outcome'],'re-converted')
        self.assertFalse(row['fork_form_reproduced'])
        self.assertIn(b'CATALOG_CHANNEL=any',row['data'])

    def test_long_recipe_is_converted_again_with_its_policies(self):
        original=show(BASE,LONG);changed=original.replace(b'notify-send "$APP is updated!"',b'notify-send "$APP updated"')
        row=plan({LONG:original},{LONG:show(FORK,LONG)},{LONG:changed},registry=POLICIES)[LONG]
        self.assertEqual((row['outcome'],row['form_before'],row['form_after']),('re-converted','long','long'))
        self.assertIn(b'notify-send "$APP updated"',row['data'])
        self.assertEqual(row['policies'][0]['source_sha256'],m.digest(row['data']))

    def test_upstream_deletion_additions_and_unconverted_changes(self):
        self.assertEqual(self.one(None)['outcome'],'deleted')
        self.assertIsNone(self.one(None)['data'])
        self.assertEqual(self.one(None)['identities'][0]['repository_id'],1186679146)
        rows=plan({'programs/x86_64/plain':b'old\n'},{'programs/x86_64/plain':b'old\n'},
                  {'programs/x86_64/plain':b'new\n','programs/x86_64/added':b'fresh\n'})
        self.assertEqual({path:(row['outcome'],row['data']) for path,row in rows.items()},
            {'programs/x86_64/plain':('taken from upstream',b'new\n'),'programs/x86_64/added':('taken from upstream',b'fresh\n')})

    def test_fork_owned_recipe_is_never_overwritten_and_upstream_changes_are_named(self):
        changed=self.original+b'# upstream edit\n'
        row=self.one(changed,owned=[DECLARED])
        self.assertEqual((row['outcome'],row['data'],row['upstream']),('fork-owned kept',self.declaration,'changed'))
        row=self.one(None,owned=[DECLARED])
        self.assertEqual((row['outcome'],row['data'],row['upstream']),('fork-owned kept',self.declaration,'deleted'))
        only='programs/x86_64/mine'
        row=plan({},{only:b'mine\n'},{only:b'theirs\n'},owned=[only])[only]
        self.assertEqual((row['outcome'],row['data'],row['upstream']),('fork-owned kept',b'mine\n','added'))

    def test_undecided_cases_stop_the_plan(self):
        only='programs/x86_64/mine'
        for arguments,message in ((({},{only:b'mine\n'},{}),'not in the fork-owned list'),
                (({},{only:b'mine\n'},{only:b'theirs\n'}),'both added'),
                (({only:b'x\n'},{},{only:b'x\n'},[only]),'does not have')):
            with self.assertRaisesRegex(m.Problem,message):plan(*arguments)

    def test_every_path_in_either_parent_has_one_row(self):
        ours={DECLARED:self.declaration,'programs/x86_64/kept':b'k\n','programs/aarch64/mine':b'm\n'}
        theirs={DECLARED:self.original,'programs/x86_64/kept':b'k\n','programs/i686/new':b'n\n'}
        rows=plan({DECLARED:self.original,'programs/x86_64/kept':b'k\n','programs/x86_64/both-gone':b'g\n'},
                  ours,theirs,owned=['programs/aarch64/mine'])
        self.assertEqual(set(rows),set(ours)|set(theirs))
        self.assertTrue(all(row['outcome'] in m.OUTCOMES for row in rows.values()))


class Lists(unittest.TestCase):
    def test_fork_lines_are_added_to_upstreams_list_in_name_order(self):
        base='◆ alpha : a\n◆ gamma : c\n'
        ours='◆ alpha : a\n◆ beta : mine\n◆ gamma : c\n◆ zeta : mine too\n'
        theirs='◆ alpha : a, reworded\n◆ delta : new\n'
        self.assertEqual(m.merge_list(base,ours,theirs),
            '◆ alpha : a, reworded\n◆ beta : mine\n◆ delta : new\n◆ zeta : mine too\n')

    def test_owned_list_is_exact_paths(self):
        self.assertEqual(m.owned_paths('# note\n\nprograms/x86_64/zmx\n'),{'programs/x86_64/zmx'})
        for source in ('programs/x86_64/zmx\nprograms/x86_64/zmx\n','x86_64/zmx\n','programs/x86_64/a/b\n'):
            with self.assertRaises(m.Problem):m.owned_paths(source)


class Gate(unittest.TestCase):
    """A small real Git merge, with the receipt its plan would write."""

    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory();self.addCleanup(self.temporary.cleanup)
        self.root=Path(self.temporary.name)
        self.git('init','-q','-b','fork');self.git('config','user.email','t@example.org');self.git('config','user.name','t')
        manager='#!/bin/sh\nAMREPO="https://raw.githubusercontent.com/ivan-hc/AM/main"\necho run\n'
        self.write({'APP-MANAGER':manager,'modules/install.am':'install\n','README.md':'r\n',
                    'programs/x86_64/kept':'kept\n','programs/x86_64/gone':'gone\n','programs/x86_64/plain':'old\n'})
        self.commit('base');self.git('branch','upstream')
        self.write({'APP-MANAGER':manager.replace('ivan-hc/AM/main','mareklangiewicz/AM/main-marek')
                        +'ALT_GH="https://api.github.com" # MAREK-FORK\n',
                    'programs/x86_64/kept':'kept, converted\n','programs/x86_64/mine':'mine\n'})
        self.commit('fork');self.ours=self.head()
        self.git('checkout','-q','upstream')
        self.write({'APP-MANAGER':manager+'echo more\n','programs/x86_64/plain':'new\n','programs/x86_64/added':'added\n'})
        (self.root/'programs/x86_64/gone').unlink()
        self.commit('upstream');self.theirs=self.head()
        self.git('checkout','-q','fork')
        subprocess.run(['git','-C',str(self.root),'merge','-q','--no-commit','--no-ff','upstream'],capture_output=True)
        self.write({'APP-MANAGER':manager.replace('ivan-hc/AM/main','mareklangiewicz/AM/main-marek')
                        +'ALT_GH="https://api.github.com" # MAREK-FORK\necho more\n'})
        self.git('add','-A')
        rows=[('kept','untouched','kept, converted\n'),('mine','fork-owned kept','mine\n'),
              ('plain','taken from upstream','new\n'),('added','taken from upstream','added\n'),('gone','deleted',None)]
        self.receipt=dict(ours=self.ours,upstream=self.theirs,files={},recipes=[
            dict(path='programs/x86_64/'+name,outcome=outcome,sha256=m.digest(data.encode() if data else None))
            for name,outcome,data in rows])

    def git(self,*arguments):
        subprocess.run(['git','-C',str(self.root),*arguments],check=True,capture_output=True)

    def head(self):
        return subprocess.check_output(['git','-C',str(self.root),'rev-parse','HEAD'],text=True).strip()

    def write(self,files):
        for path,content in files.items():
            (self.root/path).parent.mkdir(parents=True,exist_ok=True);(self.root/path).write_text(content)

    def commit(self,message):
        self.git('add','-A');self.git('commit','-q','-m',message)

    def test_a_merge_that_matches_its_receipt_passes_before_and_after_the_commit(self):
        self.assertEqual(m.gate(self.root,self.receipt),[])
        self.commit('merge')
        self.assertEqual(m.gate(self.root,self.receipt),[])

    def test_each_kind_of_wrong_merge_is_named(self):
        cases=((lambda:self.write({'programs/x86_64/kept':'kept, edited\n'}),'programs/x86_64/kept: differs from the receipt'),
               (lambda:self.write({'programs/x86_64/stray':'s\n'}),'programs/x86_64/stray: in the merge but not in the receipt'),
               (lambda:self.write({'programs/x86_64/gone':'gone\n'}),'programs/x86_64/gone: differs from the receipt'),
               (lambda:self.write({'APP-MANAGER':(self.root/'APP-MANAGER').read_text().replace(' # MAREK-FORK','')}),
                'APP-MANAGER: 0 of 1 MAREK-FORK marks left'),
               (lambda:self.write({'APP-MANAGER':(self.root/'APP-MANAGER').read_text().replace('mareklangiewicz/AM/main-marek','ivan-hc/AM/main')}),
                'APP-MANAGER: lost AMREPO="https://raw.githubusercontent.com/mareklangiewicz/AM/main-marek"'),
               (lambda:self.receipt['recipes'].pop(),'programs/x86_64/gone: 0 receipt rows'),
               (lambda:self.receipt.update(upstream=self.ours),'the receipt is for another pair of parents'))
        for change,expected in cases:
            saved={path:path.read_bytes() for path in self.root.rglob('*') if path.is_file() and '.git' not in path.parts}
            receipt=json.loads(json.dumps(self.receipt))
            change()
            self.assertIn(expected,m.gate(self.root,self.receipt))
            for path in list(self.root.rglob('*')):
                if path.is_file() and '.git' not in path.parts and path not in saved:path.unlink()
            for path,data in saved.items():path.write_bytes(data)
            self.receipt=receipt
        self.assertEqual(m.gate(self.root,self.receipt),[])

    def test_a_receipt_without_its_listing_reads_it_from_the_git_directory(self):
        recipes=self.receipt.pop('recipes');self.receipt['recipes_sha256']=m.listing_digest(recipes)
        path=m.listing_path(self.root)
        self.assertEqual(path.parent,(self.root/'.git').resolve())
        with self.assertRaisesRegex(m.Problem,'no per-recipe listing'):m.with_listing(self.receipt,path)
        path.write_text(json.dumps(recipes[:-1]))
        with self.assertRaisesRegex(m.Problem,'not the listing of this receipt'):m.with_listing(self.receipt,path)
        path.write_text(json.dumps(recipes))
        self.assertEqual(m.gate(self.root,m.with_listing(self.receipt,path)),[])

    def test_a_row_must_mean_what_its_outcome_says(self):
        self.write({'programs/x86_64/plain':'neither\n'})
        self.receipt['recipes'][2]['sha256']=m.digest(b'neither\n')
        self.assertIn('programs/x86_64/plain: not what "taken from upstream" means',m.gate(self.root,self.receipt))


if __name__=='__main__':unittest.main()
