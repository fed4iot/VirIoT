# License

PEP-Proxy Project source code files are made avaialable under the Apache License, Version 2.0 (Apache-2.0), located into the LICENSE file.

# Test files introduction (nodejs)
The next files are an example of how integrate with authentication (Keyrock) and authorisation components (Capability Manager and PEP-Proxy)  to access a generic target througth PEP-Proxy using nodejs.
- app.js: Main file. Contains all integration requests to authentication and authorisation components.
- keyrock.js, capman.js, pepproxy.js: Util files. Where the client really connects to differents authentication and authorisation components.
- config.json: Contains differents param's of the program that must be configured.
- package.json: Contains the definition of npm software (dependencies, main file...).

# Launch test file
To launch test file you can execute next commands, previously configure config.json (endpoints and policy's devices):

To install required modules.
```sh
npm install
```

To launch it.
```sh
npm start
```