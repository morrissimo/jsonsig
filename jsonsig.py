# -*- coding: utf-8 -*-

import argparse
import codecs
import json
import logging
import os
import os.path
import stat

# use the pycrypto package
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


# permission specs for chmod purposes
RW_OWNER = stat.S_IRUSR | stat.S_IWUSR
RW_OWNER_R_GO = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH


class JsonSigner(object):

    # payloads greater than this length will raise a ValueError
    # TODO: could be a runtime option..?
    MAX_INPUT_LEN = 250

    @property
    def private_key_path(self):
        return os.path.join(self.args.key_cache_dir, self.args.key_cache_name)

    @property
    def public_key_path(self):
        return os.path.join(self.args.key_cache_dir, self.args.key_cache_name) + ".pub"

    def write_file(self, path, contents, perms=None):
        """
        Write provided content to disk and (optionally) apply
        the specified permissions.
        """
        # ensure the target dir exists
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "wb") as f:
            f.write(contents)
        if perms:
            os.chmod(path, perms)

    def generate_keys(self, bits=4096):
        """
        Generate a new RSA public/private keypair of the specified bit length.
        Returns the pycrypto key object, the PEM-encoded public key object,
        and the PEM-encoded private key object.
        """
        self.logger.debug("Generating new {} bit key pair...".format(bits))
        key = RSA.generate(bits=bits)
        pub = key.publickey().exportKey("PEM")
        pri = key.exportKey("PEM")
        self.logger.debug("...done")
        return key, pri, pub

    def cache_keys(self, pri, pub):
        """
        Store the provided private and public key objects on the file system, chmodded with
        reasonably secure permissions.
        """
        self.logger.debug("Caching new private key in {}".format(self.private_key_path))
        self.write_file(self.private_key_path, pri, perms=RW_OWNER)
        self.logger.debug("Caching new public key in {}".format(self.public_key_path))
        self.write_file(self.public_key_path, pub, perms=RW_OWNER_R_GO)

    def read_keys(self):
        """
        Look for cached key objects; if found, import and return them.
        If not found, return (None, None, None).
        """
        key = pri = pub = None
        # if either the public or private key object is missing, bail
        if os.path.exists(self.private_key_path) and os.path.exists(self.public_key_path):
            self.logger.debug("Reading existing private key from {}".format(self.private_key_path))
            with open(self.private_key_path, "rb") as f:
                key = RSA.importKey(f.read())
                pri = key.exportKey("PEM")
            self.logger.debug("Reading existing public key from {}".format(self.public_key_path))
            with open(self.public_key_path, "rb") as f:
                pub = f.read()
        return key, pri, pub

    def get_keys(self):
        """
        If a cached keypair is available, return it; otherwise, generate, cache and
        return a new keypair.
        """
        key, pri, pub = self.read_keys()
        if not all([key, pri, pub]):
            key, pri, pub = self.generate_keys()
            self.cache_keys(pri, pub)
        return key, pub, pri

    def encrypt_payload(self, payload, key):
        """
        Encrypt the provided payload using the cached pub-pri keypair according to PKCS#1 OAEP.
        See https://www.dlitz.net/software/pycrypto/api/2.6/Crypto.Cipher.PKCS1_OAEP-module.html
        and http://www.ietf.org/rfc/rfc3447.txt
        """
        cipher = PKCS1_OAEP.new(key, hashAlgo=SHA256)
        return cipher.encrypt(bytes(payload, "utf-8"))

    def build_response(self):
        """
        Generate and return the final dictionary, ready for JSONification
        Care must be given to encodings: the encrypted payload must first be converted from it's native byte structure
        to a base64 string, then to unicode for JSON readiness. Similarly, the PEM-encoded public key must be coverted
        to unicode as well.
        """
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
        # check params for validity
        if len(self.args.payload) > self.MAX_INPUT_LEN:
            raise ValueError('Input value must be {} chars or less'.format(self.MAX_INPUT_LEN))
        # set param defaults
        # ..handle these here instead of inline in the argument construct since they're a bit heavy
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
