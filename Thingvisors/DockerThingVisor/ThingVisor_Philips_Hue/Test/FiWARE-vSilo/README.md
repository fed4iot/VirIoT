# License

Tenant Simulator source code files are made avaialable under the Apache License, Version 2.0 (Apache-2.0), located into the LICENSE file.

# README

This software sends updates to vSilo local broker to cause the commands' executions in the provider environment.


## How To Run

### Local Docker deployment

By default configuration, the docker-compose file is configured to deploy a unique tenant which starts and stops alternatively a device (device001). 

Configure the next docker-compose environment variables:
- `vSiloProtocol`, `vSiloHost`: the protocol and public IP of the vSilo Context Broker
- `vSiloPort`: <broker-exposed-port-vSilo>

and run:

```bash
./build.sh
docker-compose up -d
```