
#
#Copyright Odin Solutions S.L. All Rights Reserved.
#
#SPDX-License-Identifier: Apache-2.0
#

#!/bin/bash

mosquitto_sub -h localhost -p 1884 -t "#" -v | xargs -d$'\n' -L1 bash -c 'date "+%Y-%m-%d %T.%3N $0"'
