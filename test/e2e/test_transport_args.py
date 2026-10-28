import unittest
from pathlib import Path

from transport_args import download_destination


class DownloadDestination(unittest.TestCase):
    def test_supported_destinations(self):
        for tool, option in (('wget', '-O'), ('curl', '-o'), ('curl', '--output'), ('curl', '-Lo')):
            with self.subTest(tool=tool, option=option):
                self.assertEqual(download_destination(tool, [option, 'a file', 'https://fixture']), Path('a file'))

    def test_curl_stdout(self):
        self.assertIsNone(download_destination('curl', ['-Ls', 'https://fixture']))

    def test_invalid_forms(self):
        for tool, args in (('other', []), ('wget', ['https://fixture']),
                           ('curl', ['-O', 'https://fixture']), ('curl', ['-o']),
                           ('wget', ['-O', '']), ('curl', ['-o', '--head']),
                           ('curl', ['-o', 'a', '-o', 'b'])):
            with self.subTest(tool=tool, args=args), self.assertRaises(ValueError):
                download_destination(tool, args)
