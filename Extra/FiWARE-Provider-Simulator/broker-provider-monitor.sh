#
#Copyright Odin Solutions S.L. All Rights Reserved.
#
#SPDX-License-Identifier: Apache-2.0
#

#!/bin/bash
while true; do curl --location --request GET 'http://localhost:1026/v2/entities?limit=100&options=count' --header 'Accept: application/json' --header 'Fiware-Service: demo1' --header 'Fiware-ServicePath: /demo'; echo ""; sleep 3; done
