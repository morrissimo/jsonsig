# jsonsig
Hackery for the ACS Code Challenge: http://info.smartperimeter.io/jobs/codechallenge

## Requirements
* Python 3
* Access to Pypi (for pip-specified dependencies)

## Setup
* Clone or fork this repo:
```bash
$ git clone https://github.com/morrissimo/jsonsig.git
```
* Create a new virtualenv (using python3!) in the cloned directory:
```bash
$ cd jsonsig
$ virtualenv ./venv
```
* install requirements via pip:
```bash
$ pip install -r requirements.txt
```

## Usage
Help is included!
```bash
$ python jsonsig.py -h
usage: jsonsig [-h] [--key-cache-dir KEY_CACHE_DIR]
               [--key-cache-name KEY_CACHE_NAME] [--verbose]
               payload

RSA public/private key encode and repackage an input string as JSON

positional arguments:
  payload               A UTF-8 string to be pub/pri key encoded, up to 250
                        chars.

optional arguments:
  -h, --help            show this help message and exit
  --key-cache-dir KEY_CACHE_DIR
                        Where cached RSA keys will be stored. Defaults to
                        '<current working dir>/keys'
  --key-cache-name KEY_CACHE_NAME
                        The basename of the cached keys. Defaults to jsonsig
  --verbose             Enable extra status output
```


## Todos
* unit tests
* branched implementation demonstrating no-third-party architecture (but, yuk)

## Notes
I've opted to ignore the "no third party" requirement from my initial implementation because:
* there are several mature libraries that are either first-class crypto libraries unto themselves (eg, pycrypto) or wrap and "prettify" usage of other crypto libraries (eg, pyopenssl);
* it would make the resulting implementation messier (Shell out to OpenSSL binaries..? Bleh) and possibly open to various security risks that seemed to make the constraint unjustifiable - at least, not without more context as to why the constraint was specified
