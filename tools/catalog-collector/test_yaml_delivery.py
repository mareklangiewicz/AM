"""Offline authenticated acquisition and adversarial archive checks."""
import copy
import hashlib
import io
from pathlib import Path
import stat
import struct
import unittest
from unittest.mock import patch
import zipfile

from storage import canonical
import test_yaml_staging as staging_tests
from test_yaml_staging import POLICY, REV
import yaml_delivery as delivery
import yaml_staging as staging


def zipped(files):
    output = io.BytesIO()
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as archive:
        for name, body in files:
            archive.writestr(name,body)
    return output.getvalue()


class Acquisition(unittest.TestCase):
    setUpClass = classmethod(staging_tests.Staging.setUpClass.__func__)
    setUp = staging_tests.Staging.setUp
    produce = staging_tests.Staging.produce

    def package(self):
        self.produce()
        files = [(p.relative_to(self.output).as_posix(),p.read_bytes())
                 for p in self.output.rglob('*') if p.is_file()]
        self.files = files
        self.raw_zip = zipped(files)
        self.sha = hashlib.sha256(self.raw_zip).hexdigest()
        self.meta = dict(id=42,expired=False,name='yaml-bootstrap-10-1',
            size_in_bytes=len(self.raw_zip),digest='sha256:'+self.sha,
            workflow_run=dict(id=10,head_sha=REV,repository_id=1,
                              head_repository_id=1,head_branch='main-marek'))
        self.accepted = Path(self.directory.name)/'accepted'

    def acquire(self, meta=None, raw=None, sha=None):
        with patch('delivery.bounded',side_effect=[canonical(meta or self.meta),
                                                  self.raw_zip if raw is None else raw]) as api:
            result = delivery.acquire(self.context,self.raw,REV,POLICY,self.recipes,
                '42',self.sha if sha is None else sha,b'opaque-token',self.accepted,repo=self.repo)
        return result, api

    def test_authenticated_round_trip_and_no_publication(self):
        self.package()
        tree, api = self.acquire()
        actual, receipt = staging.read_staged(self.accepted,self.limits)
        self.assertEqual(actual,tree)
        self.assertEqual(actual,staging.read_staged(self.output,self.limits)[0])
        self.assertEqual(api.call_count,2)
        self.assertEqual(api.call_args_list[1].kwargs['cap'],delivery.archive_cap(self.limits))
        self.assertEqual(self.accepted.stat().st_mode & 0o777,0o700)
        self.assertEqual(__import__('yaml_publication').git(self.repo,'for-each-ref'),b'')

    def test_wrong_identity_digest_and_bounds_reject(self):
        self.package()
        for key, value in (('id',43),('expired',True),('name','yaml-bootstrap-10-2'),
                           ('digest','sha256:'+'a'*64),('size_in_bytes',True),
                           ('size_in_bytes',delivery.archive_cap(self.limits)+1)):
            meta = copy.deepcopy(self.meta); meta[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.acquire(meta=meta)
        for key,value in (('id',11),('head_sha','a'*40),('repository_id',2),
                          ('head_repository_id',2),('head_branch','other')):
            meta = copy.deepcopy(self.meta); meta['workflow_run'][key] = value
            with self.subTest(key=key),self.assertRaises(ValueError):
                self.acquire(meta=meta)
        with self.assertRaises(ValueError):
            self.acquire(raw=self.raw_zip+b'corruption')
        self.assertFalse(self.accepted.exists())

    def test_context_refusal_and_existing_output_before_network(self):
        with patch('delivery.bounded') as api:
            self.context['yaml_policy_sha256'] = 'a'*64
            with self.assertRaises(ValueError):
                delivery.acquire(self.context,self.raw,REV,POLICY,self.recipes,
                    '42','a'*64,b'token',self.output,repo=self.repo)
            api.assert_not_called()
        self.context['yaml_policy_sha256'] = hashlib.sha256(POLICY).hexdigest()
        self.output.mkdir()
        with patch('delivery.bounded') as api, self.assertRaises(ValueError):
            delivery.acquire(self.context,self.raw,REV,POLICY,self.recipes,
                '42','a'*64,b'token',self.output,repo=self.repo)
        api.assert_not_called()

    def test_authenticated_but_invalid_receipt_creates_no_output(self):
        self.package()
        self.raw_zip = zipped([(p,b'{}' if p == 'receipt.json' else b) for p,b in self.files])
        self.sha = hashlib.sha256(self.raw_zip).hexdigest()
        self.meta.update(digest='sha256:'+self.sha,size_in_bytes=len(self.raw_zip))
        with self.assertRaises((ValueError,KeyError)):
            self.acquire()
        self.assertFalse(self.accepted.exists())

    def test_closed_layout_duplicate_traversal_and_modes(self):
        self.package()
        bad_paths = ['../outside','/absolute','candidate/../apps.yaml','candidate/receipt.json',
                     'candidate/repositories/01.yaml']
        for path in bad_paths:
            with self.subTest(path=path),self.assertRaises(ValueError):
                delivery.unpack(zipped(self.files+[(path,b'bad')]),self.limits)
        raw = self.raw_zip.replace(b'candidate/apps.yaml',b'candidate/apps\x00yaml')
        with self.assertRaises(ValueError):
            delivery.unpack(raw,self.limits)
        for mode in (stat.S_IFLNK|0o600,stat.S_IFREG|0o700,stat.S_IFIFO|0o600):
            info = zipfile.ZipInfo('candidate/apps.yaml'); info.external_attr = mode << 16
            with self.assertRaises(ValueError):
                delivery.unpack(zipped([(info,b'bad'),('receipt.json',b'{}')]),self.limits)
        with self.assertWarns(UserWarning):
            raw = zipped(self.files+[self.files[0]])
        with self.assertRaises(ValueError):
            delivery.unpack(raw,self.limits)

    def test_directory_entries_and_all_resource_bounds(self):
        self.package()
        tree, receipt = delivery.unpack(zipped([('candidate/',b''),
            ('candidate/repositories/',b''),*self.files]),self.limits)
        self.assertIn('apps.yaml',tree)
        for key in ('max_files','max_file_bytes','max_tree_bytes','max_receipt_bytes'):
            with self.subTest(key=key),self.assertRaises(ValueError):
                delivery.unpack(self.raw_zip,dict(self.limits,**{key:1}))
        for raw in (b'not zip',self.raw_zip[:-1],self.raw_zip+b'extra'):
            with self.assertRaises(ValueError):
                delivery.unpack(raw,self.limits)
        raw = bytearray(self.raw_zip)
        eocd = raw.rfind(b'PK\x05\x06')
        struct.pack_into('<HH',raw,eocd+8,65535,65535)
        with patch('yaml_delivery.zipfile.ZipFile') as parser,self.assertRaises(ValueError):
            delivery.unpack(bytes(raw),self.limits)
        parser.assert_not_called()


if __name__ == '__main__':
    unittest.main()
