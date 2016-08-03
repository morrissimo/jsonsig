# -*- coding: utf-8 -*-

import codecs
import json
import os
import os.path
import shutil
import unittest

from jsonsig import JsonSigner


class CLITests(unittest.TestCase):

    def setUp(self):
        self.jsonsig = JsonSigner()

    def test_payload_arg_valid(self):
        self.jsonsig.parse_args(['this is a test payload'])

    def test_payload_arg_too_long(self):
        with self.assertRaises(ValueError):
            self.jsonsig.parse_args(['a' * (self.jsonsig.MAX_INPUT_LEN + 1)])


class FileIOTests(unittest.TestCase):

    def setUp(self):
        self.jsonsig = JsonSigner()
        self.jsonsig.parse_args(['testing file i/o stuff'])
        self.target_file_path = os.path.join(os.path.abspath(os.getcwd()), 'test', 'test.tmp')
        self.target_file_contents = 'This is a test file. It can be safely deleted.'

    def tearDown(self):
        if os.path.exists(self.target_file_path):
            os.remove(self.target_file_path)

    def test_can_create_file(self):
        self.jsonsig.write_file(self.target_file_path, bytes(self.target_file_contents, 'utf-8'))
        self.assertTrue(os.path.exists(self.target_file_path))
        # treat reading the file and validating its content as a separate test
        with self.subTest():
            with open(self.target_file_path, 'rb') as f:
                contents = f.read()
            self.assertEqual(codecs.decode(contents, 'utf-8'), self.target_file_contents)


class KeyTests(unittest.TestCase):
    """
    Some test case name games in here (test_1_*, test_2_*, etc) to ensure the cases run
    in the order we want (order is determined by string-sorting the method names); namely,
    that basic key generation works first, then key caching (which leverages the key gen
    test), then cached key reading (which leverages key gen and caching)
    """

    def setUp(self):
        self.jsonsig = JsonSigner()
        self.jsonsig.parse_args(['testing key stuff'])
        # override select args for testing
        self.jsonsig.args.key_size = 1024
        self.jsonsig.args.key_cache_dir = os.path.join(os.path.abspath(os.getcwd()), 'test')
        self.jsonsig.args.key_cache_name = 'jsonsig.test'

    def tearDown(self):
        if os.path.exists(self.jsonsig.args.key_cache_dir):
            shutil.rmtree(self.jsonsig.args.key_cache_dir)

    def test_1_can_generate_keys(self):
        key, pri, pub = self.jsonsig.generate_keys()
        self.assertIsNotNone(key, msg="new RSA key object is None")
        self.assertIsNotNone(pri, msg="new private key object is None")
        self.assertIsNotNone(pub, msg="new public key object is None")
        return key, pri, pub

    def test_2_can_cache_keys(self):
        key, pri, pub = self.test_1_can_generate_keys()
        self.jsonsig.cache_keys(pri, pub)
        self.assertTrue(os.path.exists(self.jsonsig.private_key_path), msg="cached private key not found")
        self.assertTrue(os.path.exists(self.jsonsig.public_key_path), msg="cached public key not found")

    def test_3_can_read_cached_keys(self):
        self.test_2_can_cache_keys()
        key, pri, pub = self.jsonsig.read_keys()
        self.assertIsNotNone(key, msg="cached RSA key object is None")
        self.assertIsNotNone(pri, msg="cached private key object is None")
        self.assertIsNotNone(pub, msg="cached public key object is None")


class PayloadTests(unittest.TestCase):

    def setUp(self):
        self.jsonsig = JsonSigner()
        self.jsonsig.parse_args(['testing payload stuff'])
        # override select args for testing
        self.jsonsig.args.key_size = 1024
        self.jsonsig.args.key_cache_dir = os.path.join(os.path.abspath(os.getcwd()), 'test')
        self.jsonsig.args.key_cache_name = 'jsonsig.test'

    def tearDown(self):
        if os.path.exists(self.jsonsig.args.key_cache_dir):
            shutil.rmtree(self.jsonsig.args.key_cache_dir)

    def test_can_encrypt_payload(self):
        key, pri, pub = self.jsonsig.generate_keys()
        enc_payload = self.jsonsig.encrypt_payload(self.jsonsig.args.payload, key)
        self.assertIsNotNone(enc_payload, msg="encrypted payload is None")

    def test_can_build_response(self):
        response = self.jsonsig.build_response()
        # verify we got something back from the response building code..
        self.assertIsNotNone(response, msg="response dict is None")
        # ..and that it was a dict with the required keys
        self.assertIn("message", response.keys())
        self.assertIn("signature", response.keys())
        self.assertIn("pubkey", response.keys())

    def test_response_is_jsonifiable(self):
        """
        not explicitly checking for anything here - if it's jsonifiable,
        it'll return; otherwise, it'll blow up
        """
        response = self.jsonsig.build_response()
        response_json = json.dumps(response, indent=2)


if __name__ == '__main__':
    unittest.main()
