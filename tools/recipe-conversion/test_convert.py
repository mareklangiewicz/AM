"""The conversion reproduces the fork's converted recipes and refuses the rest.

Originals come from the upstream merge base and expected results from the
fork commit that published the bulk conversion: pinned Git objects, so later
recipe changes do not move these tests.
"""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr,redirect_stdout
from unittest.mock import patch

import convert as c
from originals import Originals
from recipe_declarations import MARKER

BASE='7b4f831e66705ef7a0064fff25940ce972d331bf'
FORK='6277377aeb91daff3bed22f98bea39ba67a4b2c3'
ORIGINALS=Originals(c.ROOT)
TEMPLATES=c.layouts()


def show(commit,recipe):
    return ORIGINALS.read(commit,'programs/'+recipe)


STRIP='DESKTOP_STRIP_NO_SANDBOX=true\n'


def stripping(published):
    """A published 3.6 declaration as converted since ticket 32: the template's
    desktop sed removes --no-sandbox, so the declaration opts in to the same."""
    alias=published.index('\n',published.index('\nCATALOG_ALIAS=')+1)+1
    return published[:alias]+STRIP+published[alias:]


def identity(repository_id=1186679146,repository='averagenative/0xFX',requested='averagenative/0xfx'):
    return [dict(repository_id=repository_id,repository=repository,requested_repository=requested)]


