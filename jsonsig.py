# -*- coding: utf-8 -*-

import argparse
import codecs
import json
import os
import os.path

# use the pycrypto package for cleaner access to OpenSSL
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

# TODO: add logging


class JsonSigner(object):

    MAX_INPUT_LEN = 250

    @property
    def private_key_path(self):
        return os.path.join(self.args.key_cache_dir, self.args.key_cache_name)

    @property
    def public_key_path(self):
        return os.path.join(self.args.key_cache_dir, self.args.key_cache_name) + ".pub"

    def read_keys(self):
        key = pri = pub = None
        if os.path.exists(self.private_key_path) and os.path.exists(self.public_key_path):
            print("Reading existing private key from {}".format(self.private_key_path))
            with open(self.private_key_path, "rb") as f:
                key = RSA.importKey(f.read())
                pri = key.exportKey("PEM")
            print("Reading existing public key from {}".format(self.public_key_path))
            with open(self.public_key_path, "rb") as f:
                pub = f.read()
        return key, pri, pub

    def generate_keys(self):
        print("Generating new key pair...")
        key = RSA.generate(bits=4096)
        pub = key.publickey().exportKey("PEM")
        pri = key.exportKey("PEM")
        os.makedirs(self.args.key_cache_dir, exist_ok=True)
        print("Caching new private key in {}".format(self.private_key_path))
        with open(self.private_key_path, "wb") as f:
            f.write(pri)
        print("Caching new public key in {}".format(self.public_key_path))
        with open(self.public_key_path, "wb") as f:
            f.write(pub)
        # TODO chmod generated keyfiles for security
        print("...done")
        return key, pri, pub

    def get_keys(self):
        key, pri, pub = self.read_keys()
        if not all([key, pri, pub]):
            key, pri, pub = self.generate_keys()
        return key, pub, pri

    def encrypt_payload(self, payload, key):
        cipher = PKCS1_OAEP.new(key, hashAlgo=SHA256)
        return cipher.encrypt(bytes(payload, "utf-8"))

    def build_response(self):
        key, pub, pri = self.get_keys()
        enc_payload = self.encrypt_payload(self.args.payload, key)
        response = {
            "message": self.args.payload,
            "signature": codecs.encode(enc_payload, "base64").decode("utf-8"),
            "pubkey": pub.decode("utf-8"),
        }
        return response

    def parse_args(self):
        parser = argparse.ArgumentParser(description="Public key encode and repackage an input string as JSON", prog="jsonsig")
        parser.add_argument('payload', help="The string to be encoded, up to {} chars.".format(self.MAX_INPUT_LEN))
        parser.add_argument('--key-cache-dir', default=None, help="Where cached RSA keys will be stored. Defaults to 'os.getcwd()/keys'")
        parser.add_argument('--key-cache-name', default=None, help="The basename of the cached keys. Defaults to %{prog}s")
        self.args = parser.parse_args()
        if len(self.args.payload) > self.MAX_INPUT_LEN:
            raise ValueError('Input value must be {} chars or less'.format(self.MAX_INPUT_LEN))
        if self.args.key_cache_dir is None:
            self.args.key_cache_dir = os.path.abspath(os.path.join(os.getcwd(), "keys"))
        if self.args.key_cache_name is None:
            self.args.key_cache_name = parser.prog

    def main(self):
        self.parse_args()
        response = self.build_response()
        print(json.dumps(response, indent=2))


if __name__ == '__main__':
    JsonSigner().main()
