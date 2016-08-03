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
# don't forget to activate the new virtualenv!
$ . ./venv/bin/activate
```
* install requirements via pip:
```bash
$ pip install -r requirements.txt
```
* run tests (optional):
```bash
$ python tests.py
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
An actual example: issuing the following command...
```bash
$ python jsonsig.py 'testing'
```
...should produce output like (but not exactly like!) this:
```bash
$ python jsonsig.py 'testing'
{
  "pubkey": "-----BEGIN PUBLIC KEY-----\nMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEA4jEpVnxibGQRBSmjU1rY\nNjfsS8cJ/6USQh4Oe2sUdlGKJuYf7cU6a4nSBNApkPkhpVosSAbZPuxGcCNQ6nq5\nZipg4M3f5vmf0y1Di+0Zj5f4xztsY5NI9um0yH8Z8e8+b2Vpn2SuEXAJ54NLo/Zd\nPJ2u4O0O/OoCzk+jgHsXzZuWibhWmO7SqFDf48boVZg5vUI4HU7dVgw5c7CQIN0/\nX7Bzp0SAVus48J2G6s+pp0JIMBb9dCPRz2cJohNm8FPrmjExJ5GOtWjyE5dJUAFg\nfvIVsOIfDVpOIE1vkEhcdhlOLuR8myxB/SzK+zR/rQCCJOKajJBuaIfKJdUmdRjq\nGosvDiUTh20OXpnwpY5ZcBmU3nTvWs9hVouX0gH3paPoWL02903lOCs4eVUvw5IG\nKBpzMznaj+Sp0g8Rq370tLy7e0vX2tLx+GuBoltwXSH6fzVhi2dQIxwblBcJGOZK\nK6WoJR8sN3V90gxH+Z03gkDCfGSnPThxRMxgeai8Xc7MSjK6zo32r8kiO/lpjwI4\nLlgVrHJNMohwdHFMlIp792HB4F3KmSmbtCcl1RGNsmkDTkE/bSXVDBLPoyWpsOLN\no04E79sDy14bOepoa3U8ahZceynZJGBkRAxPQY5n76EKmPqrfRkMFfoUQtxbFIjS\nOSXNSfUHsDBgsXRLk8FlNjcCAwEAAQ==\n-----END PUBLIC KEY-----",
  "message": "testing",
  "signature": "RPvc+AiqtydeBjCO1YCFjQKkeEU44611Gv+XFNwmJgivwip4U9+8UrHtpW88/MGoFRfC5D8QLEul\n86IgLNusvoUC+i8geIEkrC2XJt7iUKtSNbFSsZkMPbEBWmcgFMTjWnWVabsoyFF7Z6xnx3Nfr96m\ny9Zk7JdJuzFma+1pivEn6pL2r1xyqRPBd6czyiD4GZOyx+moC4F874dpbaa2oE8oi8ICzYYhVypi\n5rUiZkwXbCwNiJUBgtn4GtuP1GWpbTDI6Y7cCWXOZ9H7heCzbYrHnHHcPCh97pfum5xOmbt0OwwJ\nfK9QbkFOql+i8F9JjXSXqo07KRefhI7dZ2eZ8lnZPu3OjU+cLbE+sPyZ6zDX2BE43t1I59f8tUvi\nSfJHHhuxbL5V6EC/MNowIzBnnm4T/cbpZVXIhyN3sZQAG2rKSjxfHplgVJe89uJbMj4SPpWS1yZx\nahGdKfkeCKUaOfq5eTpgUVba3Z+lIDdlisLxHXiw8WhkHfKBNly/1wxc3zNCLNE0jTrI2dMQNAe6\ncZ3cEwAuI5yPVKhFZaujReSV2O7qADHMAQAcW5Fn9mZZS8NS6NpWr/JAWFN0ukwRbpIU/AGqBxdS\nmFfxEkyHkNvL0+gCGXASAhRIgfESPXRA5pKDmMOE5BTX9EgYyg2Qq/vmECDdpSIzQEf4rBBYwDU=\n"
}
```


## Todos
* ~~unit tests~~ done!
* branched implementation demonstrating no-third-party architecture (but, yuk)

## Notes
I've opted to ignore the "no third party" requirement from my initial implementation because:
* there are several mature libraries that are either first-class crypto libraries unto themselves (eg, pycrypto) or wrap and "prettify" usage of other crypto libraries (eg, pyopenssl);
* it would make the resulting implementation messier (Shell out to OpenSSL binaries..? Bleh) and possibly open to various security risks that seemed to make the constraint unjustifiable - at least, not without more context as to why the constraint was specified
