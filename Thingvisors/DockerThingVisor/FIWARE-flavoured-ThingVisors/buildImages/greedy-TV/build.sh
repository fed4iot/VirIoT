#
#Copyright Odin Solutions S.L. All Rights Reserved.
#
#SPDX-License-Identifier: Apache-2.0
#

#!/bin/bash

cd ../../
docker build -t fed4iot/fiware-greedy-tv -f buildImages/greedy-TV/Dockerfile  ./
cd buildImages/greedy-TV/
