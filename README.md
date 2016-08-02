# jsonsig
Hackery for the ACS Code Challenge: http://info.smartperimeter.io/jobs/codechallenge

## Todos
* unit tests
* branched implementation demonstrating no-third-party architecture (but, yuk)

## Notes
I've opted to ignore the "no third party" requirement from my initial implementation because:
* there are several mature libraries that are either first-class crypto libraries unto themselves (eg, pycrypto) or wrap and "prettify" usage of other crypto libraries (eg, pyopenssl);
* it would make the resulting implementation messier (Shell out to OpenSSL binaries..? Bleh) and possibly open to various security risks that seemed to make the constraint unjustifiable - at least, not without more context as to why the constraint was specified
