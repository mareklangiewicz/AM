"""A recipe's selection policies as CATALOG_* lines in its own header (ticket 26)."""
import unittest

from recipe_declarations import policy_lines, policy_rows, with_policy

HEAD = '#!/bin/sh\n# AM-CATALOG-RECIPE 1\nCATALOG_FORMAT=3\nAMREPO=${AMREPO-}\n'
BODY = 'version=$(sh "/opt/am/modules/catalog-yaml.am" x86_64/demo --url "$@") || exit 1\n'
UPDATER = "cat >> ./AM-updater << 'EOF'\n#!/bin/sh\n# AM-CATALOG-RECIPE 1\nCATALOG_FORMAT=3\nset -u\nEOF\n"
RULES = [dict(pattern='https.*mage$', ignore_case=True, exclude=False),
         dict(pattern='aarch64|arm64', ignore_case=True, exclude=True)]


def url_row(recipe='x86_64/demo', **fields):
    row = dict(recipe=recipe, source_recipe='x86_64/demo', repository_id=7, repository='Owner/Demo',
               channel='any', url_rules=RULES, catalog_app='demo', dispatch_recipe=recipe,
               source_aliases=['Owner/Demo'])
    row.update(fields)
    return row


IMAGE = dict(recipe='x86_64/demo', repository_id=9, endpoint='latest', release_rule='stable_published_desc',
             rules=RULES)


class PolicyLines(unittest.TestCase):
    def round_trip(self, urls=(), image=None, head=HEAD):
        text = with_policy(head+BODY+UPDATER, policy_lines(list(urls), image))
        self.assertEqual(policy_rows('x86_64/demo', text), (list(urls), image))
        return text

    def test_one_selection_writes_only_what_differs_from_its_defaults(self):
        text = self.round_trip([url_row()])
        self.assertEqual(text, HEAD.replace('CATALOG_FORMAT=3\n', 'CATALOG_FORMAT=3\n'
            'CATALOG_REPOSITORY_ID=7\nCATALOG_REPOSITORY=Owner/Demo\nCATALOG_CHANNEL=any\n'
            'CATALOG_URL_RULES=\'[{"pattern":"https.*mage$","ignore_case":true,"exclude":false},'
            '{"pattern":"aarch64|arm64","ignore_case":true,"exclude":true}]\'\n')+BODY+UPDATER)

    def test_later_selections_are_numbered_and_keep_their_own_fields(self):
        second = url_row('x86_64/demo.select-2', repository_id=8, repository='other/demo', channel='stable',
                         catalog_app='demo-two', dispatch_recipe='x86_64/demo',
                         source_aliases=['Old/Name', 'other/demo'], selection='git-branch',
                         git_ref='refs/heads/main', git_file='VERSION')
        third = url_row('x86_64/demo.select-3', tag_pattern='^v[0-9]', tag_exclude='rc')
        text = self.round_trip([url_row(), second, third])
        self.assertIn("CATALOG_DISPATCH_RECIPE_2=x86_64/demo\n", text)
        self.assertIn("CATALOG_SOURCE_ALIASES_2=Old/Name\n", text)
        self.assertIn("CATALOG_TAG_PATTERN_3='^v[0-9]'\n", text)

    def test_a_lowercase_alias_of_the_repository_is_implied(self):
        # Dispatch compares aliases lowercased, so the case variant adds nothing.
        text = with_policy(HEAD+BODY, policy_lines([url_row(source_aliases=['Owner/Demo', 'owner/demo'])], None))
        self.assertNotIn('ALIASES', text)
        self.assertEqual(policy_rows('x86_64/demo', text)[0][0]['source_aliases'], ['Owner/Demo'])

    def test_an_appimage_policy_keeps_the_lines_already_after_the_format(self):
        head = HEAD.replace('CATALOG_FORMAT=3\n', 'CATALOG_FORMAT=3\nCATALOG_RECIPE="x86_64/demo"\n'
                            'CATALOG_ALIAS="https://api.github.com/repos/o/demo/releases"\n')
        text = self.round_trip(image=IMAGE, head=head)
        self.assertIn('CATALOG_ALIAS="https://api.github.com/repos/o/demo/releases"\n'
                      'CATALOG_APPIMAGE_ENDPOINT=latest\nCATALOG_REPOSITORY_ID=9\nCATALOG_CHANNEL=stable\n', text)
        self.round_trip(image=dict(IMAGE, release_rule='published_desc', endpoint='list'), head=head)

    def test_rewriting_replaces_the_old_lines_and_nothing_else(self):
        once = with_policy(HEAD+BODY+UPDATER, policy_lines([url_row(), url_row('x86_64/demo.select-2')], None))
        again = with_policy(once, policy_lines([url_row(channel='stable')], None))
        self.assertEqual(again, with_policy(HEAD+BODY+UPDATER, policy_lines([url_row(channel='stable')], None)))
        self.assertEqual(with_policy(once, []), HEAD+BODY+UPDATER)
        self.assertEqual(policy_rows('x86_64/demo', HEAD+BODY), ([], None))

    def test_malformed_blocks_are_refused(self):
        good = with_policy(HEAD+BODY, policy_lines([url_row(), url_row('x86_64/demo.select-2')], None))
        for name, text in (
                ('gap', good.replace('_2=', '_3=')),
                ('unknown name', good.replace('CATALOG_CHANNEL=any', 'CATALOG_COLOUR=any')),
                ('duplicate', good.replace('CATALOG_CHANNEL=any\n', 'CATALOG_CHANNEL=any\nCATALOG_CHANNEL=any\n', 1)),
                ('not literal', good.replace('CATALOG_REPOSITORY_ID=7', 'CATALOG_REPOSITORY_ID=$ID')),
                ('bad channel', good.replace('CATALOG_CHANNEL=any', 'CATALOG_CHANNEL=beta', 1)),
                ('bad rules', good.replace('"exclude":false}', '"exclude":0}', 1)),
                ('missing field', good.replace('CATALOG_REPOSITORY=Owner/Demo\n', '', 1)),
                ('both kinds', good.replace('CATALOG_FORMAT=3\n', 'CATALOG_FORMAT=3\nCATALOG_APPIMAGE_ENDPOINT=list\n'))):
            with self.subTest(name), self.assertRaises(ValueError):
                policy_rows('x86_64/demo', text)
        with self.assertRaises(ValueError):
            with_policy('#!/bin/sh\n'+BODY, policy_lines([url_row()], None))


if __name__ == '__main__':
    unittest.main()
