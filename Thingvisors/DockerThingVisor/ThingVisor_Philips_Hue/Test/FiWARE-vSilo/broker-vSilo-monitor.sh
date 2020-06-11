#
#Copyright Odin Solutions S.L. All Rights Reserved.
#
#SPDX-License-Identifier: Apache-2.0
#

#!/bin/bash
while true; do curl -X GET -H 'Accept: application/json' http://localhost:$1/v2/entities?limit=100&options=count ; echo ""; sleep 3; done