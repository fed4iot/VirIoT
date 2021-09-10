# License

PEP-Proxy Project source code files are made avaialable under the Apache License, Version 2.0 (Apache-2.0), located into the LICENSE file.

# Test files introduction (python)
The next files are full examples of authentication, authorisation and access to MRD througth PEP.
- TestPOST.py: Sends a POST request of "urn:ngsi-ld:Sector:5" entity.
- TestGET.py: Sends a GET request of "urn:ngsi-ld:Sector:5" entity.
- TestPATCH.py: Sends a PATCH request to "urn:ngsi-ld:Sector:5" entity.
- TestDELETE.py: Sends a DELETE request to "urn:ngsi-ld:Sector:5" entity.

# Launch test files
To launch test files you can execute the next command, previously configure config.cfg (endpoints and policy's devices):

```sh
python3 <file.py>
```
