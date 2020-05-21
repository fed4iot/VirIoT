# License

FIWARE ThingVisor source code files are made avaialable under the Apache License, Version 2.0 (Apache-2.0), located into the LICENSE file.

# README

This project contains different ThingVisors which obtain information from a FIWARE's Orion Context Broker (OCB) using NGSIv2 API.

## How To Run

Inside of buildImages's folder, you can find a subfolder per ThingVisor type. Each buildImages's subfolder contains README.md and Test.md files which explain how can deploy and test each ThingVisor individually. The ThingVisor type are:

- [AggrValue](./buildImages/AggrValue-TV): obtains an entity, which contains the sum of free spaces of parking sites (aggregated value).
- [greedy](./buildImages/greedy-TV): obtains various information depending "Fiware-Services" that want to be considered.
- [ParkingSite](./buildImages/ParkingSite-TV): obtains parking sites information.
- [Regulated Parking Zone (RPZ)](./buildImages/RPZ-TV): obtains regulated parking zones information (RPZ).

Optionally, if you want to build all different ThingVisors images in one step, you can run [build-all-images.sh](./build-all-images.sh) and read the corresponding README.md and Test.md files.