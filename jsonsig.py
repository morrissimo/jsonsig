# -*- coding: utf-8 -*-

import argparse
import codecs
import json
import logging
import os
import os.path

# use the pycrypto package for cleaner access to OpenSSL
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA


def build_logger(log_level=logging.DEBUG):
    """
    Build and return console logger instance with the specified logging level
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    ch.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s'))
    logger.addHandler(ch)
    return logger


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
            self.logger.debug("Reading existing private key from {}".format(self.private_key_path))
            with open(self.private_key_path, "rb") as f:
                key = RSA.importKey(f.read())
                pri = key.exportKey("PEM")
            self.logger.debug("Reading existing public key from {}".format(self.public_key_path))
            with open(self.public_key_path, "rb") as f:
                pub = f.read()
        return key, pri, pub

    def generate_keys(self):
        self.logger.debug("Generating new {} bit key pair...".format(bits))
        key = RSA.generate(bits=4096)
        pub = key.publickey().exportKey("PEM")
        pri = key.exportKey("PEM")
        os.makedirs(self.args.key_cache_dir, exist_ok=True)
        self.logger.debug("Caching new private key in {}".format(self.private_key_path))
        with open(self.private_key_path, "wb") as f:
            f.write(pri)
        self.logger.debug("Caching new public key in {}".format(self.public_key_path))
        with open(self.public_key_path, "wb") as f:
            f.write(pub)
        # TODO chmod generated keyfiles for security
        self.logger.debug("...done")
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
        """
        Process command line args and options, ensuring valid values and setting defaults
        """
        parser = argparse.ArgumentParser(prog="jsonsig",
                description="RSA public/private key encode and repackage an input string as JSON")
        parser.add_argument('payload',
                help="A UTF-8 string to be pub/pri key encoded, up to {} chars.".format(self.MAX_INPUT_LEN))
        parser.add_argument('--key-cache-dir', default=None,
                help="Where cached RSA keys will be stored. Defaults to '<current working dir>/keys'")
        parser.add_argument('--key-cache-name', default=parser.prog,
                help="The basename of the cached keys. Defaults to %(prog)s")
        parser.add_argument('--verbose', action="store_true", help="Enable extra status output")
        self.args = parser.parse_args()
        if len(self.args.payload) > self.MAX_INPUT_LEN:
            raise ValueError('Input value must be {} chars or less'.format(self.MAX_INPUT_LEN))
        if self.args.key_cache_dir is None:
            self.args.key_cache_dir = os.path.abspath(os.path.join(os.getcwd(), "keys"))
        if self.args.key_cache_name is None:
            self.args.key_cache_name = parser.prog
        # build logger
        log_level = logging.DEBUG if self.args.verbose else logging.INFO
        self.logger = build_logger(log_level=log_level)

    def main(self):
        self.parse_args()
        response = self.build_response()
        print(json.dumps(response, indent=2))


if __name__ == '__main__':
    JsonSigner().main()
