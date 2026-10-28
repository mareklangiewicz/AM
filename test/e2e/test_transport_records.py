import json
from pathlib import Path
import tempfile
import unittest

from transport_records import read_transport_records


class TransportRecords(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def test_empty(self):
        self.assertEqual(read_transport_records(self.root), [])

    def test_checkpoint_and_deterministic_order(self):
        old = self.root/'00.json'; old.write_text('{"url":"old"}')
        checkpoint = set(self.root.iterdir())
        (self.root/'02.json').write_text('{"url":"second"}')
        (self.root/'01.json').write_text('{"url":"first"}')
        self.assertEqual(read_transport_records(self.root, excluding=checkpoint),
                         [{'url':'first'}, {'url':'second'}])
        self.assertEqual(len(read_transport_records(self.root)), 3)

    def test_malformed_record_is_not_silenced(self):
        (self.root/'bad.json').write_text('{')
        with self.assertRaises(json.JSONDecodeError):
            read_transport_records(self.root)