class Declaration(unittest.TestCase):
    def convert(self,source,recipe='x86_64/0xfx',identities=None):
        return c.convert(source,recipe,'declaration',identities or identity(),TEMPLATES)

    def test_original_becomes_the_published_declaration(self):
        result=self.convert(show(BASE,'x86_64/0xfx'))
        self.assertEqual(result['text'],stripping(show(FORK,'x86_64/0xfx')))
        self.assertEqual(result['policies'],[])
        self.assertIn(MARKER,result['text'])

    def test_single_quotes_and_spacing_are_the_same_literals(self):
        for recipe in ('aarch64/cc-switch','x86_64/geeqie'):
            expected=show(FORK,recipe)
            if recipe=='aarch64/cc-switch':expected=stripping(expected)
            self.assertEqual(self.convert(show(BASE,recipe),recipe,c.declaration_identities(expected))['text'],expected)

    def test_template_that_strips_no_sandbox_declares_the_same(self):
        # 3.6 (cf50304fc) removes --no-sandbox from the desktop entry; 3.5
        # (b7c72a974) does not. The declaration keeps that behavior.
        self.assertIn(STRIP,self.convert(show(BASE,'x86_64/0xfx'))['text'])
        geeqie=show(FORK,'x86_64/geeqie')
        self.assertNotIn('DESKTOP_STRIP_NO_SANDBOX',
            self.convert(show(BASE,'x86_64/geeqie'),'x86_64/geeqie',c.declaration_identities(geeqie))['text'])

    def test_literal_app_variable_in_a_selector_is_written_out(self):
        source=show(BASE,'x86_64/0xfx').replace('grep -oi "https.*download.*mage$"','grep -oi "https.*download.*$APP.*mage$"')
        self.assertIn('"pattern":"https.*download.*0xfx.*mage$"',self.convert(source)['text'])

    def test_anything_outside_the_template_refuses(self):
        source=show(BASE,'x86_64/0xfx')
        updater=source.index('cat >> ./AM-updater')
        for changed,reason in (
                (source.replace('# LINK TO PATH\n','# LINK TO PATH\ntouch /tmp/unwanted\n'),'not an instance'),
                (source.replace('wget "$version" || exit 1','wget "$version" || exit 2',1),'not an instance'),
                (source[:updater]+source[updater:].replace('grep -vi "i386','grep -vi "x86_64\\|i386'),'disagree'),
                (source.replace('SITE="averagenative/0xfx"','SITE="other/project"'),'different repositories'),
                (source.replace('https://api.github.com/repos/averagenative/0xfx/releases','https://example.org/releases'),'not one GitHub releases read'),
                (source.replace('| head -1','| head -1; touch /tmp/unwanted'),'unsupported selector'),
                (source.replace('grep -oi "https.*download.*mage$"','grep -oi "https.*$(uname -m).*mage$"'),'dynamic selector'),
                (source.replace('grep -oi "https.*download.*mage$"','grep -oi "https.*$ARCH.*mage$"'),'dynamic selector'),
                (source.replace('grep -oi "https.*download.*mage$"','grep -oi "https.*download.*zip$"'),'direct AppImage suffix')):
            self.assertNotEqual(changed,source)
            with self.assertRaisesRegex(c.Refusal,reason):self.convert(changed)

    def test_identity_must_be_the_source_the_original_names(self):
        source=show(BASE,'x86_64/0xfx')
        with self.assertRaisesRegex(c.Refusal,'source alias mismatch'):
            self.convert(source,identities=identity(requested='other/project'))
        with self.assertRaisesRegex(c.Refusal,'exactly one catalog source'):
            self.convert(source,identities=identity()+identity(repository_id=2,repository='other/project',requested='other/project'))
        with self.assertRaisesRegex(c.Refusal,'app identity'):self.convert(source,recipe='x86_64/other')
        with self.assertRaisesRegex(c.Refusal,'no verified catalog source'):
            c.convert(source,'x86_64/0xfx','declaration',[],TEMPLATES)

    def test_converted_input_and_malformed_requests_are_not_converted_again(self):
        with self.assertRaisesRegex(c.Refusal,'already converted'):self.convert(show(FORK,'x86_64/0xfx'))
        source=show(BASE,'x86_64/0xfx')
        for arguments in ((source,'0xfx','declaration',identity()),(source,'x86_64/0xfx','wrapper',identity()),
                          (source,'x86_64/0xfx','declaration',[dict(repository_id='1',repository='a/b')])):
            with self.assertRaises(ValueError) as raised:c.convert(*arguments,TEMPLATES)
            self.assertNotIsInstance(raised.exception,c.Refusal)

    def test_changed_layout_object_refuses_to_load(self):
        rows=json.loads(c.LAYOUTS.read_text());rows[0]['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'reviewed hash'):load(rows)


def load(rows):
    """c.layouts() over these rows instead of the reviewed layouts.json."""
    with tempfile.TemporaryDirectory() as temporary:
        changed=Path(temporary)/'layouts.json';changed.write_text(json.dumps(rows))
        with patch.object(c,'LAYOUTS',changed):return c.layouts()


# bb53f3180 differs from the base b7c72a974 by this one desktop sed line.
SED='sed -i "s#Exec=[^ ]*#Exec=$APP#g; s#Icon=.*#Icon=/opt/$APP/icons/$APP#g'
SED_BASE='-'+SED+'" ./"$APP".desktop'
SED_STRIP='+'+SED+'; s# --no-sandbox##g" ./"$APP".desktop'


class LayoutDifferences(unittest.TestCase):
    """Every line a layout differs by from the base layout is accounted for."""

    def rows(self):
        return json.loads(c.LAYOUTS.read_text())

    def test_unmapped_differing_line_refuses_to_load(self):
        rows=self.rows()
        strip=next(row for row in rows if row['commit'].startswith('bb53f3180'))
        strip['differences']=[entry for entry in strip['differences'] if entry['line']!=SED_STRIP]
        with self.assertRaisesRegex(ValueError,'unmapped difference: bb53f3180.*--no-sandbox'):load(rows)

    def test_entry_for_a_line_that_no_longer_differs_refuses(self):
        rows=self.rows()
        rows[1]['differences'].append(dict(line='+touch /tmp/unwanted',neutral='stale'))
        with self.assertRaisesRegex(ValueError,'no longer differs: bb53f3180 [+]touch'):load(rows)

    def test_settings_and_mapped_lines_agree(self):
        rows=self.rows();strip=rows[1]
        strip['settings']={}
        with self.assertRaisesRegex(ValueError,'unset setting: bb53f3180'):load(rows)
        rows=self.rows();rows[0]['settings']={'DESKTOP_STRIP_NO_SANDBOX':'true'}
        with self.assertRaisesRegex(ValueError,'not backed by a difference: b7c72a974 DESKTOP_STRIP_NO_SANDBOX'):load(rows)

    def test_each_entry_is_exactly_one_kind_and_dropped_names_its_ticket(self):
        for change in (lambda entry:entry.update(neutral='also'),
                       lambda entry:entry.pop('setting'),
                       lambda entry:entry.update(setting=None,dropped='gone')):
            rows=self.rows();change(next(entry for entry in rows[1]['differences'] if entry['line']==SED_STRIP))
            with self.assertRaisesRegex(ValueError,'needs one setting, neutral or dropped'):load(rows)

    def test_reviewed_layouts_load_with_their_mappings(self):
        # 3.6's launcher lines were dropped until the shared installer took
        # them over for every declaration (ticket 37); now nothing is dropped.
        layouts={layout.identity:layout for layout in load(self.rows())}
        self.assertEqual(len(layouts),3)
        rows={row['commit'][:9]:row for row in self.rows()}
        self.assertEqual([entry['line'] for entry in rows['bb53f3180']['differences']],[SED_BASE,SED_STRIP])
        self.assertEqual([entry for row in rows.values() for entry in row.get('differences',[]) if 'dropped' in entry],[])
        handler=next(entry for entry in rows['cf50304fc']['differences'] if "if grep -qi '^NoDisplay=true$'" in entry['line'])
        self.assertIn('ticket 37',handler['neutral'])


class Long(unittest.TestCase):
    def test_install_steps_stay_and_selection_moves_to_a_policy(self):
        source=show(BASE,'x86_64/1devtool')
        found=[dict(repository_id=1179864103,repository='stoicsoft/1devtool-releases',catalog_app='1devtool')]
        result=c.convert(source,'x86_64/1devtool','long',found)
        self.assertEqual(result['text'],show(FORK,'x86_64/1devtool'))
        self.assertEqual([row['recipe'] for row in result['policies']],['x86_64/1devtool'])
        self.assertEqual(result['policies'][0]['source_sha256'],hashlib.sha256(result['text'].encode()).hexdigest())

    def test_each_selected_repository_needs_its_own_identity(self):
        source=show(BASE,'aarch64/86box')
        main=dict(repository_id=61964127,repository='86Box/86Box',catalog_app='86box')
        other=dict(repository_id=1177491291,repository='pkgforge-dev/86box-AppImage-Enhanced',catalog_app='86box.src-1177491291')
        result=c.convert(source,'aarch64/86box','long',[main,other])
        self.assertEqual(result['text'],show(FORK,'aarch64/86box'))
        self.assertEqual([row['recipe'] for row in result['policies']],['aarch64/86box','aarch64/86box.select-2'])
        with self.assertRaisesRegex(c.Refusal,'unverified selection source: pkgforge-dev/86box-AppImage-Enhanced'):
            c.convert(source,'aarch64/86box','long',[main])

    def test_run_time_source_choice_needs_an_identity_for_every_offered_repository(self):
        source=show(BASE,'x86_64/mpv')
        offered=c.SITE.findall(source)
        self.assertGreater(len(offered),1)
        self.assertRegex(source,c.bulk_recipe_urls.DYNAMIC)
        found=[dict(repository_id=index+1,repository=name) for index,name in enumerate(offered)]
        self.assertEqual(c.convert(source,'x86_64/mpv','long',found)['form'],'long')
        with self.assertRaisesRegex(c.Refusal,'no verified identity for source: '+offered[-1]):
            c.convert(source,'x86_64/mpv','long',found[:-1])

    def test_declaration_refusal_does_not_decide_the_long_form(self):
        source=show(BASE,'x86_64/1devtool')
        found=[dict(repository_id=1179864103,repository='stoicsoft/1devtool-releases')]
        with self.assertRaises(c.Refusal):c.convert(source,'x86_64/1devtool','declaration',found,TEMPLATES)
        self.assertEqual(c.convert(source,'x86_64/1devtool','long',found)['form'],'long')


class CommandLine(unittest.TestCase):
    def run_main(self,*arguments):
        out,err=io.StringIO(),io.StringIO()
        with redirect_stdout(out),redirect_stderr(err):code=c.main([str(a) for a in arguments])
        return code,out.getvalue(),err.getvalue()

    def test_prints_the_recipe_or_refuses_with_a_reason(self):
        with tempfile.TemporaryDirectory() as temporary:
            original=Path(temporary)/'original';original.write_text(show(BASE,'x86_64/0xfx'))
            arguments=(original,'--recipe','x86_64/0xfx','--form','declaration','--repository-id',1186679146,
                       '--repository','averagenative/0xFX','--requested-repository','averagenative/0xfx')
            code,out,err=self.run_main(*arguments)
            self.assertEqual((code,out,err),(0,stripping(show(FORK,'x86_64/0xfx')),''))
            original.write_text(show(BASE,'x86_64/0xfx')+'touch /tmp/unwanted\n')
            code,out,err=self.run_main(*arguments)
            self.assertEqual((code,out),(2,''))
            self.assertIn('refused: not an instance of a reviewed AppImage template',err)

    def test_long_recipe_is_not_printed_without_a_place_for_its_policies(self):
        with tempfile.TemporaryDirectory() as temporary:
            original=Path(temporary)/'original';original.write_text(show(BASE,'x86_64/1devtool'))
            arguments=(original,'--recipe','x86_64/1devtool','--form','long','--repository-id',1179864103,
                       '--repository','stoicsoft/1devtool-releases')
            code,out,err=self.run_main(*arguments)
            self.assertEqual((code,out),(2,''))
            policies=Path(temporary)/'policies.json'
            code,out,err=self.run_main(*arguments,'--policies',policies)
            self.assertEqual((code,out),(0,show(FORK,'x86_64/1devtool')))
            self.assertEqual(json.loads(policies.read_text())[0]['repository_id'],1179864103)


class Corpus(unittest.TestCase):
    """Every recipe the bulk conversion published is reproduced from its original."""

    @classmethod
    def setUpClass(cls):
        cls.base={};cls.fork={}
        for arch in ('x86_64','aarch64','i686','armv7l'):
            cls.base.update(ORIGINALS.recipes(BASE,'programs/'+arch+'/'))
            cls.fork.update(ORIGINALS.recipes(FORK,'programs/'+arch+'/'))

    def test_declarations(self):
        identical=stripped=0;refused=[]
        for path,expected in sorted(self.fork.items()):
            if MARKER not in expected or 'CATALOG_URL_RULES=' not in expected or path not in self.base:continue
            try:
                result=c.convert(self.base[path],path.removeprefix('programs/'),'declaration',c.declaration_identities(expected),TEMPLATES)
            except c.Refusal as refusal:
                refused.append((path,str(refusal)));continue
            if path=='programs/x86_64/pdf4qt':
                # Published with the selector's $APP kept as pattern text, which
                # matches nothing; the conversion writes the app name out.
                self.assertEqual(result['text'],expected.replace('https.*$APP.*x86_64','https.*pdf4qt.*x86_64'))
                self.assertNotEqual(result['text'],expected)
                continue
            if result['text']!=expected:
                # Ticket 32: the bulk conversion dropped 3.6's --no-sandbox strip.
                self.assertEqual(result['text'],stripping(expected),path)
                stripped+=1;continue
            identical+=1
        # odicto's original carries a hand-edited comment line, so it is not a
        # template instance; its declaration came through the old wrapper form.
        # 398 are 3.5 instances; 586 are 3.6 instances that now opt in to the strip.
        self.assertEqual((identical,stripped,refused),(398,586,[('programs/x86_64/odicto',
            'not an instance of a reviewed AppImage template')]))

    def test_long_recipes(self):
        # The registry is larger than the recipe reader's 1 MiB bound.
        registry=json.loads(subprocess.check_output(['git','-C',str(c.ROOT),'show',
            FORK+':tools/catalog-collector/recipe-url-policies.json']))
        rows={}
        for row in registry:rows.setdefault(row['source_recipe'],[]).append(row)
        identical=refused=0
        for recipe,expected in sorted(rows.items()):
            path='programs/'+recipe
            if path not in self.base:continue
            try:
                result=c.convert(self.base[path],recipe,'long',c.policy_identities(expected))
            except c.Refusal:
                refused+=1;continue
            self.assertEqual(result['text'],self.fork[path],path)
            self.assertEqual(result['policies'],expected,path)
            identical+=1
        # The refusals are the recipes adapted by hand after the bulk conversion.
        self.assertEqual((identical,refused),(8770,103))


if __name__=='__main__':unittest.main()
