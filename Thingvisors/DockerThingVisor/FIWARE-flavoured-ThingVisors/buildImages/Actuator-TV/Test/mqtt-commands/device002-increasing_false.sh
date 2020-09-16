
#
#Copyright Odin Solutions S.L. All Rights Reserved.
#
#SPDX-License-Identifier: Apache-2.0
#

#!/bin/bash

mosquitto_pub -h localhost -p 1883 -t vThing/thingvisorid-actuator/Device1/data_in -q 0 -m '{"meta":{"vSiloID":"tenant1_Silo1"},"data":[{"id":"urn:ngsi-ld:Device:002","type":"Device","increasing":{"type":"Property","value":{"cmd-value": "false","cmd-qos":"0","cmd-id":"4","cmd-nuri":["viriot:vSilo/tenant1_Silo1/data_in"]}}}]}';