#!/usr/bin/env python3
"""Normalization of GitHub releases responses."""
import unittest
from bounded import normalize


def release(rid=457):
    return dict(id=rid, draft=False, tag_name='v3', name='café\n\u2028',
                html_url='https://github.com/example/app/releases/tag/v3',
                published_at='2026-11-03T00:00:00Z', prerelease=True,
                assets=[dict(id=790, name='app', browser_download_url='https://example.com/app',
                             size=0, content_type='', digest=None)])


class Normalize(unittest.TestCase):
    def test_keeps_text_exact_and_omits_null_digest(self):
        result = normalize([release()], 100)
        self.assertEqual(result['457']['title'], 'caf\u00e9\n\u2028')
        self.assertNotIn('digest', result['457']['assets']['790'])

    def test_drafts_are_not_releases(self):
        draft = release(); draft['draft'] = True
        self.assertEqual(normalize([draft], 100), {})

    def test_reject_unrepresentable_and_wrong_types(self):
        for key, value in [('id', True), ('id', 2**63), ('prerelease', 1),
                           ('published_at', '2026-02-30T00:00:00Z'),
                           ('tag_name', '\x00'), ('tag_name', '\ud800'),
                           ('html_url', 'http://example.com')]:
            raw = release(); raw[key] = value
            with self.assertRaises((ValueError, UnicodeError)):
                normalize([raw], 100)
        raw = release(); raw['assets'] *= 2
        with self.assertRaises(ValueError):
            normalize([raw], 100)
